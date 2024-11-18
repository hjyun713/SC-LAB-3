import sys
import time

import cv2
import os
import numpy as np
import math
import mediapipe as mp
import copy
from PyQt5.QtCore import QThread, pyqtSignal
from PIL import Image, ImageDraw



def sec_to_time(sec):
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)

def draw_landmarks(image, landmarks, color, p_size):
    image_width, image_height = image.shape[1], image.shape[0]

    # landmark 연산
    for index, landmark in enumerate(landmarks.landmark):
        if landmark.visibility < 0 or landmark.presence < 0:
            continue
        landmark_x = landmark.x
        landmark_y = landmark.y
        landmark_z = landmark.z

        # landmark_point
        result_x = min(int(landmark_x * image_width), image_width - 1)
        result_y = min(int(landmark_y * image_height), image_height - 1)

        cv2.circle(image, (result_x, result_y), 1, color, p_size)

    return image

# 정합 함수 - hoi's
def ptRegistration(landmark_0, landmark_pt):

    # 소수 과학적 표기법 억제 ex: 10e-10가 아니라 0.00--1로 나오도록
    np.set_printoptions(suppress=True)

    landmark_0 = np.array(landmark_0)
    landmark_pt = np.array(landmark_pt)

    # # 3D to 2D (z axie is zero)
    # for i in range(len(landmark_0)):
    #     landmark_0[i][2] = 0
    
    # for i in range(len(landmark_pt)):
    #     landmark_pt[i][2] = 0
    
    # print(f'ldpt 0 chg: {landmark_0[pt]}')
    # print(f'ldpt 1 chg: {landmark_pt[pt]}')

    # ??
    inlier_rmse = get_inlier_rmse(landmark_0, landmark_pt)
    # print(f'inlier_rmse : {inlier_rmse}')

    landmark_0, landmark_pt = axis_move(landmark_0, landmark_pt)
    landmark_0, landmark_pt = axis_rotation(landmark_0, landmark_pt)
    landmark_0, landmark_pt = axis_scale(landmark_0, landmark_pt)

    return landmark_0, landmark_pt

# initial rmse (??)
def get_inlier_rmse(n_key, s_key):
    e_t = 0 # total error
    for i in range(478):
        nx, ny, nz = n_key[i]
        sx, sy, sz = s_key[i]

        e_i = math.pow((nx-sx), 2) + math.pow((ny-sy), 2) + math.pow((nz-sz), 2)
        # e_t += math.sqrt(e_i) # rmse 식 안에 에러의 제곱이 들어가니 상쇄
        e_t += e_i

    inlier_rmse = math.sqrt(e_t/478)

    return inlier_rmse

# 좌우 양 끝 점 사이 중앙점
def middle_point(point):
    m_point = (point[127] + point[356]) / 2
    if point[168][0] - point[10][0] > 0:
        yvalue = 1
    else:
        yvalue = -1

    if  m_point[2] - point[10][2] > 0:
        xvalue = -1
    else:
        xvalue = 1

    if  m_point[0] - point[10][0] > 0:
        zvalue = 1
    else:
        zvalue = -1
    
    return abs(point[127][0] - point[356][0]), m_point, xvalue, yvalue, zvalue

# 원점 이동 - 위치 정합
def axis_move(a_point, b_point):
    ma_point = np.empty((0,3))
    mb_point = np.empty((0,3))
    for n in range(len(a_point)):
        ma_point = np.append(ma_point, np.array([a_point[n] - a_point[10]]), axis=0)
        mb_point = np.append(mb_point, np.array([b_point[n] - b_point[10]]), axis=0)
    # print(ma_point.shape, mb_point.shape)
    return ma_point, mb_point

# 코사인 유사도를 통한 각도 구하기
def angle_landmark(A, B ,C):
    a = np.radians(np.array(A))
    b = np.radians(np.array(B))
    c = np.radians(np.array(C))

    avec = a - b
    cvec = c - b

    lat = b[0]
    avec[1] *= math.cos(lat)
    cvec[1] *= math.cos(lat)

    return np.degrees(math.acos(np.dot(avec, cvec) / (np.linalg.norm(avec) * np.linalg.norm(cvec))))

