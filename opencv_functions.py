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
