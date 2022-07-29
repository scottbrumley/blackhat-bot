import os
import re
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
    "xsoar_health":
        {
            "cmd": "xsoar_health",
            "args": "",
            "description": "Check That XSOAR is Up.\n"
        },
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
    "check_ioc":
        {
            "cmd": "check_ioc",
            "args": "url=<list of urls>,\n\t\t\t\t\tip=<list of IPs>,\n\t\t\t\t\temail=<list of emails>,"
                    "\n\t\t\t\t\tdomain=<list of domains>",
            "description": "Check & Enrich IOCs\n\n\n\n\n\n\n\n"
        },
    "my_incidents":
        {
            "cmd": "my_incidents",
            "args": "",
            "description": "List Your Incidents\n"
        },
    "xsoar_invite":
        {
            "cmd": "xsoar_invite",
            "args": "email=<preferred email address>",
            "description": "Get sent an invite to use XSOAR for Case Management and Automation.\n"
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


def is_email(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if(re.fullmatch(regex, email)):
        return True

    else:
        return False


def clean_urls(url_str):
    ret_str = ""
    i = 0
    val_list = url_str.split(",")
    for val in val_list:
        i = i + 1
        domain_str = val.split("|")
        ret_str = ret_str + domain_str[0].replace("<", "")
        if i < len(val_list):
            ret_str = ret_str + ","
    return ret_str


def clean_domains(dom_str):
    ret_str = ""
    i = 0
    val_list = dom_str.split(",")
    for val in val_list:
        i = i + 1
        domain_str = val.split("|")
        ret_str = ret_str + domain_str[1].replace(">", "")
        if i < len(val_list):
            ret_str = ret_str + ","
    return ret_str


def clean_emails(email_str):
    ret_str = ""
    i = 0
    val_list = email_str.split(",")

    if val_list == -1:
        domain_str = email_str.split("|")
        email_str = ret_str + domain_str[1].replace(">", "")
        if is_email(email_str):
            ret_str = email_str
    else:
        for val in val_list:
            i = i + 1
            domain_str = val.split("|")
            ret_str = ret_str + domain_str[1].replace(">", "")
            if i < len(val_list) and is_email(ret_str):
                ret_str = ret_str + ","
    return ret_str


class DemistoConnect:
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
        try:
            response_api = requests.get(self.url + "/health", headers=self.headers, verify=ssl_verify)
        except Exception as e:
            print("Error Occurred. " + str(e.args))
            return str(e.args)
        else:
            return response_api.status_code

    def create_incident(self, incident_type, incident_owner, incident_name, incident_severity, incident_detail):
        data = {
            "type": incident_type,
            "name": incident_name,
            "details": incident_detail,
            "severity": incident_severity,
            "owner": incident_owner
            }
        try:
            response_api = requests.post(self.url + "/incident", headers=self.headers, data=json.dumps(data), verify=ssl_verify)
        except Exception as e:
            print("Error Occurred. " + str(e.args))
            return str(e.args)
        else:
            if response_api.status_code == 201:
                return response_api.text
            else:
                return response_api.status_code

    def search_incident(self, data):
        try:
            response_api = requests.post(self.url + "/incidents/search", headers=self.headers, data=json.dumps(data), verify=ssl_verify)
        except Exception as e:
            print("Error Occurred. " + str(e.args))
            return str(e.args)
        else:
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
    demisto = DemistoConnect(url,api_key)
    command_text = command_text.strip().replace('!', '')
    command_line = command_text.split(" ")

    # Slack Command Run Method
    if command_line[0] == command_list["xsoar_health"]['cmd']:

        demisto_val = demisto.health
        if demisto_val == 200:
            return_val = "XSOAR is Up!"
        else:
            return_val = "XSOAR may not be Up. " + demisto_val
        return return_val
    elif command_line[0] == command_list["block_mac"]['cmd']:
        incident = get_params(command_line)
        incident_json = demisto.create_incident("Blackhat MAC", "", "Block Mac " + incident['mac'],
                                       SEVERITY_DICT['High'], "mac=" + incident['mac'] + "\nslack_handle=" + user +
                                                "\nbot_handle=" + bot_handle + "\nslack_channel=" + channel)
        incident_dict = return_dict(incident_json)
        incident_id = str(incident_dict['id']).strip()
        incident_link = demisto_url + "/#/Details/" + incident_id
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
        incident_json = demisto.create_incident("Blackhat Qos", "", "Qos Mac " + incident['mac'],
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
    elif command_line[0] == command_list["check_ioc"]['cmd']:
        incident = get_params(command_line)
        incident_details = ""
        if "url" in incident:
            url_list = clean_urls(incident['url'])
            incident_details = incident_details + "url=" + url_list + "\n"
        if "domain" in incident:
            dom_list = clean_domains(incident['domain'])
            incident_details = incident_details + "domain=" + dom_list + "\n"
        if "ip" in incident:
            incident_details = incident_details + "ip=" + incident['ip'] + "\n"
        if "email" in incident:
            email_list = clean_emails(incident['email'])
            incident_details = incident_details + email_list + "\n"

        if incident_details:
            incident_json = demisto.create_incident("Blackhat IOC Check", "", "Enrich IOC " + incident_details[0:20],
                                                    SEVERITY_DICT['Low'],
                                                    incident_details +
                                                    "slack_handle=" + user +
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
        else:
            json_string = "Invalid IOC"
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
            incident_link = f"#{incident['id']} - {incident['name']}     *Status:* {incident['runStatus']}\n{demisto_url}:443/#/WarRoom/{str(incident['id'])}\n"
            return_str = return_str + incident_link

        return return_str
    elif command_line[0] == command_list["xsoar_invite"]['cmd']:
        incident = get_params(command_line)
        incident_details = ""
        if "email" in incident:
            email_list = clean_emails(incident['email'])
            incident_details = incident_details + email_list + "\n"
        incident_json = demisto.create_incident("Blackhat XSOAR Invite", "", "XSOAR Invite " + incident_details[0:20],
                                                SEVERITY_DICT['Low'],
                                                incident_details +
                                                "slack_handle=" + user +
                                                "\nbot_handle=" + bot_handle + "\nslack_channel=" + channel)
        incident_dict = return_dict(incident_json)
        incident_id = str(incident_dict['id']).strip()
        incident_link = demisto_url + "/#/Details/" + incident_id
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


@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)


@app.event("app_mention")
def event_test(body,say):
    user = body['event']['user']
    text = body['event']['text']
    channel = body['event']['channel']
    bot_handle = body['authorizations'][0]['user_id']
    text = text.replace(f"<@{bot_handle}>", "")  # Remove the bot handle from
    print(body)
    # print('Bot = ' + bot_handle + ' Channel=' + channel + ' Text=' + text + ' from User=' + user)

    if is_command(text):
        say(f"Your wish is my command, <@{user}>!")
        command_response = run_command(text,demisto_url,demisto_api_key, channel, user, bot_handle)
        say(command_response)
    else:
        say(f"Hi there, <@{user}>!\n  If you need help use the !help command.")


if __name__ == "__main__":
    try:
        SocketModeHandler(app, app_token).start()
    except Exception as e:
        print("Error Occurred. " + str(e.args))
        print(str(e.args))
