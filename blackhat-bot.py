import os
import urllib3
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

ssl_verify = True

if os.environ.get("VERIFY_SSL") == "False":
    ssl_verify = False
    urllib3.disable_warnings()

bot_token = os.environ.get("SLACK_BOT_TOKEN")
app_token = os.environ.get("SLACK_APP_TOKEN")
demisto_url = os.environ.get("DEMISTO_URL")
demisto_api_key = os.environ.get("DEMISTO_API_KEY")

app = App(token=bot_token)


class demistoConnect:
    def __init__(self, url, api_key):
        self.url = url
        self.api_key = api_key
        self.headers = {'Authorization': 'Bearer {}'.format(api_key)}

    # Slack Command Methods
    def health(self):
        print(ssl_verify)
        response_api = requests.get(self.url, headers=self.headers, verify=ssl_verify)
        if response_api.status_code == 200:
            return "ok"


def is_command(textmessage):
    textmessage = textmessage.strip()
    if textmessage[:1] == "!":
        return True
    else:
        return False


def run_command(command_text, url, api_key):
    demisto = demistoConnect(url,api_key)
    command_text = command_text.strip().replace('!', '')

    # Slack Command Run Method
    if command_text == "xsoar_health":
        return demisto.health()
    else:
        return "Command Not Found!"


@app.action("approve_button")
def approve_request(ack,say):
    ack()
    say("Request approved!")


@app.action("rejection_button")
def approve_request(ack,say):
    ack()
    say("Request rejected!")


@app.event("app_mention")
def event_test(body,say):
    user = body['event']['user']
    text = body['event']['text']
    channel = body['event']['channel']
    bot_handle = body['authorizations'][0]['user_id']
    text = text.replace(f"<@{bot_handle}>", "")  # Remove the bot handle from

    print('Bot = ' + bot_handle + ' Channel=' + channel + ' Text=' + text + ' from User=' + user)

    if is_command(text):
        say(f"Your wish is my command, <@{user}>!")
        command_response = run_command(text,demisto_url,demisto_api_key)

        # Slack Command Action
        if text == "!xsoar_health":
            if command_response == "ok":
                say("XSOAR is Up!")
            else:
                say("XSOAR may not be Up.")

        """
        say({
            "channel": channel,
            "text": "New Paid Time Off request from Fred Enriquez",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "New request",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*Type:*\nPaid Time Off"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*Created by:*\n<example.com|Fred Enriquez>"
                        }
                    ]
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*When:*\nAug 10 - Aug 13"
                        }
                    ]
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "action_id": "approve_button",
                            "text": {
                                "type": "plain_text",
                                "emoji": True,
                                "text": "Approve"
                            },
                            "style": "primary",
                            "value": "click_me_123"
                        },
                        {
                            "type": "button",
                            "action_id": "rejection_button",
                            "text": {
                                "type": "plain_text",
                                "emoji": True,
                                "text": "Reject"
                            },
                            "style": "danger",
                            "value": "click_me_123"
                        }
                    ]
                }
            ]
        })
        """
    else:
        say(f"Hi there, <@{user}>!")


if __name__ == "__main__":
    SocketModeHandler(app, app_token).start()
