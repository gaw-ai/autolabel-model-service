import argparse
import os
from urllib.parse import urlparse

import flask
import ray
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from match_multiple_rev import COLOR, templateMatching

REDIS_PASSWORD = os.environ["RAY_REDIS_PASSWORD"]
ray.init(address="auto", _redis_password=REDIS_PASSWORD)


def mock_templateMatching(imageUrl: str, templates: list) -> dict:
    imageDict = {}
    imageDict = {
        'fileName': os.path.basename(urlparse(imageUrl).path),
    }
    imageDict['regions'] = []
    return imageDict


def handle_mock_req(flask_req: flask.Request):
    payload = flask_req.json
    colorToType = {}
    templ_mtch_results = [
        mock_templateMatching(imageUrl, payload["templates"])
        for i, imageUrl in enumerate(payload['images'])]
    count = 0
    for templ_mtch_res in templ_mtch_results:
        for region in templ_mtch_res["regions"]:
            if region['cls'] in colorToType:
                region['color'] = colorToType[region['cls']]
            else:
                region['color'] = COLOR[count % len(COLOR)]
                colorToType[region['cls']] = region['color']
                count += 1
    project = {
        "images": templ_mtch_results,
        "projectName": payload["projectName"].strip(),
        "userId": payload["userId"].strip()
    }
    return project


def handle_templateMatching_req(flask_req: flask.Request):
    payload = flask_req.json
    colorToType = {}
    templ_mtch_results = [
        templateMatching(imageUrl, payload["templates"])
        for i, imageUrl in enumerate(payload['images'])]
    count = 0
    for templ_mtch_res in templ_mtch_results:
        for region in templ_mtch_res["regions"]:
            if region['cls'] in colorToType:
                region['color'] = colorToType[region['cls']]
            else:
                region['color'] = COLOR[count % len(COLOR)]
                colorToType[region['cls']] = region['color']
                count += 1
    project = {
        "images": templ_mtch_results,
        "projectName": payload["projectName"].strip(),
        "userId": payload["userId"].strip()
    }
    return project


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--use_mock_model',
        default=False,
        action='store_true',
        help='use mock model instead')

    args = parser.parse_args()
    print("Starting Ray Serve instance as a long-running service...")
    client = ray.serve.start(
        detached=True,
        http_host=os.environ["SERVE_HTTP_HOST"],
        http_port=int(os.environ["SERVE_HTTP_PORT"]),
        http_middlewares=[
            Middleware(
                CORSMiddleware,
                allow_origins=[os.environ.get("SERVE_ALLOW_ORIGINS", "*")],
                allow_methods=["GET,POST"])
        ])
    if args.use_mock_model:
        print("Using mock model...")
    client.create_backend(
        "templateMatching_backend",
        handle_mock_req if args.use_mock_model else handle_templateMatching_req,
        ray_actor_options={"memory": 4 * 1024 * 1024 * 1024})
    client.create_endpoint(
        "templateMatching_endpoint",
        backend="templateMatching_backend",
        route="/api/templateMatching",
        methods=["POST"])
    client.create_backend(
        "welcome_backend",
        lambda: "Hello, world!",
        ray_actor_options={"num_cpus": 0.001})
    client.create_endpoint(
        "welcome_endpoint",
        backend="welcome_backend",
        route="/",
        methods=["GET", "POST"])
    print("Started Ray Serve instance as a long-running service.")
