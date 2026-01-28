
from duckduckgo_search import DDGS
import time

def find_prospects(query, max_results=10):
    """
    DuckDuckGoを使って見込み客リストを自動生成する
    """
    results = []
    try:
        with DDGS() as ddgs:
            # 検索実行
            search_results = list(ddgs.text(query, max_results=max_results))
            
            for r in search_results:
                title = r.get('title', '')
                href = r.get('href', '')
                body = r.get('body', '')
                
                # 簡易フィルタリング（Wikiやまとめサイトを除外）
                ignore_domains = ['wikipedia.org', 'amazon', 'rakuten', 'qiita', 'note.com', 'youtube']
                if any(x in href for x in ignore_domains):
                    continue
                
                results.append({
                    "company_name": title,
                    "url": href,
                    "snippet": body
                })
                
    except Exception as e:
        print(f"Search Error: {e}")
        return []

    return results
