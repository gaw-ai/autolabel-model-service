"""
utils
"""
import cv2
import numpy as np


def match_result_to_bboxes(
        result: np.ndarray,
        templ_h: int,
        templ_w: int,
        threshold: float,
        match_method,
        x_offset: int = 0,
        y_offset: int = 0) -> tuple:
    bboxes, scores = [], []
    loc = np.where(result >= threshold)
    for x_min, y_min in zip(loc[1], loc[0]):
        score = result[y_min, x_min]
        if match_method in (cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED):
            # lower better
            if score > threshold:
                continue
        elif score < threshold:
            # higher better
            continue
        x_min += x_offset
        y_min += y_offset
        bboxes.append(
            np.array(
                [x_min, y_min, x_min+templ_w, y_min+templ_h], dtype=np.int32))
        scores.append(score)
    if not bboxes:
        bboxes = np.empty((0, 4), np.int32)
        scores = np.empty((0,), dtype=np.float32)
    else:
        bboxes = np.array(bboxes, dtype=np.int32)
        scores = np.array(scores, dtype=np.float32)
    return bboxes, scores
