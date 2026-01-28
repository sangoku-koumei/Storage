"""
---
tags: [00_Tool, Python, Preprocessor, Cleaning, Regex]
date: 2026-01-19
source: [[Vol.54_iOSアプリ開発・小説朗読ツール完全攻略バイブル_深層対話]]
link: [[00_知識マップ|⬅️ 知識マップへ戻る]]
---
# Kotosekai Prototype - Preprocessor Module

取得したテキストを「耳で聞きやすい形」に整形するモジュール。
Vol.54バイブルで定義された「TextPreprocessor」のPython実装版。
"""

import re

class TextPreprocessor:
    def process(self, raw_text: str) -> str:
        """
        生のテキストを受け取り、読み上げ用に整形して返す。
        """
        text = raw_text
        
        # 1. 不要な空白・空行の圧縮
        # 連続する改行を2つまでに制限
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 2. ルビの処理 (青空文庫形式 《》 や HTML残りカス対応)
        # ※Scraperでget_textしてるのでHTMLタグはないはずだが、
        # カクヨムなどでルビがどう落ちてくるかによる。
        # Scraper側で text を取ると ルビもそのまま文字として入ってしまうことが多い。
        # 例： 漢字(かんじ) のようにカッコ書きになるか、単に連続するか。
        # ここでは単純化のため、全角括弧内のひらがな/カタカナが短い場合、読み上げ補助として残すか削除するか選べるようにしたいが
        # MVPでは「記号の正規化」を優先する。
        
        # 3. 記号の正規化
        # 「……」のような連続点を「…」に
        text = re.sub(r'…{2,}', '…', text)
        text = re.sub(r'‥{2,}', '…', text)
        text = re.sub(r'—{2,}', 'ー', text) # ダッシュ
        text = re.sub(r'―{2,}', 'ー', text) # ダッシュ
        
        # 4. 読み上げに邪魔な記号の削除
        # 連続する = や - など
        text = re.sub(r'[=\-]{3,}', '', text)
        
        # 5. 文末の空白除去
        text = "\n".join([line.strip() for line in text.splitlines()])
        
        return text

    def split_to_paragraphs(self, text: str) -> list[str]:
        """
        テキストを段落（空行区切り）ごとのリストに分割する。
        Bibleの「段落ハイライト」機能の基盤。
        """
        # 空行で分割
        paragraphs = re.split(r'\n\s*\n', text)
        # 空要素を削除
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        return paragraphs

if __name__ == "__main__":
    p = TextPreprocessor()
    sample = "これは……テストです。\n\n\n次の段落。\nここにも  無駄な空白  があります。"
    print(p.process(sample))
