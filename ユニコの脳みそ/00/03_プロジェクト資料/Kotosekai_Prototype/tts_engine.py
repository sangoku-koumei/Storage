"""
---
tags: [00_Tool, Python, TTS, edge-tts, Audio]
date: 2026-01-19
source: [[Vol.54_iOSアプリ開発・小説朗読ツール完全攻略バイブル_深層対話]]
link: [[00_知識マップ|⬅️ 知識マップへ戻る]]
---
# Kotosekai Prototype - TTS Engine Module

テキストを音声に変換・再生するモジュール。
高品質な `edge-tts` (Microsoft Edge Online TTS) を使用する。
"""

import asyncio
import os
import subprocess
from datetime import datetime

# edge-ttsがインストールされているかチェック
# pip install edge-tts playback

class TTSEngine:
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
    async def generate_audio_file(self, text: str, filename: str) -> str:
        """
        テキストから音声ファイルを生成する (edge-tts使用)
        """
        # path
        output_path = os.path.join(self.output_dir, filename)
        
        # edge-tts コマンドラインを使用する（ライブラリ依存を減らすためsubprocess経由も手だが、
        # ここではライブラリとして使いたいが、import edge_tts がない場合のフォールバックも考える。
        # MVPなので CLIラッパーとして実装するのが一番確実。
        
        voice = "ja-JP-NanamiNeural" # 人気の声
        
        # コマンド構築
        # edge-tts --text "こんにちは" --write-media hello.mp3 --voice ja-JP-NanamiNeural
        
        # テキストを一時ファイルに保存（コマンドライン引数制限回避）
        # しかし短い段落なら直接でもいけるが、安全のため
        
        print(f"Generating audio: {filename} ({len(text)} chars)...")
        
        command = [
            "edge-tts",
            "--voice", voice,
            "--text", text,
            "--write-media", output_path
        ]
        
        try:
            # 非同期でサブプロセス実行
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                print(f"Error in TTS: {stderr.decode()}")
                return None
                
            return output_path
            
        except FileNotFoundError:
            print("Error: 'edge-tts' command not found. Please install with: pip install edge-tts")
            return None

    def play_audio(self, file_path: str):
        """
        生成した音声ファイルを再生する (OS標準コマンド使用)
        """
        if not file_path or not os.path.exists(file_path):
            return

        print(f"Playing: {file_path}")
        
        # Windows command to play audio (start)
        try:
            os.startfile(file_path) # 非ブロッキング再生（デフォルトプレイヤー）
            # 注意: startfileは非同期的に開くので、「再生終わるまで待つ」制御は難しい。
            # MVPとしては「再生を開始する」までで良しとするか、
            # もし「連続再生」をやるなら winsound や pygame が必要。
            # 今回はプロトタイプなので startfile で「確認」できればOKとする。
        except Exception as e:
            print(f"Play error: {e}")

if __name__ == "__main__":
    engine = TTSEngine()
    asyncio.run(engine.generate_audio_file("これは、コトセカイ・プロトタイプの音声テストです。", "test.mp3"))
    engine.play_audio(os.path.join("output", "test.mp3"))
