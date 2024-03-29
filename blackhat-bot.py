import os
import shlex
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
SCORE_DICT = {
    'Unknown': 0,
    'Good': 1,
    'Suspicious': 2,
    'Bad': 3
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
            "args": "n/a",
            "description": "Check That XSOAR is Up.\n"
        },
    "block_mac":
        {
            "cmd": "block_mac",
            "args": "*mac*=MAC Address",
            "description": "Block by MAC in Firewalls\n"
        },
    "block_ip":
        {
            "cmd": "block_ip",
            "args": "*ip*=IP Address",
            "description": "Block by IP in Firewalls\n"
        },
    "wireless_client_lookup":
        {
            "cmd": "wireless_client_lookup",
            "args": "*mac*=MAC Address\n*ip*=IP Address",
            "description": "Search For Wireless Clients by MAC\n"
        },
    "firewall_request":
        {
            "cmd": "firewall_request",
            "args": "*option*=change|outage|threat|other\n*details*=\"Request something Here.\"",
            "description": "Send request to the firewall team."
        },
    "qos_mac":
        {
            "cmd": "qos_mac",
            "args": "*mac*=MAC Address",
            "description": "Set QoS by MAC in Firewalls\n"
        },
    "check_ioc":
        {
            "cmd": "check_ioc",
            "args": "*url*=<list of urls>\n*ip*=<list of IPs>\n*email*=<list of emails>"
                    "\n*domain*=<list of domains>\nrep=Unknown|Good|Suspicious|Bad\n",
            "description": "Check & Enrich IOCs\n"
        },
    "my_incidents":
        {
            "cmd": "my_incidents",
            "args": "n/a",
            "description": "List Your Incidents\n"
        },
    "xsoar_invite":
        {
            "cmd": "xsoar_invite",
            "args": "*email*=<preferred email address>",
            "description": "Invite yourself to XSOAR.\n"
        }
}


def human_date_time(date_time_str):
    """
    print(date_time_str)
    time_zone = []
    # Get Date
    date_time = date_time_str.split("T")
    date_str = str(date_time[0])

    # Get Time
    if "-"  in date_time[1]:
        time_zone = date_time[1].split("-")
    elif "+" in date_time[1]:
        time_zone = date_time[1].split("+")

    print(time_zone)
    time_str = str(time_zone[0])

    # Get Time Zone
    get_zone = date_time[1].split(time_str)
    zone_str = str(get_zone[1])

    new_time = date_str + " " + time_str.split(".")[0] + " TZ= " + zone_str
    """

    return str(date_time_str)


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
        if "|" in val:
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
            "owner": incident_owner,
            "createInvestigation": True
            }
        try:
            response_api = requests.post(self.url + "/incident", headers=self.headers, data=json.dumps(data), verify=ssl_verify)
        except Exception as e:
            print("Error Occurred. " + str(e.args))
            return str(e.args)
        else:
                return response_api.text

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


def is_command(text_message):
    text_message = text_message.strip()
    if text_message[:1] == "!":
        return True
    else:
        return False


def get_params(param_list):
    param_list = re.sub('\s*=\s*', "=", param_list)
    if "\u201d" in param_list:
        param_list = param_list.replace("\u201d", "\"")
    if "\u201c" in param_list:
        param_list = param_list.replace("\u201c", "\"")
    param_dict = dict(token.split('=') for token in shlex.split(param_list))
    return param_dict


def return_dict(json_string):
    return json.loads(json_string)


def append_section(dict_obj, key, value):
    if key in dict_obj:
        if not isinstance(dict_obj[key], list):
            dict_obj[key] = [[dict_obj[key]]]

        dict_obj[key].append(value)
    else:
        dict_obj[key] = value
    return dict_obj


def create_menu(json_string):
    divider_dict = {
                    "type": "divider"
                   }

    for command in command_list:
        section_dict = {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": "*Description:*"
                            },
                            {
                                "type": "mrkdwn",
                                "text": str(command_list[command]['description'])
                            },
                            {
                                "type": "plain_text",
                                "text": " "
                            },
                            {
                                "type": "plain_text",
                                "text": " "
                            },
                            {
                                "type": "mrkdwn",
                                "text": "*!" + str(command_list[command]['cmd']) + "*"
                            },
                            {
                                "type": "mrkdwn",
                                "text": " " + str(command_list[command]['args'])
                            }
                        ]
                       }
        append_section(json_string, 'blocks', section_dict)
        append_section(json_string, 'blocks', divider_dict)
    return json_string


def checkKey(dict, key):
    if key in dict.keys():
        return True
    else:
        return False


