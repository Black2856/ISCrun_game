#####################################################
# ET-robot-contest Game Area Detection and find block color.
# Copyright © 2022 naoki hunada. All rights reserved.
#####################################################

from operator import index
from sklearn.decomposition import PCA
from PIL import Image, ImageDraw
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import cv2

from copy import deepcopy
import sys
import math

class option:
    PROCESS_IMAGE_SIZE = [0, 0]
    IMAGE_MASK_MIN_THRESHOLD = [0, 0, 0] #HSV
    IMAGE_MASK_MAX_THRESHOLD = [0, 0, 0] #HSV
    LINE_COLOR_DETECTION_FINENESS = 0
    LINE_COLOR_DETECTION_SCORE_THRESHOLD = 0
    LINE_COLOR_DETECTION_MAX_THRESHOLD = [0, 0, 0] #HSV
    LINE_DETECTION_ROTATE_RANGE = 0
    POINT_DETECTION_MIN_AREA_THRESHOLD = 0
    POINT_DETECTION_MAX_AREA_THRESHOLD = 0
    BLUE_CIRCLE_DETECTION_MIN_THRESHOLD = [0, 0, 0] #HSV
    BLUE_CIRCLE_DETECTION_MAX_THRESHOLD = [0, 0, 0] #HSV
    GREEN_CIRCLE_DETECTION_MIN_THRESHOLD = [0, 0, 0] #HSV
    GREEN_CIRCLE_DETECTION_MAX_THRESHOLD = [0, 0, 0] #HSV

