#!/bin/bash
docker run \
--rm -it \
--network=host \
--env-file=defaults.env \
--env-file=config.env \
--ulimit nofile=65536:65536 \
--name="autolabel-model-service-worker-node" \
--shm-size=384M \
--volume=${PWD}/autolabel_models:/home/gawai/autolabel_models \
--volume=${PWD}/ray_node_scripts:/home/gawai/ray_node_scripts \
--volume=/home/yahya:/home/yahya:ro \
--workdir=/home/gawai \
--memory=4G \
--memory-swap=4G \
--cpus=2 \
gaw-ai/autolabel-models-base:latest \
ray_node_scripts/./ray_start_worker.sh
