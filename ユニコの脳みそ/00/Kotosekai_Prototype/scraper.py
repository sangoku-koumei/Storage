"""
---
tags: [00_Tool, Python, Scraper, Novel, Narou, Kakuyomu]
date: 2026-01-19
source: [[Vol.54_iOSアプリ開発・小説朗読ツール完全攻略バイブル_深層対話]]
link: [[00_知識マップ|⬅️ 知識マップへ戻る]]
---
# Kotosekai Prototype - Scraper Module

小説家になろう、カクヨムから本文を抽出するモジュール。
"""

import requests
from bs4 import BeautifulSoup
import re

class NovelScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def fetch_novel(self, url: str) -> dict:
        """
        URLから小説データを取得し、辞書形式で返す。
        対応: 小説家になろう, カクヨム
        """
        print(f"Fetching: {url}")
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            response.encoding = response.apparent_encoding  # 自動判別
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            if "syosetu.com" in url:
                return self._parse_narou(soup)
            elif "kakuyomu.jp" in url:
                return self._parse_kakuyomu(soup)
            else:
                return {"error": "未対応のサイトです"}
                
        except Exception as e:
            return {"error": f"取得エラー: {str(e)}"}

    def _parse_narou(self, soup) -> dict:
        # タイトル
        title_elem = soup.select_one("p.novel_title") or soup.select_one("h1.novel_title")
        title = title_elem.get_text(strip=True) if title_elem else "不明なタイトル"
        
        # 本文 (ID: novel_honbun)
        content_elem = soup.select_one("#novel_honbun")
        if not content_elem:
            return {"error": "本文が見つかりませんでした (Narou)"}
            
        # 本文抽出 (HTMLタグ除去はPreprocessorでやるが、最低限の構造は保つ)
        # ここではraw textを取得
        content = content_elem.get_text("\n")
        
        return {
            "title": title,
            "content": content,
            "site": "Narou"
        }

    def _parse_kakuyomu(self, soup) -> dict:
        # タイトル (widget-episodeTitle)
        title_elem = soup.select_one(".widget-episodeTitle")
        title = title_elem.get_text(strip=True) if title_elem else "不明なタイトル"
        
        # 本文 (widget-episodeBody)
        content_elem = soup.select_one(".widget-episodeBody")
        if not content_elem:
            return {"error": "本文が見つかりませんでした (Kakuyomu)"}
            
        content = content_elem.get_text("\n")
        
        return {
            "title": title,
            "content": content,
            "site": "Kakuyomu"
        }

if __name__ == "__main__":
    # Test
    scraper = NovelScraper()
    # url = "https://ncode.syosetu.com/nXXXXXX/1/" # Example
    print("Scraper module loaded.")