# 회전 정합
def axis_rotation(a_point, b_point):

    #z
    ra_point = []
    rb_point = []
    _, ma, _, _, azvalue = middle_point(a_point)
    _, mb, _, _, bzvalue = middle_point(b_point)

    a_A = (ma[0], ma[1])
    a_B = (a_point[10][0], a_point[10][1])
    a_C = (a_point[10][0], ma[1])
    b_A = (mb[0], mb[1])
    b_B = (b_point[10][0], b_point[10][1])
    b_C = (b_point[10][0], mb[1])
    a_angle = angle_landmark(a_A, a_B, a_C) * azvalue
    b_angle = angle_landmark(b_A, b_B, b_C) * bzvalue

    for n in range(len(a_point)):
        xa = a_point[n][0]*math.cos(math.radians(a_angle)) - a_point[n][1]*math.sin(math.radians(a_angle))
        ya = a_point[n][0]*math.sin(math.radians(a_angle)) + a_point[n][1]*math.cos(math.radians(a_angle))
        za = a_point[n][2]

        ra_point.append([xa, ya, za])

        xb = b_point[n][0]*math.cos(math.radians(b_angle)) - b_point[n][1]*math.sin(math.radians(b_angle))
        yb = b_point[n][0]*math.sin(math.radians(b_angle)) + b_point[n][1]*math.cos(math.radians(b_angle))
        zb = b_point[n][2]

        rb_point.append([xb, yb, zb])

    ra_point = np.array(ra_point)
    rb_point = np.array(rb_point)

    # pt = 165
    # print(f'ldpt 0 chg rot1: {ra_point[pt]}')
    # print(f'ldpt 1 chg rot1: {rb_point[pt]}')

    #x
    _, ma2, axvalue, _, _ = middle_point(ra_point)
    _, mb2, bxvalue, _, _ = middle_point(rb_point)

    ra_point = ra_point.tolist()
    rb_point = rb_point.tolist()
    a_A2 = (ma2[1], ma2[2])
    a_B2 = (ra_point[10][1], ra_point[10][2])
    a_C2 = (ma2[1], ra_point[10][2])
    b_A2 = (mb2[1], mb2[2])
    b_B2 = (rb_point[10][1], rb_point[10][2])
    b_C2 = (mb2[1], rb_point[10][2])
    a_angle2 = (angle_landmark(a_A2, a_B2, a_C2) * axvalue)
    b_angle2 = (angle_landmark(b_A2, b_B2, b_C2) * bxvalue)

    ra_point2 = []
    rb_point2 = []

    for n in range(len(ra_point)):
        xa = ra_point[n][0]
        ya = ra_point[n][1] * math.cos(math.radians(a_angle2)) - ra_point[n][2] * math.sin(math.radians(a_angle2))
        za = ra_point[n][1] * math.sin(math.radians(a_angle2)) + ra_point[n][2] * math.cos(math.radians(a_angle2))

        ra_point2.append([xa, ya, za])

        xb = rb_point[n][0]
        yb = rb_point[n][1] * math.cos(math.radians(b_angle2)) - rb_point[n][2] * math.sin(math.radians(b_angle2))
        zb = rb_point[n][1] * math.sin(math.radians(b_angle2)) + rb_point[n][2] * math.cos(math.radians(b_angle2))

        rb_point2.append([xb, yb, zb])

    ra_point2 = np.array(ra_point2)
    rb_point2 = np.array(rb_point2)

    # print(f'ldpt 0 chg rot2: {ra_point2[pt]}')
    # print(f'ldpt 1 chg rot2: {rb_point2[pt]}')

    #y
    _, ma2, _, ayvalue, _ = middle_point(ra_point2)
    _, mb2, _, byvalue, _ = middle_point(rb_point2)

    ra_point2 = ra_point2.tolist()
    rb_point2 = rb_point2.tolist()
    a_A3 = (ra_point2[8][0], ra_point2[8][2])
    a_B3 = (ra_point2[10][0], ra_point2[10][2])
    a_C3 = (ra_point2[10][0], ra_point2[8][2])
    b_A3 = (rb_point2[8][0], rb_point2[8][2])
    b_B3 = (rb_point2[10][0], rb_point2[10][2])
    b_C3 = (rb_point2[10][0], rb_point2[8][2])
    a_angle3 = angle_landmark(a_A3, a_B3, a_C3) * ayvalue
    b_angle3 = angle_landmark(b_A3, b_B3, b_C3) * byvalue

    ra_point3 = []
    rb_point3 = []

    for n in range(len(ra_point2)):
        xa = ra_point2[n][2] * math.sin(math.radians(a_angle3)) + ra_point2[n][0] * math.cos(
            math.radians(a_angle3))
        ya = ra_point2[n][1]
        za = ra_point2[n][2] * math.cos(math.radians(a_angle3)) - ra_point2[n][0] * math.sin(
            math.radians(a_angle3))

        ra_point3.append([xa, ya, za])

        xb = rb_point2[n][2] * math.sin(math.radians(b_angle3)) + rb_point2[n][0] * math.cos(
            math.radians(b_angle3))
        yb = rb_point2[n][1]
        zb = rb_point2[n][2] * math.cos(math.radians(b_angle3)) - rb_point2[n][0] * math.sin(
            math.radians(b_angle3))

        rb_point3.append([xb, yb, zb])

    ra_point3 = np.array(ra_point3)
    rb_point3 = np.array(rb_point3)

    # print(f'ldpt 0 chg rot3: {ra_point3[pt]}')
    # print(f'ldpt 1 chg rot3: {rb_point3[pt]}')


    return ra_point3, rb_point3

# 크기 정합
def axis_scale(a_point, b_point):
    wa, ma, _, _, _ = middle_point(a_point)
    wb, mb, _, _, _ = middle_point(b_point)
    
    w_ratio = float(wa)/float(wb)
    h_ratio = float(abs(ma[1] - a_point[10][1])) / float(abs(mb[1] - b_point[10][1]))
    z_ratio = float(abs(ma[2] - a_point[8][2])) / float(abs(mb[2] - b_point[8][2]))

    # print(f'scale_ratio [w: {w_ratio} | h: {h_ratio} | z: {z_ratio}]')

    for n in range(len(b_point)):
        b_point[n][0] = b_point[n][0] * w_ratio
        b_point[n][1] = b_point[n][1] * h_ratio
        b_point[n][2] = b_point[n][2] * z_ratio

    return a_point, b_point

