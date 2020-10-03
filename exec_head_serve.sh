#!/bin/bash
docker exec \
-it --rm \
"autolabel-model-service-worker-node" \
python3 start_serving.py