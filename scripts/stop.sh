#!/usr/bin/env bash
source $(pwd)/scripts/settings.sh
echo "Stoping Container ${product_container_name}"
docker stop ${product_container_name}
docker rm ${product_container_name}