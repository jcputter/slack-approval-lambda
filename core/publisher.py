import redis
import os
import json
from core.log import log

redis_host = os.environ.get("REDIS_HOST", "localhost")
redis_port = os.environ.get("REDIS_PORT", 6379)


def approval_payload_queue(user, deploy_id, approval_status):
    payload = {
        "user": user,
        "deployment_id": deploy_id,
        "approval_status": approval_status,
    }

    send_approval_to_queue(payload)


def send_approval_to_queue(payload):
    try:
        r = redis.Redis(host=redis_host, port=redis_port, ssl=True , decode_responses=True)
        message_body = json.dumps(payload)
        channel_id = payload['deployment_id']
        response = r.publish(channel_id, message_body)
        log.info(f"Message published to {channel_id} for Deployment ID {payload['deployment_id']}")
    except Exception as e:
        log.error(f"Connection to redis failed, {str(e)}")
        return None

    return response
