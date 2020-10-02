"""
match template
"""
import numpy as np
import cv2


def partitioned_matchTemplate(
        image,
        templ,
        method,
        result=None,
        mask=None,
        part_shapelim=(1024, 1024)):
    """
    cv2.matchTemplate, but operated using
    partitioned image. Useful to limit memory usage.

    PARAMETERS
    ----------
    image
        Image where the search is running.
        It must be 8-bit or 32-bit floating-point.
    templ
        Searched template. It must be not greater than
        the source image and have the same data type.
    method
        Parameter specifying the comparison method,
        see TemplateMatchModes
    result
        Optional container array for map of comparison results.
        It must be single-channel 32-bit floating-point.
        If image is W×H and templ is w×h , then result
        is (W−w+1)×(H−h+1) .
    mask
        Optional mask. It must have the same size as templ.
        It must either have the same number of channels as
        template or only one channel, which is then used for
        all template and image channels. If the data type is
        CV_8U, the mask is interpreted as a binary mask,
        meaning only elements where mask is nonzero are used
        and are kept unchanged independent of the actual mask
        value (weight equals 1). For data tpye CV_32F, the mask
        values are used as weights. The exact formulas are
        documented in TemplateMatchModes.
    part_shapelim
        Tuple of integers defining maximum limit of the partition's
        height and width (Hp, Wp). If float values given, partition's
        height and width will be calculated as (int(Hp*H), int(Wp*W)).
        Float values must in range [0..1].
        Lower values will resulting lower memory usage, but higher
        function call overhead.
        If None given, no partitioning will be done (bypass).
    """
    if part_shapelim is None:
        return cv2.matchTemplate(
            image=image,
            templ=templ,
            method=method,
            result=result,
            mask=mask)
    if type(part_shapelim[0]) != type(part_shapelim[1]):
        raise TypeError(
            "part_shapelim has mixed type '({}, {})'".format(
                type(part_shapelim[0]), type(part_shapelim[1])))
    img_h, img_w = image.shape[:2]
    if isinstance(part_shapelim[0], float):
        part_shapelim = (
            int(part_shapelim[0]*img_h),
            int(part_shapelim[1]*img_w))
    ps_h, ps_w = part_shapelim
    if img_h <= ps_h and img_w <= ps_w:
        return cv2.matchTemplate(
            image=image,
            templ=templ,
            method=method,
            result=result,
            mask=mask)
    templ_h, templ_w = templ.shape[:2]
    ps_h = templ_h if ps_h <= templ_h else ps_h
    ps_w = templ_w if ps_w <= templ_w else ps_w

    # Result container
    res_h, res_w = img_h - templ_h + 1, img_w - templ_w + 1
    if result is None:
        result = np.empty((res_h, res_w), dtype=np.float32)
    if not (
            result.shape[0] == res_h and
            result.shape[1] == res_w and
            result.dtype == np.float32):
        raise ValueError("given result array does not fulfill requirements")

    # Calculate partition count
    y_parts_cnt = int(np.ceil(img_h / ps_h))
    x_parts_cnt = int(np.ceil(img_w / ps_w))

    # Variable placeholders
    x_part_s, y_part_s = 0, 0
    x_part_e, y_part_e = 0, 0
    x_res_s, y_res_s = 0, 0
    x_res_e, y_res_e = 0, 0

    # Partition-wise calculation
    for j_y in range(y_parts_cnt):
        for i_x in range(x_parts_cnt):
            x_part_s, y_part_s = i_x * ps_w, j_y * ps_h
            x_part_e, y_part_e = x_part_s + ps_w, y_part_s + ps_h + templ_h - 1
            x_part_e = img_w if x_part_e > img_w else x_part_e
            y_part_e = img_h if y_part_e > img_h else y_part_e
            part_view = image[
                y_part_s:y_part_e,
                x_part_s:x_part_e]
            if part_view.shape[0] < templ_h:
                continue
            x_res_s, y_res_s = i_x * ps_w, j_y * ps_h
            x_res_e, y_res_e = x_res_s + ps_w - templ_w + 1, y_res_s + ps_h
            x_res_e = res_w if x_res_e > res_w else x_res_e
            y_res_e = res_h if y_res_e > res_h else y_res_e
            cv2.matchTemplate(
                image=part_view,
                templ=templ,
                method=method,
                result=result[
                    y_res_s:y_res_e,
                    x_res_s:x_res_e],
                mask=mask)

    # x-axis separator-part-wise calculation
    for j_y in range(y_parts_cnt):
        for i_x in range(x_parts_cnt):
            x_part_s = i_x * ps_w + (ps_w - templ_w + 1)
            y_part_s = j_y * ps_h
            x_part_e = x_part_s + (2 * templ_w - 2)
            y_part_e = y_part_s + ps_h + templ_h - 1
            y_part_e = img_h if y_part_e > img_h else y_part_e
            part_view = image[
                y_part_s:y_part_e,
                x_part_s:x_part_e]
            if not part_view.size or part_view.shape[0] < templ_h:
                continue
            x_res_s = i_x * ps_w + (ps_w - templ_w + 1)
            y_res_s = j_y * ps_h
            x_res_e, y_res_e = x_res_s + templ_w - 1, y_res_s + ps_h
            y_res_e = res_h if y_res_e > res_h else y_res_e
            cv2.matchTemplate(
                image=part_view,
                templ=templ,
                method=method,
                result=result[
                    y_res_s:y_res_e,
                    x_res_s:x_res_e],
                mask=mask)
    return result
