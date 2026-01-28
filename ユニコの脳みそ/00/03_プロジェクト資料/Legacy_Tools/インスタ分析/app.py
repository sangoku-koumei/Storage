"""
Instagram競合・過去投稿調査分析ツール - Streamlitアプリ
"""
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import time

from config import OUTPUT_DIR
from collect_own_posts import collect_own_posts
from collect_competitor_posts import collect_competitor_posts, collect_from_url
from collect_video_views import collect_views_for_posts
from analyze_data import (
    calculate_basic_stats,
    create_comparison_charts,
    export_to_csv,
    export_to_excel
)
from prompt_template import save_prompt_template, generate_quick_analysis_summary

# ページ設定
st.set_page_config(
    page_title="Instagram分析ツール",
    page_icon="📊",
    layout="wide"
)

# タイトル
st.title("📊 Instagram競合・過去投稿調査分析ツール")
st.markdown("---")

# セッション状態の初期化
if 'own_posts_df' not in st.session_state:
    st.session_state.own_posts_df = pd.DataFrame()
if 'competitor_posts_df' not in st.session_state:
    st.session_state.competitor_posts_df = pd.DataFrame()
if 'combined_df' not in st.session_state:
    st.session_state.combined_df = pd.DataFrame()


# サイドバー
st.sidebar.title("📋 メニュー")
menu = st.sidebar.radio(
    "機能を選択",
    ["🏠 ホーム", "📥 データ収集", "📊 データ分析", "💾 データ出力", "📝 プロンプト生成"]
)

# ホーム
if menu == "🏠 ホーム":
    st.header("ツールの使い方")
    
    st.markdown("""
    ### 1. データ収集
    - **自分の投稿**: Instagram Graph APIを使用して自分の投稿データを収集
    - **競合アカウント**: Instaloaderを使用して競合アカウントの投稿を収集
    - **再生数取得**: Seleniumを使用して動画投稿の再生数を取得（オプション）
    
    ### 2. データ分析
    - 収集したデータの基本統計を表示
    - 自分と競合の比較グラフを生成
    
    ### 3. データ出力
    - CSV形式でエクスポート
    - Excel形式でエクスポート（複数シート対応）
    
    ### 4. プロンプト生成
    - ChatGPTなどで分析するためのプロンプトテンプレートを生成
    """)
    
    st.info("💡 ヒント: まず「データ収集」から始めてください。")

