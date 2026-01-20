import pyautogui
import time
import os
import glob
import subprocess
import datetime

# --- 設定 ---
# 画像検索の間隔（秒）
CHECK_INTERVAL_SECONDS = 1.0

# 画像フォルダ（スクリプトと同じ場所にある .png ファイルを全て対象にする）
IMAGE_FOLDER = os.path.dirname(os.path.abspath(__file__))

# Git自動保存の間隔（秒） 15分 = 900秒
GIT_SAVE_INTERVAL = 900

# Pushするかどうか（リモートリポジトリが設定されていない場合は False にしてください）
DO_PUSH = False 
# ----------------

def git_auto_save():
    """Gitの自動保存を行う関数"""
    print("--- Starting Git Auto Save ---")
    try:
        # ステージング
        subprocess.run(["git", "add", "."], check=False, shell=True)
        
        # コミットメッセージ作成
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_msg = f"Auto save: {now}"
        
        # コミット
        result = subprocess.run(["git", "commit", "-m", commit_msg], check=False, shell=True)
        
        if result.returncode == 0:
            print(f"Git Commit Successful: {commit_msg}")
            
            # Push (オプション)
            if DO_PUSH:
                print("Git Pushing...")
                push_res = subprocess.run(["git", "push"], check=False, shell=True)
                if push_res.returncode == 0:
                    print("Git Push Successful.")
                else:
                    print("Git Push Failed (might be up to date or network issue).")
        else:
            print("Nothing to commit or Git error.")
            
    except Exception as e:
        print(f"Git Auto Save Error: {e}")
    print("------------------------------")

def main():
    print("=== Auto Accept & Git Save Tool Started ===")
    print(f"Watching folder: {IMAGE_FOLDER}")
    
    # ターゲット画像を全て取得
    image_paths = glob.glob(os.path.join(IMAGE_FOLDER, "*.png"))
    
    if not image_paths:
        print("Error: .png images not found in directory.")
        print("Target button screenshots (e.g. accept1.png, accept2.png) are required.")
        input("Press Enter to exit...")
        return

    print(f"Loaded {len(image_paths)} target images:")
    for img in image_paths:
        print(f" - {os.path.basename(img)}")

    print(f"Git Auto Save Interval: {GIT_SAVE_INTERVAL} seconds")
    print("Press Ctrl+C to stop.")

    last_git_save_time = time.time()
    # 初回起動時にもGit保存を試みる（オプション）
    # git_auto_save() 

    try:
        while True:
            # 1. 画像認識 & クリック
            for image_path in image_paths:
                try:
                    # grayscale=True で高速化
                    # OpenCVがない環境でも動くように confidence は指定しない
                    location = pyautogui.locateOnScreen(image_path, grayscale=True)
                    
                    if location:
                        print(f"Button found! ({os.path.basename(image_path)}) Clicking...")
                        # 中心をクリック
                        center = pyautogui.center(location)
                        pyautogui.click(center)
                        
                        # 連打防止のため少し待つ
                        time.sleep(2) 
                        # マウスを少しずらす（ツールチップなどが邪魔する場合があるため）
                        pyautogui.moveRel(10, 10)
                        
                        break # 1つ見つかったらこの回は終了
                except pyautogui.ImageNotFoundException:
                    pass # 見つからなければ次へ
                except Exception as e:
                    # その他のエラー（画面認識権限など）
                    # print(f"Search error: {e}") 
                    pass

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\nStopped by user.")

if __name__ == "__main__":
    main()
