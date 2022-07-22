#!/usr/bin/env bash
source $(pwd)/scripts/settings.sh
source $(pwd)/private/creds.sh

if [[ "$1" = "prod" ]]; then
    echo "Starting Container ${product_container_name} from Image ${product_version}"
    if [[ -z "${APP_TOKEN}" ]]; then
        if [[ -z "$1" ]]; then
            echo "Missing Slack App Token (i.e. = ./start.sh app_token_value bot_token_value demisto_url demisto_api_key)"
            exit 1
        else
            APP_TOKEN=$1
        fi
    fi

    if [[ -z "${BOT_TOKEN}" ]]; then
        if [[ -z "$2" ]]; then
            echo "Missing Slack Bot Token (i.e. = ./start.sh bot_token_value bot_token_value demisto_url demisto_api_key)"
            exit 1
        else
            BOT_TOKEN=$2
        fi
    fi

    if [[ -z "${DEMISTO_URL}" ]]; then
        if [[ -z "$3" ]]; then
            echo "Missing XSOAR URL (i.e. = ./start.sh bot_token_value bot_token_value demisto_url demisto_api_key)"
            exit 1
        else
            DEMISTO_URL=$3
        fi
    fi

    if [[ -z "${DEMISTO_API_KEY}" ]]; then
        if [[ -z "$4" ]]; then
            echo "Missing XSOAR API KEY (i.e. = ./start.sh bot_token_value bot_token_value demisto_url demisto_api_key)"
            exit 1
        else
            DEMISTO_API_KEY=$4
        fi
    fi

    app_token=$1
    bot_token=$2
    demisto_url=$3
    demisto_api_key=$4

    docker run -dit --restart always --name ${product_container_name} -e "VERIFY_SSL=${production_ssl_verify}" -e "SLACK_BOT_TOKEN=${BOT_TOKEN}" -e "SLACK_APP_TOKEN=${APP_TOKEN}" -e "DEMISTO_URL=${DEMISTO_UR}" -e "DEMISTO_API_KEY=${DEMISTO_API_KEY}" ${product_version}
else
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
fi
