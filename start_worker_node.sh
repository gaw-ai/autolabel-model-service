#!/bin/bash
docker run \
-d \
--network host \
--name="autolabel-model-service-worker-node" \
--env-file=defaults.env \
--env-file=config.env \
--restart=unless-stopped \
--shm-size=384M \
--ulimit nofile=65536:65536 \
gaw-ai/autolabel-model-service:latest \
ray start --block \
--port=${RAY_PORT} \
--gcs-server-port=${RAY_GCS_SERVER_PORT} \
--node-manager-port=${RAY_NODE_MANAGER_PORT} \
--object-manager-port=${RAY_OBJECT_MANAGER_PORT} \
--redis-password=${RAY_REDIS_PASSWORD} \
--min-worker-port=${RAY_MIN_WORKER_PORT} \
--max-worker-port=${RAY_MAX_WORKER_PORT} \
--object-store-memory=${RAY_OBJECT_STORE_MEMORY}
