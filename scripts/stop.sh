#!/usr/bin/env bash
source $(pwd)/scripts/settings.sh

if [[ "$1" = "prod" ]]; then
    echo "Stopping Container ${product_container_name}"
    docker stop ${product_container_name}
    docker rm ${product_container_name}
else
    echo "Stopping Container ${test_container_name}"
    docker stop ${test_container_name}
    docker rm ${test_container_name}
fi