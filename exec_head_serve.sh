#!/bin/bash
docker exec \
-it \
--workdir=/home/gawai/autolabel_models \
"autolabel-model-service-head-node" \
python3 start_serving.py