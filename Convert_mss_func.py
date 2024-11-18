import os
import numpy as np
import pandas as pd
import cv2
import math
import mediapipe as mp
import copy
import time
import csv
import random

# from scipy.linalg import svd

def CONVERT_MSS(video):
    retval = operation_File(video)
    write_csv(retval)
    windows_user_name_DBPD = os.path.expanduser('~') + '/DBPD/'
    df = pd.read_csv(windows_user_name_DBPD + 'DBPD_MSS.csv')
    data_array = df.to_numpy()
    normalized_data = (data_array - data_array.min()) / (data_array.max() - data_array.min())
    normalized_data *= 255
    normalized_data = normalized_data.astype(np.uint8)
    print(normalized_data.shape)
    img = cv2.resize(normalized_data,(478,478))  # H, W -> Fixed
    # filename = f'BS_HBG_dataset/1/2.jpg'
    # cv2.imwrite(filename, img)

    return img


def load_Data(f_path):
    # # 시작 시간 측정
    # start0 = time.perf_counter_ns()

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

    # # 초기 설정 시간 측정
    # duration = (time.perf_counter_ns() - start0)
    # # print(f"init time : {duration // 1000000}ms.")
    # print("init time : %2fs." % (duration / 1000000000))

    # # 영상 처리 시작 시간 측정
    # start = time.perf_counter_ns()

    # load video
    cap = cv2.VideoCapture(f_path)

    cap_frames = []
    cnt = 0

    while True:

        ret, src = cap.read()
        # src = cv.resize(src, dsize=(960, 540), interpolation=cv.INTER_AREA)
        if not ret:
            break

        view_img = src.copy()
        view_img = cv2.flip(view_img, 1)
        results = face_mesh.process(view_img)

        if results.multi_face_landmarks is not None:
            for face_landmarks in results.multi_face_landmarks:
                temp_landmarks = []
                for id, landmark in enumerate(face_landmarks.landmark):
                    temp_landmarks.append([landmark.x, landmark.y, landmark.z])

                cap_frames.append(temp_landmarks)

            cnt += 1
        else:
            prev_landmarks = None

    cap.release()
    cv2.destroyAllWindows()

    return cap_frames


def get_MSS_Data(frames_landmarks):
    # print(f'len(frames_landmarks) : {len(frames_landmarks)}')

    frame_step = 5
    pt_MV = []

    # 프레임간 이동량 연산
    for idx in range(len(frames_landmarks)):

        temp_MV = []

        if (idx != 0) and (idx % frame_step == 0):

            # 랜드마크 움직임 연산
            pre_x = [landmark[0] for landmark in frames_landmarks[idx - frame_step]]
            pre_y = [landmark[1] for landmark in frames_landmarks[idx - frame_step]]  # y 좌표 반전
            pre_z = [landmark[2] for landmark in frames_landmarks[idx - frame_step]]  # z 좌표 반전

            next_x = [landmark[0] for landmark in frames_landmarks[idx]]
            next_y = [landmark[1] for landmark in frames_landmarks[idx]]  # y 좌표 반전
            next_z = [landmark[2] for landmark in frames_landmarks[idx]]  # z 좌표 반전

            vx = [nx - px for nx, px in zip(next_x, pre_x)]
            vy = [ny - py for ny, py in zip(next_y, pre_y)]
            vz = [nz - pz for nz, pz in zip(next_z, pre_z)]

            # vx, vy, vz를 통한 랜드마크 누적이동량 연산
            for ld_id in range(len(vx)):
                displacement = (vx[ld_id] ** 2 + vy[ld_id] ** 2) ** 1.2

                # sum value of selected point
                temp_MV.append(displacement)

            pt_MV.append(temp_MV)

        else:
            pass

    return pt_MV

def operation_File(video):

    root = video
    pt_MV = []

    if os.path.exists(root):

        cap_frames = load_Data(root)

        pt_MV = get_MSS_Data(cap_frames)

        print(f'pt_MV : {len(pt_MV)} | {root}')

        # hb_idx = load_dict['Name'].index(p_id)

        # record_dict[type_id].append()

    else:
        print(root)
        pass

    print(f'Patient cnt complete')

    return pt_MV


def write_csv(retval):
    # HD_MSS_path = video.split('/')
    # print(HD_MSS_path[-1])
    # csv_path = open(WindowUsername + "/Desktop/HBD_dataset/" + f"{HD_MSS_path[-1]}.csv", 'w', newline='')
    windows_user_name_DBPD = os.path.expanduser('~') + '/DBPD/'
    if not os.path.exists(windows_user_name_DBPD):
        os.mkdir(windows_user_name_DBPD)
    csv_path = open(windows_user_name_DBPD + 'DBPD_MSS.csv', 'w', newline='')
    writer = csv.writer(csv_path)
    writer.writerow([x for x in range(478)])

    for idx, data in enumerate(retval):
        writer.writerow('{:.15f}'.format(x) if isinstance(x, float) else x for x in data)

    csv_path.close()