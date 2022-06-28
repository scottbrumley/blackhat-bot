import os
import json
import urllib3
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

SEVERITY_DICT = {
    'Unknown': 0,
    'Low': 1,
    'Medium': 2,
    'High': 3,
    'Critical': 4
}

ssl_verify = True

if os.environ.get("VERIFY_SSL") == "False":
    ssl_verify = False
    urllib3.disable_warnings()

bot_token = os.environ.get("SLACK_BOT_TOKEN")
app_token = os.environ.get("SLACK_APP_TOKEN")
demisto_url = os.environ.get("DEMISTO_URL")
demisto_api_key = os.environ.get("DEMISTO_API_KEY")

app = App(token=bot_token)

command_list = {
    "block_mac":
    {
        "cmd": "block_mac",
        "args": "mac=MAC Address",
        "description": "Block by MAC in Firewalls\n"
    },
    "qos_mac":
    {
        "cmd": "qos_mac",
        "args": "mac=MAC Address",
        "description": "Set QoS by MAC in Firewalls\n"
    },
    "my_incidents":
        {
            "cmd": "my_incidents",
            "args": "",
            "description": "List Your Incidents\n"
        }
}

def human_date_time(date_time_str):
    time_zone = ""
    # Get Date
    date_time = date_time_str.split("T")
    date_str = str(date_time[0])

    # Get Time
    if "-"  in date_time[1]:
        time_zone = date_time[1].split("-")
    elif "+" in date_time[1]:
        time_zone = date_time[1].split("+")

    time_str = str(time_zone[0])

    # Get Time Zone
    get_zone = date_time[1].split(time_str)
    zone_str = str(get_zone[1])

    new_time = date_str + " " + time_str.split(".")[0] + " TZ= " + zone_str

    return new_time


class demistoConnect:
    def __init__(self, url, api_key):
        self.url = url
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            'Authorization': api_key
                       }

    # Slack Command Methods
    @property
    def health(self):
        response_api = requests.get(self.url + "/health", headers=self.headers, verify=ssl_verify)
        return response_api.status_code

    def create_incident(self, incident_type, incident_owner, incident_name, incident_severity, incident_detail):
        data = {
            "type": incident_type,
            "name": incident_name,
            "details": incident_detail,
            "severity": incident_severity,
            "owner": incident_owner
            }
        response_api = requests.post(self.url + "/incident", headers=self.headers, data=json.dumps(data), verify=ssl_verify)
        if response_api.status_code == 201:
            return response_api.text
        else:
            return response_api.status_code

    def search_incident(self, data):
        response_api = requests.post(self.url + "/incidents/search", headers=self.headers, data=json.dumps(data), verify=ssl_verify)
        if response_api.status_code == 200:
            return response_api.text
        else:
            return response_api.status_code


def is_command(textmessage):
    textmessage = textmessage.strip()
    if textmessage[:1] == "!":
        return True
    else:
        return False


def get_params(param_list):
    param_dict = {}
    for param in param_list:
        if "=" in param:
            key_val_pair = param.split("=")
            param_dict[key_val_pair[0]] = key_val_pair[1]
    return param_dict


def return_dict(json_string):
    return json.loads(json_string)


def build_command_string():
    my_commands = ""
    for command in command_list:
        my_commands = my_commands + "!" + command_list[command]['cmd'] + " " + command_list[command]['args'] + "\n\n"
    return my_commands


def build_description_string():
    my_args = ""
    for command in command_list:
        my_args = my_args + command_list[command]['description'] + "\n"
    return my_args


