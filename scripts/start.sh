#!/usr/bin/env bash
source $(pwd)/scripts/settings.sh

echo "Starting Container ${product_container_name} from Image ${product_version}"
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

docker run -dit --restart always --name ${product_container_name} -e "VERIFY_SSL=False" -e "SLACK_BOT_TOKEN=$2" -e "SLACK_APP_TOKEN=$1" -e "DEMISTO_URL=$3" -e "DEMISTO_API_KEY=$4" ${product_version}