class AreaDetection:

    ### 環境変数
    __param = option()

    def set_option(self, set_param: option):
        self.__param.PROCESS_IMAGE_SIZE = set_param.PROCESS_IMAGE_SIZE
        self.__param.IMAGE_MASK_MIN_THRESHOLD = set_param.IMAGE_MASK_MIN_THRESHOLD
        self.__param.IMAGE_MASK_MAX_THRESHOLD = set_param.IMAGE_MASK_MAX_THRESHOLD
        self.__param.LINE_COLOR_DETECTION_FINENESS = set_param.LINE_COLOR_DETECTION_FINENESS
        self.__param.LINE_COLOR_DETECTION_SCORE_THRESHOLD = set_param.LINE_COLOR_DETECTION_SCORE_THRESHOLD
        self.__param.LINE_COLOR_DETECTION_MAX_THRESHOLD = set_param.LINE_COLOR_DETECTION_MAX_THRESHOLD
        self.__param.LINE_DETECTION_ROTATE_RANGE = set_param.LINE_DETECTION_ROTATE_RANGE
        self.__param.POINT_DETECTION_MIN_AREA_THRESHOLD = set_param.POINT_DETECTION_MIN_AREA_THRESHOLD
        self.__param.POINT_DETECTION_MAX_AREA_THRESHOLD = set_param.POINT_DETECTION_MAX_AREA_THRESHOLD
        self.__param.BLUE_CIRCLE_DETECTION_MIN_THRESHOLD = set_param.BLUE_CIRCLE_DETECTION_MIN_THRESHOLD
        self.__param.BLUE_CIRCLE_DETECTION_MAX_THRESHOLD = set_param.BLUE_CIRCLE_DETECTION_MAX_THRESHOLD
        self.__param.GREEN_CIRCLE_DETECTION_MIN_THRESHOLD = set_param.GREEN_CIRCLE_DETECTION_MIN_THRESHOLD
        self.__param.GREEN_CIRCLE_DETECTION_MAX_THRESHOLD = set_param.GREEN_CIRCLE_DETECTION_MAX_THRESHOLD

    @property
    def param(self):
        return self.__param

    ### 座標から0~360度の範囲で返す 引数 pos = [x,y]
    def __pos2deg(self, pos):
        posh = [i + 0.001 for i in pos]
        deg = math.degrees(math.atan(posh[1]/posh[0]))
        if(posh[0] >= 0 and posh[1] < 0):
            deg += 360
        elif(posh[0] < 0 and posh[1] >= 0):
            deg += 180
        elif(posh[0] < 0 and posh[1] < 0):
            deg += 180
        return deg

    ### ラインの中心座標を求める
    def __line_COG(self, line_pos_list):
        lpl = deepcopy(line_pos_list)
        line_COG = []
        line_pos_COG = []
        # 各座標から重心を求める
        for i in lpl:
            x = 0
            y = 0
            for j in i:
                x += j[0]
                y += j[1]
            x = x / len(i)
            y = y / len(i)
            # 重心からの距離を求める
            distance = []
            for num, j in enumerate(i):
                distance.append([num, math.sqrt((j[0] - x)**2 + (j[1] - y)**2)])
            distance = sorted(distance, key=lambda x: x[1], reverse=True)

            pos = np.round((i[distance[0][0]] + i[distance[1][0]]) / 2)
            line_COG.append(pos.astype(np.int64))
            line_pos_COG.append([i[distance[0][0]].tolist(), i[distance[1][0]].tolist()])
            #line_COG.append([i[distance[0][0]], i[distance[1][0]]])

        return line_COG, line_pos_COG

    ### 推測した直線を描画する
    def __drawline(self, img, line_pos_list, color=(0, 0, 255), size= 1):
        for i in line_pos_list:
            for j in i:
                for k in i:
                    cv2.line(img, (j[0], j[1]), (k[0], k[1]), color, size)

    ### 指定座標にポイントを描画する
    def __drawpoint(self, img, point_pos_list, color=(255, 255, 255), size=3):
        for num,i in enumerate(point_pos_list):
            cv2.circle(img, i, size, color, thickness=-1, lineType=cv2.LINE_AA, shift=0)
            cv2.circle(img, i, size, (0, 0, 0), thickness=1, lineType=cv2.LINE_AA, shift=0)
        #cv2.putText(point_pos_list, str(num), i, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), thickness=2)

    ### pos1 から pos2までの直線pxのlistを返す nは分割数
    def __create_line_point(self, pos1, pos2, n):
        npos1 = np.array(pos1)
        npos2 = np.array(pos2)

        dpos = (npos2 - npos1) / (n + 1)

        pos = npos1
        li = []
        for i in range(n):
            pos = pos + dpos
            li.append(pos.tolist())
        li = np.unique(np.round(li, 0), axis=0)
        li = li.astype(np.int64)
        return li.tolist()

    ### 2値化imgからpos_listの座標の色を取得した平均を返す(HSV)
    def __get_avg_color(self, bit_img, pos_list):
        bias_list = []
        bias = 0

        for i in pos_list:
            if(bit_img[i[1], i[0]] == 255):
                if(bias >= 0):
                    bias += 1
                else:
                    bias_list.append(bias)
                    bias = 1
            else:
                if(bias <= 0):
                    bias -= 1
                else:
                    bias_list.append(bias)
                    bias = -1
        bias_list.append(bias)
        return np.sum(bias_list * np.abs(bias_list))

    ### 2値化img画像とline_list間の適合を調べる(find_line関数で主に使用)
    def __check_color(self, bit_img, line):
        li_COG, li_pos_COG = self.__line_COG([line])
        pos_list = self.__create_line_point(li_pos_COG[0][0], li_pos_COG[0][1], self.__param.LINE_COLOR_DETECTION_FINENESS) # |n 調整箇所|
        ret = self.__get_avg_color(bit_img, pos_list)
        return ret >= self.__param.LINE_COLOR_DETECTION_SCORE_THRESHOLD

    ### 検知した直線のポイントにlimit数分の制限にして返す(削除の順番はtarget_point座標から一番遠い場所) (find_line関数で主に使用)
    def __limit_point(self, target_point, line, li_pos, limit):
        target_index = li_pos.index(target_point)
        ret_line = []
        ret_li_pos = []
        if(len(line) > limit):
            pca = PCA(n_components=1)
            pca.fit(li_pos)
            pca_line = pca.transform(li_pos)
            pca_line = abs(pca_line - pca_line[target_index])
            pca_line = [[i, a[0]] for i,a in enumerate(pca_line)]
            pca_line = sorted(pca_line, reverse=False, key = lambda x: x[1])
            for i,a in enumerate(pca_line):
                ret_line.append(line[a[0]])
                ret_li_pos.append(li_pos[a[0]])
                if(i == limit - 1):
                    break
        else:
            ret_line = line
            ret_li_pos = li_pos
        return ret_line, ret_li_pos

    ### ポイント[x, y]の配列からpoint以上の数からなる直線を探す {引数} point:[[座標]], min_point:最小ポイント数 bit_img:２値化画像
    def __find_line(self, point, count, tolerance, bit_img):
        c_point = []
        point2 = [[i, a] for i, a in enumerate(point)]
        #print(point2)
        used_point = [[i] for i in range(len(point2))]
        line_list = []

        for i, x in enumerate(point2): #各ポイントからポイントへの角度を割り出す
            comp = deepcopy(point2)
            comp = [[j[0], j[1]] for j in comp if not(j[0] in used_point[i])] #used_pointのポイントを除外
            relative = np.array([a[1] - x[1] for a in comp])

            #相対角度の計算
            deg = np.array([[[comp[j][0], self.__pos2deg([a[0], a[1]])] for j, a in enumerate(relative)]])
            deg = deg[0][np.argsort(deg[0][:, 1])]
            diff = np.array([abs(deg[i][1] - deg[i+1][1]) for i in range(len(deg)-1)]) #ソートした相対角度を角度の差分値でとる
            #直線であるポイントを探索
            match_count = 0 #直線上のポイント数
            line = [x[0]]
            for a, val in enumerate(diff):
                if(val <= tolerance):# tolerance度以内であれば直線と判断
                    if(not(deg[a][0] in line)):
                       line.append(int(deg[a][0]))
                    if(not(deg[a + 1][0] in line)):
                       line.append(int(deg[a + 1][0]))
                else:# 満たしてなければ引数条件で直線リストに格納
                    li_pos = [point2[i][1] for i in line]
                    line, li_pos = self.__limit_point(x[1], line, li_pos, count)
                    if(len(line) >= count and self.__check_color(bit_img, li_pos)): # |色 調整箇所|
                        for b in line:
                            for c in line:
                                if(not(c in used_point[b])):
                                    used_point[b].append(c)
                        line_list.append(line)
                    line = [x[0]]

            li_pos = [point2[i][1] for i in line]
            line, li_pos = self.__limit_point(x[1], line, li_pos, count)
            if(len(line) >= count and self.__check_color(bit_img, li_pos)):# 終了時の格納 |色 調整箇所|
                for b in line:
                    for c in line:
                        if(not(c in used_point[b])):
                            used_point[b].append(c)
                line_list.append(line)
        #推測したポイント番号を座標に変換
        line_pos_list = []
        for i in line_list:
            line_pos = []
            for j in i:
                line_pos.append(point2[j][1])
            line_pos_list.append(line_pos)
        return line_pos_list

    ### 画像処理 閾値マスク (hsv)
    def __img_mask(self, img, min, max):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hsv_min = np.array(min)
        hsv_max = np.array(max) # |調整箇所|
        mask = cv2.inRange(hsv, hsv_min, hsv_max)
        masked_img = cv2.bitwise_and(img, img, mask=mask)

        return masked_img

    ### 画像と特定したポイントから並び替える
    def __sort_point(self, point, li_pos_COG2, blue_circle_img, green_circle_img):
        if not(len(point) == 4): #pointが4つであるかどうか
            return point, False

        #緑と青のpointを調べる
        point_color = [0, 0, 0, 0]
        new_point = [[], [], [], []]
        for i, a in enumerate(point):
            if(blue_circle_img[a[1]][a[0]] == 255):
                point_color[i] = 1
                new_point[0] = a
            if(green_circle_img[a[1]][a[0]] == 255):
                point_color[i] = 2
                new_point[1] = a
        
        if not(point_color.count(1) == 1 and point_color.count(2) == 1): #青と緑がそれぞれ1つずつであるか
            return point, False
        #並び替え
        find_pos = [new_point[1], new_point[0]] #[見つける要素, 含まない要素]
        for i in range(2, len(new_point)):
            for j, a in enumerate(li_pos_COG2):
                if(not(find_pos[1] in a) and (find_pos[0] in a)):
                    find_pos[1] = find_pos[0]
                    if(a.index(find_pos[0]) == 0):
                        find_pos[0] = a[1]
                    else:
                        find_pos[0] = a[0]
                    new_point[i] = find_pos[0]
                    break
        return new_point, True

    ### 難所の検出
    def detect(self, img):
        size = self.__param.PROCESS_IMAGE_SIZE# |調整箇所|

        image = img
        image = cv2.resize(image, dsize=size)
        outputImg = deepcopy(image)
        rawImg = deepcopy(image)
        height, width, channels = image.shape[:3]

        # 画像処理
        #サークル間の黒ライン　と カラーサークル
        mask_line = self.__img_mask(image, [0, 0, 0], self.__param.LINE_COLOR_DETECTION_MAX_THRESHOLD)
        mask_line = cv2.cvtColor(mask_line, cv2.COLOR_BGR2GRAY)
        ret, mask_line = cv2.threshold(mask_line, 1, 255, cv2.THRESH_BINARY)
        #カラーサークル
        mask_circle = self.__img_mask(image, self.__param.IMAGE_MASK_MIN_THRESHOLD, self.__param.IMAGE_MASK_MAX_THRESHOLD)
        blue_circle = self.__img_mask(mask_circle, self.__param.BLUE_CIRCLE_DETECTION_MIN_THRESHOLD, self.__param.BLUE_CIRCLE_DETECTION_MAX_THRESHOLD)
        green_circle = self.__img_mask(mask_circle, self.__param.GREEN_CIRCLE_DETECTION_MIN_THRESHOLD, self.__param.GREEN_CIRCLE_DETECTION_MAX_THRESHOLD)
        mask_circle = cv2.cvtColor(mask_circle, cv2.COLOR_BGR2GRAY)
        blue_circle = cv2.cvtColor(blue_circle, cv2.COLOR_BGR2GRAY)
        green_circle = cv2.cvtColor(green_circle, cv2.COLOR_BGR2GRAY)
        ret, mask_circle = cv2.threshold(mask_circle, 1, 255, cv2.THRESH_BINARY)
        ret, blue_circle = cv2.threshold(blue_circle, 1, 255, cv2.THRESH_BINARY)
        ret, green_circle = cv2.threshold(green_circle, 1, 255, cv2.THRESH_BINARY)

        #(サークル間の黒ライン　と カラーサークル) モルフォロジー処理、合成
        bit_area = mask_circle | mask_line
        kernel = np.ones((4,4),np.uint8)
        bit_area = cv2.dilate(bit_area, kernel, iterations = 1)
        #(カラーサークル) エッジ、モルフォロジー処理
        mask_circle = cv2.Canny(mask_circle, 50, 100)
        kernel = np.ones((2,2),np.uint8)
        mask_circle = cv2.dilate(mask_circle, kernel, iterations = 1)
        blue_circle = cv2.dilate(blue_circle, kernel, iterations = 1)
        green_circle = cv2.dilate(green_circle, kernel, iterations = 1)

        #輪郭取得    
        contours, hierarchy= cv2.findContours(mask_circle, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        pointer = [i for i in range(len(contours))] #排除用
        len(contours) 

        # 輪郭の面積を計算する。
        for i in pointer:
            cnt = contours[i]
            area = cv2.contourArea(cnt)
            #print(f"contour: {i}, area: {area}")
            if(not(self.__param.POINT_DETECTION_MIN_AREA_THRESHOLD < area and area < self.__param.POINT_DETECTION_MAX_AREA_THRESHOLD)):# |領域 調整箇所|
                pointer[i] = -1

        pointer = [i for i in pointer if i != -1] #除外された輪郭を削除

        COG = [] #重心の配列

        for i in pointer:
            try:
                cnt = contours[i]
                # 輪郭のモーメントを計算する。
                M = cv2.moments(cnt)
                # モーメントから重心を計算する。
                cx = int(round(M["m10"] / M["m00"],0))
                cy = int(round(M["m01"] / M["m00"],0))
                COG.append([cx, cy])
            except:
                pointer[i] = -1
            #print(f"contour: {i}, centroid: ({cx:.2f}, {cy:.2f})")

        pointer = [i for i in pointer if i != -1] #除外された輪郭を削除


        if(len(COG) < 3):
            return outputImg
        #COG.append([122, 305])
        #絞りだしたポイントから4つの重なる直線を調べる
        COG = np.array(COG)
        li_list = self.__find_line(COG, 4, self.__param.LINE_DETECTION_ROTATE_RANGE, bit_area)# |直線 調整箇所|
        li_COG, li_pos_COG = self.__line_COG(li_list)
        self.__drawline(outputImg, li_list)
        #推測した直線の端のポイントを対象として再度ラインを見つける
        point = np.array([i[0] for i in li_pos_COG] + [i[1] for i in li_pos_COG])
        point = np.unique(point, axis=0)

        li_list = self.__find_line(point, 4, self.__param.LINE_DETECTION_ROTATE_RANGE, bit_area)# |直線 調整箇所|
        li_COG, li_pos_COG = self.__line_COG(li_list)

        #推測したラインの端のポイントから引いているラインの数を数えて、2未満のものは削除
        point = np.array([i[0] for i in li_pos_COG] + [i[1] for i in li_pos_COG])
        point, count = np.unique(point, return_counts=True, axis=0)
        point = [a.tolist() for i,a in enumerate(point) if count[i] >= 2]

        li_pos_COG2 = [i for i in li_pos_COG if i[0] in point and i[1] in point]
        success = False
        point, success = self.__sort_point(point, li_pos_COG2, blue_circle, green_circle)
        if(success == False):
            point = []
        else:
            point = [point[2], point[1], point[0], point[3]]

        #self.__drawline(outputImg, li_pos_COG2)
        #print(li_pos_COG)
        #self.__drawline(outputImg, COG)
        #print(li_list)
        #print(point)

        #推測したサークルポイントを表示させる
        self.__drawline(outputImg, li_pos_COG2, color=(0, 255, 0), size= 3)
        self.__drawpoint(outputImg, COG)
        self.__drawpoint(outputImg, point, color=(0, 255, 0))

        #表示
        return [outputImg, bit_area, rawImg], point, success



