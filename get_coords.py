from pynput import mouse
import time

# 使用一個 list 來儲存點擊的座標
coords = []

def on_click(x, y, button, pressed):
    """
    滑鼠點擊事件的處理函式
    """
    # 我們只在滑鼠 "按下" 時記錄座標
    if pressed:
        # 將座標加入清單中
        coords.append((int(x), int(y)))
        
        # 根據已收集的座標數量，給予不同的提示
        if len(coords) == 1:
            print(f"已記錄【左上角】座標: {coords[0]}")
            print(">>> 現在請點擊您想擷取區域的【右下角】...")
        
        elif len(coords) == 2:
            print(f"已記錄【右下角】座標: {coords[1]}")
            # 當收集到兩個座標後，返回 False 來停止監聽
            return False

# --- 主程式開始 ---
print("這是一個座標輔助工具。")
print(">>> 請在 3 秒後，點擊您想擷取區域的【左上角】...")
time.sleep(3)

# 啟動監聽器，它會一直運行直到 on_click 函式返回 False
with mouse.Listener(on_click=on_click) as listener:
    listener.join()

# 監聽器停止後，代表我們已成功收集到兩個座標
print("\n座標收集完成！")

# 計算並印出最終結果
top_left = coords[0]
bottom_right = coords[1]

monitor_config = {
    "top": top_left[1],
    "left": top_left[0],
    "width": bottom_right[0] - top_left[0],
    "height": bottom_right[1] - top_left[1]
}

print("\n請將下方的字典複製到您的主程式中：")
print(f"MONITOR = {monitor_config}")