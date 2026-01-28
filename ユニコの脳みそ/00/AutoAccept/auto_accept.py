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
# しきい値
CONFIDENCE_THRESHOLD = 0.8
# Git保存間隔
GIT_SAVE_INTERVAL = 900
# 状態監視タイムアウト
STATE_TRANSITION_TIMEOUT = 5.0
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
        print(f"Stealth Click Error: {e}")
    return False

def find_button_hybrid():
    """Antigravity環境に特化したボタン検知ロジック"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    # ターゲットウィンドウの特定
    try:
        root = auto.GetRootControl()
        # "Antigravity" という名称を含むウィンドウを優先
        target_vsc = [w for w in root.GetChildren() if "Antigravity" in w.Name]
        
        if not target_vsc:
            # フォールバック: Visual Studio Code ベースの名称を探す
            target_vsc = [w for w in root.GetChildren() if "Visual Studio Code" in w.Name]

        if not target_vsc:
            return None

        # print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {len(target_vsc)}個のAntigravityウィンドウを走査中...")

        for vsc in target_vsc:
            for ctrl, depth in auto.WalkControl(vsc, maxDepth=50):
                name = ctrl.Name.strip()
                # 承認ボタンのキーワード
                if ctrl.ControlTypeName == "ButtonControl" and any(kw in name for kw in ["Accept", "Yes (Done)", "Allow", "Done", "Start Session", "OK", "Confirm", "Execute", "Approve", "Proceed", "Next", "Continue", "承認", "次へ", "実行", "はい", "OK (次へ)"]):
                    rect = ctrl.BoundingRectangle
                    if rect.width > 0 and rect.height > 0:
                        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] ボタン検知: '{name}'")
                        
                        # 承認実行 (Invokeパターン)
                        success = False
                        try:
                            if hasattr(ctrl, 'Invoke'):
                                ctrl.Invoke()
                                success = True
                            else:
                                ctrl.DoDefaultAction()
                                success = True
                        except:
                            # 最終手段: 座標クリック
                            center_x = rect.left + (rect.width // 2)
                            center_y = rect.top + (rect.height // 2)
                            stealth_click_at_point(center_x, center_y)
                            success = True
                        
                        if success:
                            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 自動承認完了.")
                            time.sleep(1)
                            return {"pos": (0, 0), "type": "api", "name": name}
    except Exception:
        pass
    
    return None

def main():
    print("==============================================")
    print("   Antigravity Native Stealth Engine v7.0")
    print("==============================================")
    print("Agent: Antigravity")
    print("Status: Monitoring for Approval Buttons...")
    print("----------------------------------------------")
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    last_git_save = time.time()
    
    try:
        while True:
            res = find_button_hybrid()
            if res:
                # 状態遷移待ち
                time.sleep(1.0)
            
            # Git 自動同期
            if time.time() - last_git_save > GIT_SAVE_INTERVAL:
                try:
                    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Antigravity 同期システム起動中...")
                    tools_path = r"c:\Users\user\Desktop\保管庫\git-auto-tools\git-auto-push.ps1"
                    if os.path.exists(tools_path):
                        p = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", tools_path, "-autoCommit"], capture_output=True, text=True)
                        if p.returncode == 0:
                            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] グローバルバックアップ成功.")
                        else:
                            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] バックアップエラー (Code {p.returncode})")
                    last_git_save = time.time()
                except Exception as e:
                    print(f"Sync Error: {e}")
                
            time.sleep(CHECK_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nEngine offline.")

if __name__ == "__main__":
    main()
