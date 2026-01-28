import streamlit as st
import os

# Page Config
st.set_page_config(
    page_title="Naked Strategy | 最強リサーチツール",
    page_icon="🕵️‍♀️",
    layout="wide"
)

# Title and Intro
st.title("🕵️‍♀️ Naked Strategy (MVP)")
st.caption("競合のアカウント戦略を丸裸にするAIリサーチ参謀")

# Sidebar Navigation
st.sidebar.title("メニュー")
tool_selection = st.sidebar.radio(
    "ツールを選択してください",
    ["YouTube悩みマイニング", "Coconalaトレンドハンター", "LINE/コンテンツ解析"]
)

# API Key Management (Placeholder)
with st.sidebar.expander("設定 (API Keys)"):
    openai_key = st.text_input("OpenAI API Key", type="password")
    youtube_key = st.text_input("YouTube Data API Key", type="password")
    if openai_key:
        os.environ["OPENAI_API_KEY"] = openai_key
    if youtube_key:
        os.environ["YOUTUBE_API_KEY"] = youtube_key

# Main Content Routing
if tool_selection == "YouTube悩みマイニング":
    st.header("📺 YouTube Comment 'Pain' Miner")
    st.info("YouTubeのコメント欄から、ユーザーの『満たされない欲求（不満）』を採掘します。")
    
    query = st.text_input("検索キーワード (例: 既読無視, 復縁)", "既読無視")
    if st.button("リサーチ開始"):
        if not os.environ.get("YOUTUBE_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
            st.error("APIキー設定が必要です（サイドバーで入力してください）。")
        else:
            from modules import youtube_miner
            
            with st.spinner(f"『{query}』の動画を検索中..."):
                videos = youtube_miner.search_videos(query, os.environ["YOUTUBE_API_KEY"])
            
            if videos:
                st.subheader("🔍 検索された動画 (上位10件)")
                
                # Checkbox to select videos to analyze
                video_df = pd.DataFrame(videos)
                # Simple display
                for i, v in enumerate(videos):
                    st.write(f"**{i+1}. {v['title']}** ({v['channel']})")
                    st.image(v['thumbnail'], width=120)
                
                video_ids = [v['id'] for v in videos]
                
                if st.button("💬 コメントを分析して「悩み」を抽出する"):
                    with st.spinner("コメント収集中 & AI分析中..."):
                        comments = youtube_miner.get_comments_for_videos(video_ids, os.environ["YOUTUBE_API_KEY"])
                        st.write(f"取得コメント数: {len(comments)}件")
                        
                        analysis_result = youtube_miner.extract_pains_from_comments(comments, os.environ["OPENAI_API_KEY"])
                        
                        st.success("分析完了！")
                        st.markdown("### 🧠 AI分析レポート: ユーザーの深層心理と勝ち筋")
                        st.markdown(analysis_result)
            else:
                st.warning("動画が見つかりませんでした。")

elif tool_selection == "Coconalaトレンドハンター":
    st.header("🛒 Coconala Trend Hunter")
    st.info("ココナラで『新着なのに売れている』最強の競合商品を特定します。")
    
    category_url = st.text_input("カテゴリURL (例: 恋愛占い)", "https://coconala.com/categories/3")
    if st.button("ハンティング開始"):
        from modules import coconala_hunter
        
        with st.spinner("ココナラの市場データを解析中... (※デモモード作動中)"):
            # In a real scenario, this would scrape multiple pages
            df = coconala_hunter.scrape_coconala_category(category_url)
            
        if not df.empty:
            st.subheader("📦 抽出された商品リスト")
            st.dataframe(df)
            
            st.subheader("🧠 戦略分析レポート")
            report = coconala_hunter.analyze_strategy(df)
            st.markdown(report)
        else:
            st.error("データが見つかりませんでした。")

elif tool_selection == "LINE/コンテンツ解析":
    st.header("📱 LINE & Content Analyzer")
    st.info("集めたテキストデータから『売れる構成』や『キラーフレーズ』を抽出します。")
    
    tab1, tab2 = st.tabs(["📂 ログ解析 (リバース)", "✍️ コンテンツ生成 (クリエイト)"])
    
    with tab1:
        st.subheader("競合のステップメール/チャット解析")
        uploaded_file = st.file_uploader("チャット履歴/テキストファイルをアップロード", type=["txt"])
        
        if uploaded_file and st.button("解析実行 (AI)"):
            if not os.environ.get("OPENAI_API_KEY"):
                st.error("OpenAI API Keyが必要です。")
            else:
                from modules import content_gen
                text_data = uploaded_file.read().decode("utf-8")
                
                with st.spinner("AIが『売れる仕組み』を解読しています..."):
                    result = content_gen.analyze_sales_flow(text_data, os.environ["OPENAI_API_KEY"])
                    st.markdown(result)

    with tab2:
        st.subheader("特典コンテンツ(Lead Magnet)の自動生成")
        target_persona = st.text_input("ターゲット (例: 30代 恋愛こじらせ女子)", "恋愛こじらせ女子")
        target_pain = st.text_input("解決したい悩み (例: 既読無視)", "既読無視")
        
        if st.button("最強の特典目次を作成"):
            if not os.environ.get("OPENAI_API_KEY"):
                st.error("OpenAI API Keyが必要です。")
            else:
                from modules import content_gen
                
                with st.spinner("ターゲットの脳髄に響くコンテンツを設計中..."):
                    outline = content_gen.generate_lead_magnet_outline(target_pain, target_persona, os.environ["OPENAI_API_KEY"])
                    st.markdown("### 🎁 提案された特典コンテンツ案")
                    st.markdown(outline)
