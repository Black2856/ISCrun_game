#####################################################
# ET-robot-contest Game Area Detection and find block color.
# Copyright © 2022 naoki hunada. All rights reserved.
#####################################################

import numpy as np
import cv2

### 交点を求める(未使用)
def find_intersection(line1_pos1, line1_pos2, line2_pos1, line_2_pos2):
    x1, y1 = line1_pos1
    x2, y2 = line1_pos2
    x3, y3 = line2_pos1
    x4, y4 = line_2_pos2

    denom = ((y4 - y3) * (x2 - x1)) - ((x4 - x3) * (y2 - y1))
    if denom == 0:
        return None

    numerator1 = ((x4 - x3) * (y1 - y3)) - ((y4 - y3) * (x1 - x3))
    numerator2 = ((x2 - x1) * (y1 - y3)) - ((y2 - y1) * (x1 - x3))

    a = numerator1 / denom
    b = numerator2 / denom

    if a > 0 and a < 1 and b > 0 and b < 1:
        x = x1 + (a * (x2 - x1))
        y = y1 + (a * (y2 - y1))
        return (x, y)

    return None

### 難所の中心座標から各点までの相対座標を求める(未使用)
def point_scale(point, scale):
    p = np.array(point)
    COG = find_intersection(point[0], point[2], point[1], point[3])
    relative_p = p - COG
    ret = np.round(relative_p * scale + COG, 0)
    ret = ret.astype(np.int64)
    return ret.tolist()

### エリアの角のポイントからscale分の距離で射影変換する
def area_perspective_transform(img, point, scale):
    height, width, channels = img.shape[:3]
    size = 300

    source_points1 = np.array([point[0], point[1], point[2], point[3]], dtype=np.float32)
    target_points = np.array([[0, 0], [0, size], [size, size], [size, 0]], dtype=np.float32)

    mat1 = cv2.getPerspectiveTransform(source_points1, target_points)
    mat2 = cv2.getPerspectiveTransform(target_points, source_points1)

    diff = scale
    new_point = np.array([[[0-diff, 0-diff], [size+diff, 0-diff], [size+diff, size+diff], [0-diff, size+diff]]], dtype='float32')
    new_point = cv2.perspectiveTransform(new_point, mat2)
    new_point = new_point[0]
    source_points2 = np.array([new_point[0], new_point[1], new_point[2], new_point[3]], dtype=np.float32)
    mat3 = cv2.getPerspectiveTransform(source_points2, target_points)

    perspective_image = cv2.warpPerspective(img, mat3, (size, size))

    p = np.array([[[-50, -50]]], dtype='float32')
    pointsOut = cv2.perspectiveTransform(p, mat2)

    return perspective_image

#img = cv2.imread("a.png")
#point = [[282, 195], [196, 71], [59, 104], [109, 261]]
#drawpoint(img, point)
#img = area_perspective_transform(img, point, 82)
#plt.imshow(np.asarray(img))