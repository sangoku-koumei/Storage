
import time
import schedule
from job_agent import find_jobs
from ai_generator import generate_sales_emails, scrape_company_info
from db import add_company
from data import DEFAULT_HEARING_ITEMS

def job_automation_cycle():
    """
    1サイクルの自動業務フロー
    1. 案件を探す
    2. 詳細をスクレイピング
    3. 提案メールを作成
    4. DBに保存（ステータス: Auto-Drafted）
    """
    print("🔄 Meta-Agent: Starting Cycle...")
    
    # 1. Search
    jobs = find_jobs(category="Web制作", max_results=3) # デモ用: 3件
    print(f"Found {len(jobs)} potential jobs.")
    
    for job in jobs:
        c_url = job['url']
        c_name = job['company_name']
        
        # 2. Scrape
        scraped = scrape_company_info(c_url)
        vision = scraped['vision'] if scraped else ""
        
        # 3. Generate Proposal
        info = DEFAULT_HEARING_ITEMS.copy()
        info['company_name'] = c_name
        info['goal'] = "案件への応募・業務提携の打診"
        
        emails = generate_sales_emails(info, scraped)
        
        # 4. Save
        add_company(c_name, c_url, "Auto-Agent", emails, vision)
        print(f"✅ Drafted proposal for {c_name}")

    print("zzz... Sleeping until next cycle.")

def start_autonomous_loop(interval_minutes=60):
    print(f"🚀 Meta-Agent Started! Running every {interval_minutes} minutes.")
    
    # 初回即時実行
    job_automation_cycle()
    
    # スケジュール設定
    schedule.every(interval_minutes).minutes.do(job_automation_cycle)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    # テスト実行（本来はバックグラウンドプロセスで動かす）
    start_autonomous_loop(interval_minutes=1)
