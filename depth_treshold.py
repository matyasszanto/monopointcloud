import cv2 as cv
import numpy as np


def create_mask(depth):

    depth_non_extreme = depth.copy()

    for i in range(20):
        current_max = np.nanmax(depth_non_extreme)
        depth_non_extreme[depth > np.floor(current_max-1)] = np.nan
    depth_non_extreme[depth < 3] = np.nan

    #non_extreme_median_depth = np.nanmedian(depth_non_extreme)
    non_extreme_max_depth = np.nanmax(depth_non_extreme)
    #non_extreme_mean_depth = np.nanmean(depth_non_extreme)

    t = non_extreme_max_depth

    depth_stretched_img = depth_non_extreme.astype(np.uint8)

    _, thresh = cv.threshold(depth_stretched_img, t, 255, cv.THRESH_BINARY_INV)

    return thresh
