"""
Seleniumを使用して動画投稿の再生数をスクリーンショットで取得するモジュール
"""
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from datetime import datetime
from typing import Optional, Dict
from config import (
    INSTAGRAM_USERNAME,
    INSTAGRAM_PASSWORD,
    SCREENSHOTS_DIR
)
import pytesseract
from PIL import Image
import re


def setup_driver(headless: bool = False) -> webdriver.Chrome:
    """
    Selenium WebDriverをセットアップ
    
    Args:
        headless: ヘッドレスモードで実行するか
        
    Returns:
        WebDriverインスタンス
    """
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()
    
    return driver


def login_instagram(driver: webdriver.Chrome) -> bool:
    """
    Instagramにログイン
    
    Args:
        driver: WebDriverインスタンス
        
    Returns:
        ログイン成功したかどうか
    """
    if not INSTAGRAM_USERNAME or not INSTAGRAM_PASSWORD:
        print("ログイン情報が設定されていません。")
        return False
    
    try:
        driver.get('https://www.instagram.com/accounts/login/')
        time.sleep(3)
        
        # ユーザー名を入力
        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'username'))
        )
        username_input.send_keys(INSTAGRAM_USERNAME)
        
        # パスワードを入力
        password_input = driver.find_element(By.NAME, 'password')
        password_input.send_keys(INSTAGRAM_PASSWORD)
        
        # ログインボタンをクリック
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        
        # ログイン完了を待つ
        time.sleep(5)
        
        # ホーム画面に遷移したか確認
        if 'instagram.com' in driver.current_url and 'login' not in driver.current_url:
            print("ログイン成功")
            return True
        else:
            print("ログイン失敗")
            return False
            
    except Exception as e:
        print(f"ログインエラー: {e}")
        return False


def get_video_views_screenshot(post_url: str, driver: Optional[webdriver.Chrome] = None) -> Optional[str]:
    """
    投稿URLから再生数を表示している画面をスクリーンショットで保存
    
    Args:
        post_url: Instagram投稿のURL
        driver: WebDriverインスタンス（Noneの場合は新規作成）
        
    Returns:
        スクリーンショットのファイルパス、またはNone
    """
    should_close_driver = driver is None
    
    try:
        if driver is None:
            driver = setup_driver(headless=False)  # スクショのためヘッドレスはFalse
        
        # ログイン
        if not login_instagram(driver):
            return None
        
        # 投稿ページに移動
        driver.get(post_url)
        time.sleep(5)  # ページ読み込み待機
        
        # 動画かどうか確認（簡易的な方法）
        try:
            # 再生ボタンや動画要素を探す
            video_elements = driver.find_elements(By.TAG_NAME, 'video')
            if not video_elements:
                print("この投稿は動画ではありません。")
                return None
        except:
            pass
        
        # 再生数が表示されるまで少し待つ
        time.sleep(3)
        
        # スクリーンショットを撮影
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        shortcode = post_url.split('/p/')[-1].rstrip('/')
        screenshot_path = os.path.join(SCREENSHOTS_DIR, f'{shortcode}_{timestamp}.png')
        
        driver.save_screenshot(screenshot_path)
        print(f"スクリーンショット保存: {screenshot_path}")
        
        return screenshot_path
        
    except Exception as e:
        print(f"スクリーンショット取得エラー: {e}")
        return None
    finally:
        if should_close_driver and driver:
            driver.quit()


def extract_views_from_screenshot(screenshot_path: str) -> Optional[int]:
    """
    スクリーンショット画像からOCRで再生数を抽出（実験的機能）
    
    Args:
        screenshot_path: スクリーンショットのファイルパス
        
    Returns:
        再生数、またはNone
    """
    try:
        # 画像を読み込み
        image = Image.open(screenshot_path)
        
        # OCRでテキスト抽出
        text = pytesseract.image_to_string(image, lang='eng')
        
        # 再生数らしき数字を探す（例: "1.2K views", "500 views"など）
        # これは簡易的な実装で、実際の画面レイアウトに依存します
        view_patterns = [
            r'(\d+\.?\d*)\s*[KkMm]?\s*views?',
            r'再生数[：:]\s*(\d+\.?\d*)\s*[KkMm]?',
        ]
        
        for pattern in view_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                views_str = match.group(1)
                try:
                    views = float(views_str)
                    # KやMの単位を考慮（簡易実装）
                    if 'K' in text.upper() or 'k' in text:
                        views *= 1000
                    elif 'M' in text.upper() or 'm' in text:
                        views *= 1000000
                    return int(views)
                except:
                    pass
        
        return None
        
    except Exception as e:
        print(f"OCRエラー: {e}")
        return None


def collect_views_for_posts(df: pd.DataFrame, driver: Optional[webdriver.Chrome] = None) -> pd.DataFrame:
    """
    複数の投稿の再生数を一括で取得
    
    Args:
        df: 投稿データのDataFrame（投稿URL列が必要）
        driver: WebDriverインスタンス
        
    Returns:
        再生数が追加されたDataFrame
    """
    import pandas as pd
    
    if df.empty or '投稿URL' not in df.columns:
        return df
    
    should_close_driver = driver is None
    
    try:
        if driver is None:
            driver = setup_driver(headless=False)
            if not login_instagram(driver):
                return df
        
        views_list = []
        
        for idx, row in df.iterrows():
            post_url = row.get('投稿URL', '')
            media_type = row.get('メディアタイプ', '')
            
            if not post_url or media_type != '動画':
                views_list.append('')
                continue
            
            print(f"再生数取得中: {idx+1}/{len(df)}")
            
            # スクリーンショット取得
            screenshot_path = get_video_views_screenshot(post_url, driver)
            
            if screenshot_path:
                # OCRで再生数を抽出（試行）
                views = extract_views_from_screenshot(screenshot_path)
                views_list.append(views if views else '')
            else:
                views_list.append('')
            
            # BAN対策の遅延
            time.sleep(10)
        
        # DataFrameに再生数列を追加
        df = df.copy()
        df['再生数'] = views_list
        
        return df
        
    except Exception as e:
        print(f"一括取得エラー: {e}")
        return df
    finally:
        if should_close_driver and driver:
            driver.quit()


if __name__ == '__main__':
    # テスト実行
    # screenshot = get_video_views_screenshot('https://www.instagram.com/p/example/')
    # if screenshot:
    #     views = extract_views_from_screenshot(screenshot)
    #     print(f"再生数: {views}")
    pass

