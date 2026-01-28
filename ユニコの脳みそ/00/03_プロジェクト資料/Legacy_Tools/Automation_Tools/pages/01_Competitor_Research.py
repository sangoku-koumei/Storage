import streamlit as st
from duckduckgo_search import DDGS
import pandas as pd
from openai import OpenAI
import time
import requests
from bs4 import BeautifulSoup
import urllib.parse
import json
import os

# --- Bridge Helper ---
DATA_DIR = "c:\\Users\\user\\Desktop\\保管庫\\ユニコの脳みそ\\Automation_Tools\\data"
os.makedirs(DATA_DIR, exist_ok=True)
STRATEGY_FILE = os.path.join(DATA_DIR, "latest_strategy.json")

# --- 3. Save Data Bridge (Updated for Multi-Account) ---
def save_strategy_data(strategy_text, keyword, project_name="default"):
    """
    Save the generated strategy to a JSON file for the 02 tool to pick up.
    Multi-Account: Saves as `strategy_{project_name}.json`
    """
    # Clean project name
    safe_name = "".join([c for c in project_name if c.isalnum() or c in ('-', '_')]).strip()
    if not safe_name: safe_name = "default"
    
    filename = f"strategy_{safe_name}.json"
    filepath = os.path.join(DATA_DIR, filename)

    data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "project_name": safe_name,
        "keyword": keyword,
        "strategy_content": strategy_text
    }
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        st.toast(f"✅ Strategy Saved: {filename}", icon="💾")
    except Exception as e:
        st.error(f"Failed to save strategy data: {e}")

# --- Main App ---
st.title("🕵️ Competitor Research (Naked Strategy)")

# --- Sidebar ---
with st.sidebar:
    st.header("🔑 API Keys")
    openai_key = st.text_input("OpenAI API Key", type="password")
    
    st.divider()
    # Project Name Input in Sidebar for better layout
    project_name = st.text_input("Project / Brand Name", value="default", help="Used for file saving (Alphanumeric)")
    
    debug_mode = st.checkbox("🐛 Debug Mode", value=True)

if not openai_key:
    st.warning("👈 OpenAI API Key required")
    st.stop()

client = OpenAI(api_key=openai_key)

col1, col2 = st.columns([1, 2])
with col1:
    search_theme = st.text_input("調査テーマ", "溺愛") # Default to simple keyword, logic adds context
with col2:
    target_url = st.text_input("あなたのURL (Gap分析用)", placeholder="https://...")

# Search Assist Buttons
st.markdown("### 🔗 Search Assist (Manual Discovery)")
cols = st.columns(6)
for pf_name, config in PLATFORM_CONFIG.items():
    q = urllib.parse.quote(f"site:{config['domain']} {search_theme}")
    url = f"https://www.google.com/search?q={q}"
    cols[list(PLATFORM_CONFIG.keys()).index(pf_name)].link_button(f"🔍 {pf_name}", url)
st.divider()

