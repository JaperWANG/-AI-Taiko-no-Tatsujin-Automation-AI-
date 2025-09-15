import cv2
import numpy as np

# 一個什麼都不做的函式，給 createTrackbar 使用
def nothing(x):
    pass

# 讀取您事先準備好的遊戲截圖
# !!! 請確保圖片檔名和路徑正確 !!!
try:
    image = cv2.imread('allin.png')
    image = cv2.resize(image, (600, 400)) # 縮小圖片以方便顯示
except:
    print("錯誤：找不到 'game_screenshot.png' 檔案。")
    print("請先截圖並存檔，確保與此程式在同一個資料夾中。")
    exit()


# 建立一個視窗來放置調整工具
cv2.namedWindow('Trackbars')

# 建立 HSV 的六個調整滑桿
cv2.createTrackbar('H_min', 'Trackbars', 0, 179, nothing)
cv2.createTrackbar('H_max', 'Trackbars', 179, 179, nothing)
cv2.createTrackbar('S_min', 'Trackbars', 0, 255, nothing)
cv2.createTrackbar('S_max', 'Trackbars', 255, 255, nothing)
cv2.createTrackbar('V_min', 'Trackbars', 0, 255, nothing)
cv2.createTrackbar('V_max', 'Trackbars', 255, 255, nothing)

while True:
    # 複製一份原始影像，避免被修改
    img_copy = image.copy()
    
    # 轉換到 HSV
    hsv = cv2.cvtColor(img_copy, cv2.COLOR_BGR2HSV)
    
    # 從滑桿讀取目前的 HSV 範圍
    h_min = cv2.getTrackbarPos('H_min', 'Trackbars')
    h_max = cv2.getTrackbarPos('H_max', 'Trackbars')
    s_min = cv2.getTrackbarPos('S_min', 'Trackbars')
    s_max = cv2.getTrackbarPos('S_max', 'Trackbars')
    v_min = cv2.getTrackbarPos('V_min', 'Trackbars')
    v_max = cv2.getTrackbarPos('V_max', 'Trackbars')
    
    # 建立 NumPy 陣列
    lower_bound = np.array([h_min, s_min, v_min])
    upper_bound = np.array([h_max, s_max, v_max])
    
    # 根據範圍建立遮罩
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    
    # 將遮罩應用到原始影像上
    result = cv2.bitwise_and(img_copy, img_copy, mask=mask)

    # 顯示原始影像、遮罩和結果
    cv2.imshow('Original Image', image)
    cv2.imshow('Mask', mask)
    cv2.imshow('Result', result)
    
    # 按下 'q' 鍵來中斷程式
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 關閉所有視窗
cv2.destroyAllWindows()

print("\n調整完成！您剛剛看到的最後一組 H, S, V 值就是您要的範圍。")
print("例如：")
print("LOWER_RED = np.array([H_min, S_min, V_min])")
print("UPPER_RED = np.array([H_max, S_max, V_max])")