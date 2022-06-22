#!/usr/bin/env bash

if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
    exit 1
fi

if [ -z "$1" ]
  then
    echo "Missing Slack App Token (i.e. = ./start.sh app_token_value bot_token_value demisto_url demisto_api_key)"
    exit 1
fi

if [ -z "$2" ]
  then
    echo "Missing Slack App Token (i.e. = ./start.sh bot_token_value bot_token_value demisto_url demisto_api_key)"
    exit 1
fi

if [ -z "$3" ]
  then
    echo "Missing XSOAR URL (i.e. = ./start.sh bot_token_value bot_token_value demisto_url demisto_api_key)"
    exit 1
fi

if [ -z "$4" ]
  then
    echo "Missing XSOAR API KEY (i.e. = ./start.sh bot_token_value bot_token_value demisto_url demisto_api_key)"
    exit 1
fi

app_token=$1
bot_token=$2
demisto_url=$3
demisto_api_key=$4

sudo docker run -dit --restart always --name blackhat -e "VERIFY_SSL=False" -e "SLACK_BOT_TOKEN=$2" -e "SLACK_APP_TOKEN=$1" -e "DEMISTO_URL=$3" -e "DEMISTO_API_KEY=$4" sbrumley/blackhat:0.9
