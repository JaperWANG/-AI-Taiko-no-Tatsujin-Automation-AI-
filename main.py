# ==============================================================================
# 太鼓達人自動演奏 AI (Taiko no Tatsujin Automation AI)
# ==============================================================================

import cv2
import numpy as np
import mss
import time
import pydirectinput
from collections import OrderedDict
from scipy.spatial import distance as dist
from threading import Thread

# --- 物件追蹤器 Class ---
class NoteTracker:
    def __init__(self, maxDisappeared=15): 
        self.nextObjectID = 0
        self.objects = OrderedDict()
        self.disappeared = OrderedDict()
        self.maxDisappeared = maxDisappeared
    def register(self, centroid):
        self.objects[self.nextObjectID] = centroid
        self.disappeared[self.nextObjectID] = 0
        self.nextObjectID += 1
    def deregister(self, objectID):
        del self.objects[objectID]
        del self.disappeared[objectID]
    def update(self, centroids):
        if len(centroids) == 0:
            for objectID in list(self.disappeared.keys()):
                self.disappeared[objectID] += 1
                if self.disappeared[objectID] > self.maxDisappeared:
                    self.deregister(objectID)
            return self.objects
        if len(self.objects) == 0:
            for i in range(len(centroids)):
                self.register(centroids[i])
        else:
            objectIDs = list(self.objects.keys())
            objectCentroids = list(self.objects.values())
            D = dist.cdist(np.array(objectCentroids), centroids)
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]
            usedRows, usedCols = set(), set()
            for (row, col) in zip(rows, cols):
                if row in usedRows or col in usedCols: continue
                objectID = objectIDs[row]
                self.objects[objectID] = centroids[col]
                self.disappeared[objectID] = 0
                usedRows.add(row)
                usedCols.add(col)
            unusedRows = set(range(0, D.shape[0])).difference(usedRows)
            unusedCols = set(range(0, D.shape[1])).difference(usedCols)
            if D.shape[0] >= D.shape[1]:
                for row in unusedRows:
                    objectID = objectIDs[row]
                    self.disappeared[objectID] += 1
                    if self.disappeared[objectID] > self.maxDisappeared:
                        self.deregister(objectID)
            else:
                for col in unusedCols:
                    self.register(centroids[col])
        return self.objects

# --- 1. 設定區 ---
DEBUG_MODE = 0
DON_KEY_L, DON_KEY_R = 'z', 'x'
KA_KEY_L, KA_KEY_R = 'n', 'm'
MONITOR = {'top': 307, 'left': 516, 'width': 1308, 'height': 209}
JUDGEMENT_AREA_X_START, JUDGEMENT_AREA_X_END = 75, 125
LOWER_RED = np.array([0, 165, 230])
UPPER_RED = np.array([21, 255, 255])
LOWER_BLUE = np.array([87, 102, 135])
UPPER_BLUE = np.array([91, 121, 196])
MIN_NOTE_AREA = 50
BIG_NOTE_AREA_THRESHOLD = 4000
MORPH_KERNEL = np.ones((3, 3), np.uint8)

red_tracker = NoteTracker(maxDisappeared=15)
blue_tracker = NoteTracker(maxDisappeared=15)
hit_notes_ids = set()
sct = mss.mss()

if DEBUG_MODE:
    cv2.namedWindow('Game Capture')
    cv2.moveWindow('Game Capture', 50, 50)

# --- 2. 主程式開始 ---
print("程式 已啟動！")
time.sleep(3)

try:
    while True:
        img_bgr = np.array(sct.grab(MONITOR))
        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

        # --- 偵測所有紅色和藍色音符的中心點 ---
        red_centroids, blue_centroids = [], []
        big_red_ids, big_blue_ids = [], []

        # 步驟 1: 建立遮罩
        red_mask = cv2.inRange(img_hsv, LOWER_RED, UPPER_RED)
        # 步驟 2: 降噪
        red_mask_clean = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, MORPH_KERNEL)
        # 步驟 3: 找輪廓
        red_contours, _ = cv2.findContours(red_mask_clean, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in red_contours:
            area = cv2.contourArea(cnt)
            if area > MIN_NOTE_AREA:
                M = cv2.moments(cnt)
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                red_centroids.append((cx, cy))
                if area > BIG_NOTE_AREA_THRESHOLD:
                    big_red_ids.append((cx, cy))
        
        
        blue_mask = cv2.inRange(img_hsv, LOWER_BLUE, UPPER_BLUE)
        blue_mask_clean = cv2.morphologyEx(blue_mask, cv2.MORPH_OPEN, MORPH_KERNEL)
        blue_contours, _ = cv2.findContours(blue_mask_clean, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in blue_contours:
            area = cv2.contourArea(cnt)
            if area > MIN_NOTE_AREA:
                M = cv2.moments(cnt)
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                blue_centroids.append((cx, cy))
                if area > BIG_NOTE_AREA_THRESHOLD:
                    big_blue_ids.append((cx, cy))
        
        red_objects = red_tracker.update(np.array(red_centroids))
        blue_objects = blue_tracker.update(np.array(blue_centroids))
        
        for (objectID, centroid) in red_objects.items():
            if JUDGEMENT_AREA_X_START < centroid[0] < JUDGEMENT_AREA_X_END and objectID not in hit_notes_ids:
                if tuple(centroid) in big_red_ids:
                    pydirectinput.keyDown(DON_KEY_L)
                    pydirectinput.keyDown(DON_KEY_R)
                    time.sleep(0.01)
                    pydirectinput.keyUp(DON_KEY_L)
                    pydirectinput.keyUp(DON_KEY_R)
                else:
                    pydirectinput.press(DON_KEY_L)
                hit_notes_ids.add(objectID)

        for (objectID, centroid) in blue_objects.items():
            if JUDGEMENT_AREA_X_START < centroid[0] < JUDGEMENT_AREA_X_END and objectID not in hit_notes_ids:
                if tuple(centroid) in big_blue_ids:
                    pydirectinput.keyDown(KA_KEY_L)
                    pydirectinput.keyDown(KA_KEY_R)
                    time.sleep(0.01)
                    pydirectinput.keyUp(KA_KEY_L)
                    pydirectinput.keyUp(KA_KEY_R)
                else:
                    pydirectinput.press(KA_KEY_L)
                hit_notes_ids.add(objectID)

        if DEBUG_MODE:
            # (除錯模式的視覺化程式碼)
            for (objectID, centroid) in red_objects.items():
                text = f"ID {objectID}"
                cv2.putText(img_bgr, text, (centroid[0] - 10, centroid[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                cv2.circle(img_bgr, (centroid[0], centroid[1]), 4, (0, 0, 255), -1)
            cv2.line(img_bgr, (int(JUDGEMENT_AREA_X_START), 0), (int(JUDGEMENT_AREA_X_START), MONITOR['height']), (0, 255, 0), 2)
            cv2.line(img_bgr, (int(JUDGEMENT_AREA_X_END), 0), (int(JUDGEMENT_AREA_X_END), MONITOR['height']), (0, 255, 0), 2)
            cv2.imshow('Game Capture', img_bgr)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
except KeyboardInterrupt:
    print("\n偵測到 Ctrl+C，程式 已停止。")
finally:
    if DEBUG_MODE:
        cv2.destroyAllWindows()