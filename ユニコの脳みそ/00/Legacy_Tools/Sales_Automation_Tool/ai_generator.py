

import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

try:
    import openai
except ImportError:
    openai = None

def get_api_key():
    return os.getenv("OPENAI_API_KEY")

def set_api_key(api_key):
    if openai:
        openai.api_key = api_key
        os.environ["OPENAI_API_KEY"] = api_key

def scrape_with_selenium(url):
    """
    Seleniumを使った強力なスクレイピング（Headless Browser）
    requestsで取れないSPAやWAF回避用
    """
    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        driver.set_page_load_timeout(30)
        driver.get(url)
        
        html = driver.page_source
        title = driver.title
        
        # テキスト抽出
        soup = BeautifulSoup(html, 'html.parser')
        vision_text = extract_vision(soup)
        
        driver.quit()
        return {"title": title, "vision": vision_text + " (Fetched via Selenium)"}
        
    except Exception as e:
        return {"error": f"Selenium Error: {str(e)}", "title": "Error", "vision": ""}

def extract_vision(soup):
    vision_text = ""
    keywords = ["理念", "ミッション", "ビジョン", "想い", "Mission", "Vision", "Values", "About", "Message"]
    for p in soup.find_all(['p', 'div', 'h2', 'h3', 'li']):
        text = p.get_text().strip()
        if any(k in text for k in keywords) and 20 < len(text) < 400:
            vision_text = text
            break
    return vision_text

def scrape_company_info(url):
    """
    Hybrid Scraping: requests -> 失敗 -> Selenium
    """
    if not url.startswith("http"):
        return {"error": "Invalid URL"}
    
    # Try 1: Requests (Fast)
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=5)
        response.encoding = response.apparent_encoding
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            vision = extract_vision(soup)
            if vision:
                return {"title": soup.title.string.strip() if soup.title else "No Title", "vision": vision}
            else:
                # ビジョンが見つからない場合もSeleniumを試す価値あり（JS描画の可能性があるため）
                pass
        else:
            # 403 Forbiddenなどの場合
            pass
            
    except Exception as e:
        print(f"Requests failed: {e}")

    # Try 2: Selenium (Strong)
    print("⚠️ Switching to Selenium for deep scraping...")
    return scrape_with_selenium(url)

def verify_email_faithfulness(scraped_vision, generated_email):
    """
    【AI嘘発見器】
    生成されたメールが、元のスクレイピング情報（理念）に基づいているか、
    勝手な幻覚（ハルシネーション）を見ていないかチェックする。
    """
    if not openai: return "Error"
    
    prompt = f"""
    あなたは「厳格なファクトチェッカー」です。
    以下の「ソース情報」と「生成されたメール」を比較し、
    メールの中に「ソース情報にない嘘の事実（創業年、売上、存在しない事業など）」が含まれていないか判定してください。
    
    【ソース情報】: {scraped_vision}
    【生成メール】: {generated_email}
    
    判定結果を以下のフォーマットだけ出力してください。
    SAFE (問題なし) or WARNING (幻覚の疑いあり: <理由>)
    """
    try:
        res = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        return res.choices[0].message.content
    except:
        return "Check Failed"


