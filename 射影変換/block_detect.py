#####################################################
# ET-robot-contest Game Area Detection and find block color.
# Copyright © 2022 naoki hunada. All rights reserved.
#####################################################

from sklearn.decomposition import PCA
from PIL import Image, ImageDraw
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import cv2

class option:
    BLOCK_POS = [[],[],[],[],[],[],[],[],[],[],[],[],[]]
    RED_BLOCK_MIN_THRESHOLD1 = [0, 0, 0] #HSV
    RED_BLOCK_MAX_THRESHOLD1 = [0, 0, 0] #HSV
    RED_BLOCK_MIN_THRESHOLD2 = [0, 0, 0] #HSV
    RED_BLOCK_MAX_THRESHOLD2 = [0, 0, 0] #HSV
    GREEN_BLOCK_MIN_THRESHOLD = [0, 0, 0] #HSV
    GREEN_BLOCK_MAX_THRESHOLD = [0, 0, 0] #HSV
    BLUE_BLOCK_MIN_THRESHOLD = [0, 0, 0] #HSV
    BLUE_BLOCK_MAX_THRESHOLD = [0, 0, 0] #HSV
    YELLOW_BLOCK_MIN_THRESHOLD = [0, 0, 0] #HSV
    YELLOW_BLOCK_MAX_THRESHOLD = [0, 0, 0] #HSV

class blockAreaDetect:

    __param = option()

    def set_option(self, set_param: option):
        self.__param.BLOCK_POS = set_param.BLOCK_POS
        self.__param.RED_BLOCK_MIN_THRESHOLD1 = set_param.RED_BLOCK_MIN_THRESHOLD1
        self.__param.RED_BLOCK_MAX_THRESHOLD1 = set_param.RED_BLOCK_MAX_THRESHOLD1
        self.__param.RED_BLOCK_MIN_THRESHOLD2 = set_param.RED_BLOCK_MIN_THRESHOLD2
        self.__param.RED_BLOCK_MAX_THRESHOLD2 = set_param.RED_BLOCK_MAX_THRESHOLD2
        self.__param.GREEN_BLOCK_MIN_THRESHOLD = set_param.GREEN_BLOCK_MIN_THRESHOLD
        self.__param.GREEN_BLOCK_MAX_THRESHOLD = set_param.GREEN_BLOCK_MAX_THRESHOLD
        self.__param.BLUE_BLOCK_MIN_THRESHOLD = set_param.BLUE_BLOCK_MIN_THRESHOLD
        self.__param.BLUE_BLOCK_MAX_THRESHOLD = set_param.BLUE_BLOCK_MAX_THRESHOLD
        self.__param.YELLOW_BLOCK_MIN_THRESHOLD = set_param.YELLOW_BLOCK_MIN_THRESHOLD
        self.__param.YELLOW_BLOCK_MAX_THRESHOLD = set_param.YELLOW_BLOCK_MAX_THRESHOLD

    @property
    def param(self):
        return self.__param

    ### 画像処理 閾値マスク -> 2値化 (hsv)
    def img_mask(self, img, min, max):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hsv_min = np.array(min)
        hsv_max = np.array(max) # |調整箇所|
        mask = cv2.inRange(hsv, hsv_min, hsv_max)
        masked_img = cv2.bitwise_and(img, img, mask=mask)
        mask_gray = cv2.cvtColor(masked_img, cv2.COLOR_BGR2GRAY)
        ret, mask_bit = cv2.threshold(mask_gray, 1, 255, cv2.THRESH_BINARY)
        kernel = np.ones((4, 4), np.uint8)
        mask_bit = cv2.dilate(mask_bit, kernel, iterations = 1)
        return mask_bit

    ### エリア内のブロックの検出 300×300の場合
    def detect_block(self, img):
        block_color = [0 for i in self.__param.BLOCK_POS] #0:無, 1:赤, 2:緑, 3:青, 4:黄色

        #画像の平滑化
        size = 4
        kernel = np.ones((size, size),np.float32) / (size**2)
        blurred_img = cv2.filter2D(img,-1,kernel)

        #マスク
        red_bit1 = self.img_mask(blurred_img, self.__param.RED_BLOCK_MIN_THRESHOLD1, self.__param.RED_BLOCK_MAX_THRESHOLD1)
        red_bit2 = self.img_mask(blurred_img, self.__param.RED_BLOCK_MIN_THRESHOLD2, self.__param.RED_BLOCK_MAX_THRESHOLD2)
        red_bit = red_bit1 | red_bit2
        green_bit = self.img_mask(blurred_img, self.__param.GREEN_BLOCK_MIN_THRESHOLD, self.__param.GREEN_BLOCK_MAX_THRESHOLD)
        blue_bit = self.img_mask(blurred_img, self.__param.BLUE_BLOCK_MIN_THRESHOLD, self.__param.BLUE_BLOCK_MAX_THRESHOLD)
        yellow_bit = self.img_mask(blurred_img, self.__param.YELLOW_BLOCK_MIN_THRESHOLD, self.__param.YELLOW_BLOCK_MAX_THRESHOLD)

        #検知
        for i, a in enumerate(self.__param.BLOCK_POS):
            if(red_bit[a[1]][a[0]] == 255):
                block_color[i] = 1
            if(green_bit[a[1]][a[0]] == 255):
                block_color[i] = 2
            if(blue_bit[a[1]][a[0]] == 255):
                block_color[i] = 3
            if(yellow_bit[a[1]][a[0]] == 255):
                block_color[i] = 4

        block_color[4] = 0

        #ブロックの数が正しいか
        success = False
        if(block_color.count(1) == 3 and block_color.count(2) == 3 and block_color.count(3) == 3 and block_color.count(4) == 3):
            success = True

        #plt.imshow(np.array(green_bit))
        return block_color, success

    