def run_command(command_text, url, api_key, channel, user, bot_handle, channel_name, thread):
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
        command_line = command_text.strip().replace(command_list['block_mac']['cmd'] + " ", '')
        incident = get_params(command_line)
        incident_json = demisto.create_incident("Blackhat MAC", "", "Block Mac " + incident['mac'],
                                       SEVERITY_DICT['High'], "mac=" + incident['mac'] + "\nslack_handle=" + user +
                                                "\nbot_handle=" + bot_handle + "\nchannel_name=" + channel_name +
                                                "\nslack_channel=" + channel)
        incident_dict = return_dict(incident_json)
        incident_id = str(incident_dict['id']).strip()
        incident_link = demisto_url + "/#/WarRoom/" + incident_id
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
    elif command_line[0] == command_list["block_ip"]['cmd']:
        command_line = command_text.strip().replace(command_list['block_ip']['cmd'] + " ", '')
        incident = get_params(command_line)
        incident_json = demisto.create_incident("Blackhat IP", "", "Block IP " + incident['ip'],
                                                SEVERITY_DICT['High'], "ip=" + incident['ip'] + "\nslack_handle=" + user +
                                                "\nbot_handle=" + bot_handle + "\nchannel_name=" + channel_name +
                                                "\nslack_channel=" + channel)
        incident_dict = return_dict(incident_json)
        incident_id = str(incident_dict['id']).strip()
        incident_link = demisto_url + "/#/WarRoom/" + incident_id
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
        command_line = command_text.strip().replace(command_list['qos_mac']['cmd'] + " ", '')
        incident = get_params(command_line)
        incident_json = demisto.create_incident("Blackhat Qos", "", "Qos Mac " + incident['mac'],
                                       SEVERITY_DICT['Low'], "mac=" + incident['mac'] + "\nslack_handle=" + user +
                                                "\nbot_handle=" + bot_handle + "\nslack_channel=" + channel)
        incident_dict = return_dict(incident_json)
        incident_link = f"{demisto_url}/#/WarRoom/{str(incident_dict['id'])}"
        json_string = {
            "channel": channel,
            "text": f"New Incident created by <@{user}>",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "New XSOAR Incident #" + str(incident_dict['id']),
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*Type:*\n" + str(incident_dict['type'])
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
    elif command_line[0] == command_list["wireless_client_lookup"]['cmd']:
        command_line = command_text.strip().replace(command_list["wireless_client_lookup"]["cmd"] + " ", '')
        incident = get_params(command_line)
        incident_details = ""
        if "mac" in incident:
            mac_list = clean_urls(incident['mac'])
            incident_details = incident_details + "mac=" + str(mac_list) + "\n"
        if "ip" in incident:
            ip_list = clean_urls(incident['ip'])
            incident_details = incident_details + "ip=" + str(ip_list) + "\n"

        incident_json = demisto.create_incident("Blackhat-wireless-client-lookup", "", "Wireless Search " +
                                                incident_details, SEVERITY_DICT['Low'], incident_details +
                                                "\nslack_handle=" + user + "\nbot_handle=" + bot_handle +
                                                "\nslack_channel=" + channel)
        incident_dict = return_dict(incident_json)
        incident_link = f"{demisto_url}/#/WarRoom/{str(incident_dict['id'])}"
        json_string = {
            "channel": channel,
            "text": f"New Incident created by <@{user}>",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "New XSOAR Incident #" + str(incident_dict['id']),
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*Type:*\n" + str(incident_dict['type'])
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
    elif command_line[0] == command_list["firewall_request"]['cmd']:
        if len(command_line) > 2:
            command_line = command_text.strip().replace(command_list['firewall_request']['cmd'] + " ", '')
            incident = get_params(command_line)
            incident_json = demisto.create_incident("Blackhat Firewall Request", "", "Black Hat Firewall Request " + incident['option'],
                                                    SEVERITY_DICT['Low'], "option=" + incident['option'] + "\nslack_handle=" + user +
                                                    "\nbot_handle=" + bot_handle + "\nslack_channel=" + channel +
                                                    "\n\nDetails:\n" + incident['details'])
            incident_dict = return_dict(incident_json)
            incident_link = f"{demisto_url}/#/WarRoom/{str(incident_dict['id'])}"
            json_string = {
                "channel": channel,
                "text": f"New Incident created by <@{user}>",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "New XSOAR Incident #" + str(incident_dict['id']),
                            "emoji": True
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": "*Type:*\n" + str(incident_dict['type'])
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
        else:
            return "This command requires parameters. " + command_list['firewall_request']['args']
    elif command_line[0] == command_list["check_ioc"]['cmd']:
        if len(command_line) > 1:
            indicator_set = False
            command_line = command_text.strip().replace(command_list['check_ioc']['cmd'] + " ", '')
            incident = get_params(command_line)
            incident_details = ""
            if "url" in incident:
                url_list = clean_urls(incident['url'])
                incident_details = incident_details + "url=" + str(url_list) + "\n"
                indicator_set = True
            if "domain" in incident:
                # dom_list = clean_domains(incident['domain'])
                dom_list = incident['domain']
                incident_details = incident_details + "domain=" + str(dom_list) + "\n"
                indicator_set = True
            if "ip" in incident:
                incident_details = incident_details + "ip=" + str(incident['ip']) + "\n"
                indicator_set = True
            if "email" in incident:
                email_list = clean_emails(incident['email'])
                incident_details = incident_details + str(email_list) + "\n"
                indicator_set = True
            if "rep" in incident:
                incident_details = incident_details + "reputation=" + str(incident['rep']) + "\n"
                if not checkKey(SCORE_DICT, incident['rep']):
                    return "Reputation is case sensitive. " + command_list['check_ioc']['args']

            if incident_details and indicator_set:
                incident_json = demisto.create_incident("Blackhat IOC Check", "", "Enrich IOC " + incident_details[0:20],
                                                        SEVERITY_DICT['Low'],
                                                        incident_details +
                                                        "slack_handle=" + user +
                                                        "\nslack_thread=" + thread +
                                                        "\nbot_handle=" + bot_handle + "\nchannel_name=" + channel_name +
                                                        "\nslack_channel=" + channel)
                if len(str(incident_json)) > 0:
                    incident_dict = return_dict(incident_json)
                    incident_link = f"{demisto_url}/#/WarRoom/{str(incident_dict['id'])}"
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
                                    },
                                    {
                                        "type": "mrkdwn",
                                        "text": incident_link
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
                    json_string = "No Data"
            else:
                json_string = "Invalid IOC.  You need an IOC"
            return json_string

        else:
            return "This command requires parameters. " + command_list['check_ioc']['args']
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
            incident_link = f"#{incident['id']} - {incident['name']}     *Status:* {incident['runStatus']}\n{demisto_url}/#/WarRoom/{str(incident['id'])}\n"
            return_str = return_str + incident_link

        return return_str
    elif command_line[0] == command_list["xsoar_invite"]['cmd']:
        command_line = command_text.strip().replace(command_list['xsoar_invite']['cmd'] + " ", '')
        incident = get_params(command_line)
        incident_details = ""
        if "email" in incident:
            email_list = clean_emails(incident['email'])
            incident_details = incident_details + "email=" + email_list + "\n"
        incident_json = demisto.create_incident("Blackhat XSOAR Invite", "", "XSOAR Invite " + incident_details[0:20],
                                                SEVERITY_DICT['Low'],
                                                incident_details +
                                                "slack_handle=" + user +
                                                "\nbot_handle=" + bot_handle + "\nslack_channel=" + channel)
        incident_dict = return_dict(incident_json)
        incident_id = str(incident_dict['id']).strip()
        incident_link = demisto_url + "/#/WarRoom/" + incident_id
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
                        "text": "List of Commands\n",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*Command:*"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*Parameters:*"
                        }
                    ]
                },
                {
                    "type": "divider"
                }
            ]
        }
        json_string = create_menu(json_string)
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
    if checkKey(body['event'], 'user'):
        user = body['event']['user']
    else:
        user = body['event']['bot_id']
    text = body['event']['text']
    channel = body['event']['channel']
    bot_handle = body['authorizations'][0]['user_id']
    text = text.replace(f"<@{bot_handle}>", "")  # Remove the bot handle from
    channel_info = app.client.conversations_info(channel=channel)
    channel_name = channel_info['channel']['name']
    thread = body['event']['ts']

    # print('Bot = ' + bot_handle + ' Channel=' + channel + ' Text=' + text + ' from User=' + user)

    if is_command(text):
        say(f"Your wish is my command, <@{user}>!")
        command_response = run_command(text,demisto_url,demisto_api_key, channel, user, bot_handle, channel_name, thread)
        if command_response:
            say(command_response)
        else:
            say("No Text in Response to channel=" + channel_name)
    else:
        say(f"Hi there, <@{user}>!\n  If you need help use the !help command.")


if __name__ == "__main__":
    try:
        SocketModeHandler(app, app_token).start()
    except Exception as e:
        print("Error Occurred. " + str(e.args))
        print(str(e.args))
