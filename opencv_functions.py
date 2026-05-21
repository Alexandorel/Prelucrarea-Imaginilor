import cv2
import numpy as np


def canny_edge_detection_cv(matrix, low_threshold=50, high_threshold=150):

    arr = np.array(matrix, dtype=np.uint8)
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 1.4)

    edges = cv2.Canny(blurred, low_threshold, high_threshold,
                      apertureSize=3, L2gradient=True)

    height, width = edges.shape
    result = [[[int(edges[y, x])] * 3 for x in range(width)] for y in range(height)]
    return result


def canny_edge_detection_adaptive_cv(matrix, sigma=0.33):
    arr = np.array(matrix, dtype=np.uint8)
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 1.4)

    median = float(np.median(blurred))
    low_threshold = int(max(0, (1.0 - sigma) * median))
    high_threshold = int(min(255, (1.0 + sigma) * median))

    edges = cv2.Canny(blurred, low_threshold, high_threshold,
                      apertureSize=3, L2gradient=True)

    height, width = edges.shape
    result = [[[int(edges[y, x])] * 3 for x in range(width)] for y in range(height)]
    return result
