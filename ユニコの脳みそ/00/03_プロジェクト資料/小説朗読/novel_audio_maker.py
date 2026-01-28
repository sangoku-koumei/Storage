import os
import re
import shutil
import asyncio
import requests
from bs4 import BeautifulSoup
import edge_tts
from tqdm import tqdm

# ==========================================
# 【設定エリア】
# ==========================================
LIBRARY_DIR = "Master_Library"  # 保存保管用
TRANSFER_DIR = "For_iPhone"     # iPhone転送用

# 読み飛ばしたい定型文（共通）
IGNORE_PHRASES = [
    "ブックマーク", "評価", "感想", "誤字報告", "次回の更新", 
    "ポイント", "活動報告", "広告", "下記バナー", "星を", "レビュー"
]

VOICE = "ja-JP-NanamiNeural"
RATE = "+0%"
VOLUME = "+0%"
# ==========================================

def get_soup(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        # Debug
        # print(f"DEBUG: Downloaded {len(response.text)} chars from {url}")
        return BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        print(f"アクセスエラー: {e}")
        return None

# ... (detect_site, get_novel_info, clean_text, process_novel functions remain the same) ...

# Only replacing the end of the file and get_soup function for brevity in this tool call? 
# No, replace_file_content works on chunks. I need to be careful.
# I will just replace `get_soup` first.

# Actually, the user's issue might be the `if __name__` block not pausing on error.
# So I should strictly target those areas. 

# Let's do get_soup first.


def detect_site(url):
    """URLからサイトの種類を判定"""
    if "syosetu.com" in url:
        return "narou"
    elif "kakuyomu.jp" in url:
        return "kakuyomu"
    else:
        return "unknown"

def get_novel_info(url):
    """サイトに合わせてタイトルと各話リストを取得"""
    site_type = detect_site(url)
    soup = get_soup(url)
    if not soup: return None, [], None

    chapters = []
    title = "Unknown"

    if site_type == "narou":
        # なろうの処理
        # タイトル取得
        # タイトル取得
        # 新: .p-novel__title, 旧: .novel_title
        t_elem = soup.select_one(".p-novel__title") or soup.select_one(".novel_title")
        if not t_elem: t_elem = soup.select_one("h1") # Fallback
        if t_elem: title = t_elem.get_text(strip=True)
        
        # ページネーション対応ループ
        page = 1
        base_url = url.split("?")[0].rstrip("/") # クエリパラメータを除去
        
        while True:
            current_url = f"{base_url}/?p={page}" if page > 1 else base_url
            if page > 1: # 2ページ目以降は再取得
                print(f"  ...目次読み込み中 (Page {page})")
                soup = get_soup(current_url)
                if not soup: break

            # 1. 標準的な目次クラス (.subtitle) で探す
            # 1. 標準的な目次クラス (.subtitle) で探す
            # 新: .p-eplist__subtitle, 旧: .subtitle a
            page_chapters = []
            # 両方のセレクタを検索対象にする
            chapter_links = soup.select(".p-eplist__subtitle") or soup.select(".subtitle a")
            
            for a in chapter_links:
                chap_title = a.get_text(strip=True)
                chap_url = "https://ncode.syosetu.com" + a.get("href")
                page_chapters.append((chap_title, chap_url))
            
            # ページ独自の章が見つからなければ終了 (ページネーション終了判定)
            if not page_chapters:
                # ただし1ページ目でFallback（短編等）が必要な場合を除く
                if page == 1:
                    pass # Fallback処理へ
                else:
                    break
            
            chapters.extend(page_chapters)

            # 次のページがあるか確認 (.pager_next があるか、または取得できた章数が100件(上限)か)
            # なろうは通常1ページ100話表示
            # 新: .c-pager__item--next, 旧: .pager_next
            has_next = soup.select_one(".c-pager__item--next") or soup.select_one(".pager_next")
            if not has_next and len(page_chapters) < 100:
                 break
            
            page += 1
            
        # 1ページ目かつ章が見つからない場合のFallback
        if not chapters:
           # 2. 見つからない場合、正規表現でリンクを総当たりする (Fallback)
            ncode_match = re.search(r'syosetu\.com/(n[a-zA-Z0-9]+)', url)
            if ncode_match:
                ncode = ncode_match.group(1)
                for a in soup.find_all("a", href=re.compile(f"/{ncode}/\\d+/")):
                    chap_title = a.get_text(strip=True)
                    chap_url = "https://ncode.syosetu.com" + a.get("href")
                    # 重複除外
                    if not any(c[1] == chap_url for c in chapters):
                        chapters.append((chap_title, chap_url))

        # 3. それでも見つからず、本文枠があるなら短編とみなす
        if not chapters:
            if soup.select_one("#novel_honbun"):
                chapters.append((title, url))

    elif site_type == "kakuyomu":
        # ... (kakuyomu logic remains same)
        # カクヨムの処理
        t_elem = soup.select_one("#workTitle") or soup.select_one("h1")
        if t_elem: title = t_elem.get_text(strip=True)

        base_url = "https://kakuyomu.jp"
        for a in soup.select(".widget-toc-episode a"):
            chap_title = a.select_one(".widget-toc-episode-titleLabel")
            if chap_title:
                chap_title = chap_title.get_text(strip=True)
            else:
                chap_title = a.get_text(strip=True)
                
            href = a.get("href")
            if href.startswith("/"):
                chap_url = base_url + href
            else:
                chap_url = href
            chapters.append((chap_title, chap_url))
    
    else:
        print("対応していないサイトです。")
        return None, [], None

    if len(chapters) == 0:
        print(f"警告: '{title}' の章が見つかりませんでした。サイトの構造が変わったか、ログインが必要な可能性があります。")

    # Windowsファイル名に使えない文字を除去
    safe_title = re.sub(r'[\\/:*?"<>|]', '_', title)
    return safe_title, chapters, site_type

def clean_text(soup, site_type):
    """サイトに合わせて本文を抽出"""
    text = ""
    
    if site_type == "narou":
        # なろうの新旧構造に対応 (.p-novel__body が新, #novel_honbun が旧)
        content = soup.select_one(".p-novel__body") or soup.select_one("#novel_honbun")
    elif site_type == "kakuyomu":
        content = soup.select_one(".widget-episodeBody")
    else:
        content = None

    if not content: return ""

    # ルビ処理（共通）
    soup_copy = BeautifulSoup(str(content), "html.parser")
    for ruby in soup_copy.find_all("ruby"):
        rt = ruby.find("rt")
        if rt: ruby.replace_with(rt.get_text())
    
    raw_text = soup_copy.get_text()
    
    # URL削除
    raw_text = re.sub(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+', '', raw_text)

    # 行ごとのクリーニング
    lines = []
    for line in raw_text.splitlines():
        line = line.strip()
        if not line: continue
        # 定型文除外
        if not any(phrase in line for phrase in IGNORE_PHRASES):
            lines.append(line)
            
    return "\n".join(lines)

async def process_novel(url):
    """小説処理メイン"""
    safe_title, chapters, site_type = get_novel_info(url)
    if not safe_title: return None, 0

    # フォルダパス
    lib_path = os.path.join(LIBRARY_DIR, safe_title)
    iphone_path = os.path.join(TRANSFER_DIR, safe_title)

    if not os.path.exists(lib_path): os.makedirs(lib_path)
    
    # URL記憶
    with open(os.path.join(lib_path, "url.txt"), "w", encoding="utf-8") as f:
        f.write(url)

    print(f"確認中: {safe_title} ({site_type}) - 全{len(chapters)}話")
    
    new_count = 0
    pbar = tqdm(chapters, desc="  Check", leave=False)

    for i, (chap_title, chap_url) in enumerate(pbar, 1):
        safe_chap = re.sub(r'[\\/:*?"<>|]', '_', chap_title)
        filename = f"{i:03}_{safe_chap}.mp3"
        file_master = os.path.join(lib_path, filename)

        # すでにファイルがあればスキップ
        if os.path.exists(file_master):
            continue

        # 新規作成
        pbar.set_description(f"  New: {i}話")
        
        c_soup = get_soup(chap_url)
        if c_soup:
            body = clean_text(c_soup, site_type)
            full_text = f"{chap_title}。\n\n{body}"
            
            # 音声化
            communicate = edge_tts.Communicate(full_text, VOICE, rate=RATE, volume=VOLUME)
            await communicate.save(file_master)
            
            # iPhone用フォルダへコピー
            if not os.path.exists(iphone_path): os.makedirs(iphone_path)
            shutil.copy2(file_master, os.path.join(iphone_path, filename))
            
            new_count += 1
            await asyncio.sleep(2) # 負荷軽減

    return safe_title, new_count

async def main():
    if not os.path.exists(LIBRARY_DIR): os.makedirs(LIBRARY_DIR)
    if not os.path.exists(TRANSFER_DIR): os.makedirs(TRANSFER_DIR)

    print("\n=== なろう＆カクヨム 音声化ツール ===")
    
    while True:
        print("\n------------------------------")
        print("1. 新規追加 (URL入力: カンマ区切りで複数可)")
        print("2. 一括更新 (全フォルダチェック)")
        print("3. 終了")
        
        mode = input("番号を選択 (1-3): ").strip()

        if mode == "1":
            print("URLを入力してください (複数可: スペース、カンマ、改行など何でもOK)")
            raw_input = input(">> ")
            
            # URLらしき文字列をすべて抽出する (http/https で始まり、空白や記号で終わるまで)
            urls = re.findall(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+', raw_input)
            
            if not urls:
                print("URLが見つかりませんでした。")
                continue

            for i, url in enumerate(urls, 1):
                print(f"\n--- [{i}/{len(urls)}] 処理中: {url} ---")
                
                # カクヨムのURL調整
                if "kakuyomu.jp" in url:
                    match = re.search(r'(https://kakuyomu\.jp/works/\d+)', url)
                    if match: url = match.group(1)

                try:
                    title, count = await process_novel(url)
                    if title:
                        print(f"完了: {count}話を追加 -> '{TRANSFER_DIR}/{title}'")
                except Exception as e:
                    print(f"エラーが発生しました ({url}): {e}")

        elif mode == "2":
            novels = [d for d in os.listdir(LIBRARY_DIR) if os.path.isdir(os.path.join(LIBRARY_DIR, d))]
            print(f"\n{len(novels)}作品の更新をチェック中...")
            
            total_new = 0
            for folder in novels:
                url_file = os.path.join(LIBRARY_DIR, folder, "url.txt")
                if os.path.exists(url_file):
                    with open(url_file, "r", encoding="utf-8") as f:
                        url = f.read().strip()
                    try:
                        title, count = await process_novel(url)
                        if count > 0:
                            print(f"  ★更新: {folder} (+{count}話)")
                            total_new += count
                    except Exception as e:
                        print(f"  エラー: {folder} - {e}")
            
            print(f"\n更新完了。合計 {total_new} ファイルを転送用フォルダに作成しました。")

        elif mode == "3" or mode == "q":
            print("終了します。")
            break
        
        else:
            print("1, 2, 3 のいずれかを入力してください。")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
    finally:
        input("\nEnterキーを押して終了してください...")
