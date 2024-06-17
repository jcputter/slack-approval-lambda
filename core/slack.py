import os
from core.log import log
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

slack_token = os.environ.get('SLACK_TOKEN')
slack_client = WebClient(token=slack_token)


def get_user_email(user_id):
    try:
        user_info_response = slack_client.users_info(user=user_id)

        if not user_info_response["ok"]:
            raise Exception(f"Slack API error: {user_info_response['error']}")

        user_info = user_info_response["user"]
        email = user_info.get("profile", {}).get("email", None)

        return email
    except Exception as e:
        log.error(f"Error retrieving email for user {user_id}: {str(e)}")
        return None


def send_giphy_response(channel_id, user_id):
    user = user_id.split("@")[0]
    try:
        slack_client.chat_postMessage(
            link_names=True,
            channel=channel_id,
            blocks=slack_giphy_response(user)
        )
    except SlackApiError as e:
        log.error(f"Error sending Giphy response: {e.response['error']}")


def update_slack_message(channel_id, ts, blocks):
    try:
        slack_client.chat_update(
            channel=channel_id,
            ts=ts,
            blocks=blocks,
            text="Original message cannot be rendered"
        )
    except SlackApiError as e:
        log.error(f"Error updating Slack message: {e.response['error']}")


def slack_giphy_response(user):
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f":alert: That was a fine effort <@{user}>"
            }
        },
        {
            "type": "image",
            "image_url": "https://media.giphy.com/media/oxFDq4E9CHb7W/giphy.gif",
            "alt_text": "Approval denied"
        }
    ]

