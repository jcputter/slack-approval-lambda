def divider():
    return {"type": "divider"}


def message_header():
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*Deployment Approval*"
        }
    }


def approval_msg():
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": ":white_check_mark: Deployment was approved"
        }
    }


def final_approval(deploy_id, next_approval):
    return {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "style": "primary",
                "text": {
                    "type": "plain_text",
                    "text": "2nd Approval"
                },
                "value": deploy_id,
                "action_id": next_approval
            },
            {
                "type": "button",
                "style": "danger",
                "text": {
                    "type": "plain_text",
                    "text": "Reject"
                },
                "value": deploy_id,
                "action_id": "reject_1"
            }
        ]
    }


def rejected_msg(user):
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f":x: Deployment was rejected by {user}, build will be failed"
        }
    }


def context_info(author, service, commit, build_id, environment, run_url):
    return {
        "type": "context",
        "elements": [
            {"type": "plain_text", "text": f"Actor: {author}"},
            {"type": "plain_text", "text": f"Service: {service}"},
            {"type": "plain_text", "text": f"Commit: {commit}"},
            {"type": "plain_text", "text": f"Build ID: {build_id}"},
            {"type": "plain_text", "text": f"Build ID: {environment}"},
            {"type": "mrkdwn", "text": f"Build: <{run_url}|Workflow Run>"}
        ]
    }


def approvers(first_approver, second_approver):
    return {
        "type": "context",
        "elements": [
            {"type": "plain_text", "text": f"First Approver: {first_approver}"},
            {"type": "plain_text", "text": f"Second Approver: {second_approver}"}
        ]
    }
