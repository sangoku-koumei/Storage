import cv2
import numpy as np
import pyautogui
import win32gui
import win32api
import win32con
import time
import datetime
import subprocess
import os
import uiautomation as auto
from PIL import ImageGrab

# --- 設定 ---
# 監視間隔
CHECK_INTERVAL_SECONDS = 0.8

# しきい値（0.8 = 80%の一致でボタンとみなす）
CONFIDENCE_THRESHOLD = 0.8

# Git保存間隔
GIT_SAVE_INTERVAL = 900

# 状態監視タイムアウト
STATE_TRANSITION_TIMEOUT = 5.0
# -----------------

def stealth_click_at_point(abs_x, abs_y):
    """指定した絶対座標に対して、マウスを動かさずにクリック信号を送信する"""
    try:
        hwnd = win32gui.WindowFromPoint((abs_x, abs_y))
        if hwnd:
            rect = win32gui.GetWindowRect(hwnd)
            rel_x = abs_x - rect[0]
            rel_y = abs_y - rect[1]
            
            lparam = win32api.MAKELONG(rel_x, rel_y)
            win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
            time.sleep(0.01)
            win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lparam)
            return True
    except Exception as e:
        print(f"Stealth Click Error: {e}")
    return False

def find_button_hybrid():
    """画像（最速）と UI Automation（深層）を組み合わせたハイブリッド探索"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    # --- 1. 視覚スキャン (Vision) ---
    target_images = [f for f in os.listdir(base_path) if f.lower().endswith(".png")]
    if target_images:
        try:
            screenshot = np.array(ImageGrab.grab(all_screens=True))
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
            for img_name in target_images:
                img_path = os.path.join(base_path, img_name)
                try:
                    img_array = np.fromfile(img_path, np.uint8)
                    template = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                except Exception: continue
                if template is None: continue
                th, tw = template.shape[:2]
                result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)
                if max_val >= CONFIDENCE_THRESHOLD:
                    cx, cy = max_loc[0] + tw // 2, max_loc[1] + th // 2
                    return {"pos": (cx, cy), "type": "vision", "name": img_name}
        except Exception: pass

    # --- 2. 深層スキャン (UI Automation) ---
    try:
        root = auto.GetRootControl()
        target_vsc = [w for w in root.GetChildren() if "Antigravity" in w.Name or "Visual Studio Code" in w.Name]
        for vsc in target_vsc:
            vsc_rect = vsc.BoundingRectangle
            for ctrl, depth in auto.WalkControl(vsc, maxDepth=50):
                name = ctrl.Name.strip()
                if ctrl.ControlTypeName == "ButtonControl" and any(kw in name for kw in ["Accept", "Yes (Done)", "Allow", "Done", "Start Session", "OK", "Confirm", "Execute"]):
                    rect = ctrl.BoundingRectangle
                    is_offscreen = (rect.bottom < vsc_rect.top or rect.top > vsc_rect.bottom)
                    if is_offscreen or rect.width <= 0:
                        try:
                            ctrl.SetFocus()
                            if hasattr(ctrl, "ScrollIntoView"):
                                ctrl.ScrollIntoView()
                            win32api.SendMessage(vsc.NativeWindowHandle, win32con.WM_VSCROLL, win32con.SB_PAGEDOWN, 0)
                            time.sleep(0.2)
                            rect = ctrl.BoundingRectangle
                        except: pass
                    
                    if rect.width > 0 and rect.height > 0:
                        cx, cy = (rect.left + rect.right) // 2, (rect.top + rect.bottom) // 2
                        return {"pos": (cx, cy), "type": "deep", "name": name, "ctrl": ctrl}
    except Exception: pass
    
    return None

def main():
    print("==============================================")
    print("   Antigravity Hybrid Stealth Engine v5.6")
    print("==============================================")
    print("Mode: Multi-Vision + Deep Scan (Dynamic State)")
    print("Status: Force-Scroll & State Monitoring Active.")
    print("----------------------------------------------")
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    last_git_save = time.time()
    
    try:
        while True:
            res = find_button_hybrid()
            if res:
                pos = res["pos"]
                name = res["name"]
                
                if stealth_click_at_point(pos[0], pos[1]):
                    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] TRIGGER LOCK: '{name}' ({res['type']})")
                    
                    # --- Dynamic State Monitoring ---
                    # ボタンが消えるか、無効化されるまで待機（二重クリック防止）
                    start_wait = time.time()
                    while time.time() - start_wait < STATE_TRANSITION_TIMEOUT:
                        time.sleep(0.5)
                        check = find_button_hybrid()
                        if not check or check["name"] != name:
                            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] STATE TRANSITION CONFIRMED.")
                            break
                    
                    time.sleep(1.0)
            
            if time.time() - last_git_save > GIT_SAVE_INTERVAL:
                try:
                    subprocess.run(["git", "add", "."], check=False, shell=True, cwd=base_path)
                    subprocess.run(["git", "commit", "-m", f"Auto save: {datetime.datetime.now()}"], check=False, shell=True, cwd=base_path)
                    last_git_save = time.time()
                    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Git Auto Save Completed.")
                except: pass
                
            time.sleep(CHECK_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nEngine offline.")

if __name__ == "__main__":
    main()
