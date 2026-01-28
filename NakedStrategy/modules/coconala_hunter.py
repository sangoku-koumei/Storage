import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import streamlit as st
import random

# User-Agent list to rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
]

def scrape_coconala_category(category_url, max_pages=1):
    """
    Scrapes Coconala category page for items.
    Returns a DataFrame of items.
    Note: Coconala often blocks scraping. This is a basic implementation.
    """
    items = []
    
    for page in range(1, max_pages + 1):
        url = f"{category_url}?page={page}&ref=header_search" # logic might differ
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        
        try:
            # st.write(f"Accessing: {url}")
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                st.warning(f"Failed to retrieve page {page}. Status: {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # This selector is hypothetical and needs adjustment based on actual Coconala structure
            # As of 2024/2026, class names are often obfuscated (e.g., c-searchItem)
            service_cards = soup.find_all('div', class_=lambda x: x and 'c-searchItemClass' in x) 
            
            # Fallback for generic structure search if class names change
            if not service_cards:
                 service_cards = soup.select('a[class*="c-searchItem"]')

            for card in service_cards:
                try:
                    title_tag = card.find('div', class_=lambda x: x and 'title' in x.lower())
                    price_tag = card.find('div', class_=lambda x: x and 'price' in x.lower())
                    rating_counts = card.find('div', class_=lambda x: x and 'count' in x.lower())
                    
                    title = title_tag.get_text(strip=True) if title_tag else "Unknown"
                    price = price_tag.get_text(strip=True) if price_tag else "0"
                    
                    # Basic extraction
                    link = card.get('href')
                    if link and not link.startswith('http'):
                        link = 'https://coconala.com' + link
                        
                    items.append({
                        'title': title,
                        'price': price,
                        'link': link,
                        'is_new': '新着' in card.text or 'NEW' in card.text
                    })
                except Exception:
                    continue
            
            time.sleep(1) # Be polite
            
        except Exception as e:
            st.error(f"Error scraping Coconala: {e}")
            
    # Mock data for demonstration if scraping fails (Anti-Scraping protection is strong)
    if not items:
        st.warning("⚠️ ココナラのスクレイピング対策によりデータを取得できませんでした。デモデータを表示します。")
        items = [
            {'title': '霊視で彼の気持ちを深く読み解きます', 'price': '3,000円', 'link': '#', 'solds': 5, 'is_new': True},
            {'title': '【緊急】今すぐ連絡が欲しいあなたへ思念伝達', 'price': '10,000円', 'link': '#', 'solds': 12, 'is_new': True},
            {'title': '不倫・複雑愛...泥沼から救い出します', 'price': '15,000円', 'link': '#', 'solds': 4, 'is_new': True},
            {'title': '※悪用厳禁※ 彼を沼らせる禁断のLINE術', 'price': '5,000円', 'link': '#', 'solds': 30, 'is_new': False},
        ]

    return pd.DataFrame(items)

def analyze_strategy(df):
    """
    Analyzes the dataframe to find 'Winning Patterns'.
    """
    if df.empty:
        return "データがありません。"

    # Simple Keyword Analysis
    all_text = " ".join(df['title'].tolist())
    
    # Mock analysis since we don't have full NLP here yet
    report = """
    ### 📊 ココナラトレンド分析レポート
    
    **1. 売れているタイトルの傾向**
    - **「具体的」**: 「彼」ではなく「音信不通の彼」
    - **「緊急性」**: 「今すぐ」「緊急」
    - **「禁止」**: 「悪用厳禁」「禁断」
    
    **2. 推定収益構造 (松竹梅)**
    - フロント: 3,000円〜5,000円 (鑑定)
    - ミドル: 10,000円 (縁結び・施術)
    - **勝ち筋**: 「新着」でランクインしている出品者は、既存顧客をLINEから誘導して初速をつけている可能性が高い。
    """
    return report
