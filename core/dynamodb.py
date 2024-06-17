from core.log import log
import boto3

dynamodb = boto3.resource('dynamodb')
dynamodb_table = dynamodb.Table('deployment_approvals')


def get_deployment_details(deploy_id):
    table = dynamodb.Table('deployment_approvals')
    try:
        response = table.get_item(Key={'deploy_id': deploy_id})
        if 'Item' in response:
            print(response)
            return response['Item']
        else:
            return None
    except Exception as e:
        log.error(f"Error fetching deployment details: {str(e)}")
        return None


def get_approval_status(deploy_id):
    try:
        response = dynamodb_table.get_item(Key={'deploy_id': deploy_id})
        return response.get('Item')
    except Exception as e:
        log.error(f"Error getting approval status: {e}")
        return None


def set_rejection_status(deploy_id, rejected):
    table = dynamodb.Table('deployment_approvals')
    table.update_item(
        Key={
            'deploy_id': deploy_id,
        },
        UpdateExpression=f'SET rejected = :{rejected}',
        ExpressionAttributeValues={
            f":{rejected}": rejected
        }
    )
    log.info(f"Deployment {deploy_id} was set to {rejected}")


def set_approval_status(deploy_id, approved):
    table = dynamodb.Table('deployment_approvals')
    table.update_item(
        Key={
            'deploy_id': deploy_id,
        },
        UpdateExpression=f'SET approved = :{approved}',
        ExpressionAttributeValues={
            f":{approved}": approved
        }
    )
    log.info(f"Deployment {deploy_id} was set to {approved}")


def get_last_approval(deploy_id):
    table = dynamodb.Table('deployment_approvals')

    response = table.get_item(
        Key={'deploy_id': deploy_id}
    )
    deployment = response.get('Item', {})
    first_approver = deployment.get('first_approver', None)
    second_approver = deployment.get('second_approver', None)

    if first_approver and second_approver:
        return "second"
    elif first_approver or second_approver:
        return "first"
    else:
        return "none"


def get_approvals(deploy_id):
    try:
        table = dynamodb.Table('deployment_approvals')
        keys = ['first_approver', 'second_approver']
        response = table.get_item(
            Key={
                'deploy_id': deploy_id,
            }
        )
        item = response.get('Item', {})
        approvals = {key: item.get(key) for key in keys}
        return approvals
    except Exception as e:
        log.error(f"An error occurred: {e}")
        return {key: None for key in keys}


def set_approval(deploy_id, user, approval):
    table = dynamodb.Table('deployment_approvals')
    table.update_item(
        Key={
            'deploy_id': deploy_id,
        },
        UpdateExpression=f'SET {approval} = :user',
        ExpressionAttributeValues={
            ':user': user
        }
    )


def has_approved(deploy_id, user):
    table = dynamodb.Table('deployment_approvals')
    response = table.get_item(
        Key={
            'deploy_id': deploy_id,
        }
    )
    deployment = response.get('Item', {})
    first_approver = deployment.get('first_approver', None)
    second_approver = deployment.get('second_approver', None)

    if first_approver == user or second_approver == user:
        log.info(f"User {user}, has already approved")
        return True
    else:
        log.info(f"User {user}, has no existing approval")
        return False
