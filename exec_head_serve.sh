#!/bin/bash
docker exec \
-it --rm \
"autolabel-model-service-head-node" \
python3 start_serving.py