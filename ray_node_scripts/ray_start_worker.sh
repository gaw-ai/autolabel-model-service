#!/bin/bash
ray start --block \
--port=${G_RAY_PORT} \
--gcs-server-port=${G_RAY_GCS_SERVER_PORT} \
--node-manager-port=${G_RAY_NODE_MANAGER_PORT} \
--object-manager-port=${G_RAY_OBJECT_MANAGER_PORT} \
--redis-password=${G_RAY_REDIS_PASSWORD} \
--min-worker-port=${G_RAY_MIN_WORKER_PORT} \
--max-worker-port=${G_RAY_MAX_WORKER_PORT} \
--object-store-memory=${G_RAY_OBJECT_STORE_MEMORY}
