#!/bin/bash
docker run \
-d \
--network=host \
--env-file=defaults.env \
--env-file=config.env \
--restart=unless-stopped \
--ulimit nofile=65536:65536 \
--name="autolabel-model-service-worker-node" \
--shm-size=384M \
--volume=${PWD}/ray_node_scripts:/home/gawai/ray_node_scripts \
--workdir=/home/gawai \
gaw-ai/autolabel-models-base:latest \
ray_node_scripts/./ray_start_worker.sh
