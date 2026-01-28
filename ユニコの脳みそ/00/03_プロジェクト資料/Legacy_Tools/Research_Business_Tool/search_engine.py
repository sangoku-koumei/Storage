
from duckduckgo_search import DDGS
import time

def search_web(query, num_results=5):
    """
    DuckDuckGoを使ってWeb検索を行う
    """
    results = []
    try:
        with DDGS() as ddgs:
            # 検索実行
            search_results = list(ddgs.text(query, max_results=num_results))
            for r in search_results:
                results.append({
                    "title": r.get("title", ""),
                    "href": r.get("href", ""),
                    "body": r.get("body", "")
                })
    except Exception as e:
        print(f"Search Error: {e}")
        return []
    
    return results

def search_with_retry(query, num_results=5, retries=3):
    """
    リトライ付き検索
    """
    for i in range(retries):
        results = search_web(query, num_results)
        if results:
            return results
        time.sleep(2)
    return []