# データ収集
elif menu == "📥 データ収集":
    st.header("📥 データ収集")
    
    tab1, tab2, tab3 = st.tabs(["自分の投稿", "競合アカウント", "再生数取得"])
    
    # 自分の投稿収集
    with tab1:
        st.subheader("自分の投稿を収集")
        st.markdown("Instagram Graph APIを使用して自分の投稿データを収集します。")
        
        limit = st.number_input("取得する投稿数", min_value=1, max_value=500, value=50)
        
        if st.button("自分の投稿を収集", type="primary"):
            with st.spinner("投稿を収集中..."):
                try:
                    df = collect_own_posts(limit=limit)
                    if not df.empty:
                        st.session_state.own_posts_df = df
                        st.success(f"✅ {len(df)}件の投稿を収集しました！")
                        st.dataframe(df.head(10))
                    else:
                        st.error("投稿が見つかりませんでした。設定を確認してください。")
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
    
    # 競合アカウント収集
    with tab2:
        st.subheader("競合アカウントの投稿を収集")
        st.markdown("Instaloaderを使用して競合アカウントの投稿を収集します。")
        
        collection_method = st.radio(
            "収集方法",
            ["アカウント名で収集", "投稿URLで収集"]
        )
        
        if collection_method == "アカウント名で収集":
            username = st.text_input("アカウント名（@なし）", placeholder="example_account")
            max_posts = st.number_input("取得する投稿数", min_value=1, max_value=200, value=50)
            
            if st.button("競合アカウントを収集", type="primary"):
                if username:
                    with st.spinner(f"@{username} の投稿を収集中..."):
                        try:
                            df = collect_competitor_posts(username, max_posts=max_posts)
                            if not df.empty:
                                if st.session_state.competitor_posts_df.empty:
                                    st.session_state.competitor_posts_df = df
                                else:
                                    st.session_state.competitor_posts_df = pd.concat([
                                        st.session_state.competitor_posts_df,
                                        df
                                    ], ignore_index=True)
                                st.success(f"✅ {len(df)}件の投稿を収集しました！")
                                st.dataframe(df.head(10))
                            else:
                                st.error("投稿が見つかりませんでした。")
                        except Exception as e:
                            st.error(f"エラーが発生しました: {e}")
                else:
                    st.warning("アカウント名を入力してください。")
        
        else:  # 投稿URLで収集
            post_url = st.text_input("投稿URL", placeholder="https://www.instagram.com/p/...")
            
            if st.button("投稿を収集", type="primary"):
                if post_url:
                    with st.spinner("投稿を収集中..."):
                        try:
                            post_data = collect_from_url(post_url)
                            if post_data:
                                df = pd.DataFrame([post_data])
                                if st.session_state.competitor_posts_df.empty:
                                    st.session_state.competitor_posts_df = df
                                else:
                                    st.session_state.competitor_posts_df = pd.concat([
                                        st.session_state.competitor_posts_df,
                                        df
                                    ], ignore_index=True)
                                st.success("✅ 投稿を収集しました！")
                                st.dataframe(df)
                            else:
                                st.error("投稿を取得できませんでした。")
                        except Exception as e:
                            st.error(f"エラーが発生しました: {e}")
                else:
                    st.warning("投稿URLを入力してください。")
    
    # 再生数取得
    with tab3:
        st.subheader("動画投稿の再生数を取得")
        st.markdown("Seleniumを使用して動画投稿の再生数をスクリーンショットで取得します。")
        st.warning("⚠️ この機能は時間がかかります。動画投稿のみが対象です。")
        
        if not st.session_state.competitor_posts_df.empty:
            video_posts = st.session_state.competitor_posts_df[
                st.session_state.competitor_posts_df['メディアタイプ'] == '動画'
            ]
            
            if not video_posts.empty:
                st.info(f"動画投稿が {len(video_posts)}件 見つかりました。")
                
                if st.button("再生数を取得", type="primary"):
                    with st.spinner("再生数を取得中...（時間がかかります）"):
                        try:
                            updated_df = collect_views_for_posts(video_posts)
                            # 元のDataFrameを更新
                            for idx, row in updated_df.iterrows():
                                original_idx = video_posts.index[video_posts['投稿URL'] == row['投稿URL']].tolist()
                                if original_idx:
                                    st.session_state.competitor_posts_df.loc[original_idx[0], '再生数'] = row['再生数']
                            
                            st.success("✅ 再生数の取得が完了しました！")
                            st.dataframe(st.session_state.competitor_posts_df[
                                st.session_state.competitor_posts_df['メディアタイプ'] == '動画'
                            ][['投稿URL', '再生数', 'いいね数']])
                        except Exception as e:
                            st.error(f"エラーが発生しました: {e}")
            else:
                st.info("動画投稿が見つかりませんでした。")
        else:
            st.info("まず競合アカウントの投稿を収集してください。")