class LandmarkAnalysis():
    def __init__(self):
        
        self.num_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219]
        
        # 왼쪽과 오른쪽 포인트 220쌍
        self.list_L = [109, 108, 107, 67, 69, 66, 103, 104, 105, 54, 68, 63, 21, 71, 70, 162, 139, 156, 127, 34, 143, 35, 124, 46, 53, 52, 65, 55, 226, 113, 225, 224, 223, 222, 221, 193, 130, 247, 30, 29, 27, 28, 56, 189, 190, 33, 246, 161, 160, 159, 158, 157, 173, 133, 7, 163, 144, 145, 153, 154, 155, 25, 110, 24, 23, 22, 26, 112, 243, 244, 245, 122, 31, 228, 229, 230, 231, 232, 233, 111, 117, 118, 119, 120, 121, 128, 234, 227, 116, 100, 47, 114, 188, 142, 126, 217, 174, 196, 209, 198, 236, 3, 129, 49, 131, 134, 51, 102, 48, 115, 220, 45, 64, 219, 218, 237, 44, 235, 166, 79, 239, 98, 240, 59, 75, 60, 20, 238, 241, 125, 242, 141, 99, 97, 93, 137, 123, 50, 101, 36, 203, 205, 206, 132, 177, 147, 187, 207, 58, 215, 213, 172, 138, 192, 216, 92, 165, 167, 212, 186, 57, 185, 40, 39, 37, 61, 76, 62, 184, 74, 73, 72, 183, 42, 41, 38, 78, 191, 80, 81, 82, 95, 88, 178, 87, 96, 89, 179, 86, 77, 90, 180, 85, 146, 91, 181, 84, 202, 43, 106, 182, 83, 204, 194, 201, 214, 210, 211, 32, 208, 135, 169, 170, 140, 171, 136, 150, 149, 176, 148]
        self.list_R = [338, 337, 336, 297, 299, 296, 332, 333, 334, 284, 298, 293, 251, 301, 300, 389, 368, 383, 356, 264, 372, 265, 353, 276, 283, 282, 295, 285, 446, 342, 445, 444, 443, 442, 441, 417, 359, 467, 260, 259, 257, 258, 286, 413, 414, 263, 466, 388, 387, 386, 385, 384, 398, 362, 249, 390, 373, 374, 380, 381, 382, 255, 339, 254, 253, 252, 256, 341, 463, 464, 465, 351, 261, 448, 449, 450, 451, 452, 453, 340, 346, 347, 348, 349, 350, 357, 454, 447, 345, 329, 277, 343, 412, 371, 355, 437, 399, 419, 429, 420, 456, 248, 358, 279, 360, 363, 281, 331, 278, 344, 440, 275, 294, 439, 438, 457, 274, 455, 392, 309, 459, 327, 460, 289, 305, 290, 250, 458, 461, 354, 462, 370, 328, 326, 323, 366, 352, 280, 330, 266, 423, 425, 426, 361, 401, 376, 411, 427, 288, 435, 433, 397, 367, 416, 436, 322, 391, 393, 432, 410, 287, 409, 270, 269, 267, 291, 306, 292, 408, 304, 303, 302, 407, 272, 271, 268, 308, 415, 310, 311, 312, 324, 318, 402, 317, 325, 319, 403, 316, 307, 320, 404, 315, 375, 321, 405, 314, 422, 273, 335, 406, 313, 424, 418, 421, 434, 430, 431, 262, 428, 364, 394, 395, 369, 396, 365, 379, 378, 400, 377]
        
        self.area0_green = [163, 162, 170, 169, 174, 173, 178, 179, 182, 183, 186, 187, 190, 194, 195, 161, 168, 172, 177, 181, 185, 189, 193, 176, 167, 166, 165]
        self.area1_blue = [142, 156, 155, 154, 159, 160, 158, 197, 198, 199] + self.area0_green
        self.area2_yellow = [102, 140, 121, 142, 156, 157, 155, 154, 159]
        self.area3_red = [164, 171, 175, 180, 184, 188, 192, 196] + self.area0_green

        self.eye = [21, 28, 29, 30, 31, 32, 33, 34, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85]
        self.eyebrow = [1, 2, 4, 5, 7, 8, 10, 11, 13, 14, 16, 17, 22, 23, 24, 25, 26, 27]
        self.cheek = [19, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 98, 99, 102, 121, 135, 136, 137, 138, 139, 140, 141, 142, 144, 145, 146, 147, 149, 150]
        self.mouth = [152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214]
        
        self.Selected = []

        # 첫 프레임의 랜드마크 리스트
        self.landmark_0 = []
        # 첫 프레임인지 체크하는 변수
        self.first_frame = True

        # 이전 프레임의 랜드마크 리스트
        self.landmark_pre = []

        # 연산 결과 여부 체크
        self.result_chk = False

        # 벡터 값 저장 dict
        self.vData = dict()
        for i in range(478):
            self.vData[str(i)] = []

        # 벡터 크기 연산 결과 저장 dict
        self.vNorm = dict()
        for i in range(478):
            self.vNorm[str(i)] = []

        # 참조 실측 크기 연산 결과 저장
        self.vNorm_ref = []
        # self.vNorm_ref = dict()
        # for i in range(478):
        #     self.vNorm_ref[str(i)] = []

        # 실측 크기 연산 결과 저장 dict
        self.vNorm_real = dict()
        for i in range(478):
            self.vNorm_real[str(i)] = []

        # 결과 저장 dict
        self.result = dict()
        self.areas = ['area0_green', 'area1_blue', 'area2_yellow', 'area3_red']
        self.f_areas = ['eye', 'eyebrow', 'cheek', 'mouth']
        self.selected_areas = ['Selected']
        self.LR = ['left', 'right']

        for t0 in self.f_areas:
            for t2 in self.LR:
                fild = f'{t0} {t2}'

                # 영상 이동량 누적합의 영역별 평균 결과
                self.result[fild] = 0

                # 영상 이동량의 영역별 평균 실측치 결과
                self.result[fild + ' (max)'] = 0

                # 영역별 평균의 대칭성 결과
                self.result['Symmetry ' + t0] = 0

        for t0 in self.areas:
            for t2 in self.LR:
                fild = f'{t0} {t2}'

                # 영상 이동량 누적합의 영역별 평균 결과
                self.result[fild] = 0

                # 영상 이동량의 영역별 평균 실측치 결과
                self.result[fild + ' (max)'] = 0

                # 영역별 평균의 대칭성 결과
                self.result['Symmetry ' + t0] = 0
        
        for t0 in self.selected_areas:
            for t2 in self.LR:
                fild = f'{t0} {t2}'

                # 영상 이동량 누적합의 영역별 평균 결과
                self.result[fild] = 0

                # 영상 이동량의 영역별 평균 실측치 결과
                self.result[fild + ' (max)'] = 0

                # 영역별 평균의 대칭성 결과
                self.result['Symmetry ' + t0] = 0

        # 기준 : 홍채 크기 / 임계값 : mm
        self.realThreshold = 11.77

    def selected_landmarks_set(self, marks):
        self.Selected = marks

    # 실측치 기준 리스트 작성
    def realMeasure(self, lp):
        
        # 좌측 홍채 크기 연산
        x = lp[471][0] - lp[469][0]
        y = lp[471][1] - lp[469][1]

        # Lnorm = abs(x)
        Lnorm = np.sqrt(x ** 2 + y ** 2)

        # 우측 홍채 크기 연산
        x = lp[476][0] - lp[474][0]
        y = lp[476][1] - lp[474][1]

        # Rnorm = abs(x)
        Rnorm = np.sqrt(x ** 2 + y ** 2)

        # 기준 : 홍채 크기 / 값 : 랜드마크 거리
        # result = max([Lnorm, Rnorm])
        result = sum([Lnorm, Rnorm]) / 2

        # print(f'LR : {Lnorm} | {Rnorm}')
        # print(result)
        
        return result

    # vector 연산
    def vectorCalc(self, next):
        f_frame = self.landmark_0
        previous = self.landmark_pre
        f_frame_reg, next_reg = ptRegistration(f_frame, next)

        # 기준 : 홍채 크기 / 값 : 랜드마크 거리
        ref_norm_before = self.realMeasure(f_frame_reg)
        ref_norm_after = self.realMeasure(next_reg)

        # ref_norm = max([ref_norm_before, ref_norm_after])
        ref_norm = sum([ref_norm_before, ref_norm_after]) / 2

        # 참조 홍채 크기 저장
        self.vNorm_ref.append(ref_norm)
        c = 0
        for i in range(478):

            # 벡터 연산
            vx = next[i][0] - previous[i][0]
            vy = next[i][1] - previous[i][1]
            vz = next[i][2] - previous[i][2]

            # 벡터 크기 (이동량) 연산
            # norm = np.sqrt(vx ** 2 + vy ** 2 + vz ** 2)
            norm = np.sqrt(vx ** 2 + vy ** 2)

            # 벡터 크기 저장
            self.vNorm[str(i)].append(norm)

            # 실측용 정합된 포인트로 연산
            vx_r = next_reg[i][0] - f_frame_reg[i][0]
            vy_r = next_reg[i][1] - f_frame_reg[i][1]
            vz_r = next_reg[i][2] - f_frame_reg[i][2]
            
            norm = np.sqrt((vx_r ** 2) + (vy_r ** 2))
            print(norm)
            c += 1
            print("LandMark :" + str(c))
            real_measure = abs(self.realThreshold * norm) / ref_norm
            print(real_measure)
            self.vNorm_real[str(i)].append(real_measure)

            # if i in self.list_L:
            #     self.leftsum = real_measure + self.leftsum
            #     print(self.leftsum)
            # elif i in self.list_R:
            #     self.rightsum = real_measure + self.rightsum
            #     print(self.rightsum)
    # 랜드마크 구조 변경
    def calcLandmark(self, landmarks):
        lp = []

        # landmark 연산
        for index, landmark in enumerate(landmarks.landmark):
            if landmark.visibility < 0 or landmark.presence < 0:
                continue

            # xy만 사용
            landmark_x = landmark.x
            landmark_y = landmark.y
            landmark_z = landmark.z

            # # z 평균
            # self.z_mean += landmark.z

            # 3d Coordinates
            lp.append([landmark_x, landmark_y, landmark_z])

        # 첫 프레임일 때 랜드 마크 저장
        if self.first_frame:
            self.landmark_0 = lp
            self.landmark_pre = lp
            self.first_frame = False
        else:
            # 벡터 연산
            self.vectorCalc(lp)
            self.landmark_pre = lp
            self.result_chk = True

        # 첫 프레임일 때 랜드 마크가 비었을 때 출력
        if len(self.landmark_0) == 0:
            print(f'First Landmark is Empty!!')
            self.first_frame = True

    # self.resultCalc 에서 사용되는 영역별 이동량 분석 함수
    def valuePerArea(self, area_pt_list, left=True):

        value_per_LP = []
        value_per_LP_Real = []
            
        for i in area_pt_list:
            if left:
                idx = str(self.list_L[i])
            else:
                idx = str(self.list_R[i])

            c_sum = sum(self.vNorm[idx])
            value_per_LP.append(c_sum)

        # 영역별 이동량 평균
        area_mean = sum(value_per_LP) / len(value_per_LP)
        # 영역별 이동량 최대
        area_max = max(value_per_LP)

        # 영역별 실측치 연산
        area_cnt = 0
        for i in area_pt_list:

            if area_cnt == 0:
                real_max = max(self.vNorm_real[idx])
                real_min = min(self.vNorm_real[idx])
            else:
                pass

            # 랜드마크별 최대 실측치
            r_max = max(self.vNorm_real[idx])

            # 랜드마크별 최소 실측치
            r_min = min(self.vNorm_real[idx])

            # 영역별 최대 실측치
            if real_max < r_max:
                real_max = r_max
            else:
                pass
            
            # 영역별 최소 실측치
            if real_min > r_min:
                real_min = r_min
            else:
                pass
            
            area_cnt += 1

        return area_mean, real_max, real_min, area_max
    
    # 대칭성 분석 값 반환 함수
    def mvSymmetry(self, a, b):
        print((1 - (abs(a - b) / (a + b))) * 100)
        return (1-(abs(a - b) / (a + b))) * 100

        # return (max(0, ((1-(abs(a - b) / (a + b))) * 100 - 80) / 20)) * 100
    
    # 백분율로 변환 함수
    def chngPercent(self, a, b, c):
        under_value = max([b, c])

        return (a / under_value) * 100
    
    # 분석 결과 값 반환 함수
    def resultCalc(self):

        if self.result_chk:
            # 부위별 영역
            # 왼쪽 및 오른쪽 구역 값 계산
            for area in self.f_areas:
                key = f'{area} left'
                values = self.valuePerArea(getattr(self, f'{area}'), left=True)
                self.result[key], self.result[f'{key} (max)'], self.result[f'{key} (min)'], self.result[f'{key} (refmax)'] = values

                key = f'{area} right'
                values = self.valuePerArea(getattr(self, f'{area}'), left=False)
                self.result[key], self.result[f'{key} (max)'], self.result[f'{key} (min)'], self.result[f'{key} (refmax)'] = values

            # 대칭성 계산
            for area in self.f_areas:
                self.result[f'Symmetry {area}'] = self.mvSymmetry(self.result[f'{area} left'], self.result[f'{area} right'])

            # 평균값 백분율로 변경
            for area in self.f_areas:
                for side in ['left', 'right']:
                    key = f'{area} {side}'
                    self.result[key] = self.chngPercent(self.result[key], self.result[f'{area} left (refmax)'], self.result[f'{area} right (refmax)'])

            # 4 area
            # 왼쪽 및 오른쪽 구역 값 계산
            for area in self.areas:
                key = f'{area} left'
                values = self.valuePerArea(getattr(self, f'{area}'), left=True)
                self.result[key], self.result[f'{key} (max)'], self.result[f'{key} (min)'], self.result[f'{key} (refmax)'] = values

                key = f'{area} right'
                values = self.valuePerArea(getattr(self, f'{area}'), left=False)
                self.result[key], self.result[f'{key} (max)'], self.result[f'{key} (min)'], self.result[f'{key} (refmax)'] = values

            # 대칭성 계산
            for area in self.areas:
                self.result[f'Symmetry {area}'] = self.mvSymmetry(self.result[f'{area} left'], self.result[f'{area} right'])

            # 평균값 백분율로 변경
            for area in self.areas:
                for side in ['left', 'right']:
                    key = f'{area} {side}'
                    self.result[key] = self.chngPercent(self.result[key], self.result[f'{area} left (refmax)'], self.result[f'{area} right (refmax)'])
            
            # 선택 영역
            # 왼쪽 및 오른쪽 구역 값 계산
            for area in self.selected_areas:
                key = f'{area} left'
                values = self.valuePerArea(getattr(self, f'{area}'), left=True)
                self.result[key], self.result[f'{key} (max)'], self.result[f'{key} (min)'], self.result[f'{key} (refmax)'] = values

                key = f'{area} right'
                values = self.valuePerArea(getattr(self, f'{area}'), left=False)
                self.result[key], self.result[f'{key} (max)'], self.result[f'{key} (min)'], self.result[f'{key} (refmax)'] = values

            # 대칭성 계산
            for area in self.selected_areas:
                self.result[f'Symmetry {area}'] = self.mvSymmetry(self.result[f'{area} left'], self.result[f'{area} right'])

            # 평균값 백분율로 변경
            for area in self.selected_areas:
                for side in ['left', 'right']:
                    key = f'{area} {side}'
                    self.result[key] = self.chngPercent(self.result[key], self.result[f'{area} left (refmax)'], self.result[f'{area} right (refmax)'])

            return self.result
            
        else:
            print('Failed to Analyze!!')
            return []

