
import os
import sys

def clear_screen():
    """OSに合わせた画面クリアコマンドを実行する"""
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def print_header(title):
    """ヘッダーを表示する"""
    clear_screen()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)
    print()

def get_input(prompt, required=True):
    """ユーザー入力を取得する。required=Trueの場合、空入力を許可しない"""
    while True:
        value = input(f"{prompt}: ").strip()
        if not required:
            return value
        if value:
            return value
        print(">> 入力が必要です。")

def save_to_file(content, filename):
    """コンテンツをファイルに保存する"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n>> ファイルを保存しました: {filename}")
    except Exception as e:
        print(f"\n>> 保存に失敗しました: {e}")

def wait_for_enter():
    """Enterキー入力を待つ"""
    input("\n>> Enterキーを押してメニューに戻る...")
