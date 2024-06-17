import json
import yaml
from core.log import log
from urllib.parse import parse_qs, unquote
from core.slack import get_user_email, update_slack_message, send_giphy_response
from core.dynamodb import (set_approval, set_approval_status, set_rejection_status,
                           get_last_approval, has_approved, get_approvals, get_deployment_details)
from core.publisher import approval_payload_queue
from core.responses import divider, message_header, approval_msg, final_approval, approvers, context_info, rejected_msg

AUTHORIZED_USERS = None


def lambda_handler(event, context):
    body = parse_qs(event['body-json'])
    payload_encoded = body['payload'][0]
    payload_str = unquote(payload_encoded)
    payload = json.loads(payload_str)

    actions = payload.get('actions', [])
    user = payload.get('user', {})
    container = payload.get('container', {})
    channel_id = container.get('channel_id')
    message_ts = container.get('message_ts')

    action = actions[0]
    action_id = action.get('action_id')
    deploy_id = action.get('value')

    user_id = get_user_email(user.get('id'))

    log.info(f"Approval request from {user_id} for deployment id {deploy_id} with action {action_id} ")
    if action_id == 'reject_1':
        handle_rejection(user_id, channel_id, message_ts, deploy_id)
    else:
        handle_approval(user_id, channel_id, deploy_id, message_ts, action_id)


def response(status_code, message):
    return {
        'statusCode': status_code,
        'body': json.dumps({'text': message}),
        'headers': {
            'Content-Type': 'application/json'
        }
    }


def handle_approval(user_id, channel_id, deploy_id, message_ts, action_id):
    approver_mapping = {
        "second_approver": "first_approver",
        "first_approver": "second_approver",
        "rejected": "reject_1"
    }

    next_approval = approver_mapping.get(action_id)

    if authorised_user(user_id):
        if not has_approved(deploy_id, user_id):
            log.info(f"Setting approval for {user_id} as {action_id}")
            set_approval(deploy_id, user_id, action_id)
            approvals = get_approvals(deploy_id)
            deployment_details = get_deployment_details(deploy_id)
            author = deployment_details['author']
            service = deployment_details['service']
            commit = deployment_details['commit']
            build_id = deployment_details['github_build_id']
            environment = deployment_details['environment']
            run_url = deployment_details['run_url']

            if get_last_approval(deploy_id) == 'second':
                set_approval_status(deploy_id, "true")
                approval_payload_queue(user_id, deploy_id, 'true')
                message_blocks = [divider(), message_header(), approval_msg(),
                                  context_info(author, service, commit, build_id, environment, run_url),
                                  approvers(approvals['first_approver'], approvals['second_approver'])]
            else:
                message_blocks = [divider(), message_header(), final_approval(deploy_id, next_approval),
                                  context_info(author, service, commit, build_id, environment, run_url),
                                  approvers(approvals['first_approver'], approvals['second_approver'])]

            update_slack_message(channel_id, message_ts, message_blocks)
            return response(200, 'success')
        else:
            send_giphy_response(channel_id, user_id)
            return response(200, 'success')
    else:
        send_giphy_response(channel_id, user_id)
    return response(200, 'success')


def handle_rejection(user_id, channel_id, message_ts, deploy_id):
    if authorised_user(user_id):
        deployment_details = get_deployment_details(deploy_id)
        author = deployment_details['author']
        service = deployment_details['service']
        commit = deployment_details['commit']
        build_id = deployment_details['github_build_id']
        environment = deployment_details['environment']
        run_url = deployment_details['run_url']
        message_blocks = [divider(), message_header(), rejected_msg(user_id),
                          (context_info(author, service, commit, build_id, environment, run_url))]
        set_approval_status(deploy_id, 'false')
        set_rejection_status(deploy_id, 'true')
        approval_payload_queue(user_id, deploy_id, 'false')
        update_slack_message(channel_id, message_ts, message_blocks)
    else:
        send_giphy_response(channel_id, user_id)
        return response(200, 'success')


def load_authorized_users():
    global AUTHORIZED_USERS
    if AUTHORIZED_USERS is None:
        with open('./approvers.yaml') as f:
            config = yaml.safe_load(f)
            AUTHORIZED_USERS = set(config["authorise"]["authorised_users"])
    return AUTHORIZED_USERS


def authorised_user(user_id):
    authorized_users = load_authorized_users()
    if user_id in authorized_users:
        log.info(f"{user_id} is authorised")
        return True
    else:
        log.warning(f"{user_id} is not authorised")
        return False
