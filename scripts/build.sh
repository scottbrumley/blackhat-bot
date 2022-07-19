#!/usr/bin/env bash
source $(pwd)/scripts/settings.sh
echo "Building Container ${product_version}"
docker build -t ${product_version} --target production-env .

