"""
---
tags: [00_Tool, Python, CLI, MVP, Kotosekai]
date: 2026-01-19
source: [[Vol.54_iOSアプリ開発・小説朗読ツール完全攻略バイブル_深層対話]]
link: [[00_知識マップ|⬅️ 知識マップへ戻る]]
---
# Kotosekai Prototype - Main CLI

小説朗読ツールのMVPメインエントリーポイント。
URLを受け取り、スクレイピング、整形、音声生成・再生の一連の流れを実行する。

Usage:
    python main.py
"""

import asyncio
import os
import sys

# モジュールインポート
from scraper import NovelScraper
from preprocessor import TextPreprocessor
from tts_engine import TTSEngine

async def main():
    print("=== Kotosekai Prototype MVP ===")
    print("Vol.54 バイブルに基づくプロトタイプ実装")
    print("-----------------------------------")
    
    # 1. URL入力
    url = input("小説のURLを入力してください (なろう/カクヨム): ").strip()
    if not url:
        print("URLが入力されませんでした。終了します。")
        return

    # 2. スクレイピング
    scraper = NovelScraper()
    print("\n[Step 1] Fetching content...")
    novel_data = scraper.fetch_novel(url)
    
    if "error" in novel_data:
        print(f"Error: {novel_data['error']}")
        return
        
    print(f"Title: {novel_data['title']}")
    print(f"Site: {novel_data['site']}")
    print(f"Raw Length: {len(novel_data['content'])} chars")
    
    # 3. 前処理 (Cleaning & Segmentation)
    preprocessor = TextPreprocessor()
    print("\n[Step 2] Preprocessing content...")
    
    clean_text = preprocessor.process(novel_data['content'])
    paragraphs = preprocessor.split_to_paragraphs(clean_text)
    
    print(f"Cleaned Length: {len(clean_text)} chars")
    print(f"Paragraphs: {len(paragraphs)}")
    
    # 4. 読み上げ (TTS)
    # MVPでは最初の3段落だけテスト再生する（全部やると長いので）
    tts = TTSEngine(output_dir="audio_cache")
    
    print("\n[Step 3] Generating Audio (Preview first 3 paragraphs)...")
    
    preview_count = min(3, len(paragraphs))
    for i in range(preview_count):
        p_text = paragraphs[i]
        print(f"\n--- Paragraph {i+1} ---")
        print(p_text)
        
        filename = f"p_{i}.mp3"
        file_path = await tts.generate_audio_file(p_text, filename)
        
        if file_path:
            print(f"Playing {file_path}...")
            tts.play_audio(file_path)
            
            # 簡易的に少し待つ（連続再生の実装はMVP外だが、雰囲気のため）
            # os.startfile は非ブロッキングなので、ウェイトを入れないと一気に開いてしまうリスクがあるが
            # ここではユーザー入力待ちを入れて擬似的に「次へ」とする
            input("Press Enter to play next paragraph...")
    
    print("\n=== Playback Finished ===")
    print("MVP検証完了。")

if __name__ == "__main__":
    # Windowsでasyncioイベントループポリシーの設定が必要な場合がある
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nAborted.")
