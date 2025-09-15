# 太鼓達人 自動演奏 AI (Taiko no Tatsujin Automation AI)

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-blue?logo=opencv)
![License](https://img.shields.io/badge/License-MIT-green)

本專案記錄了從零開始，打造一個能夠即時遊玩《太鼓達人》AI Bot 的完整開發歷程。專案深入探索了多種電腦視覺技術，從基礎的顏色篩選，到為了應對複雜譜面而實作的物件追蹤 (Object Tracking) 演算法，並在過程中對 AI 的性能進行了多輪的迭代與優化。

**This project documents the development journey of creating a real-time AI bot for the rhythm game *Taiko no Tatsujin*. It explores various computer vision techniques, from basic color filtering to implementing an advanced **Object Tracking** algorithm, in order to tackle the challenges of complex, high-speed note charts.**

---

## 效果展示 (Demo)

*[![太鼓達人 AI 運作展示](https://img.youtube.com/vi/th5lPIBCkNQ/0.jpg)](https://www.youtube.com/watch?v=th5lPIBCkNQ)

## 核心功能 (Features)

* **即時畫面分析**: 透過 `mss` 進行高效率的螢幕擷取，延遲極低。
* **智慧物件追蹤 (`NoteTracker`)**:
    * 採用基於質心追蹤的演算法，為每一個出現的音符分配獨一無二的 ID。
    * 透過「已打擊 ID 黑名單」機制，確保每個音符**一生只會被打擊一次**，從根本上解決了高速連打漏拍和鬼影重複打擊問題。
    * 透過可調校的 `maxDisappeared` 參數，賦予追蹤器「耐心」，使其在音符因動態模糊而短暫消失時，依然能穩定鎖定目標。
* **進階音符辨識**:
    * 使用 HSV 顏色空間，穩定篩選出「咚」(紅) 與「咔」(藍) 音符。
    * 透過輪廓面積 (`contourArea`)，精準區分**一般音符**與**大音符**，並執行對應的單鍵/雙鍵指令。
* **性能優化**: 透過影像降噪 (`morphologyEx`) 和最佳化的擷取範圍，確保 AI 的反應速度。
* **視覺化除錯模式**: 內建 `DEBUG_MODE` 開關，啟用後可即時觀看 AI 的視野、判定區、以及**為每個音符標記的追蹤 ID**，讓複雜的追蹤過程一目了然。

## 已知限制與未來展望 (Known Limitations & Future Work)

**性能瓶頸 (Performance Bottleneck):**

由於 Python + OpenCV (CPU) 的技術組合在即時高頻應用中的固有延遲（畫面擷取、影像處理、指令傳輸等延 new york city, usa遲的累積），目前的 AI 在處理中、低難度的歌曲時表現穩定，但在應對「魔王」級等極高難度歌曲的密集高速譜面時，可能會出現延遲或漏拍。

**未來展望 (Future Work):**

要突破目前的性能極限，未來的改進方向將需要進行架構級的升級，例如：
* **更換底層語言**: 使用 C++ 等編譯式語言重寫核心的影像處理與判斷邏輯。
* **更換擷取方式**: 研究直接掛鉤 (Hook) 遊戲渲染管線（如 DirectX）等更底層的技術，以獲得近乎零延遲的畫面數據。

本專案清晰地探測並定義了當前技術棧的性能邊界，為後續的底層開發提供了寶貴的實踐依據。

## 技術棧 (Tech Stack)

* **Python 3**
* **OpenCV-Python**: 核心電腦視覺函式庫，用於影像處理與輪廓分析。
* **SciPy**: 用於高效計算物件之間的距離，是物件追蹤演算法的核心。
* **mss**: 用於高速、低延遲的螢幕擷取。
* **pydirectinput**: 專為遊戲設計的鍵盤模擬函式庫，確保指令相容性。
* **NumPy**: 為所有影像和科學計算提供高效的底層陣列運算支持。

## 安裝與設定 (Setup & Installation)

**1. 事前準備 (Prerequisites)**
* 已安裝 Python 3.9 或更高版本 (建議透過 Anaconda 管理)。
* 一台能夠順暢運行《太鼓達人》的電腦。

**2. 下載專案**
```bash
git clone [https://github.com/](https://github.com/)[您的GitHub使用者名稱]/[您的專案儲存庫名稱].git
cd [您的專案儲存庫名稱]
```

**3. 建立虛擬環境與安裝依賴套件**
* **使用 Conda (推薦):**
    ```bash
    conda create -n taiko_ai python=3.9
    conda activate taiko_ai
    pip install -r requirements.txt
    ```
* **手動建立 `requirements.txt` 檔案**，並將以下內容貼入:
    ```
    opencv-python
    mss
    pydirectinput
    numpy
    scipy
    ```

## 使用教學 (How to Use)

1.  **校準參數**: 打開 `main.py`，所有可調整的參數都集中在 `--- 1. 設定區 ---`。
    * `MONITOR`: **(必須)** 執行附帶的 `get_coords.py` (或手動測量)，取得並更新遊戲音符軌道的螢幕座標。
    * `LOWER_RED`, `UPPER_RED`, `LOWER_BLUE`, `UPPER_BLUE`: **(必須)** 使用 `hsv_finder.py` 校準「咚」和「咔」的 HSV 顏色範圍。
    * `JUDGEMENT_AREA`: **(必須)** 微調判定區的 `_START` 和 `_END` X座標，以校準 AI 的打點時機。
    * `BIG_NOTE_AREA_THRESHOLD`: **(建議)** 開啟 `DEBUG_MODE` 並觀察一個大音符的 `area` 數值，設定一個比它略小的門檻值。
2.  **啟動 AI**:
    * 將 `DEBUG_MODE` 設為 `False` 以獲得最佳性能。
    * **務必以系統管理員身分**執行 `main.py`。
    * 在倒數計時結束前，用滑鼠點擊遊戲視窗使其成為焦點。
    * 若要停止 AI，請點擊終端機視窗，然後按下 `Ctrl + C`。


## 授權 (License)

本專案採用 [MIT License](https://choosealicense.com/licenses/mit/) 授權。
