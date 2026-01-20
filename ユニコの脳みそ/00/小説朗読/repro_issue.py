import requests
from bs4 import BeautifulSoup
import re

# Headers from original script
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8"
}

IGNORE_PHRASES = [
    "ブックマーク", "評価", "感想", "誤字報告", "次回の更新", 
    "ポイント", "活動報告", "広告", "下記バナー", "星を", "レビュー"
]

def get_soup(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        return BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def clean_text(soup, site_type):
    text = ""
    if site_type == "narou":
        content = soup.select_one("#novel_honbun")
    elif site_type == "kakuyomu":
        content = soup.select_one(".widget-episodeBody")
    else:
        content = None

    if not content:
        print(f"DEBUG: clean_text failed to find content for {site_type}")
        return ""

    soup_copy = BeautifulSoup(str(content), "html.parser")
    for ruby in soup_copy.find_all("ruby"):
        rt = ruby.find("rt")
        if rt: ruby.replace_with(rt.get_text())
    
    raw_text = soup_copy.get_text()
    raw_text = re.sub(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+', '', raw_text)

    lines = []
    for line in raw_text.splitlines():
        line = line.strip()
        if not line: continue
        if not any(phrase in line for phrase in IGNORE_PHRASES):
            lines.append(line)
            
    return "\n".join(lines)

def detect_site(url):
    if "syosetu.com" in url: return "narou"
    if "kakuyomu.jp" in url: return "kakuyomu"
    return "unknown"

def main():
    # 1. Narou Test
    print("--- Testing Narou ---")
    rank_url = "https://yomou.syosetu.com/rank/novelgenre/day/short/"
    soup = get_soup(rank_url)
    if soup:
        # Find a novel link
        link = soup.select_one("a[href*='ncode.syosetu.com']")
        if link:
            url = link.get("href")
            print(f"Target: {url}")
            n_soup = get_soup(url)
            if n_soup:
                body = clean_text(n_soup, "narou")
                print(f"Body Length: {len(body)}")
                if len(body) == 0:
                     print("DEBUG: Dumping soup structure for #novel_honbun search:")
                     # Print partial HTML to see structure
                     print(n_soup.prettify()[:2000])

    # 2. Kakuyomu Test (Optional, but good to check)
    # Kakuyomu structure is harder to find a random single page without search, 
    # but let's try a known structure if possible or skip.
    
if __name__ == "__main__":
    main()