class VdAnalysis(QThread):
    finished_signal = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.vd_path = None

    def start_with(self, arg, marks):
        self.leftsum = 0
        self.vd_path = arg
        self.selected_marks = marks
        self.start()

    def run(self):

        # 백그라운드에서 수행할 작업을 여기에 구현
        # try:

        # 미디어파이프 설정
        max_num_faces = 1
        min_detection_confidence = 0.7
        min_tracking_confidence = 0.5

        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=max_num_faces,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            refine_landmarks=True,
        )

        # 랜드마크 분석 용 인스턴스 생성
        v_calc = LandmarkAnalysis()
        v_calc.selected_landmarks_set(self.selected_marks)

        # 프레임 카운트
        cnt = 0
        # 영상 가져오기
        cap = cv2.VideoCapture(self.vd_path)

        while True:
            # 영상 프레임 가져오기
            ret, src = cap.read()
            if not ret:
                break
            print(cnt)
            img = copy.deepcopy(src)

            # 테스트한 웹켐에서 영상이 좌우반전되어 나오기에 flip 적용
            img = cv2.flip(img, 1)

            # 랜드마크 추출
            results = face_mesh.process(img)

            if results.multi_face_landmarks is not None:
                for face_landmarks in results.multi_face_landmarks:
                    v_calc.calcLandmark(face_landmarks)
            cnt += 1
        
        # 분석 결과 반환
        result = v_calc.resultCalc()
        cap.release()
        
        self.finished_signal.emit(result)

        # except:
        #     print('vdAnalysis error')
        #     traceback.format_exc()


