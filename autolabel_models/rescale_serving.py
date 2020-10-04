"""
Rescale serving
"""
import argparse
import os
from pprint import pprint

import ray
from ray import serve

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-n', '--num_replicas',
        type=int,
        help='target number of replicas')

    args = parser.parse_args()

    REDIS_PASSWORD = os.environ["G_RAY_REDIS_PASSWORD"]
    ray.init(
        address="auto",
        _redis_password=REDIS_PASSWORD)
    pprint(ray.nodes())
    client = serve.connect()

    config = serve.BackendConfig()
    config.num_replicas = args.num_replicas
    client.update_backend_config(
        "templateMatching_backend", config_options=config)
    pprint(client.list_backends())
