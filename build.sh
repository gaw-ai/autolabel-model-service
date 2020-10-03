#!/bin/bash
VERSION=$(git describe --tag)
echo ${VERSION} > autolabel_models/VERSION
docker build \
-t gaw-ai/autolabel-models-base:${VERSION} \
-t gaw-ai/autolabel-models-base:latest \
--build-arg UID=$(id -u) \
--build-arg GID=$(id -g)\
.