def generate_sales_emails(client_info, scraped_data=None):
    """
    営業メールセット生成（プロスペクティング用）
    """
    if not openai: return "Error: OpenAI library not installed."
    api_key = get_api_key()
    if not api_key: return "Error: API Key not set."

    personalization_instruction = ""
    if scraped_data and "vision" in scraped_data and scraped_data["vision"]:
        personalization_instruction = f"""
        【重要：個別化指示】
        相手企業の理念「{scraped_data['vision']}」を引用し、共感を示してください。
        """

    prompt = f"""
    あなたは凄腕の営業コピーライターです。
    以下の情報を元に、アポイント獲得のためのメール3通を作成してください。

    【相手企業】: {client_info.get('company_name', '貴社')}
    【ターゲットの課題】: {client_info['problem']}
    【提案サービス】: {client_info['service']}
    {personalization_instruction}

    出力形式:
    ---EMAIL 1 (初回)---
    件名: ...
    本文: ...
    ---EMAIL 2 (3日後)---
    件名: ...
    本文: ...
    ---EMAIL 3 (7日後)---
    件名: ...
    本文: ...
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Error: {e}"

def generate_manual_content(client_info):
    """
    旧マニュアル生成（互換性のため残す）
    """
    return generate_deliverable("Inside Sales Setup", client_info)

def generate_deliverable(job_type, client_info):
    """
    【納品物生成機能】
    受注した仕事の内容に合わせて、納品物（ドキュメント、設計図）を生成する。
    """
    if not openai: return "Error"
    if not get_api_key(): return "Error: API Key required."


    prompts = {
        "AI Sales Auto Package": f"""
        あなたは「AI営業自動化パッケージ」の作成者です。
        クライアント（{client_info['company_name']}）に納品する以下の「5点セット」を作成してください。

        【納品物リスト】
        1. **営業メールテンプレ**（初回アプローチ用）
        2. **フォローアップ文**（3日後、7日後、1ヶ月後の3通）
        3. **ChatGPT用プロンプト**（クライアントが自分で文面を変えるためのプロンプト）
        4. **自動送信フロー設計図**（いつ、誰に、何を送るかの図解テキスト）
        5. **運用マニュアル**（誰でも回せるA4一枚レベルの手順書）

        商材: {client_info['service']}
        ターゲット: {client_info['target']}
        """,

        "AI Hiring Package": f"""
        あなたは「AI採用パッケージ」の作成者です。
        クライアント（{client_info['company_name']}）に納品する以下の「採用キット」を作成してください。

        1. **求人原稿**（魅力的なタイトルと本文）
        2. **スカウトメール文面**（優秀な候補者に送るDM）
        3. **面接質問リスト**（カルチャーフィットを見極める質問5選）
        4. **自動返信文**（応募があった際の即時返信メール）

        募集職種: {client_info['service']} (※職種として解釈してください)
        求める人物像: {client_info['target']}
        """,

        "MA/HubSpot Setup": f"""
        あなたはMAツール（Marketing Automation）の導入コンサルタントです。
        クライアント（{client_info['company_name']}）向けに、以下の「導入設計書」を作成してください。

        1. **メールナーチャリング設計図**
           - リード獲得後のステップメール（全5通）の件名と概要フロー
           - 分岐条件（開封した人、クリックした人の振り分け）
        2. **スコアリングルール定義**
           - 何をしたら何点加点するか（例：資料請求+10点）
           - ホットリードの定義
        
        ターゲット: {client_info['target']}
        課題: {client_info['problem']}
        """,
        
        "Inside Sales Setup": f"""
        あなたはインサイドセールスの立ち上げ責任者です。
        クライアント（{client_info['company_name']}）向けに、以下の「運用マニュアル」を作成してください。

        1. **コールスクリプト（トーク台本）**
           - 受付突破トーク
           - 担当者への課題ヒアリングトーク
           - アポイント打診のクロージング
        2. **切り返しトーク集（Objection Handling）**
           - 「今は忙しい」と言われたら
           - 「資料だけ送って」と言われたら
        
        商材: {client_info['service']}
        強み: {client_info['strength']}
        """,
        
        "DX Consulting": f"""
        あなたはDXコンサルタントです。
        クライアント（{client_info['company_name']}）向けに、以下の「DX推進ロードマップ」を作成してください。

        1. **現状分析 (As-Is)**
           - {client_info['problem']} に対するボトルネック特定
        2. **あるべき姿 (To-Be)**
           - DX後の理想的な業務フロー
        3. **導入推奨ツール選定**
           - 課題解決に最適なSaaSツール3選とその選定理由
        4. **3ヶ月実行計画**
        """
    }

    selected_prompt = prompts.get(job_type, prompts["AI Sales Auto Package"])

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a top-tier consultant."},
                {"role": "user", "content": selected_prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Error: {e}"
