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
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "auto_accept.log")

def log_message(msg):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    full_msg = f"[{timestamp}] {msg}"
    print(full_msg)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(full_msg + "\n")
    except:
        pass

# 監視間隔
CHECK_INTERVAL_SECONDS = 0.8
# しきい値
CONFIDENCE_THRESHOLD = 0.8
# -----------------

def stealth_click_at_point(abs_x, abs_y):
    """指定した絶対座標に対してクリック信号を送信する"""
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
        log_message(f"クリックエラー: {e}")
    return False

def find_button_hybrid():
    """承認ボタン検知ロジック"""
    try:
        root = auto.GetRootControl()
        target_vsc = [w for w in root.GetChildren() if "Antigravity" in w.Name or "Visual Studio Code" in w.Name]
        
        if not target_vsc:
            return None

        for vsc in target_vsc:
            for ctrl, depth in auto.WalkControl(vsc, maxDepth=30):
                name = ctrl.Name.strip()
                # 承認ボタンのキーワード（日本語対応）
                if ctrl.ControlTypeName == "ButtonControl" and any(kw in name for kw in [
                    "Accept", "Yes (Done)", "Allow", "Done", "Start Session", "OK", "Confirm", "Execute", "Approve", "Proceed", "Next", "Continue",
                    "承認", "次へ", "実行", "はい", "OK (次へ)", "許可", "完了", "セッション開始"
                ]):
                    rect = ctrl.BoundingRectangle
                    if rect.width > 0 and rect.height > 0:
                        log_message(f"ボタン検知: '{name}'")
                        
                        success = False
                        try:
                            if hasattr(ctrl, 'Invoke'):
                                ctrl.Invoke()
                                success = True
                            else:
                                ctrl.DoDefaultAction()
                                success = True
                        except:
                            center_x = rect.left + (rect.width // 2)
                            center_y = rect.top + (rect.height // 2)
                            stealth_click_at_point(center_x, center_y)
                            success = True
                        
                        if success:
                            log_message(f"自動承認を完了しました: {name}")
                            time.sleep(1)
                            return True
    except Exception:
        pass
    return None

def main():
    log_message("==============================================")
    log_message("   仮想脳 自動承認エンジン 稼働開始")
    log_message("==============================================")
    log_message("状態: 承認ボタンを監視中...")
    
    try:
        while True:
            find_button_hybrid()
            time.sleep(CHECK_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        log_message("エンジンを停止しました。")

if __name__ == "__main__":
    main()