def run_command(command_text, url, api_key, channel, user, bot_handle):
    demisto = demistoConnect(url,api_key)
    command_text = command_text.strip().replace('!', '')
    command_line = command_text.split(" ")

    # Slack Command Run Method
    if command_line[0] == "xsoar_health":

        if demisto.health == 200:
            return_val = "XSOAR is Up!"
        else:
            return_val = "XSOAR may not be Up."
        return return_val

    elif command_line[0] == command_list["block_mac"]['cmd']:
        incident = get_params(command_line)
        incident_json = demisto.create_incident("Blackhat MAC", "sbrumley", "Block Mac " + incident['mac'],
                                       SEVERITY_DICT['High'], "mac=" + incident['mac'] + "\nslack_handle=" + user +
                                                "\nbot_handle=" + bot_handle + "\nslack_channel=" + channel)
        incident_dict = return_dict(incident_json)
        incident_id = str(incident_dict['id']).strip()
        incident_link = demisto_url + "/#/Details/" + incident_id
        print("dd" + incident_link + "dd")
        json_string = {
            "channel": channel,
            "text": f"New Incident created by <@{user}>",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "New XSOAR Incident #" + incident_dict['id'],
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*Type:*\n" + incident_dict['type']
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Created by:*\n<@{user}>"
                        }
                    ]
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*When:*\n" + human_date_time(str(incident_dict["created"]))
                        }
                    ]
                },
                {
                    "type": "actions",
                    "block_id": "actionblock789",
                    "elements": [
                        {
                            "type": "button",
                            "action_id": "openincident",
                            "text": {
                                "type": "plain_text",
                                "text": "Open Incident"
                            },
                            "url": incident_link
                        }
                    ]
                }
            ]
        }
        return json_string
    elif command_line[0] == command_list["qos_mac"]['cmd']:
        incident = get_params(command_line)
        incident_json = demisto.create_incident("Blackhat Qos", "sbrumley", "Qos Mac " + incident['mac'],
                                       SEVERITY_DICT['Low'], "mac=" + incident['mac'] + "\nslack_handle=" + user +
                                                "\nbot_handle=" + bot_handle + "\nslack_channel=" + channel)
        incident_dict = return_dict(incident_json)
        incident_link = f"{demisto_url}/#/Details/{str(incident_dict['id'])}"
        json_string = {
            "channel": channel,
            "text": f"New Incident created by <@{user}>",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "New XSOAR Incident #" + incident_dict['id'],
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*Type:*\n" + incident_dict['type']
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Created by:*\n<@{user}>"
                        }
                    ]
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*When:*\n" + human_date_time(str(incident_dict["created"]))
                        }
                    ]
                },
                {
                    "type": "actions",
                    "block_id": "actionblock789",
                    "elements": [
                        {
                            "type": "button",
                            "action_id": "openincident",
                            "text": {
                                "type": "plain_text",
                                "text": "Open Incident"
                            },
                            "url": incident_link
                        }
                    ]
                }
            ]
        }
        return json_string
    elif command_line[0] == command_list["my_incidents"]['cmd']:
        search_str = {
            "filter": {
                "query": f"-status:closed -category:job details:\"*slack_handle={user}*\""
            }
        }
        incident_json = demisto.search_incident(search_str)
        incident_dict = return_dict(incident_json)
        return_str = ""

        for incident in incident_dict['data']:
            incident_link = f"#{incident['id']} - {incident['name']}\n{demisto_url}/#/Details/{str(incident['id'])}\n"
            return_str = return_str + incident_link

        return return_str
    elif command_line[0] == "help":
        json_string = {
            "channel": channel,
            "text": f"List of Commands",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "List of Commands",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*Command:*\n" + build_command_string()
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Description:*\n" + build_description_string()
                        }
                    ]
                }
            ]
        }

        return json_string
    else:
        return "Command Not Found!"


@app.event("team_join")
def ask_for_introduction(event, say):
    user_id = event['user']
    text = f"Welcome to the team, <@{user_id}>!"
    say(text=text)


@app.action("approve_button")
def approve_request(ack,say):
    ack()
    say("Request approved!")


@app.action("openincident")
def approve_request(ack,say):
    ack()
    say("Opening Incident!")


@app.action("actionblock789")
def approve_request(ack,say):
    ack()
    say("Opening Incident!")


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
        command_response = run_command(text,demisto_url,demisto_api_key, channel, user, bot_handle)
        say(command_response)
    else:
        say(f"Hi there, <@{user}>!\n  If you need help use the !help command.")


if __name__ == "__main__":
    SocketModeHandler(app, app_token).start()