# データ分析
elif menu == "📊 データ分析":
    st.header("📊 データ分析")
    
    # データを結合
    dfs = []
    if not st.session_state.own_posts_df.empty:
        dfs.append(st.session_state.own_posts_df)
    if not st.session_state.competitor_posts_df.empty:
        dfs.append(st.session_state.competitor_posts_df)
    
    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)
        st.session_state.combined_df = combined_df
        
        st.subheader("データ概要")
        st.dataframe(combined_df.head(20))
        
        st.subheader("基本統計")
        stats = calculate_basic_stats(combined_df)
        st.json(stats)
        
        st.subheader("比較グラフ")
        if st.button("グラフを生成", type="primary"):
            with st.spinner("グラフを生成中..."):
                chart_paths = create_comparison_charts(combined_df)
                if chart_paths:
                    st.success(f"✅ {len(chart_paths)}個のグラフを生成しました！")
                    for path in chart_paths:
                        st.image(path)
                else:
                    st.warning("グラフを生成できませんでした。")
    else:
        st.info("まずデータを収集してください。")

# データ出力
elif menu == "💾 データ出力":
    st.header("💾 データ出力")
    
    if not st.session_state.combined_df.empty:
        st.subheader("CSV形式でエクスポート")
        if st.button("CSVをエクスポート", type="primary"):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'instagram_analysis_{timestamp}.csv'
            filepath = export_to_csv(st.session_state.combined_df, filename)
            st.success(f"✅ エクスポート完了: {filepath}")
            
            with open(filepath, 'rb') as f:
                st.download_button(
                    label="CSVをダウンロード",
                    data=f.read(),
                    file_name=filename,
                    mime='text/csv'
                )
        
        st.subheader("Excel形式でエクスポート（複数シート）")
        dfs_to_export = []
        sheet_names = []
        
        if not st.session_state.own_posts_df.empty:
            dfs_to_export.append(st.session_state.own_posts_df)
            sheet_names.append("自分の投稿")
        
        if not st.session_state.competitor_posts_df.empty:
            dfs_to_export.append(st.session_state.competitor_posts_df)
            sheet_names.append("競合投稿")
        
        if dfs_to_export:
            if st.button("Excelをエクスポート", type="primary"):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'instagram_analysis_{timestamp}.xlsx'
                filepath = export_to_excel(dfs_to_export, sheet_names, filename)
                st.success(f"✅ エクスポート完了: {filepath}")
                
                with open(filepath, 'rb') as f:
                    st.download_button(
                        label="Excelをダウンロード",
                        data=f.read(),
                        file_name=filename,
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    )
    else:
        st.info("まずデータを収集してください。")

# プロンプト生成
elif menu == "📝 プロンプト生成":
    st.header("📝 ChatGPT用プロンプト生成")
    
    if not st.session_state.combined_df.empty:
        st.subheader("分析タイプを選択")
        analysis_type = st.selectbox(
            "分析タイプ",
            ["comprehensive", "caption", "hashtag", "timing"],
            format_func=lambda x: {
                "comprehensive": "総合分析",
                "caption": "キャプション分析",
                "hashtag": "ハッシュタグ分析",
                "timing": "投稿タイミング分析"
            }[x]
        )
        
        # CSVを一時保存
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f'data_for_analysis_{timestamp}.csv'
        csv_path = export_to_csv(st.session_state.combined_df, csv_filename)
        
        if st.button("プロンプトを生成", type="primary"):
            prompt_file = save_prompt_template(csv_path, analysis_type)
            st.success(f"✅ プロンプトを生成しました: {prompt_file}")
            
            # プロンプトを表示
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt_content = f.read()
            
            st.text_area("生成されたプロンプト", prompt_content, height=400)
            
            # ダウンロードボタン
            with open(prompt_file, 'rb') as f:
                st.download_button(
                    label="プロンプトをダウンロード",
                    data=f.read(),
                    file_name=os.path.basename(prompt_file),
                    mime='text/plain'
                )
            
            # 簡易サマリーも表示
            st.subheader("データサマリー（参考）")
            summary = generate_quick_analysis_summary(st.session_state.combined_df)
            st.text(summary)
    else:
        st.info("まずデータを収集してください。")

# フッター
st.markdown("---")
st.markdown("⚠️ このツールは個人利用を目的としています。Instagramの利用規約を遵守してください。")





