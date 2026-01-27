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
            vsc_hwnd = vsc.NativeWindowHandle # VS Codeのウィンドウハンドルを取得
            for ctrl, depth in auto.WalkControl(vsc, maxDepth=50):
                name = ctrl.Name.strip()
                # 許可キーワード（拡張）
                if ctrl.ControlTypeName == "ButtonControl" and any(kw in name for kw in ["Accept", "Yes (Done)", "Allow", "Done", "Start Session", "OK", "Confirm", "Execute", "Approve", "Proceed", "Next", "Continue", "承認", "次へ", "実行", "はい", "OK (次へ)"]):
                    rect = ctrl.BoundingRectangle
                    if rect.width > 0 and rect.height > 0:
                        # ショートカットキー情報を取得（あれば）
                        access_key = ctrl.AccessKey or "None"
                        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Detected: '{name}' (Shortcut: {access_key})")
                        
                        # 承認実行 (API優先)
                        success = False
                        try:
                            # InvokePatternが使えればそれが一番確実
                            if hasattr(ctrl, 'Invoke'):
                                ctrl.Invoke()
                                success = True
                            else:
                                # DoDefaultAction (UI Automation API 共通)
                                ctrl.GetRuntimeId() # 存在確認
                                ctrl.DoDefaultAction()
                                success = True
                        except:
                            # 最終手段: 位置特定してクリック（Windows Message送信）
                            center_x = rect.left + (rect.width // 2)
                            center_y = rect.top + (rect.height // 2)
                            stealth_click_at_point(center_x, center_y)
                            success = True
                        
                        if success:
                            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Automatic Approval Executed.")
                            
                            # 【視覚支援】承認後に一番下までスクロールを試みる（チャットエリアなどの場合）
                            # ボタンの親をたどってスクロール可能なコンテナを探す
                            try:
                                parent = ctrl.GetParent()
                                # Ctrl+End 送信（Cursor/VSCodeのチャット欄などはこれで一番下へ）
                                # ただしバックアップ・セーフにするため、ウィンドウがアクティブな場合のみ
                                if win32gui.GetForegroundWindow() == vsc_hwnd:
                                    # 注意：SendKeysはスレッドをブロックする可能性があるため簡易的なもの
                                    import ctypes
                                    ctypes.windll.user32.keybd_event(0x11, 0, 0, 0) # Ctrl Down
                                    ctypes.windll.user32.keybd_event(0x23, 0, 0, 0) # End Down
                                    ctypes.windll.user32.keybd_event(0x23, 0, 2, 0) # End Up
                                    ctypes.windll.user32.keybd_event(0x11, 0, 2, 0) # Ctrl Up
                            except: pass
                            
                            # 1秒待機して連打防止
                            time.sleep(1)
                            return {"pos": (0, 0), "type": "deep_api", "name": name, "ctrl": ctrl} # 成功したら即座に終了
                # 失敗した場合は座標クリックへフォールバック
                # この部分は元のコードのdeep_fallbackロジックに相当
                # ただし、上記の成功パスでreturnされるため、ここには到達しないはず
                # もし上記のAPI操作が失敗し、かつ座標クリックも失敗した場合のフォールバックとして残す
                # cx, cy = (rect.left + rect.right) // 2, (rect.top + rect.bottom) // 2
                # return {"pos": (cx, cy), "type": "deep_fallback", "name": name, "ctrl": ctrl}
    except Exception: pass
    
    return None

def main():
    print("==============================================")
    print("   Antigravity Robust Stealth Engine v6.1")
    print("==============================================")
    print("Mode: Multi-Vision + Deep API Interaction")
    print("Status: Background Safe (No Enter Key) Active.")
    print("----------------------------------------------")
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    last_git_save = time.time()
    
    try:
        while True:
            res = find_button_hybrid()
            if res:
                name = res["name"]
                pos = res["pos"]
                
                if res["type"] == "deep_api":
                    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] API TRIGGER: '{name}'")
                elif res["type"] == "vision" or res["type"] == "deep_fallback":
                    # 座標クリックのリトライ
                    clicked = False
                    for _ in range(3):
                        if stealth_click_at_point(pos[0], pos[1]):
                            clicked = True
                            break
                        time.sleep(0.2)
                    if clicked:
                        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] STEALTH CLICK: '{name}' ({res['type']})")
                
                # --- Dynamic State Monitoring ---
                start_wait = time.time()
                while time.time() - start_wait < STATE_TRANSITION_TIMEOUT:
                    time.sleep(0.5)
                    check = find_button_hybrid()
                    if not check or check["name"] != name:
                        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] STATE TRANSITION CONFIRMED.")
                        break
                time.sleep(1.0)
            
            # Git Auto Save
            if time.time() - last_git_save > GIT_SAVE_INTERVAL:
                try:
                    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Checking Global Backup...")
                    # 1. ローカルコミットを確実に行う
                    subprocess.run(["git", "add", "."], check=False, shell=True, cwd=base_path)
                    subprocess.run(["git", "commit", "-m", f"Auto save: {datetime.datetime.now()}"], check=False, shell=True, cwd=base_path)
                    
                    # 2. 外部スクリプトで強力な同期を行う (デスクトップ等含む)
                    tools_path = r"c:\Users\user\Desktop\保管庫\git-auto-tools\git-auto-push.ps1"
                    if os.path.exists(tools_path):
                        # PowerShellを非表示ウィンドウで実行
                        p = subprocess.run(["powershell", "-WindowStyle", "Hidden", "-File", tools_path, "-autoCommit"], capture_output=True, text=True)
                        
                        if p.returncode == 0:
                            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Global Backup Success.")
                        else:
                            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Global Backup Failed (Code {p.returncode}). Attempting Auto-Repair...")
                            # --- 自動修復ロジック: index.lock の削除 ---
                            repo_root = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, cwd=base_path).stdout.strip()
                            lock_file = os.path.join(repo_root, ".git", "index.lock")
                            if os.path.exists(lock_file):
                                try:
                                    os.remove(lock_file)
                                    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Auto-Repair: Removed index.lock. Retrying next cycle.")
                                except Exception as lock_e:
                                    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Auto-Repair Failed: {lock_e}")
                            else:
                                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Auto-Repair: No index.lock found. Check network or permissions.")
                    
                    last_git_save = time.time()
                except Exception as e:
                    print(f"Git Backup Error: {e}")
                
            time.sleep(CHECK_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nEngine offline.")

if __name__ == "__main__":
    main()
