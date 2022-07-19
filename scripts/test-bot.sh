#!/usr/bin/env bash
source $(pwd)/scripts/settings.sh
echo "Building Test Container ${test_version}"
docker build -t ${test_version} --target development-env .