############# STATIC ######################
num_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219]
left_list = [109, 108, 107, 67, 69, 66, 103, 104, 105, 54, 68, 63, 21, 71, 70, 162, 139, 156, 127, 34, 143, 35, 124, 46, 53, 52, 65, 55, 226, 113, 225, 224, 223, 222, 221, 193, 130, 247, 30, 29, 27, 28, 56, 189, 190, 33, 246, 161, 160, 159, 158, 157, 173, 133, 7, 163, 144, 145, 153, 154, 155, 25, 110, 24, 23, 22, 26, 112, 243, 244, 245, 122, 31, 228, 229, 230, 231, 232, 233, 111, 117, 118, 119, 120, 121, 128, 234, 227, 116, 100, 47, 114, 188, 142, 126, 217, 174, 196, 209, 198, 236, 3, 129, 49, 131, 134, 51, 102, 48, 115, 220, 45, 64, 219, 218, 237, 44, 235, 166, 79, 239, 98, 240, 59, 75, 60, 20, 238, 241, 125, 242, 141, 99, 97, 93, 137, 123, 50, 101, 36, 203, 205, 206, 132, 177, 147, 187, 207, 58, 215, 213, 172, 138, 192, 216, 92, 165, 167, 212, 186, 57, 185, 40, 39, 37, 61, 76, 62, 184, 74, 73, 72, 183, 42, 41, 38, 78, 191, 80, 81, 82, 95, 88, 178, 87, 96, 89, 179, 86, 77, 90, 180, 85, 146, 91, 181, 84, 202, 43, 106, 182, 83, 204, 194, 201, 214, 210, 211, 32, 208, 135, 169, 170, 140, 171, 136, 150, 149, 176, 148]
right_list = [338, 337, 336, 297, 299, 296, 332, 333, 334, 284, 298, 293, 251, 301, 300, 389, 368, 383, 356, 264, 372, 265, 353, 276, 283, 282, 295, 285, 446, 342, 445, 444, 443, 442, 441, 417, 359, 467, 260, 259, 257, 258, 286, 413, 414, 263, 466, 388, 387, 386, 385, 384, 398, 362, 249, 390, 373, 374, 380, 381, 382, 255, 339, 254, 253, 252, 256, 341, 463, 464, 465, 351, 261, 448, 449, 450, 451, 452, 453, 340, 346, 347, 348, 349, 350, 357, 454, 447, 345, 329, 277, 343, 412, 371, 355, 437, 399, 419, 429, 420, 456, 248, 358, 279, 360, 363, 281, 331, 278, 344, 440, 275, 294, 439, 438, 457, 274, 455, 392, 309, 459, 327, 460, 289, 305, 290, 250, 458, 461, 354, 462, 370, 328, 326, 323, 366, 352, 280, 330, 266, 423, 425, 426, 361, 401, 376, 411, 427, 288, 435, 433, 397, 367, 416, 436, 322, 391, 393, 432, 410, 287, 409, 270, 269, 267, 291, 306, 292, 408, 304, 303, 302, 407, 272, 271, 268, 308, 415, 310, 311, 312, 324, 318, 402, 317, 325, 319, 403, 316, 307, 320, 404, 315, 375, 321, 405, 314, 422, 273, 335, 406, 313, 424, 418, 421, 434, 430, 431, 262, 428, 364, 394, 395, 369, 396, 365, 379, 378, 400, 377]

