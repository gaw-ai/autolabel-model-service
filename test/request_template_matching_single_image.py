import time
from pprint import pprint

import requests


def req_template_matching():
    post_body = {
        "templates": [
            "file:///home/yahya/Documents/gawai/template_matching_dev/autolabel_model/template/solenoid1.jpg",
            "file:///home/yahya/Documents/gawai/template_matching_dev/autolabel_model/template/angle_valve.jpg"
        ],
        "images": "file:///home/yahya/Documents/gawai/template_matching_dev/autolabel_model/sample_1000dpi/test3-2.jpg",
        "projectName": "test_project",
        "userId": "test_user"
    }
    t_s = time.perf_counter()
    resp = requests.post(
        "http://172.17.0.1:3080/api/template_matching",
        json=post_body
    )
    t_e = time.perf_counter()
    print("Processing time: %.2f seconds" % (t_e - t_s))
    print("Status code:", resp.status_code)
    pprint(resp.content)


if __name__ == "__main__":
    req_template_matching()
