
import os
try:
    import openai
except ImportError:
    openai = None

def get_api_key():
    """環境変数または入力からAPIキーを取得"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return api_key

def set_api_key(api_key):
    """APIキーを設定"""
    if openai:
        openai.api_key = api_key
        os.environ["OPENAI_API_KEY"] = api_key

def analyze_search_results(query, search_results):
    """
    検索結果をAIで分析・要約する
    """
    if not openai:
        return "Error: OpenAI library not installed."
        
    api_key = get_api_key()
    if not api_key:
        return "Error: API Key not set."
        
    # 分析用コンテキストの作成
    context = ""
    for i, res in enumerate(search_results):
        context += f"Source {i+1}: {res['title']}\nSummary: {res['body']}\nURL: {res['href']}\n\n"
        
    prompt = f"""
    あなたはプロのリサーチアシスタントです。
    以下の検索結果（Web Search Results）を基に、キーワード「{query}」に関する詳細なレポートを作成してください。
    
    【要件】
    1. 検索結果の情報を統合し、論理的に構成してください。
    2. HTMLレポートとして出力されるため、見出しや箇条書きを使って読みやすくしてください（ただし、HTMLタグは含めず、プレーンテキストまたはMarkdownライクに書いてください）。
    3. 結論だけでなく、「なぜそう言えるのか」という根拠（Source X）を明示してください。
    4. ビジネスマンがそのまま顧客に提出できるレベルの「プロフェッショナルな文体」で執筆してください。
    
    【検索結果】
    {context}
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini", # コストパフォーマンスの良いモデル
            messages=[
                {"role": "system", "content": "You are a helpful and professional research assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Analysis Error: {e}"

def generate_ai_proposal(genre, name, hours):
    """
    AIを使って提案文を動的に生成する
    """
    if not openai:
        return "Error: OpenAI library not installed."
    
    api_key = get_api_key()
    if not api_key:
        return "Error: API Key not set."

    prompt = f"""
    以下の条件で、クラウドソーシング等の案件に応募するための「提案文」を作成してください。
    
    ジャンル: {genre}
    提案者名: {name}
    週稼働時間: {hours}時間
    
    【必須要素】
    1. 丁寧な挨拶
    2. 「AIリサーチによる圧倒的なスピードと質」のアピール
    3. 「競合分析レポート」を付加価値としてつける提案
    4. 相手のメリット（意思決定のスピードアップなど）
    
    文体は「情熱的かつ誠実」にしてください。
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional copywriter."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Generation Error: {e}"