def imread(filename, flags=cv2.IMREAD_COLOR, dtype=np.uint8):
    try:
        n = np.fromfile(filename, dtype)
        img = cv2.imdecode(n, flags)
        return img
    except Exception as e:
        print(e)
        return None


def imwrite(filename, img, params=None):
    try:
        ext = os.path.splitext(filename)[1]
        result, n = cv2.imencode(ext, img, params)

        if result:
            with open(filename, mode='w+b') as f:
                n.tofile(f)
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False


# 정중면 공식 연산
def cal_plane_equation(Data): # 인자는 data 그대로 넣으면 됨

    std_normal_vector = np.array([(Data[473][0] - Data[468][0]), (Data[473][1] - Data[468][1]), (Data[473][2] - Data[468][2])]) # 양쪽 홍채를 가로지르는 법선 벡터
    unit_std_normal_vector = std_normal_vector / np.linalg.norm(std_normal_vector)

    mid_point = np.array([(Data[473][0] + Data[468][0])/2, (Data[473][1] + Data[468][1])/2, (Data[473][2] + Data[468][2])/2]) # 두 홍채 사이 중간 점

    a = unit_std_normal_vector[0]
    b = unit_std_normal_vector[1]
    c = unit_std_normal_vector[2]
    d = (mid_point[0]*a) + (mid_point[1]*b) + (mid_point[2]*c)

    return [a, b, c, d] # ax + by + cz = d

