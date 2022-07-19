#!/usr/bin/env bash
source $(pwd)/scripts/settings.sh
source $(pwd)/private/creds.sh

echo "Building Test Container ${test_version}"
docker build -t ${test_version} --target development-env .


echo "Starting Container ${test_container_name} from Image ${test_version}"

if [[ -z "${TEST_APP_TOKEN}" ]]; then
    if [[ -z "$1" ]]; then
        echo "Missing Slack App Token (i.e. = ./start.sh app_token_value bot_token_value demisto_url demisto_api_key)"
        exit 1
    else
        TEST_APP_TOKEN=$1
    fi
fi

if [[ -z "${TEST_BOT_TOKEN}" ]]; then
    if [[ -z "$2" ]]; then
        echo "Missing Slack Bot Token (i.e. = ./start.sh bot_token_value bot_token_value demisto_url demisto_api_key)"
        exit 1
    else
        TEST_BOT_TOKEN=$2
    fi
fi

if [[ -z "${TEST_DEMISTO_URL}" ]]; then
    if [[ -z "$3" ]]; then
        echo "Missing XSOAR URL (i.e. = ./start.sh bot_token_value bot_token_value demisto_url demisto_api_key)"
        exit 1
    else
        TEST_DEMISTO_URL=$3
    fi
fi

if [[ -z "${TEST_DEMISTO_API_KEY}" ]]; then
    if [[ -z "$4" ]]; then
        echo "Missing XSOAR API KEY (i.e. = ./start.sh bot_token_value bot_token_value demisto_url demisto_api_key)"
        exit 1
    else
        TEST_DEMISTO_API_KEY=$4
    fi
fi

app_token=$1
bot_token=$2
demisto_url=$3
demisto_api_key=$4

docker run -dit --restart always --name ${test_container_name} -e "VERIFY_SSL=${test_ssl_verify}" -e "SLACK_BOT_TOKEN=${TEST_BOT_TOKEN}" -e "SLACK_APP_TOKEN=${TEST_APP_TOKEN}" -e "DEMISTO_URL=${TEST_DEMISTO_URL}" -e "DEMISTO_API_KEY=${TEST_DEMISTO_API_KEY}" ${test_version}
docker logs ${test_container_name}

echo "Stoping Container ${test_container_name}"
docker stop ${test_container_name}
docker rm ${test_container_name}