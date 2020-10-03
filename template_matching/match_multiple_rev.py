import argparse
import base64
import glob
import json
import multiprocessing as mp
import os
import random
import ssl
from urllib.parse import urlparse

import cv2
import flask
import numpy as np
import ray
from joblib import Parallel, delayed
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from partitioned_matchTemplate import partitioned_matchTemplate

COLOR = [
    "#FF0000", "#2196f3", "#4caf50",
    "#ef6c00", "#795548", "#689f38",
    "#e91e63", "#9c27b0", "#3f51b5",
    "#009688", "#cddc39", "#607d8b"
]

# single machine
ray.init(address="auto")

ssl._create_default_https_context = ssl._create_unverified_context


# construct the argument parser and parse the arguments
# ap = argparse.ArgumentParser()
# ap.add_argument("-t", "--templates", help="Path to template images")
# ap.add_argument(
#     "-i", "--images", help="Path to images where template will be matched")
# ap.add_argument("-p", "--projectName", help="Project name")
# ap.add_argument("-u", "--userId", help="User ID")
# args = vars(ap.parse_args())


# Returns true if two rectangles overlap
def doOverlap(bb1, bbox):
    for bb2 in bbox:
        if(bb1[0] < bb2[2] and
           bb2[0] < bb1[2] and
           bb1[1] < bb2[3] and
           bb2[1] < bb1[3]):
            return [True, bb2]
    return [False, []]


def resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation=inter)

    # return the resized image
    return resized


def templateMatching(imageUrl: str, templates: list):

    imageDict = {}
    imageDict = {
        'fileName': os.path.basename(urlparse(imageUrl).path),
    }

    # load the image, convert it to grayscale
    # img = io.imread(imagePath)
    cap = cv2.VideoCapture(imageUrl)
    _, img = cap.read()
    cap.release()  # releasing this significantly reduce memory usage!
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, img = cv2.threshold(img, 150, 255,
                           cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    imgHeight, imgWidth = img.shape[0], img.shape[1]

    # placeholder to contain selected bounding boxes
    bbox = dict()
    scales = np.linspace(0.5, 2, 25)[::-1]
    scales = set(scales)

    # loop over the scales of the image
    for scale in scales:
        # resize the image according to the scale, and keep track
        # of the ratio of the resizing
        resized = resize(img, width=int(img.shape[1] * scale))
        r = img.shape[1] / float(resized.shape[1])

        for templateUrl in templates:
            # load the template image, convert it to grayscale
            cap = cv2.VideoCapture(templateUrl)
            _, template = cap.read()
            cap.release()  # releasing this significantly reduce memory usage!
            template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            _, template = cv2.threshold(
                template, 150, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            tW, tH = template.shape[::-1]

            # determine the bounding box parameters
            valve_type = templateUrl[
                templateUrl.find("templates/")+10:templateUrl.find("lwKuT")]
            threshold = 0.6

            # if the resized image is smaller than the template,
            # we skipped that image
            if resized.shape[0] < tH or resized.shape[1] < tW:
                continue

            # perform match template
            # res = cv2.matchTemplate(resized, template, cv2.TM_CCOEFF_NORMED)
            res = partitioned_matchTemplate(
                resized, template, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= threshold)

            # only include bounding boxes that are not overlapping
            for pt in zip(*loc[::-1]):
                score = res[pt[1], pt[0]]
                bb1 = (
                    int(pt[0] * r),
                    int(pt[1] * r),
                    int((pt[0] + tW) * r),
                    int((pt[1] + tH) * r))
                isOverlap, bb2 = doOverlap(bb1, bbox)
                if len(bbox) == 0 or not isOverlap:
                    bbox[bb1] = {
                        'score': score,
                        'type': valve_type}
                elif isOverlap:
                    if valve_type != "gate_valve" and \
                            bbox[bb2]['type'] == "gate_valve":
                        del bbox[bb2]
                        bbox[bb1] = {
                            'score': score,
                            'type': valve_type}
                    elif valve_type == "gate_valve" and \
                            bbox[bb2]['type'] != "gate_valve":
                        continue
                    elif (score > bbox[bb2]['score']):
                        del bbox[bb2]
                        bbox[bb1] = {
                            'score': score,
                            'type': valve_type}
            del res
            del loc
    regions = []
    for bb in bbox.keys():
        x = bb[0] / imgWidth
        y = bb[1] / imgHeight
        w = (bb[2] - bb[0]) / imgWidth
        h = (bb[3] - bb[1]) / imgHeight
        id_ = str(x) + str(y) + str(w) + str(h)
        classType = bbox[bb]['type']
        region = {
            "id": id_,
            "color": "#FF0000",
            "cls": classType,
            "editingLabels": False,
            "highlighted": False,
            "type": "box",
            "x": x,
            "y": y,
            "w": w,
            "h": h
        }
        regions.append(region)
    imageDict['regions'] = regions
    return imageDict


def handle_templateMatching_req(flask_req: flask.Request):
    payload = flask_req.json
    colorToType = {}
    # mp.cpu_count()
    # images = Parallel(n_jobs= mp.cpu_count())(delayed(templateMatching)(i, imageUrl) \
    # 	for i, imageUrl in enumerate(list(args['images'].split(","))))
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

    project = {}

    project["images"] = templ_mtch_results
    project["projectName"] = payload["projectName"].strip()
    project["userId"] = payload["userId"].strip()

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
    config = {"memory": 4 * 1024 * 1024 * 1024}
    client.create_backend(
        "templateMatching_backend", handle_templateMatching_req, ray_actor_options=config)
    client.create_endpoint(
        "templateMatching_endpoint",
        backend="templateMatching_backend",
        route="/templateMatching",
                methods=["POST"]
    )
    print("Started Ray Serve instance as a long-running service.")