# 우측 포인트를 좌측으로 미러링
def mirror(point1, point2, plane_equation): # point2를 대칭하여 거리 계산
    [a, b, c, d] = plane_equation
    squaredsum = a*a+b*b+c*c
    px, py, pz = point2
    normlen = 1.0 / math.sqrt(squaredsum)
    nx = a * normlen # normal unit vector
    ny = b * normlen
    nz = c * normlen
    ox = a * (d) / squaredsum
    oy = b * (d) / squaredsum
    oz = c * (d) / squaredsum
    dott = nx * (px - ox) + ny * (py - oy) + nz * (pz - oz) #
    rx = px - nx * dott # 수선의 발 x
    ry = py - ny * dott # 수선의 발 y
    rz = pz - nz * dott # 수선의 발 z
    symx = 2 * rx - px #
    symy = 2 * ry - py
    symz = 2 * rz - pz
    sym_point = [symx, symy, symz]
    point_distance = abs(math.sqrt(math.pow(point1[0] - sym_point[0], 2) + math.pow(point1[1] - sym_point[1], 2) + math.pow(point1[2] - sym_point[2], 2)))

    return point_distance

# ??
def find_serrated_list_elements(index, serrated_list):
    for row in range(len(serrated_list)):
        for col in range(len(serrated_list[row])):
            if index == serrated_list[row][col]:
                return row, len(serrated_list[row])
    return None

# 대칭성 검사
def compare_symm(unit_std_noraml_vector, point_L, point_R):
    compare_normal_vector = point_L - point_R
    unit_compare_normal_vector = compare_normal_vector / np.linalg.norm(compare_normal_vector)
    result = np.abs(np.inner(unit_std_noraml_vector, unit_compare_normal_vector))

    return result

# 라디안 값을 일반 각도로 변환
def radian2degree(radian):
    pi = np.pi
    return radian*(180/pi)

# 거리 대칭성 연산
def cal_single_dist_symm(data, select_pt_list):

    global num_list, left_list, right_list

    plane = cal_plane_equation(data) #return [a, b, c, d] # ax + by + cz = d
    result_list = []

    # for match_idx, L_idx, R_idx in symm_match_keypoinst_list:
    for idx in range(len(num_list)):

        # symm_muscle_keypoint 의 index 찾기
        # muscle_index, _ = find_serrated_list_elements(match_idx, symm_muscle_keypoint) # 근육 단위 index와 해당 근육의 keypoint 개수
        if idx in select_pt_list:
            
            # source frame 에 대해 대칭성 계산
            L_keypoint = data[left_list[idx]]
            R_keypoint = data[right_list[idx]]
            source_symm_dist = mirror(L_keypoint, R_keypoint, plane)
            '''
            for iter in range(len(data)): # 반전된 키포인트 구해서 리스트에 넣기
                source_rev_point = test_mirror(data[R_idx], plane)
                rev_data.append(source_rev_point)
            '''
            
            # muscle_summation_dist[muscle_index] += source_symm_dist
            result_list.append(source_symm_dist)

        else:
            pass

    return result_list

def trans_2D(keypoint): # 3D to 2D (z axie is zero)
    for i in range(len(keypoint)):
        keypoint[i][2] = 0
    return keypoint

# 방향 대칭성 연산
def cal_single_angle_symm(data, select_pt_list):
    
    global num_list, left_list, right_list

    # 가운테 키포인트에 대한 노말 유닛 벡터 계산 [1, 2, 3]
    std_normal_vector = np.array([(data[473][0] - data[468][0]), (data[473][1] - data[468][1]), (data[473][2] - data[468][2])]) # 양쪽 홍채를 가로지르는 법선 벡터
    unit_std_normal_vector = std_normal_vector / np.linalg.norm(std_normal_vector)

    result_list = []

    for idx in range(len(num_list)):
        if idx in select_pt_list:

            # 대칭성 계산
            # L_keypoint = data[L_idx]
            # R_keypoint = data[R_idx]
            L_keypoint = data[left_list[idx]]
            R_keypoint = data[right_list[idx]]
            symm_val = compare_symm(unit_std_normal_vector, L_keypoint, R_keypoint)

            result_list.append(symm_val)

    for i in range(len(result_list)):
        result_list[i] = np.arccos(result_list[i]) # return value radian
        result_list[i] = radian2degree(result_list[i])

    return result_list

# 거리 대칭성과 방향 대칭성 반환
def single_symmetry(data, select_pt_list):
  
    dist_symm_list = cal_single_dist_symm(data, select_pt_list)
    angle_symm_list = cal_single_angle_symm(data, select_pt_list)

    # print(f"dist_symm_list : {len(dist_symm_list)} | {dist_symm_list}")
    # print(f"angle_symm_list : {len(angle_symm_list)} | {angle_symm_list}")

    dist_symm = sum(dist_symm_list) / len(dist_symm_list)
    angle_symm = sum(angle_symm_list) / len(angle_symm_list)

    # 백분율로 변환
    dist_symm = (1 - (dist_symm / max(dist_symm_list))) * 100
    angle_symm = (1 - (angle_symm / 180.0)) * 100

    return dist_symm, angle_symm


