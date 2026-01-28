"""
設定ファイル
環境変数から設定を読み込む
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Instagram Graph API設定
INSTAGRAM_ACCESS_TOKEN = os.getenv('INSTAGRAM_ACCESS_TOKEN', '')
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID', '')

# Instagramログイン情報（競合分析・再生数取得用）
INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME', '')
INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD', '')

# API設定
GRAPH_API_BASE_URL = 'https://graph.instagram.com'

# スクレイピング設定
SCRAPING_DELAY = 60  # 秒（BAN対策）
MAX_POSTS_PER_ACCOUNT = 100  # アカウントあたりの最大取得投稿数

# 出力ディレクトリ
OUTPUT_DIR = 'output'
SCREENSHOTS_DIR = 'screenshots'
DATA_DIR = 'data'

# ディレクトリ作成
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)





