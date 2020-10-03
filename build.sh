#!/bin/bash
VERSION=$(git describe --tag)
echo ${VERSION} > autolabel_models/VERSION
docker build \
-t gaw-ai/autolabel-model-service:${VERSION} \
-t gaw-ai/autolabel-model-service:latest \
--build-arg UID=$(id -u) \
--build-arg GID=$(id -g)\
.