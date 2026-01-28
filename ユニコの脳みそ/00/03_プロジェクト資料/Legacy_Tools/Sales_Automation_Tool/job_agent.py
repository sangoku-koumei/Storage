
from duckduckgo_search import DDGS
from agent import find_prospects
import time

def find_jobs(category="営業自動化", max_results=10):
    """
    具体的案件（Job）を探すエージェント
    「営業自動化」や「DX導入」のニーズを持つ、より具体的な案件ターゲットを探す。
    """
    # 検索クエリを「自動化・DX・ツール導入」に特化させる
    search_queries = [
        # 直球の自動化ニーズ
        "営業自動化 導入支援 パートナー募集",
        "MAツール 運用代行 募集",
        "インサイドセールス 立ち上げ 委託",
        
        # DX・ツール構築系（単価が高い）
        "営業DX 推進 パートナー 募集",
        "HubSpot 導入支援 依頼",
        "Salesforce 構築 外注 募集",
        "kintone 開発 案件 募集",
        
        # 課題ベース（AIソリューションが刺さる層）
        "リード獲得 自動化 外注",
        "アポ獲得 効率化 依頼",
        "ChatGPT 業務活用 コンサル 募集"
    ]
    
    all_jobs = []
    with DDGS() as ddgs:
        for query in search_queries:
            try:
                # 検索実行
                results = list(ddgs.text(query, max_results=3)) # 各クエリ3件ずつ
                for r in results:
                    title = r.get('title', '')
                    body = r.get('body', '')
                    href = r.get('href', '')
                    
                    # 求人サイトやQ&Aサイトを除外（ビジネスパートナー募集に絞る）
                    ignore_domains = ['indeed', 'doda', 'wantedly', 'chiebukuro', 'yahoo', 'job-list']
                    if any(x in href for x in ignore_domains):
                        continue
                        
                    all_jobs.append({
                        "source": "JobAgent",
                        "company_name": title, 
                        "url": href,
                        "snippet": body,
                        "query": query
                    })
            except Exception as e:
                print(f"Job Search Error ({query}): {e}")
                
    # 重複削除
    unique_jobs = {v['url']: v for v in all_jobs}.values()
    return list(unique_jobs)[:max_results]
