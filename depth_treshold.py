import cv2 as cv
import numpy as np


def create_mask(depth):

    depth_non_extreme = depth.copy()
    prev_dept_non_extreme_array = []
    for i in range(20):
        prev_dept_non_extreme_array.append(depth_non_extreme)
        current_max = np.nanmax(depth_non_extreme)
        depth_non_extreme[depth > np.floor(current_max-1)] = np.nan
        if np.count_nonzero(~np.isnan(depth_non_extreme)) == 0:
            depth_non_extreme = prev_dept_non_extreme_array[i-5 if i > 5 else i - 1]
            break
    depth_non_extreme[depth < 3] = np.nan

    #non_extreme_median_depth = np.nanmedian(depth_non_extreme)
    non_extreme_max_depth = np.nanmax(depth_non_extreme)
    #non_extreme_mean_depth = np.nanmean(depth_non_extreme)

    t = non_extreme_max_depth

    depth_img = depth.astype(np.uint8)

    _, thresh = cv.threshold(depth_img, t, 255, cv.THRESH_BINARY_INV)


    return thresh
