import streamlit as st
from openai import OpenAI
import re

def parse_chat_log(text):
    """
    Parses a exported LINE chat log (text file) or general text.
    Returns a list of messages.
    """
    # Simple regex for LINE format: [Time] [Name] [Message]
    # Example: 12:30 ユーザー A こんにちは
    
    # Just return raw lines for MVP if structure is complex
    lines = text.split('\n')
    messages = [line.strip() for line in lines if line.strip()]
    return messages

def analyze_sales_flow(chat_text, openai_key):
    """
    Analyzes the sales flow (funnel) from the text.
    """
    if not chat_text:
        return "テキストが空です。"
        
    client = OpenAI(api_key=openai_key)
    
    prompt = f"""
    あなたは凄腕のマーケターです。以下のテキストは、あるビジネスアカウントのチャット履歴（またはステップ配信の内容）です。
    ここから**「セールスの導線（ファネル）」**を解析し、図解化してください。
    
    出力フォーマット:
    ### 🛤️ セールスファネル構造図
    1. **【集客/興味付け】**: (例: 無料プレゼント配布)
    2. **【教育/信頼構築】**: (例: 自己開示、権威性アピール)
    3. **【販売/オファー】**: (例: 期間限定の高額商品提示)
    
    ### 🗝️ キラーフレーズ（刺さる言葉）
    - "..." (心理効果: 損失回避)
    
    分析対象テキスト:
    {chat_text[:3000]} 
    """ # Limit char count
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Analysis Error: {e}"

def generate_lead_magnet_outline(target_pain, target_persona, openai_key):
    """
    Generates a Lead Magnet (Freebie) outline based on the pain points.
    """
    client = OpenAI(api_key=openai_key)
    
    prompt = f"""
    ターゲット層: {target_persona}
    最大の悩み: {target_pain}
    
    このターゲットが喉から手が出るほど欲しい**「無料プレゼント（登録特典）」**の構成案を作成してください。
    形式はPDFレポート（全20ページ想定）の目次です。
    タイトルは「キャッチーで、思わずクリックしたくなるもの」にしてください。
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Generation Error: {e}"