if st.button("🚀 Start Deep Individual Analysis"):
    st.info(f"Searching & Analyzing '{search_theme}' with Context Queries... (Deep Precision Mode)")
    
    full_report_data = ""
    
    # Progress Container
    prog_bar = st.progress(0)
    status_box = st.empty()
    
    platforms_list = list(PLATFORM_CONFIG.keys())
    
    for i, pf_name in enumerate(platforms_list):
        pf_config = PLATFORM_CONFIG[pf_name]
        status_box.markdown(f"**🕵️‍♂️ Analyzing: {pf_name}**")
        
        # Debug Log Area
        log_area = None
        if debug_mode:
            with st.expander(f"🐛 Debug & Logs: {pf_name}", expanded=False):
                log_area = st.container()

        # 1. Smart Search (Context + Blacklist)
        results = smart_search(search_theme, pf_name, pf_config['domain'], log_area)
        
        if not results:
            if log_area: log_area.warning("No valid direct accounts found even with context queries.")
            full_report_data += f"\n### {pf_name}\n(有効な競合アカウントが見つかりませんでした)\n"
            continue
            
        if log_area: 
            log_area.success(f"Found {len(results)} valid targets. Starting Individual Analysis (gpt-4o-mini)...")

        # 2. Individual Analysis Loop
        platform_insights = f"### ■ {pf_name} Analysis\n"
        
        for idx, item in enumerate(results):
            # A. Direct Fetch (Good for Note/Tips)
            direct_body = fetch_content(item['href'])
            
            # B. Content Scout (For Wall Platforms or if Direct failed)
            # If direct body is short (<200 chars) or it's a Wall platform, use scout
            scouted_content = ""
            if not direct_body or len(direct_body) < 200 or pf_name in ["Instagram", "Twitter", "X", "YouTube"]:
                with st.spinner(f"🕵️Scouting posts for {item['title']}..."):
                     # Re-use headers from search
                    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"}
                    scouted_content = scout_related_posts(headers, item['href'], item['title'], pf_config['domain'])
            
            # Combine content
            item['body'] = item.get('body', '') + "\n" + (direct_body if direct_body else "")
            item['extra_content'] = scouted_content
            
            # Analyze Individually
            analysis = analyze_single_item(client, item, pf_name)
            
            # Display Realtime
            with st.expander(f"📝 Deep Analysis: {item['title']}", expanded=True):
                st.markdown(f"**URL**: {item['href']}")
                st.markdown(analysis)
            
            # Append to log
            platform_insights += f"\n#### Target {idx+1}: {item['title']}\nURL: {item['href']}\n{analysis}\n"
            time.sleep(0.5)

        full_report_data += platform_insights
        prog_bar.progress((i+1)/len(platforms_list))

    status_box.success("All Platforms Analyzed. Generating Master Market Strategy Bible...")
    
    # Final Report (Synthesis using GPT-4o for quality)
    final_prompt = f"""
    あなたは「伝説のマーケティング・ストラテジスト」です。
    これまでの膨大な競合調査データを統合し、ユーザーがこの市場を完全に制圧するための**「究極の市場攻略バイブル（Whitepaper）」**を作成してください。
    
    【要件】
    1. **分量**: A4用紙5枚〜10枚相当（10,000文字以上を目指す）。圧倒的な情報密度にすること。
    2. **フォーマット**: HTML形式。見出し、箇条書き、太字、そして**「表（Table）」**を多用すること。
    3. **視覚化**: テキストだけでなく、戦略マトリクスなどを表で表現すること。
    
    【入力データ】
    テーマ: {search_theme}
    競合分析ログ: {full_report_data}
    
    【目次構成案】
    
    # Chapter 1: Market Intelligence (市場構造の解明)
    *   **Keyword Ecosystem**: この市場で「お金になるキーワード」と「集客用キーワード」のマップ。
    *   **Competitor Landscape**: 競合のポジショニングマップ（表で表現）。
    
    # Chapter 2: The "Winner's Format" (勝者の型)
    *   **Content Architecture**: 上位勢が共通して採用している「投稿の鉄板構成」をテンプレート化して提示。
    *   **Sensory Words List**: ユーザーの脳髄に響く「キラーワード」のリスト（表形式）。
    
    # Chapter 3: Strategy Matrix (戦略マトリクス)
    *   各プラットフォーム（Insta, Note, X, etc.）ごとの役割と連携戦略。
    *   | Platform | Role | KPI | Content Type |
    *   |---|---|---|---|
    
    # Chapter 4: Action Roadmap (明日からの行動計画)
    *   **Day 1-7**: 立ち上げ期の具体的なタスクリスト。
    *   **Day 8-30**: ファン化のための投稿カレンダー案。
    
    # Chapter 5: Advanced Monetization (マネタイズの極意)
    *   フロントエンドからバックエンドへの導線設計。
    *   高単価商品を売るための心理トリガーの実装方法。
    
    ※これは「単なる要約」ではありません。「戦略指導書」です。
    読者がそのままコンサルティング資料として使えるレベルで出力してください。
    """
    
    try:
        res = client.chat.completions.create(
            model="gpt-4o", # Synthesis needs intelligence
            messages=[{"role":"user", "content": final_prompt}],
            temperature=0.7
        )
        report_html = res.choices[0].message.content.replace("```html", "").replace("```", "")
        
        st.components.v1.html(report_html, height=1000, scrolling=True)
        st.download_button("📥 Download Strategy Bible", report_html, "Strategy_Bible.html")
        
        # Bridge to 02
        save_strategy_data(report_html, search_theme, project_name)
        
    except Exception as e:
        st.error(f"Report Generation Error: {e}")
