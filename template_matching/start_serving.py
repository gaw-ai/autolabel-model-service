import os

import flask
import ray
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from match_multiple_rev import COLOR, templateMatching


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
    print("Starting Ray Serve instance as a long-running service...")
    client = ray.serve.start(
        detached=True,
        http_host=os.environ.get("SERVE_HTTP_HOST"),
        http_port=os.environ.get("SERVE_HTTP_PORT"),
        http_middlewares=[
            Middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_methods=["GET,POST"])
        ])
    client.create_backend(
        "templateMatching_backend",
        handle_templateMatching_req,
        ray_actor_options={"memory": 4 * 1024 * 1024 * 1024})
    client.create_endpoint(
        "templateMatching_endpoint",
        backend="templateMatching_backend",
        route="/api/templateMatching",
        methods=["POST"])
    print("Started Ray Serve instance as a long-running service.")
