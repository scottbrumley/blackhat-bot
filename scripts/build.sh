#!/usr/bin/env bash
source $(pwd)/scripts/settings.sh

if [[ "$1" = "prod" ]]; then
    echo "Building Container ${product_version}"
    docker build -t ${product_version} --target production-env .
else
    echo "Building Container ${test_version}"
    docker build -t ${test_version} --target development-env .
fi