def draw_landmarks_static(image, landmarks, p_color, p_size, iris_color, iris_size, line_color, line_size):
    image_width, image_height = image.shape[1], image.shape[0]

    # landmark point list
    lp = []

    cnt = 0
    # landmark 연산
    for index, landmark in enumerate(landmarks.landmark):
        if landmark.visibility < 0 or landmark.presence < 0:
            continue

        landmark_x = landmark.x
        landmark_y = landmark.y
        landmark_z = landmark.z
        
        # 3d Coordinates
        lp.append([landmark_x, landmark_y, landmark_z])

        # print("landmark : ", landmark)
        
        # landmark_point
        result_x = min(int(landmark_x * image_width), image_width - 1)
        result_y = min(int(landmark_y * image_height), image_height - 1)

        cv2.circle(image, (result_x, result_y), 1, p_color, p_size)

        cnt += 1
    
    # 좌측 홍채 크기 연산
    dx = (lp[471][0] - lp[469][0]) * image_width
    dy = (lp[471][1] - lp[469][1]) * image_height

    Lnorm = (np.sqrt(dx ** 2 + dy ** 2) / 2)

    # landmark_point
    result_x_l = min(int(lp[468][0] * image_width), image_width - 1)
    result_y_l = min(int(lp[468][1] * image_height), image_height - 1)

    # 우측 홍채 크기 연산
    dx = (lp[476][0] - lp[474][0]) * image_width
    dy = (lp[476][1] - lp[474][1]) * image_height

    Rnorm = (np.sqrt(dx ** 2 + dy ** 2) / 2)

    # landmark_point
    result_x_r = min(int(lp[473][0] * image_width), image_width - 1)
    result_y_r = min(int(lp[473][1] * image_height), image_height - 1)

    # 주어진 선분과 홍채 반지름
    line_start = (result_x_l, result_y_l)
    line_end = (result_x_r, result_y_r)
    iris_norm = int(sum([Lnorm, Rnorm]) / 2)

    cv2.circle(image, line_start, iris_norm, iris_color, iris_size)
    cv2.circle(image, line_end, iris_norm, iris_color, iris_size)

    # cv2.line(image, line_start, line_end, color_blue, 5)

    # 1. 주어진 선분의 중점 찾기
    midpoint_x = (line_start[0] + line_end[0]) // 2
    midpoint_y = (line_start[1] + line_end[1]) // 2

    # 2. 선분의 기울기 계산
    slope = (line_end[1] - line_start[1]) / (line_end[0] - line_start[0] + 1e-6)

    # 3. 수직 이등분선의 기울기 계산
    perpendicular_slope = -1 / (slope + 1e-6)

    # 5. 선분의 길이를 결정하고 양 끝점 찾기
    segment_length = int(image_height * 0.8)  # 수직 이등분선의 길이 (원하는 길이로 변경 가능)

    # 수직 이등분선의 끝점 좌표를 계산
    delta_x = np.sqrt(segment_length**2 / (1 + perpendicular_slope**2))
    delta_y = np.abs(perpendicular_slope * delta_x)

    perp_line_start = (int(midpoint_x - delta_x), int(midpoint_y - delta_y))
    perp_line_end = (int(midpoint_x + delta_x), int(midpoint_y + delta_y))

    # # 6. 수직 이등분선을 이미지에 그리기
    # cv2.line(image, perp_line_start, perp_line_end, color_blue, 5)

    # OpenCV 이미지를 Pillow(PIL) 이미지로 변환
    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # Pillow(PIL) 이미지에서 그리기 작업을 수행할 수 있는 Draw 객체 생성
    draw = ImageDraw.Draw(pil_image)

    # 정수 좌표로 변환
    line_start_int = (int(line_start[0]), int(line_start[1]))
    line_end_int = (int(line_end[0]), int(line_end[1]))
    perp_line_start_int = (int(perp_line_start[0]), int(perp_line_start[1]))
    perp_line_end_int = (int(perp_line_end[0]), int(perp_line_end[1]))

    # 선분 그리기 (안티 앨리어싱 적용)
    draw.line([line_start, line_end], fill=line_color, width=line_size)

    # 수직 이등분선 그리기 (안티 앨리어싱 적용)
    draw.line([perp_line_start, perp_line_end], fill=line_color, width=line_size)

    # Pillow(PIL) 이미지를 OpenCV 이미지로 다시 변환
    image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    return image

def get_landmarks(landmarks):

    # landmark point list
    lp = []

    cnt = 0
    # landmark 연산
    for index, landmark in enumerate(landmarks.landmark):
        if landmark.visibility < 0 or landmark.presence < 0:
            continue

        landmark_x = landmark.x
        landmark_y = landmark.y
        landmark_z = landmark.z
        
        # 3d Coordinates
        lp.append([landmark_x, landmark_y, landmark_z])

    return landmarks, lp

class StaticAnalysis():

    def __init__(self):
        # MediaPipe 검출기 생성 매개변수
        max_num_faces = 1
        min_detection_confidence = 0.7
        min_tracking_confidence = 0.5
        model_complexity = 1

        # MediaPipe face mesh 검출기 생성
        mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=max_num_faces,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            refine_landmarks=True,
        )

        self.p_size = 1

    def imgAnalysis(self, img_path):
        src = imread(img_path)
        height, width, channels = src.shape
        
        img = copy.deepcopy(src)

        # 환자의 좌우가 반전되어 있기 때문에 flip 적용
        img = cv2.flip(img, 1)

        # 환자시점 랜드마크 추출
        results = self.face_mesh.process(img)

        if results.multi_face_landmarks is not None:
            for face_landmarks in results.multi_face_landmarks:
                lp_ori_flip, lp_re_flip = get_landmarks(face_landmarks)

        # 송출 영상 다시 플립
        frame = cv2.flip(img, 1)

        # 랜드마크 추출
        results = self.face_mesh.process(frame)

        if results.multi_face_landmarks is not None:
            for face_landmarks in results.multi_face_landmarks:
                lp_ori, lp_re = get_landmarks(face_landmarks)
        
        return frame, lp_ori, lp_re_flip

