---
tags:
  - プロトタイプ
  - ソースコード
  - Instagram_AI_Prototype
  - 深層ディスカッション
created: 2026-01-19
status: Archived
---

# Instagram_AI_Prototype_Knowledge_Bible

[[00_知識マップ|⬅️ 知識マップへ戻る]]

本ドキュメントは、`Instagram_AI_Prototype` の全ソースコードおよびドキュメントを知識ベースとして保存したものです。

---

## .gitignore

```
# 環境変数
.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Streamlit
.streamlit/

# データファイル
data/
output/
*.csv
*.xlsx
*.png
*.jpg
*.jpeg
screenshots/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db






```

---

## ai_chat.py

```python
import os
import openai
import pandas as pd
import streamlit as st

def get_ai_response(user_input: str, df: pd.DataFrame, api_key: str = None) -> str:
    """
    OpenAI APIを使用して、ユーザーの質問に対する回答を生成する。
    
    Args:
        user_input: ユーザーの質問
        df: 分析データのDataFrame
        api_key: OpenAI APIキー (Noneの場合はst.secretsまたは環境変数を使用)
        
    Returns:
        AIからの回答テキスト
    """
    
    # APIキーの設定
    if api_key:
        client = openai.OpenAI(api_key=api_key)
    elif "OPENAI_API_KEY" in st.secrets:
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    else:
        return "⚠️ OpenAI APIキーが設定されていません。サイドバーの設定を確認してください。"

    # コンテキストデータの作成（データの要約）
    context_summary = "【分析データ概要】\n"
    
    if df.empty:
        context_summary += "データがありません。\n"
    else:
        # 基本統計
        if 'いいね数' in df.columns:
            df['いいね数'] = pd.to_numeric(df['いいね数'], errors='coerce')
            avg_likes = df['いいね数'].mean()
            max_likes = df['いいね数'].max()
            context_summary += f"- 平均いいね数: {avg_likes:.1f}\n"
            context_summary += f"- 最大いいね数: {max_likes}\n"
            
        if '保存数' in df.columns:
             df['保存数'] = pd.to_numeric(df['保存数'], errors='coerce')
             avg_saves = df['保存数'].mean()
             context_summary += f"- 平均保存数: {avg_saves:.1f}\n"

        # 投稿数
        context_summary += f"- 総投稿数: {len(df)}\n"
        
        # 上位投稿（いいね順）
        if 'いいね数' in df.columns and '投稿URL' in df.columns:
             top_posts = df.sort_values(by='いいね数', ascending=False).head(3)
             context_summary += "\n【人気投稿トップ3】\n"
             for idx, row in top_posts.iterrows():
                 caption = row.get('キャプション', '')[:50] + "..." if 'キャプション' in row else "なし"
                 context_summary += f"1. いいね: {row['いいね数']}, URL: {row['投稿URL']}, 内容: {caption}\n"

    # システムプロンプトの構築
    system_prompt = f"""
あなたはプロのInstagramマーケティングコンサルタントです。
以下の分析データを元に、ユーザーの質問に具体的かつ論理的に答えてください。
あなたのクライアントは分析の初心者です。

{context_summary}

## ルール
1. 初心者にもわかりやすく、専門用語は補足を入れて説明すること。
2. データに基づいた客観的な事実と、そこから推測される改善案を分けること。
3. 励ましやポジティブなフィードバックを含め、モチベーションを高めること。
4. 回答は日本語で行うこと。
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # または gpt-3.5-turbo
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"

```

---

## analyze_data.py

```python
"""
データ分析と可視化のモジュール
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import List, Optional
import os
from config import OUTPUT_DIR

# 日本語フォント設定（Windowsの場合）
plt.rcParams['font.family'] = 'DejaVu Sans'
sns.set_style("whitegrid")


def calculate_basic_stats(df: pd.DataFrame) -> dict:
    """
    基本的な統計情報を計算
    
    Args:
        df: 投稿データのDataFrame
        
    Returns:
        統計情報の辞書
    """
    stats = {}
    
    if df.empty:
        return stats
    
    # 数値列の統計
    numeric_cols = ['いいね数', 'コメント数', '保存数', 'リーチ数', 'インプレッション数']
    
    for col in numeric_cols:
        if col in df.columns:
            # 文字列を数値に変換
            df[col] = pd.to_numeric(df[col], errors='coerce')
            stats[f'{col}_平均'] = df[col].mean()
            stats[f'{col}_中央値'] = df[col].median()
            stats[f'{col}_最大'] = df[col].max()
            stats[f'{col}_最小'] = df[col].min()
    
    # キャプション文字数
    if 'キャプション' in df.columns:
        df['キャプション文字数'] = df['キャプション'].str.len()
        stats['キャプション文字数_平均'] = df['キャプション文字数'].mean()
        stats['キャプション文字数_最大'] = df['キャプション文字数'].max()
        stats['キャプション文字数_最小'] = df['キャプション文字数'].min()
    
    # ハッシュタグ数
    if 'ハッシュタグ' in df.columns:
        df['ハッシュタグ数'] = df['ハッシュタグ'].str.split().str.len()
        stats['ハッシュタグ数_平均'] = df['ハッシュタグ数'].mean()
        stats['ハッシュタグ数_最大'] = df['ハッシュタグ数'].max()
    
    # 投稿タイプ別の統計
    if '投稿タイプ' in df.columns:
        stats['投稿タイプ別件数'] = df['投稿タイプ'].value_counts().to_dict()
    
    return stats


def create_comparison_charts(df: pd.DataFrame, output_dir: str = OUTPUT_DIR) -> List[str]:
    """
    自分と競合の比較グラフを作成
    
    Args:
        df: 投稿データのDataFrame
        output_dir: 出力ディレクトリ
        
    Returns:
        作成したグラフファイルのパスリスト
    """
    if df.empty or '投稿タイプ' not in df.columns:
        return []
    
    chart_paths = []
    
    # 数値列を数値型に変換
    numeric_cols = ['いいね数', 'コメント数', '保存数']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # キャプション文字数とハッシュタグ数を計算
    if 'キャプション' in df.columns:
        df['キャプション文字数'] = df['キャプション'].str.len()
    if 'ハッシュタグ' in df.columns:
        df['ハッシュタグ数'] = df['ハッシュタグ'].str.split().str.len()
    
    # 1. いいね数の比較（箱ひげ図）
    if 'いいね数' in df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        df.boxplot(column='いいね数', by='投稿タイプ', ax=ax)
        ax.set_title('いいね数の比較', fontsize=14, fontweight='bold')
        ax.set_xlabel('投稿タイプ')
        ax.set_ylabel('いいね数')
        plt.suptitle('')  # デフォルトのタイトルを削除
        path = os.path.join(output_dir, 'comparison_likes.png')
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        chart_paths.append(path)
    
    # 2. キャプション文字数の比較
    if 'キャプション文字数' in df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        df.boxplot(column='キャプション文字数', by='投稿タイプ', ax=ax)
        ax.set_title('キャプション文字数の比較', fontsize=14, fontweight='bold')
        ax.set_xlabel('投稿タイプ')
        ax.set_ylabel('文字数')
        plt.suptitle('')
        path = os.path.join(output_dir, 'comparison_caption_length.png')
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        chart_paths.append(path)
    
    # 3. ハッシュタグ数の比較
    if 'ハッシュタグ数' in df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        df.boxplot(column='ハッシュタグ数', by='投稿タイプ', ax=ax)
        ax.set_title('ハッシュタグ数の比較', fontsize=14, fontweight='bold')
        ax.set_xlabel('投稿タイプ')
        ax.set_ylabel('ハッシュタグ数')
        plt.suptitle('')
        path = os.path.join(output_dir, 'comparison_hashtags.png')
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        chart_paths.append(path)
    
    # 4. 投稿時間帯の分布
    if '投稿時間帯' in df.columns:
        fig, ax = plt.subplots(figsize=(12, 6))
        for post_type in df['投稿タイプ'].unique():
            subset = df[df['投稿タイプ'] == post_type]
            if '投稿時間帯' in subset.columns:
                # 時間を数値に変換（例: "19:00" -> 19.0）
                times = subset['投稿時間帯'].str.split(':').str[0].astype(float)
                ax.hist(times, alpha=0.5, label=post_type, bins=24)
        ax.set_title('投稿時間帯の分布', fontsize=14, fontweight='bold')
        ax.set_xlabel('時間（時）')
        ax.set_ylabel('投稿数')
        ax.legend()
        ax.set_xticks(range(0, 24, 2))
        path = os.path.join(output_dir, 'comparison_time.png')
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        chart_paths.append(path)
    
    # 5. いいね数とキャプション文字数の相関
    if 'いいね数' in df.columns and 'キャプション文字数' in df.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        for post_type in df['投稿タイプ'].unique():
            subset = df[df['投稿タイプ'] == post_type]
            ax.scatter(
                subset['キャプション文字数'],
                subset['いいね数'],
                alpha=0.6,
                label=post_type
            )
        ax.set_title('いいね数とキャプション文字数の相関', fontsize=14, fontweight='bold')
        ax.set_xlabel('キャプション文字数')
        ax.set_ylabel('いいね数')
        ax.legend()
        path = os.path.join(output_dir, 'correlation_caption_likes.png')
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        chart_paths.append(path)
    
    return chart_paths


def export_to_csv(df: pd.DataFrame, filename: str, output_dir: str = OUTPUT_DIR) -> str:
    """
    DataFrameをCSVファイルにエクスポート
    
    Args:
        df: エクスポートするDataFrame
        filename: ファイル名
        output_dir: 出力ディレクトリ
        
    Returns:
        エクスポートしたファイルのパス
    """
    filepath = os.path.join(output_dir, filename)
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    return filepath


def export_to_excel(df_list: List[pd.DataFrame], sheet_names: List[str], filename: str, output_dir: str = OUTPUT_DIR) -> str:
    """
    複数のDataFrameをExcelファイルの別シートにエクスポート
    
    Args:
        df_list: エクスポートするDataFrameのリスト
        sheet_names: シート名のリスト
        filename: ファイル名
        output_dir: 出力ディレクトリ
        
    Returns:
        エクスポートしたファイルのパス
    """
    filepath = os.path.join(output_dir, filename)
    
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        for df, sheet_name in zip(df_list, sheet_names):
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    return filepath






```

---

## app.py

```python
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
from ai_chat import get_ai_response

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
    ["🏠 ホーム", "📥 データ収集", "📊 データ分析", "💾 データ出力", "📝 プロンプト生成", "🤖 AIチャット"]
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

# AIチャット
elif menu == "🤖 AIチャット":
    st.header("🤖 AIチャットボット")
    st.markdown("分析データについて、AIに自由に質問してみましょう！")

    # APIキーの確認
    api_key_input = None
    if "OPENAI_API_KEY" not in st.secrets:
        api_key_input = st.text_input("OpenAI APIキーを入力してください", type="password")
        if not api_key_input:
            st.warning("APIキーを入力するか、secrets.tomlに設定してください。")
            st.stop()
    
    # データを結合
    dfs = []
    if not st.session_state.own_posts_df.empty:
        dfs.append(st.session_state.own_posts_df)
    if not st.session_state.competitor_posts_df.empty:
        dfs.append(st.session_state.competitor_posts_df)
    
    combined_df = pd.DataFrame()
    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)

    # チャット履歴の初期化
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 履歴の表示
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ユーザー入力
    if prompt := st.chat_input("例: 「私の投稿の改善点は？」"):
        # ユーザーメッセージを表示
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AIの回答を取得
        with st.chat_message("assistant"):
            with st.spinner("AIが考え中..."):
                response = get_ai_response(prompt, combined_df, api_key=api_key_input)
                st.markdown(response)
        
        # 履歴に追加
        st.session_state.messages.append({"role": "assistant", "content": response})

# フッター
st.markdown("---")
st.markdown("⚠️ このツールは個人利用を目的としています。Instagramの利用規約を遵守してください。")






```

---

## collect_competitor_posts.py

```python
"""
競合アカウントのInstagram投稿をInstaloaderで収集するモジュール
"""
import instaloader
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
import time
import re
from config import (
    INSTAGRAM_USERNAME,
    INSTAGRAM_PASSWORD,
    SCRAPING_DELAY,
    MAX_POSTS_PER_ACCOUNT
)


def extract_hashtags(caption: str) -> str:
    """
    キャプションからハッシュタグを抽出
    
    Args:
        caption: キャプション文字列
        
    Returns:
        ハッシュタグの文字列（スペース区切り）
    """
    if not caption:
        return ''
    
    hashtags = re.findall(r'#\w+', caption)
    return ' '.join(hashtags)


def collect_competitor_posts(
    username: str,
    max_posts: int = MAX_POSTS_PER_ACCOUNT,
    login_required: bool = True
) -> pd.DataFrame:
    """
    競合アカウントの投稿を収集してDataFrameに変換
    
    Args:
        username: Instagramアカウント名（@なし）
        max_posts: 取得する最大投稿数
        login_required: ログインが必要かどうか（いいね数取得には必要）
        
    Returns:
        投稿データのDataFrame
    """
    print(f"競合アカウント @{username} の投稿を収集中... (最大{max_posts}件)")
    
    # Instaloaderの初期化
    loader = instaloader.Instaloader(
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False
    )
    
    # ログイン（必要に応じて）
    if login_required and INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD:
        try:
            loader.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            print("ログイン成功")
        except Exception as e:
            print(f"ログインエラー: {e}")
            print("ログインなしで続行します（いいね数などが取得できない可能性があります）")
            login_required = False
    
    try:
        # プロフィールを取得
        profile = instaloader.Profile.from_username(loader.context, username)
        print(f"アカウント名: {profile.full_name}")
        print(f"フォロワー数: {profile.followers:,}")
        
        # 投稿を取得
        posts = profile.get_posts()
        
        data = []
        count = 0
        
        for post in posts:
            if count >= max_posts:
                break
            
            count += 1
            print(f"処理中: {count}/{max_posts}")
            
            # 投稿日時をパース
            post_date = post.date_local.strftime('%Y-%m-%d')
            post_time = post.date_local.strftime('%H:%M')
            weekday = post.date_local.strftime('%A')
            
            caption = post.caption or ''
            hashtags = extract_hashtags(caption)
            
            # いいね数とコメント数を取得
            likes = post.likes
            comments = post.comments
            
            row = {
                '投稿タイプ': f'競合_{username}',
                '投稿日時': f"{post_date} {post_time}",
                '投稿日': post_date,
                '投稿時間帯': post_time,
                '曜日': weekday,
                'いいね数': likes,
                'コメント数': comments,
                '保存数': '',  # Instaloaderでは取得不可
                'リーチ数': '',
                'インプレッション数': '',
                'キャプション': caption,
                'ハッシュタグ': hashtags,
                'メディアタイプ': '動画' if post.is_video else '写真',
                '投稿URL': f"https://www.instagram.com/p/{post.shortcode}/",
                'メディアID': post.shortcode,
                '再生数': ''  # 後でSeleniumで取得
            }
            
            data.append(row)
            
            # BAN対策の遅延
            if count < max_posts:
                time.sleep(SCRAPING_DELAY)
        
        df = pd.DataFrame(data)
        print(f"収集完了: {len(df)}件の投稿を取得しました。")
        
        return df
        
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"エラー: アカウント @{username} が見つかりませんでした。")
        return pd.DataFrame()
    except instaloader.exceptions.PrivateProfileNotFollowedException:
        print(f"エラー: アカウント @{username} は非公開です。フォローが必要です。")
        return pd.DataFrame()
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return pd.DataFrame()


def collect_from_url(post_url: str) -> Optional[Dict]:
    """
    投稿URLから1件の投稿データを取得
    
    Args:
        post_url: Instagram投稿のURL
        
    Returns:
        投稿データの辞書、またはNone
    """
    # URLからshortcodeを抽出
    shortcode_match = re.search(r'/p/([^/]+)/', post_url)
    if not shortcode_match:
        print("無効なURLです。")
        return None
    
    shortcode = shortcode_match.group(1)
    
    loader = instaloader.Instaloader(
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False
    )
    
    # ログイン（必要に応じて）
    if INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD:
        try:
            loader.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        except Exception as e:
            print(f"ログインエラー: {e}")
    
    try:
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        
        post_date = post.date_local.strftime('%Y-%m-%d')
        post_time = post.date_local.strftime('%H:%M')
        weekday = post.date_local.strftime('%A')
        
        caption = post.caption or ''
        hashtags = extract_hashtags(caption)
        
        return {
            '投稿タイプ': '競合_個別',
            '投稿日時': f"{post_date} {post_time}",
            '投稿日': post_date,
            '投稿時間帯': post_time,
            '曜日': weekday,
            'いいね数': post.likes,
            'コメント数': post.comments,
            '保存数': '',
            'リーチ数': '',
            'インプレッション数': '',
            'キャプション': caption,
            'ハッシュタグ': hashtags,
            'メディアタイプ': '動画' if post.is_video else '写真',
            '投稿URL': post_url,
            'メディアID': post.shortcode,
            '再生数': ''
        }
    except Exception as e:
        print(f"投稿取得エラー: {e}")
        return None


if __name__ == '__main__':
    # テスト実行
    # df = collect_competitor_posts('example_account', max_posts=10)
    # if not df.empty:
    #     print(df.head())
    #     df.to_csv('output/competitor_posts.csv', index=False, encoding='utf-8-sig')
    pass






```

---

## collect_own_posts.py

```python
"""
自身のInstagram投稿をGraph APIで収集するモジュール
"""
import requests
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
import time
from config import (
    INSTAGRAM_ACCESS_TOKEN,
    INSTAGRAM_BUSINESS_ACCOUNT_ID,
    GRAPH_API_BASE_URL
)


def get_media_list(limit: int = 25) -> List[Dict]:
    """
    Graph APIを使用して自分の投稿一覧を取得
    
    Args:
        limit: 取得する投稿数の上限
        
    Returns:
        投稿データのリスト
    """
    if not INSTAGRAM_ACCESS_TOKEN or not INSTAGRAM_BUSINESS_ACCOUNT_ID:
        raise ValueError("Instagram Graph APIの設定が完了していません。.envファイルを確認してください。")
    
    url = f"{GRAPH_API_BASE_URL}/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media"
    params = {
        'fields': 'id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count',
        'access_token': INSTAGRAM_ACCESS_TOKEN,
        'limit': limit
    }
    
    all_posts = []
    next_url = url
    
    while next_url and len(all_posts) < limit:
        try:
            response = requests.get(next_url, params=params if next_url == url else None)
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data:
                all_posts.extend(data['data'])
            
            # 次のページがあるかチェック
            if 'paging' in data and 'next' in data['paging']:
                next_url = data['paging']['next']
                params = None  # 次のURLには既にパラメータが含まれている
                time.sleep(1)  # API制限対策
            else:
                next_url = None
                
        except requests.exceptions.RequestException as e:
            print(f"APIリクエストエラー: {e}")
            break
    
    return all_posts[:limit]


def get_media_insights(media_id: str) -> Dict:
    """
    投稿のインサイトデータ（保存数など）を取得
    
    Args:
        media_id: メディアID
        
    Returns:
        インサイトデータ
    """
    url = f"{GRAPH_API_BASE_URL}/{media_id}/insights"
    params = {
        'metric': 'saved,reach,impressions',
        'access_token': INSTAGRAM_ACCESS_TOKEN
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        insights = {}
        if 'data' in data:
            for metric in data['data']:
                insights[metric['name']] = metric['values'][0]['value'] if metric['values'] else 0
        
        return insights
    except requests.exceptions.RequestException as e:
        print(f"インサイト取得エラー (media_id: {media_id}): {e}")
        return {}


def extract_hashtags(caption: str) -> str:
    """
    キャプションからハッシュタグを抽出
    
    Args:
        caption: キャプション文字列
        
    Returns:
        ハッシュタグの文字列（カンマ区切り）
    """
    if not caption:
        return ''
    
    import re
    hashtags = re.findall(r'#\w+', caption)
    return ' '.join(hashtags)


def collect_own_posts(limit: int = 100) -> pd.DataFrame:
    """
    自分の投稿を収集してDataFrameに変換
    
    Args:
        limit: 取得する投稿数の上限
        
    Returns:
        投稿データのDataFrame
    """
    print(f"自分の投稿を収集中... (最大{limit}件)")
    
    posts = get_media_list(limit)
    
    if not posts:
        print("投稿が見つかりませんでした。")
        return pd.DataFrame()
    
    data = []
    
    for i, post in enumerate(posts, 1):
        print(f"処理中: {i}/{len(posts)}")
        
        # インサイトデータを取得（保存数など）
        insights = get_media_insights(post.get('id', ''))
        
        # 投稿日時をパース
        timestamp = post.get('timestamp', '')
        if timestamp:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            post_time = dt.strftime('%H:%M')
            post_date = dt.strftime('%Y-%m-%d')
            weekday = dt.strftime('%A')
        else:
            post_time = ''
            post_date = ''
            weekday = ''
        
        caption = post.get('caption', '')
        hashtags = extract_hashtags(caption)
        
        row = {
            '投稿タイプ': '自分',
            '投稿日時': f"{post_date} {post_time}" if post_date and post_time else timestamp,
            '投稿日': post_date,
            '投稿時間帯': post_time,
            '曜日': weekday,
            'いいね数': post.get('like_count', {}).get('count', 0) if isinstance(post.get('like_count'), dict) else post.get('like_count', 0),
            'コメント数': post.get('comments_count', {}).get('count', 0) if isinstance(post.get('comments_count'), dict) else post.get('comments_count', 0),
            '保存数': insights.get('saved', 0),
            'リーチ数': insights.get('reach', 0),
            'インプレッション数': insights.get('impressions', 0),
            'キャプション': caption,
            'ハッシュタグ': hashtags,
            'メディアタイプ': post.get('media_type', ''),
            '投稿URL': post.get('permalink', ''),
            'メディアID': post.get('id', ''),
            '再生数': ''  # Graph APIでは取得不可
        }
        
        data.append(row)
        
        # API制限対策
        if i < len(posts):
            time.sleep(1)
    
    df = pd.DataFrame(data)
    print(f"収集完了: {len(df)}件の投稿を取得しました。")
    
    return df


if __name__ == '__main__':
    # テスト実行
    df = collect_own_posts(limit=10)
    if not df.empty:
        print(df.head())
        df.to_csv('output/own_posts.csv', index=False, encoding='utf-8-sig')






```

---

## collect_video_views.py

```python
"""
Seleniumを使用して動画投稿の再生数をスクリーンショットで取得するモジュール
"""
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from datetime import datetime
from typing import Optional, Dict
from config import (
    INSTAGRAM_USERNAME,
    INSTAGRAM_PASSWORD,
    SCREENSHOTS_DIR
)
import pytesseract
from PIL import Image
import re


def setup_driver(headless: bool = False) -> webdriver.Chrome:
    """
    Selenium WebDriverをセットアップ
    
    Args:
        headless: ヘッドレスモードで実行するか
        
    Returns:
        WebDriverインスタンス
    """
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()
    
    return driver


def login_instagram(driver: webdriver.Chrome) -> bool:
    """
    Instagramにログイン
    
    Args:
        driver: WebDriverインスタンス
        
    Returns:
        ログイン成功したかどうか
    """
    if not INSTAGRAM_USERNAME or not INSTAGRAM_PASSWORD:
        print("ログイン情報が設定されていません。")
        return False
    
    try:
        driver.get('https://www.instagram.com/accounts/login/')
        time.sleep(3)
        
        # ユーザー名を入力
        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'username'))
        )
        username_input.send_keys(INSTAGRAM_USERNAME)
        
        # パスワードを入力
        password_input = driver.find_element(By.NAME, 'password')
        password_input.send_keys(INSTAGRAM_PASSWORD)
        
        # ログインボタンをクリック
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        
        # ログイン完了を待つ
        time.sleep(5)
        
        # ホーム画面に遷移したか確認
        if 'instagram.com' in driver.current_url and 'login' not in driver.current_url:
            print("ログイン成功")
            return True
        else:
            print("ログイン失敗")
            return False
            
    except Exception as e:
        print(f"ログインエラー: {e}")
        return False


def get_video_views_screenshot(post_url: str, driver: Optional[webdriver.Chrome] = None) -> Optional[str]:
    """
    投稿URLから再生数を表示している画面をスクリーンショットで保存
    
    Args:
        post_url: Instagram投稿のURL
        driver: WebDriverインスタンス（Noneの場合は新規作成）
        
    Returns:
        スクリーンショットのファイルパス、またはNone
    """
    should_close_driver = driver is None
    
    try:
        if driver is None:
            driver = setup_driver(headless=False)  # スクショのためヘッドレスはFalse
        
        # ログイン
        if not login_instagram(driver):
            return None
        
        # 投稿ページに移動
        driver.get(post_url)
        time.sleep(5)  # ページ読み込み待機
        
        # 動画かどうか確認（簡易的な方法）
        try:
            # 再生ボタンや動画要素を探す
            video_elements = driver.find_elements(By.TAG_NAME, 'video')
            if not video_elements:
                print("この投稿は動画ではありません。")
                return None
        except:
            pass
        
        # 再生数が表示されるまで少し待つ
        time.sleep(3)
        
        # スクリーンショットを撮影
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        shortcode = post_url.split('/p/')[-1].rstrip('/')
        screenshot_path = os.path.join(SCREENSHOTS_DIR, f'{shortcode}_{timestamp}.png')
        
        driver.save_screenshot(screenshot_path)
        print(f"スクリーンショット保存: {screenshot_path}")
        
        return screenshot_path
        
    except Exception as e:
        print(f"スクリーンショット取得エラー: {e}")
        return None
    finally:
        if should_close_driver and driver:
            driver.quit()


def extract_views_from_screenshot(screenshot_path: str) -> Optional[int]:
    """
    スクリーンショット画像からOCRで再生数を抽出（実験的機能）
    
    Args:
        screenshot_path: スクリーンショットのファイルパス
        
    Returns:
        再生数、またはNone
    """
    try:
        # 画像を読み込み
        image = Image.open(screenshot_path)
        
        # OCRでテキスト抽出
        text = pytesseract.image_to_string(image, lang='eng')
        
        # 再生数らしき数字を探す（例: "1.2K views", "500 views"など）
        # これは簡易的な実装で、実際の画面レイアウトに依存します
        view_patterns = [
            r'(\d+\.?\d*)\s*[KkMm]?\s*views?',
            r'再生数[：:]\s*(\d+\.?\d*)\s*[KkMm]?',
        ]
        
        for pattern in view_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                views_str = match.group(1)
                try:
                    views = float(views_str)
                    # KやMの単位を考慮（簡易実装）
                    if 'K' in text.upper() or 'k' in text:
                        views *= 1000
                    elif 'M' in text.upper() or 'm' in text:
                        views *= 1000000
                    return int(views)
                except:
                    pass
        
        return None
        
    except Exception as e:
        print(f"OCRエラー: {e}")
        return None


def collect_views_for_posts(df: pd.DataFrame, driver: Optional[webdriver.Chrome] = None) -> pd.DataFrame:
    """
    複数の投稿の再生数を一括で取得
    
    Args:
        df: 投稿データのDataFrame（投稿URL列が必要）
        driver: WebDriverインスタンス
        
    Returns:
        再生数が追加されたDataFrame
    """
    import pandas as pd
    
    if df.empty or '投稿URL' not in df.columns:
        return df
    
    should_close_driver = driver is None
    
    try:
        if driver is None:
            driver = setup_driver(headless=False)
            if not login_instagram(driver):
                return df
        
        views_list = []
        
        for idx, row in df.iterrows():
            post_url = row.get('投稿URL', '')
            media_type = row.get('メディアタイプ', '')
            
            if not post_url or media_type != '動画':
                views_list.append('')
                continue
            
            print(f"再生数取得中: {idx+1}/{len(df)}")
            
            # スクリーンショット取得
            screenshot_path = get_video_views_screenshot(post_url, driver)
            
            if screenshot_path:
                # OCRで再生数を抽出（試行）
                views = extract_views_from_screenshot(screenshot_path)
                views_list.append(views if views else '')
            else:
                views_list.append('')
            
            # BAN対策の遅延
            time.sleep(10)
        
        # DataFrameに再生数列を追加
        df = df.copy()
        df['再生数'] = views_list
        
        return df
        
    except Exception as e:
        print(f"一括取得エラー: {e}")
        return df
    finally:
        if should_close_driver and driver:
            driver.quit()


if __name__ == '__main__':
    # テスト実行
    # screenshot = get_video_views_screenshot('https://www.instagram.com/p/example/')
    # if screenshot:
    #     views = extract_views_from_screenshot(screenshot)
    #     print(f"再生数: {views}")
    pass


```

---

## config.py

```python
"""
設定ファイル
環境変数から設定を読み込む
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Instagram Graph API設定
INSTAGRAM_ACCESS_TOKEN = os.getenv('INSTAGRAM_ACCESS_TOKEN', '')
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID', '')

# Instagramログイン情報（競合分析・再生数取得用）
INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME', '')
INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD', '')

# API設定
GRAPH_API_BASE_URL = 'https://graph.instagram.com'

# スクレイピング設定
SCRAPING_DELAY = 60  # 秒（BAN対策）
MAX_POSTS_PER_ACCOUNT = 100  # アカウントあたりの最大取得投稿数

# 出力ディレクトリ
OUTPUT_DIR = 'output'
SCREENSHOTS_DIR = 'screenshots'
DATA_DIR = 'data'

# ディレクトリ作成
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)






```

---

## prompt_template.py

```python
"""
ChatGPT用プロンプトテンプレート生成モジュール
"""
import os
from datetime import datetime
from config import OUTPUT_DIR


def generate_analysis_prompt(
    csv_path: str,
    analysis_type: str = 'comprehensive'
) -> str:
    """
    ChatGPT用の分析プロンプトテンプレートを生成
    
    Args:
        csv_path: CSVファイルのパス
        analysis_type: 分析タイプ（'comprehensive', 'caption', 'hashtag', 'timing'など）
        
    Returns:
        プロンプト文字列
    """
    
    base_prompt = f"""以下は私と競合のInstagram投稿データです。
キャプション、タグ、投稿時間、反応（いいね・保存・コメント）などをもとに、
私の投稿の伸び悩みの原因を分析してください。

【分析してほしいポイント】
"""
    
    if analysis_type == 'comprehensive':
        prompt = base_prompt + """
1. バズった投稿と伸びなかった投稿の違い
   - キャプションの傾向（文字数、構成、トーン）
   - ハッシュタグの使い方（数、種類、頻度）
   - 投稿時間帯や曜日の効果
   - メディアタイプ（写真/動画）の違い

2. 自分と競合の比較
   - どの要素が最も差が出ているか
   - 競合の成功パターンで真似できるものは何か
   - 自分の強みと弱み

3. 改善提案
   - 具体的な改善アクション
   - 次回の投稿で試すべきこと
   - 避けるべきパターン

【データ】
以下のCSVデータを分析してください：

"""
    elif analysis_type == 'caption':
        prompt = base_prompt + """
1. キャプションの分析
   - 文字数の最適範囲
   - 構成パターン（導入、本文、締め）
   - 絵文字の使い方
   - 共感を呼ぶフレーズ

2. キャプション改善案
   - バズった投稿のキャプションの特徴
   - 自分のキャプションの改善点

【データ】
以下のCSVデータを分析してください：

"""
    elif analysis_type == 'hashtag':
        prompt = base_prompt + """
1. ハッシュタグの分析
   - タグ数の最適範囲
   - 効果的なタグの種類
   - タグとエンゲージメントの相関

2. ハッシュタグ戦略の改善案
   - 競合が使っている効果的なタグ
   - 自分のタグ選びの改善点

【データ】
以下のCSVデータを分析してください：

"""
    elif analysis_type == 'timing':
        prompt = base_prompt + """
1. 投稿タイミングの分析
   - 効果的な投稿時間帯
   - 曜日の効果
   - 投稿頻度の影響

2. タイミング戦略の改善案
   - 最適な投稿スケジュール
   - 避けるべき時間帯

【データ】
以下のCSVデータを分析してください：

"""
    else:
        prompt = base_prompt + """
【データ】
以下のCSVデータを分析してください：

"""
    
    prompt += f"""
---CSVデータ（{csv_path}）---
[ここにCSVデータを貼り付けてください]

分析結果は、具体的で実践的なアドバイスとして出力してください。
"""
    
    return prompt


def save_prompt_template(
    csv_path: str,
    analysis_type: str = 'comprehensive',
    output_dir: str = OUTPUT_DIR
) -> str:
    """
    プロンプトテンプレートをファイルに保存
    
    Args:
        csv_path: CSVファイルのパス
        analysis_type: 分析タイプ
        output_dir: 出力ディレクトリ
        
    Returns:
        保存したファイルのパス
    """
    prompt = generate_analysis_prompt(csv_path, analysis_type)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'chatgpt_prompt_{analysis_type}_{timestamp}.txt'
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(prompt)
    
    return filepath


def generate_quick_analysis_summary(df) -> str:
    """
    簡易分析サマリーを生成（ChatGPTに渡す前の補足情報として）
    
    Args:
        df: 投稿データのDataFrame
        
    Returns:
        サマリーテキスト
    """
    import pandas as pd
    
    if df.empty:
        return "データがありません。"
    
    summary = "【データサマリー】\n\n"
    
    # 基本統計
    if '投稿タイプ' in df.columns:
        summary += f"投稿タイプ別件数:\n"
        for post_type, count in df['投稿タイプ'].value_counts().items():
            summary += f"  - {post_type}: {count}件\n"
        summary += "\n"
    
    # 数値列の平均
    numeric_cols = ['いいね数', 'コメント数', '保存数']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            avg = df[col].mean()
            if not pd.isna(avg):
                summary += f"{col}の平均: {avg:.1f}\n"
    
    # キャプション文字数
    if 'キャプション' in df.columns:
        avg_length = df['キャプション'].str.len().mean()
        summary += f"キャプション文字数の平均: {avg_length:.1f}文字\n"
    
    # ハッシュタグ数
    if 'ハッシュタグ' in df.columns:
        avg_tags = df['ハッシュタグ'].str.split().str.len().mean()
        summary += f"ハッシュタグ数の平均: {avg_tags:.1f}個\n"
    
    return summary






```

---

## README.md

```markdown
---
tags: [prototype, tool/instagram, python, analysis, ai]
date: 2026-01-16
source: Building_AI_Sales_Prototypes
---

# Instagram競合・過去投稿調査分析ツール (Instagram Analyzer)

Tags: #Instagram #Python #データリサーチ #競合分析 #マーケティング戦略 #Zettelkasten #自動化 #Streamlit
Links: [[00_知識マップ]] [[USAGE]] [[ツール説明書]] [[会話内容整理]] [[技術資産__インスタ分析ツール]] [[2025-12-22-インスタ動画解析結果]] [[2026-01-09_SNS運用代行_知識統合バイブル_深層対話]] [[2026-01-13_ツール開発・改善知見バイブル_深層対話]]

---

Instagramの投稿を続けているが、伸びている投稿と伸びない投稿の違いが分析できていない問題を解決するツールです。

## 🎯 機能

- **自身の投稿収集**: Instagram Graph APIを使用して自分の投稿データを安全に収集
- **競合アカウント分析**: Instaloaderを使用して競合アカウントの投稿を収集・分析
- **再生数取得**: Seleniumを使用して動画投稿の再生数をスクリーンショットで取得
- **簡易分析**: データの可視化と基本的な統計分析
- **CSV出力**: ChatGPTなど外部AIで分析しやすい形式でデータを出力

## 📋 セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env`ファイルを作成し、以下の情報を設定してください：

```
# Instagram Graph API設定（自分の投稿収集用）
INSTAGRAM_ACCESS_TOKEN=your_access_token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_business_account_id

# Instagramログイン情報（競合分析・再生数取得用）
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
```

### 3. Instagram Graph APIのセットアップ

1. [Meta for Developers](https://developers.facebook.com/)でアプリを作成
2. Instagram Graph APIを有効化
3. アクセストークンを取得
4. ビジネスアカウントIDを取得

詳細は[セットアップガイド](setup_guide.md)または[公式ドキュメント](https://developers.facebook.com/docs/instagram-api/)を参照してください。

## 🚀 使用方法

### Streamlitアプリの起動

```bash
streamlit run app.py
```

ブラウザで `http://localhost:8501` が自動的に開きます。

### 機能の使い方

#### 1. データ収集
- **自分の投稿**: 「データ収集」タブで「自分の投稿」を選択し、取得数を指定して収集
- **競合アカウント**: アカウント名または投稿URLを入力して競合の投稿を収集
- **再生数取得**: 動画投稿の再生数をスクリーンショットで取得（オプション）

#### 2. データ分析
- 「データ分析」タブで収集したデータの基本統計を確認
- 比較グラフを生成して自分と競合の違いを可視化

#### 3. データ出力
- CSV形式またはExcel形式でデータをエクスポート
- 自分と競合のデータを別シートで出力可能

#### 4. プロンプト生成
- ChatGPTなどで分析するためのプロンプトテンプレートを生成
- 分析タイプ（総合、キャプション、ハッシュタグ、タイミング）を選択可能

## ⚠️ 注意事項

- Instagramの利用規約を遵守してください
- スクレイピングは適切な遅延を入れて使用してください
- 大量のデータ取得はアカウントBANのリスクがあります
- 商用利用の場合は法的リスクを考慮してください

## 📝 ライセンス

このツールは個人利用を目的としています。商用利用の場合は適切な法的確認を行ってください。

---

## 🌩️ 深層対話：分析の先にある「市場の支配」

**テーマ**: データを「眺める」フェーズから、「市場の歪み」を突く戦略フェーズへ

**参加者**:
*   **Architect**: システム設計者。データの整合性と「収集の持続性」を重視。
*   **Strategist**: ビジネス軍師。分析結果を「勝てるコンテンツ案」に変換する。
*   **Data Scientist**: 解析の専門家。相関関係から「バズの再現性」を抽出する。
*   **Unico (PM)**: プロジェクト統合者。ツールを「脳の拡張」として位置づける。

---

### 第1章：なぜ「自分の投稿」だけを分析しても勝てないのか

**Strategist**: 
多くのユーザーは、自分のインサイトだけを見て「今回の投稿は良かった、悪かった」と言っています。しかし、それは「井の中の蛙」です。

**Data Scientist**: 
統計学的にも、N=1（自分のデータだけ）では、単なる偶然（アルゴリズムの気まぐれ）と、実力（構成の良さ）の区別がつきません。

**Architect**: 
だからこそ、この README の `🎯 機能` の 2番目に「競合アカウント分析」を置きました。Meta Graph API という「正面玄関」だけでなく、Instaloader という「窓」から他人の家（競合）を観察する必要がある。

**Unico**: 
**【提言1】 常に「相対的な偏差」で判断せよ。**
昨日の自分の投稿よりも、昨日の競合の方が伸びているなら、あなたの負けです。その「負け」の理由を特定するのがこのツールの `README` に込められた真の目的です。

### 第2章：再生数という「本能」の数字をハックする

**Architect**: 
`再生数取得` 機能に Selenium と OCR を使ったのは、Instagram がリール（動画）の再生数という「最もバズが可視化されやすい数字」を API で隠しがちだからです。

**Strategist**: 
再生数は、フォロワー外への「リーチの爆発力」を示します。いいね数は「既存フォロワーへの信頼」です。この二つの乖離を見抜くことで、「新規客を呼べる投稿」か「既存客を温める投稿」かを分類できます。

**Unico**: 
それが `2025-12-22-インスタ動画解析結果` で語られた「初動の爆発力」の正体ですね。

### 第3章：AIへの「丸投げ」を「命令」に変える

**Data Scientist**: 
README の `プロンプト生成` 機能。これは単なるおまけではありません。ChatGPTという超高機能な「脳」を、このツールが集めた「データ」という燃料で駆動させるための着火剤です。

**Strategist**: 
「何かいい案ある？」と聞くのではなく、「この競合のバズ投稿3件に共通して含まれる『ベネフィットと言い回しの組み合わせ』を抽出せよ」と命令させる。

**Architect**: 
そのための土台が、このツールの出力する「CSV形式」です。AIにとって最も理解しやすい「構造化された事実」を渡すこと。

### 第4章：エピローグ：分析の泥臭さが、クリエイティブの輝きを作る

**Unico**: 
`注意事項` にある「適切な遅延」。これは、一見すると技術的な制約ですが、実は「思考のテンポ」でもあります。

**Strategist**: 
データを一気に集めるのではなく、1件1件の投稿を眺めながら、なぜこれが伸びたのかを自分でも考える。その「泥臭い思考」がないと、AIの回答を使いこなせません。

**Architect**: 
ツールは「楽」をするためではなく、**「より深い思考」に時間を割くため**にある。

**Unico**: 
さあ、`セットアップ` を完了させましょう。あなたのインスタ運用は、今日から「勘」ではなく「確信」へと変わります。

---

## 関連リンク
- [[USAGE]]
- [[ツール説明書]]
- [[会話内容整理]]
- [[技術資産__インスタ分析ツール]]
- [[2025-12-22-インスタ動画解析結果]]
- [[2026-01-09_SNS運用代行_知識統合バイブル_深層対話]]
- [[2026-01-13_ツール開発・改善知見バイブル_深層対話]]
- [[在宅ワーク考察]]
- [[00 Rules]]


```

---

## requirements.txt

```
pandas
streamlit
matplotlib
seaborn
openpyxl
instaloader
requests
selenium
webdriver_manager
openai


```

---

## setup_guide.md

```markdown
---
tags: [setup, guide, tool/instagram, python, env]
date: 2026-01-16
source: Building_AI_Sales_Prototypes
---

# セットアップガイド

Links: [[00_知識マップ]] [[README]] [[USAGE]]

## 📋 必要なもの

1. Python 3.8以上
2. Instagramビジネスアカウント（自分の投稿収集用）
3. Instagramアカウント（競合分析用、ログインが必要）

## 🔧 インストール手順

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env`ファイルをプロジェクトルートに作成し、以下の情報を設定してください：

```env
# Instagram Graph API設定（自分の投稿収集用）
INSTAGRAM_ACCESS_TOKEN=your_access_token_here
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_business_account_id_here

# Instagramログイン情報（競合分析・再生数取得用）
INSTAGRAM_USERNAME=your_username_here
INSTAGRAM_PASSWORD=your_password_here
```

### 3. Instagram Graph APIのセットアップ

#### ステップ1: Meta for Developersでアプリを作成

1. [Meta for Developers](https://developers.facebook.com/)にアクセス
2. 「マイアプリ」→「アプリを作成」をクリック
3. アプリタイプを選択（「ビジネス」を推奨）
4. アプリ名を入力して作成

#### ステップ2: Instagram Graph APIを有効化

1. アプリダッシュボードで「製品を追加」をクリック
2. 「Instagram Graph API」を選択
3. セットアップを完了

#### ステップ3: アクセストークンを取得

1. 「ツール」→「Graph APIエクスプローラー」を開く
2. ユーザー/ページを選択
3. 「アクセストークンを生成」をクリック
4. 必要な権限を選択：
   - `instagram_basic`
   - `instagram_content_publish`（投稿する場合）
   - `pages_read_engagement`（インサイト取得用）
5. 生成されたトークンを`.env`ファイルの`INSTAGRAM_ACCESS_TOKEN`に設定

#### ステップ4: ビジネスアカウントIDを取得

1. Graph APIエクスプローラーで以下を実行：
   ```
   GET /me/accounts
   ```
2. 返されたデータから、Instagramアカウントに接続されているページのIDを取得
3. そのページIDで以下を実行：
   ```
   GET /{page-id}?fields=instagram_business_account
   ```
4. 返された`instagram_business_account.id`を`.env`ファイルの`INSTAGRAM_BUSINESS_ACCOUNT_ID`に設定

詳細は[公式ドキュメント](https://developers.facebook.com/docs/instagram-api/getting-started)を参照してください。

### 4. ChromeDriverのセットアップ（再生数取得機能用）

`webdriver-manager`が自動的にChromeDriverをダウンロード・管理しますが、Chromeブラウザがインストールされている必要があります。

## 🚀 アプリの起動

```bash
streamlit run app.py
```

ブラウザで `http://localhost:8501` が自動的に開きます。

## ⚠️ 注意事項

### スクレイピングについて

- Instaloaderを使用した競合アカウントのデータ収集は、Instagramの利用規約に違反する可能性があります
- 商用利用の場合は法的リスクを考慮してください
- 適切な遅延（デフォルト60秒）を設定して使用してください
- 大量のデータ取得はアカウントBANのリスクがあります

### セキュリティについて

- `.env`ファイルには機密情報が含まれます。Gitにコミットしないでください
- パスワードは強力なものを使用してください
- 定期的にアクセストークンを更新してください

## 🐛 トラブルシューティング

### Graph APIエラー

- アクセストークンが有効か確認してください
- ビジネスアカウントIDが正しいか確認してください
- 必要な権限が付与されているか確認してください

### Instaloaderエラー

- ログイン情報が正しいか確認してください
- 2要素認証が有効な場合は、アプリパスワードを使用してください
- レート制限に達している場合は、時間をおいて再試行してください

### Seleniumエラー

- Chromeブラウザがインストールされているか確認してください
- ChromeDriverのバージョンがChromeのバージョンと一致しているか確認してください

## 📞 サポート

問題が発生した場合は、エラーメッセージと共にIssueを作成してください。






```

---

## USAGE.md

```markdown
---
tags: [usage, guide, tool/instagram, python]
date: 2026-01-16
source: Building_AI_Sales_Prototypes
---

# 使用方法ガイド（Instagram分析ツール）

Tags: #Instagram #Python #データ分析 #競合リサーチ #マーケティング #Streamlit #Zettelkasten
Links: [[00_知識マップ]] [[README]] [[ツール説明書]] [[会話内容整理]] [[技術資産__インスタ分析ツール]] [[2025-12-22-インスタ動画解析結果]] [[2026-01-09_SNS運用代行_知識統合バイブル_深層対話]]

---

## 📖 基本的な使い方

### ステップ1: 環境設定

1. `.env`ファイルを作成し、必要な情報を設定（詳細は[setup_guide.md](setup_guide.md)を参照）
2. 依存関係をインストール: `pip install -r requirements.txt`

### ステップ2: アプリを起動

```bash
streamlit run app.py
```

### ステップ3: データ収集

#### 自分の投稿を収集

1. サイドバーの「📥 データ収集」を選択
2. 「自分の投稿」タブを開く
3. 取得する投稿数を指定（1〜500件）
4. 「自分の投稿を収集」ボタンをクリック

**必要な設定**:
- Instagram Graph APIのアクセストークン
- ビジネスアカウントID

#### 競合アカウントの投稿を収集

**方法1: アカウント名で収集**

1. 「競合アカウント」タブを開く
2. 「アカウント名で収集」を選択
3. アカウント名を入力（@なし、例: `example_account`）
4. 取得する投稿数を指定
5. 「競合アカウントを収集」ボタンをクリック

**方法2: 投稿URLで収集**

1. 「投稿URLで収集」を選択
2. Instagram投稿のURLを貼り付け
3. 「投稿を収集」ボタンをクリック

**注意**: 複数の競合アカウントを収集する場合、何度でも実行できます。データは累積されます。

#### 再生数を取得（オプション）

1. 「再生数取得」タブを開く
2. 動画投稿が自動的に検出されます
3. 「再生数を取得」ボタンをクリック

**注意**: 
- この機能は時間がかかります（1投稿あたり約10秒）
- Chromeブラウザが必要です
- ログイン情報が必要です

### ステップ4: データ分析

1. サイドバーの「📊 データ分析」を選択
2. 収集したデータの概要が表示されます
3. 「グラフを生成」ボタンをクリックして比較グラフを作成

**生成されるグラフ**:
- いいね数の比較（箱ひげ図）
- キャプション文字数の比較
- ハッシュタグ数の比較
- 投稿時間帯の分布
- いいね数とキャプション文字数の相関

### ステップ5: データ出力

1. サイドバーの「💾 データ出力」を選択
2. CSVまたはExcel形式でエクスポート
3. ダウンロードボタンでファイルを保存

**出力形式**:
- **CSV**: すべてのデータを1つのファイルに
- **Excel**: 自分の投稿と競合投稿を別シートに

### ステップ6: ChatGPTで分析

1. サイドバーの「📝 プロンプト生成」を選択
2. 分析タイプを選択:
   - **総合分析**: すべての要素を包括的に分析
   - **キャプション分析**: キャプションに特化
   - **ハッシュタグ分析**: ハッシュタグ戦略に特化
   - **投稿タイミング分析**: 投稿時間に特化
3. 「プロンプトを生成」ボタンをクリック
4. 生成されたプロンプトをコピー
5. ChatGPTに貼り付けて、CSVデータも一緒に送信

## 💡 活用のコツ

### データ収集のベストプラクティス

1. **自分の投稿**: できるだけ多くの投稿を収集（50件以上推奨）
2. **競合アカウント**: 3〜5つの競合アカウントを収集して比較
3. **再生数**: 動画投稿が多い場合のみ取得（時間がかかるため）

### 分析のポイント

1. **いいね数の違い**: 自分と競合でどのくらい差があるか
2. **キャプション文字数**: 最適な文字数範囲を探る
3. **ハッシュタグ数**: 効果的なタグ数を特定
4. **投稿時間帯**: エンゲージメントが高い時間帯を発見

### ChatGPTでの分析

生成されたプロンプトに加えて、以下も伝えると良いでしょう：

- 自分の目標（フォロワー増加、エンゲージメント向上など）
- 特に知りたいこと（キャプションの書き方、タグ選びなど）
- 業界やジャンル（ファッション、ビジネス、ライフスタイルなど）

## ⚠️ よくある問題

### Graph APIエラー

**問題**: 「投稿が見つかりませんでした」

**解決方法**:
- アクセストークンが有効か確認
- ビジネスアカウントIDが正しいか確認
- ビジネスアカウントに切り替えているか確認

### Instaloaderエラー

**問題**: 「ログインエラー」または「アカウントが見つかりません」

**解決方法**:
- ログイン情報が正しいか確認
- 2要素認証が有効な場合は、アプリパスワードを使用
- アカウント名に@が含まれていないか確認

### Seleniumエラー

**問題**: 「ChromeDriverが見つかりません」

**解決方法**:
- Chromeブラウザがインストールされているか確認
- `webdriver-manager`が正しくインストールされているか確認

- [会話内容整理](会話内容整理.md): ツールの設計思想と要件

---

## 🛰️ 深層対話：データが語る「勝者の沈黙」と「敗者の饒舌」

**テーマ**: 分析ツールを単なる「集計機」から「戦略の羅針盤」へ昇華させる

**参加者**:
*   **Dev**: Pythonエンジニア。データ取得の「正確性」と「網羅性」を追求。
*   **Marketer**: 戦略家。データの裏にある「ユーザー心理」と「市場動向」を読み解く。
*   **Analyst**: データサイエンティスト。統計的有意性と「異常値」に価値を見出す。
*   **Unico (PM)**: プロジェクト全体を俯瞰し、ビジネス成果への直結を管理。

---

### 第1章：なぜ「平均値」だけでは勝てないのか？

**Analyst**: 
多くのユーザーは `ステップ4: データ分析` で生成されたグラフを見て、「平均いいね数はこれくらいか」と納得して終わってしまいます。しかし、それは死に至る病です。

**Marketer**: 
手厳しいですね。でも、その通りです。Instagramにおいて「平均」は実在しません。あるのは「バズった投稿」と「それ以外」の二極化です。平均値は、その二つの乖離を埋めるだけの無意味な数字になりがちです。

**Dev**: 
技術的にも、箱ひげ図（Box Plot）をデフォルトで実装したのはそのためです。中央値と外れ値（バズ）を一目で区別できるように。

**Unico**: 
ここでは、**「異常値（Outlier）」こそが最大の教師である**と定義しましょう。ステップ4でやるべきは、平均を見ることではなく、なぜその1投稿だけが右上に突き抜けているのか、その「理由（変数）」を探ることです。

### 第2章：キャプション文字数の「黄金比」という幻想

**Marketer**: 
`活用のコツ` に「最適な文字数範囲を探る」とありますが、これも罠ですよね。

**Analyst**: 
はい。データを見ると「文字数が多いから伸びる」のではなく、「伝えたい情報量に対して適切な密度があるか」が重要です。あるジャンルでは短文がバズり、あるジャンルでは長文（ミニブログ形式）が保存数を稼ぎます。

**Dev**: 
だからこそ、このツールでは「いいね数とキャプション文字数の相関」を散布図で出せるようにしています。特定の文字数帯にバズが集中していれば、それがそのジャンルの「戦いの型」だとわかります。

**Unico**: 
**【戦略1】 データは「答え」ではなく「仮説」を立てるために使え。**
「500文字が正解だ」と決めるのではなく、「なぜ競合Aは300文字で、競合Bは1000文字で勝っているのか？」という問いを立てるのが、このツールの正しい `USAGE` です。

### 第3章：ChatGPTを「魔法の杖」から「部下」に変える方法

**Analyst**: 
`ステップ6: ChatGPTで分析` ですが、ここが一番重要です。AIにデータを投げる際、単に「分析して」と言うだけでは、AIは「丁寧な要約」しかしてくれません。

**Marketer**: 
そう。AIに「あなたの強み」と「競合の弱み」を対比させる必要があります。

**Dev**: 
プロンプト生成機能には、そのための構成を組み込んでいます。
1.  **データ構造の明示**: LLMがカラムの意味を誤認しないように。
2.  **対比構造の要請**: 自分と競合の決定的な差を抽出させる。
3.  **アクションプランの出力**: 「明日から何をするか」まで踏み込ませる。

**Unico**: 
**【戦略2】 AI分析は「批判的（Critical）」に行わせろ。**
「褒めなくていいから、このデータから見える私の敗因を3つ挙げろ」と指示するくらいが丁度いい。

### 第4章：未来のアップデート：静的な分析から「動的な予知」へ

**Dev**: 
現在は過去のデータを集計するツールですが、今後は `2025-12-22-インスタ動画解析結果` などのリサーチ結果も自動で読み込み、最新のトレンドと照らし合わせる機能も検討しています。

**Marketer**: 
いいですね。例えば「今、リールのBGMはこのトレンドが来ているから、過去のあなたのバズ投稿のテーマでこれを使えば再現性が高い」という予測まで。

**Analyst**: 
それこそが、単なる「ツール」が「脳（Agent）」になる瞬間ですね。

---

## 関連リンク
- [[TOOL_DESCRIPTION]]
- [[会話内容整理]]
- [[技術資産__インスタ分析ツール]]
- [[2025-12-22-インスタ動画解析結果]]
- [[2025-12-15-ツール作成アイデア]]
- [[2026-01-09_SNS運用代行_知識統合バイブル_深層対話]]
- [[在宅ワーク考察]]
- [[00 Rules]]






```

---

## ツール説明書.md

```markdown
---
tags: [manual, tool/instagram, python, marketing]
date: 2026-01-16
source: Building_AI_Sales_Prototypes
---

# Instagram競合・過去投稿調査分析ツール - 完全ガイド

Tags: #Instagram #Python #マーケティング戦略 #競合分析 #データドリブン #Zettelkasten #自動化
Links: [[00_知識マップ]] [[README]] [[USAGE]] [[会話内容整理]] [[技術資産__インスタ分析ツール]] [[2025-12-22-インスタ動画解析結果]] [[2026-01-13_ツール開発・改善知見バイブル_深層対話]] [[在宅ワーク考察]]

---

## 📖 ツール概要

### ツールの目的

Instagramの投稿を続けているが、**伸びている投稿と伸びない投稿の違いが分析できていない**という問題を解決するためのツールです。

- キャプションの違いなのか？
- タグの違いなのか？
- 投稿テーマの違いなのか？

これらの疑問をデータで明確にし、改善のヒントを見つけることができます。

### ターゲットユーザー

- Instagram運用初心者〜中級者
- 毎日投稿しているが伸び悩んでいる人
- 投稿構成の最適化がわからず手探りの人
- リサーチが苦手で、何が原因で伸びないのかわからない人
- コンテンツクリエイター
- 運用代行者
- 副業でInstagramを活用している人

### ツールの特徴

✅ **データ収集に特化**: ありとあらゆるデータを自動収集  
✅ **AI非搭載**: 開発コストを抑え、ChatGPTなど外部AIと連携  
✅ **簡単操作**: Streamlitの直感的なUIで誰でも使える  
✅ **包括的分析**: 自分と競合の違いを徹底的に比較  

---

## 🎯 解決できる課題

### 課題1: 何が原因で伸びないのかわからない

**解決方法**:
- 投稿データを自動収集し、数値で見える化
- いいね数、コメント数、保存数、キャプション文字数、ハッシュタグ数など、あらゆる指標を収集
- 自分と競合のデータを比較して、差が出ている要素を特定

### 課題2: リサーチが苦手で分析できない

**解決方法**:
- データ収集を自動化（手動で調べる必要なし）
- ChatGPT用のプロンプトテンプレートを自動生成
- CSVデータをChatGPTに貼り付けるだけで詳細分析が可能

### 課題3: 競合の成功パターンがわからない

**解決方法**:
- 競合アカウントの投稿を自動収集
- バズっている投稿の構成要素（キャプション、タグ、時間帯など）を抽出
- 自分との違いを可視化して、真似できるポイントを発見

---

## 🛠️ 主要機能

### 1. 自分の投稿収集機能

#### 機能概要
Instagram Graph APIを使用して、自分の投稿データを安全かつ正確に収集します。

#### 収集できるデータ
| データ項目 | 説明 | 用途 |
|---------|------|------|
| 投稿日時 | 投稿した日付と時刻 | 時間帯分析、曜日分析 |
| いいね数 | 投稿に付けられたいいねの数 | エンゲージメント指標 |
| コメント数 | コメントの数 | エンゲージメント指標 |
| 保存数 | 投稿を保存した人数 | エンゲージメント指標 |
| リーチ数 | 投稿を見た人数 | リーチ分析 |
| インプレッション数 | 投稿が表示された回数 | 露出分析 |
| キャプション | 投稿のキャプション全文 | 文章分析、構成分析 |
| ハッシュタグ | 使用したハッシュタグ | タグ戦略分析 |
| メディアタイプ | 写真 or 動画 | メディアタイプ別分析 |
| 投稿URL | 投稿へのリンク | 参照用 |

#### 使用方法
1. 「📥 データ収集」メニューを選択
2. 「自分の投稿」タブを開く
3. 取得する投稿数を指定（1〜500件）
4. 「自分の投稿を収集」ボタンをクリック

#### 必要な設定
- Instagram Graph APIのアクセストークン
- ビジネスアカウントID
- Instagramビジネスアカウント（必須）

#### メリット
- ✅ 公式APIを使用するため安全
- ✅ 正確なデータを取得可能
- ✅ インサイトデータ（保存数など）も取得可能
- ✅ アカウントBANのリスクなし

---

### 2. 競合アカウント分析機能

#### 機能概要
Instaloaderを使用して、競合アカウントの投稿データを収集・分析します。

#### 収集方法

**方法1: アカウント名で収集**
- アカウント名（@なし）を入力
- 指定した数の投稿を遡って収集
- 複数のアカウントを収集可能（データは累積）

**方法2: 投稿URLで収集**
- 特定の投稿URLを入力
- その投稿1件のデータを収集
- 気になる投稿を個別に分析可能

#### 収集できるデータ
| データ項目 | 説明 | 備考 |
|---------|------|------|
| 投稿日時 | 投稿した日付と時刻 | - |
| いいね数 | 投稿に付けられたいいねの数 | ログイン必要 |
| コメント数 | コメントの数 | - |
| キャプション | 投稿のキャプション全文 | - |
| ハッシュタグ | 使用したハッシュタグ | キャプションから自動抽出 |
| メディアタイプ | 写真 or 動画 | - |
| 投稿URL | 投稿へのリンク | - |

#### 使用方法
1. 「📥 データ収集」メニューを選択
2. 「競合アカウント」タブを開く
3. 収集方法を選択（アカウント名 or 投稿URL）
4. 情報を入力して「収集」ボタンをクリック

#### 注意事項
- ⚠️ 非公式スクレイピングのため、利用規約に注意
- ⚠️ 適切な遅延（デフォルト60秒）を設定して使用
- ⚠️ 大量取得はアカウントBANのリスクあり
- ⚠️ 非公開アカウントはフォローが必要

#### 活用のコツ
- 3〜5つの競合アカウントを収集して比較
- バズっている投稿が多いアカウントを選ぶ
- 自分のアカウントと似たジャンルのアカウントを選ぶ

---

### 3. 再生数取得機能（オプション）

#### 機能概要
Seleniumを使用して、動画投稿の再生数をスクリーンショットで取得します。

#### 取得方法
1. Instagramにログイン
2. 投稿ページにアクセス
3. 再生数が表示されている画面をスクリーンショット
4. OCRで再生数を抽出（実験的機能）

#### 使用方法
1. 競合アカウントの投稿を収集（動画投稿が含まれていること）
2. 「再生数取得」タブを開く
3. 「再生数を取得」ボタンをクリック

#### 注意事項
- ⚠️ 時間がかかります（1投稿あたり約10秒）
- ⚠️ Chromeブラウザが必要
- ⚠️ ログイン情報が必要
- ⚠️ 動画投稿のみが対象

#### 活用のコツ
- 動画投稿が多い場合のみ使用
- 重要な投稿だけに絞って取得
- スクリーンショットは手動で確認も可能

---

### 4. データ分析機能

#### 機能概要
収集したデータを可視化し、自分と競合の違いをグラフで比較します。

#### 生成されるグラフ

**1. いいね数の比較（箱ひげ図）**
- 自分と競合のいいね数の分布を比較
- 中央値、四分位数、外れ値を可視化
- どのくらい差があるかを一目で把握

**2. キャプション文字数の比較**
- キャプションの長さの違いを比較
- 最適な文字数範囲を探る
- バズった投稿の文字数傾向を発見

**3. ハッシュタグ数の比較**
- 使用しているハッシュタグの数の違いを比較
- 効果的なタグ数を特定
- タグ戦略の違いを可視化

**4. 投稿時間帯の分布**
- いつ投稿しているかの違いを比較
- 効果的な投稿時間帯を発見
- エンゲージメントが高い時間帯を特定

**5. いいね数とキャプション文字数の相関**
- キャプションの長さといいね数の関係を可視化
- 最適な文字数範囲を発見
- 相関関係を確認

#### 基本統計情報
- 各指標の平均値、中央値、最大値、最小値
- 投稿タイプ別の件数
- キャプション文字数の統計
- ハッシュタグ数の統計

#### 使用方法
1. データを収集（自分の投稿 or 競合投稿）
2. 「📊 データ分析」メニューを選択
3. データ概要と基本統計を確認
4. 「グラフを生成」ボタンをクリック

---

### 5. データ出力機能

#### 機能概要
収集・分析したデータをCSVまたはExcel形式でエクスポートします。

#### 出力形式

**CSV形式**
- すべてのデータを1つのファイルに
- 文字コード: UTF-8 with BOM（Excelで開きやすい）
- 自分と競合のデータが混在

**Excel形式（複数シート）**
- 自分の投稿と競合投稿を別シートに
- 比較しやすい形式
- 複数の競合アカウントも別シートに

#### 出力されるデータ項目
- 投稿タイプ（自分/競合）
- 投稿日時
- いいね数
- コメント数
- 保存数
- リーチ数
- インプレッション数
- 再生数（動画の場合）
- キャプション
- ハッシュタグ
- 投稿時間帯
- 曜日
- メディアタイプ
- 投稿URL

#### 使用方法
1. データを収集・分析
2. 「💾 データ出力」メニューを選択
3. 出力形式を選択（CSV or Excel）
4. 「エクスポート」ボタンをクリック
5. 「ダウンロード」ボタンでファイルを保存

---

### 6. ChatGPT用プロンプト生成機能

#### 機能概要
ChatGPTなどで分析するためのプロンプトテンプレートを自動生成します。

#### 分析タイプ

**1. 総合分析（comprehensive）**
- すべての要素を包括的に分析
- バズった投稿と伸びなかった投稿の違い
- 自分と競合の比較
- 具体的な改善提案

**2. キャプション分析（caption）**
- キャプションに特化した分析
- 文字数の最適範囲
- 構成パターン（導入、本文、締め）
- 絵文字の使い方
- 共感を呼ぶフレーズ

**3. ハッシュタグ分析（hashtag）**
- ハッシュタグ戦略に特化
- タグ数の最適範囲
- 効果的なタグの種類
- タグとエンゲージメントの相関

**4. 投稿タイミング分析（timing）**
- 投稿時間に特化
- 効果的な投稿時間帯
- 曜日の効果
- 投稿頻度の影響

#### 生成されるプロンプトの内容
1. 分析してほしいポイントの説明
2. データの説明
3. CSVデータを貼り付ける場所
4. 分析結果の出力形式の指定

#### 使用方法
1. データを収集
2. 「📝 プロンプト生成」メニューを選択
3. 分析タイプを選択
4. 「プロンプトを生成」ボタンをクリック
5. 生成されたプロンプトをコピー
6. ChatGPTに貼り付けて、CSVデータも一緒に送信

#### 活用のコツ
- まず総合分析で全体像を把握
- 気になる要素があれば、そのタイプの分析も実行
- プロンプトに自分の目標や業界情報も追加すると良い

---

## 📊 データ収集項目の詳細

### 全データ項目一覧

| カテゴリ | データ項目 | 取得元 | 説明 |
|---------|----------|--------|------|
| **基本情報** | 投稿タイプ | 自動 | 自分 or 競合 |
| | 投稿日時 | API/スクレイピング | 投稿した日時 |
| | 投稿日 | 自動抽出 | 日付のみ |
| | 投稿時間帯 | 自動抽出 | 時刻のみ（HH:MM） |
| | 曜日 | 自動抽出 | 月曜日、火曜日など |
| **エンゲージメント** | いいね数 | API/スクレイピング | いいねの数 |
| | コメント数 | API/スクレイピング | コメントの数 |
| | 保存数 | Graph API | 保存した人数 |
| | リーチ数 | Graph API | 投稿を見た人数 |
| | インプレッション数 | Graph API | 表示された回数 |
| | 再生数 | Selenium | 動画の再生数（オプション） |
| **コンテンツ** | キャプション | API/スクレイピング | キャプション全文 |
| | ハッシュタグ | 自動抽出 | ハッシュタグ一覧 |
| | メディアタイプ | API/スクレイピング | 写真 or 動画 |
| **参照** | 投稿URL | API/スクレイピング | 投稿へのリンク |
| | メディアID | API/スクレイピング | メディアのID |

### データの活用方法

**1. エンゲージメント分析**
- いいね数、コメント数、保存数の相関を分析
- どの指標が最も重要かを特定
- エンゲージメント率を計算

**2. コンテンツ分析**
- キャプション文字数とエンゲージメントの関係
- ハッシュタグ数とエンゲージメントの関係
- メディアタイプ（写真/動画）の効果

**3. タイミング分析**
- 投稿時間帯とエンゲージメントの関係
- 曜日とエンゲージメントの関係
- 最適な投稿スケジュールを発見

**4. 競合比較**
- 自分と競合の各指標を比較
- 差が出ている要素を特定
- 真似できる成功パターンを発見

---

## 🎓 活用シナリオ

### シナリオ1: 自分の投稿が伸びない原因を特定したい

**ステップ**:
1. 自分の投稿を50件以上収集
2. 競合アカウント3〜5つを収集
3. データ分析でグラフを生成
4. 自分と競合の違いを確認
5. ChatGPTで総合分析を実行
6. 改善ポイントを特定

**期待できる結果**:
- キャプション文字数が少ないことが判明
- ハッシュタグの使い方が違うことが判明
- 投稿時間帯が効果的でないことが判明

### シナリオ2: バズる投稿のパターンを発見したい

**ステップ**:
1. 競合アカウントのバズっている投稿を収集
2. 自分の投稿も収集
3. いいね数でソートして、バズった投稿を特定
4. バズった投稿の共通点を分析
5. ChatGPTでキャプション分析を実行

**期待できる結果**:
- バズった投稿のキャプション構成パターンを発見
- 効果的なハッシュタグの組み合わせを発見
- 最適な投稿時間帯を発見

### シナリオ3: 次の投稿の戦略を立てたい

**ステップ**:
1. 過去の投稿データを収集・分析
2. 競合の成功パターンを分析
3. ChatGPTで改善提案を取得
4. 次の投稿で試すべきことをリスト化

**期待できる結果**:
- 具体的な改善アクションが明確になる
- 試すべきキャプション構成がわかる
- 効果的なハッシュタグセットがわかる

---

## 💡 ベストプラクティス

### データ収集のコツ

1. **自分の投稿**: できるだけ多くの投稿を収集（50件以上推奨）
   - データが多いほど、傾向が見えやすくなる
   - 季節や時期による変動も分析可能

2. **競合アカウント**: 3〜5つのアカウントを収集
   - 似たジャンルのアカウントを選ぶ
   - バズっている投稿が多いアカウントを選ぶ
   - 自分の目標とするアカウントを選ぶ

3. **再生数取得**: 動画投稿が多い場合のみ使用
   - 時間がかかるため、重要な投稿だけに絞る
   - スクリーンショットは手動で確認も可能

### 分析のコツ

1. **まず全体像を把握**
   - 基本統計を確認
   - グラフで視覚的に比較
   - 差が出ている要素を特定

2. **ChatGPTで深掘り**
   - 総合分析で全体像を把握
   - 気になる要素があれば、そのタイプの分析も実行
   - 自分の目標や業界情報も追加

3. **継続的に改善**
   - 定期的にデータを収集
   - 改善を試した結果を追跡
   - 成功パターンを蓄積

### ChatGPTでの分析のコツ

1. **プロンプトに追加情報を加える**
   - 自分の目標（フォロワー増加、エンゲージメント向上など）
   - 特に知りたいこと（キャプションの書き方、タグ選びなど）
   - 業界やジャンル（ファッション、ビジネス、ライフスタイルなど）

2. **複数の分析タイプを試す**
   - 総合分析で全体像を把握
   - キャプション分析で文章力を向上
   - ハッシュタグ分析でタグ戦略を最適化
   - タイミング分析で投稿スケジュールを改善

3. **結果を実践に活かす**
   - 分析結果から具体的なアクションを抽出
   - 次の投稿で試す
   - 結果を追跡して改善

---

## ⚠️ 注意事項と制限

### 利用規約について

- **Graph API**: 公式APIのため安全に使用可能
- **Instaloader**: 非公式スクレイピングのため、利用規約に注意
  - 個人利用を推奨
  - 商用利用の場合は法的リスクを考慮
  - 適切な遅延を設定して使用

### 技術的制限

- **Graph API**: 自分の投稿のみ取得可能
- **Instaloader**: 非公開アカウントはフォローが必要
- **再生数取得**: 時間がかかる（1投稿あたり約10秒）
- **レート制限**: APIやスクレイピングには制限がある

### セキュリティ

- `.env`ファイルには機密情報が含まれるため、Gitにコミットしない
- パスワードは強力なものを使用
- 定期的にアクセストークンを更新

### データの正確性

- Graph APIのデータは正確
- Instaloaderのデータは概ね正確だが、Instagramの仕様変更の影響を受ける可能性
- 再生数はOCRで抽出するため、100%正確ではない可能性

---

## 🔮 今後の拡張予定

### バージョン2以降の機能

1. **Ollama等のローカルAI対応**
   - オフラインでも分析可能
   - 無料でAI分析が利用可能

2. **自動改善提案機能**
   - データから「次にバズる投稿案」を自動提案
   - 構成・タグ・キャプションの提案

3. **投稿ジャンル分類**
   - AIで「howto系・共感系・体験談系」など分類
   - ジャンル別の分析が可能

4. **定期収集機能**
   - スケジュール実行で自動収集
   - データの推移を追跡

---

## 📚 関連ドキュメント

- [会話内容整理](会話内容整理.md): ツールの設計思想と要件定義

---

## 🔱 深層対話：データドリブン・クリエイティビティの極意

**テーマ**: 「数字」という冷徹な鏡に、いかにして「情熱」を映し出すか

**参加者**:
*   **Strategist**: 市場の歪みを見つけ、勝機を最大化させる軍師。
*   **Implementer**: 泥臭い実行を重んじ、継続の仕組みを作る実務家。
*   **Risk Manager**: 冷静な視点でBANリスクや規約違反を未然に防ぐ守護。
*   **Psychologist**: データの裏にある「フォロワーの溜息」や「羨望」を嗅ぎ取る心理学者。

---

### 第1章：データの正体は「過去の亡霊」か、「未来の種」か

**Strategist**: 
この `ツール説明書` を手にした人は、きっとこう思っています。「このツールを使えば、簡単にバズる魔法が手に入る」と。

**Implementer**: 
残念ながら、そんな魔法はありません。このツールが提供するのは、あくまで「過去の事実」の集計ですからね。

**Psychologist**: 
しかし、事実は嘘をつきません。「なぜこの投稿が伸びたのか？」という問いに対し、人間は「運が良かった」とか「自分のセンスだ」とバイアスをかけますが、データは「文字数が多かった」「金曜日の21時だった」「ハッシュタグの選定が適切だった」という物理的な証拠を突きつけます。

**Risk Manager**: 
だからこそ、`注意事項と制限` にある「正確性」が重要なんです。Instaloaderで取得したデータも、Seleniumで撮った再生数も、それは一つの「証拠品」です。

**Strategist**: 
**【提言1】 分析とは「センスの言語化」である。**
センスが良いと言われる人は、無意識にバズる変数を調整しています。このツールは、その「無意識」を「意識（データ）」に引き上げるための装置です。

### 第2章：なぜ「競合比較」が戦略の8割を占めるのか

**Psychologist**: 
多くの運用者が、自分のインサイト（保存数など）だけを見て一喜一憂します。しかし、それは暗闇でボクシングをしているようなものです。

**Strategist**: 
その通り。Instagramは相対評価の世界です。フォロワーがあなたの投稿を見る前に、誰の投稿を見ていたか。そして、あなたの後に誰を見るか。

**Implementer**: 
`活用シナリオ1` にあるように、競合3〜5つと比較することで、初めて「自分に足りない色」が見えてきます。「競合は全員動画なのに、自分だけ静止画だった」という基本的なズレも、データで見れば一目瞭然です。

**Risk Manager**: 
ただし、競合分析（スクレイピング）にはBANリスクが伴います。`注意事項` を徹底し、適切な遅延を入れること。これは「勝つため」ではなく、「戦場に立ち続けるため」の必須条件です。

### 第3章：AI（ChatGPT）との「共創」という新しいクリエイティブ

**Implementer**: 
`主要機能6` のプロンプト生成機能。これは、単なる「効率化」ではなく、「専門性の拡張」ですよね。

**Strategist**: 
はい。1万件の投稿データを人間がエクセルで見ていても、脳が処理しきれません。しかし、ChatGPTに適切なプロンプト（指示書）を渡せば、コンマ数秒で「構成の共通項」を抽出してくれます。

**Psychologist**: 
AIに「このバズ投稿のキャプションには、どんな感情トリガー（Fear, Greed, Prideなど）が使われているか？」と聞く。これが `キャプション分析` の真髄です。

**Unico (PM)**: 
我々が目指すのは、「ツール」と「AI」と「人間」のトライアングルです。ツールがデータを集め、AIがパターンを見つけ、人間が「最後に魂を込める」。この分業体制こそが、2026年以降の生き残り戦略です。

### 第4章：エピローグ：分析の先にある「静かなる勝利」

**Strategist**: 
分析を極めると、投稿ボタンを押す前に「これはこれくらい伸びる」という予測がつくようになります。

**Implementer**: 
それが `今後の拡張予定` にある「自動改善提案機能」の目指すところですね。

**Unico**: 
このガイドを読み終えた時、あなたは単なる「投稿者（Poster）」から、市場を支配する「設計者（Architect）」へと進化しているはずです。

---

## 関連リンク
- [[USAGE]]
- [[会話内容整理]]
- [[技術資産__インスタ分析ツール]]
- [[2025-12-22-インスタ動画解析結果]]
- [[2025-12-17-ツール展開プラン]]
- [[2026-01-09_SNS運用代行_知識統合バイブル_深層対話]]
- [[2026-01-13_ツール開発・改善知見バイブル_深層対話]]
- [[00 Rules]]

---

## 📞 サポート

問題が発生した場合は、以下を確認してください：

1. セットアップガイドを確認
2. エラーメッセージを確認
3. 環境変数の設定を確認
4. 必要な権限が付与されているか確認

---

**このツールは個人利用を目的としています。商用利用の場合は適切な法的確認を行ってください。**





```

---

## 会話内容整理.md

```markdown
---
tags: [design, requirements, tool/instagram, python, ai_agent]
date: 2026-01-16
source: Building_AI_Sales_Prototypes
---

# Instagram競合・過去投稿調査分析ツール - 会話内容整理

Tags: #Instagram #Python #システム設計 #要件定義 #AIエージェント #Zettelkasten #開発プロセス
Links: [[00_知識マップ]] [[README]] [[USAGE]] [[ツール説明書]] [[技術資産__インスタ分析ツール]] [[2026-01-13_ツール開発・改善知見バイブル_深層対話]] [[2025-12-22-ニッチGPTs案]]

---

## 📋 プロジェクト概要

### 目的
Instagramの投稿を続けているが、伸びている投稿と伸びない投稿の違いが分析できていない問題を解決する。
- キャプションの違いなのか
- タグの違いなのか
- 投稿テーマの違いなのか

を明確にするツール。

### ターゲットユーザー
- Instagram運用初心者〜中級者
- 毎日投稿しているが伸び悩んでいる人
- 投稿構成の最適化がわからず手探りの人
- リサーチが苦手で、何の数字やどこが原因で伸びないのかわからない人

## 🎯 ツールの方向性

### 基本コンセプト
**「収集に特化し、分析はChatGPTなど外部AIに委ねる構成」**

- ツール自体はAI非搭載、またはOllamaなど無料のAIのみ
- 詳細な分析は出力結果をChatGPTなどAIに貼り付ければ良い形で出力
- データ収集と簡単な分析までをツールで行う

### なぜこの構成か
- 開発コストを抑えつつユーザー満足度が高い
- ユーザーの実際の悩みと一致（「何がバズるか分からない」→ 収集して見える化するだけで大きな価値）
- ChatGPTと併用しやすい（CSV＋プロンプトを貼るだけで詳細分析ができる）
- 段階的に機能追加しやすい（将来的に無料AI（Ollama）やLangchain連携でAI出力も可能）

## 🛠️ 機能要件

### 1. 自身の投稿分析・収集
**方法**: Instagram Graph API（公式API）
- 前提：Instagramビジネスアカウント ＋ Facebookアプリ連携が必要

**収集項目**:
- 投稿日時（時間帯分析用）
- キャプション全文（トーン・構成・絵文字使用率の分析）
- ハッシュタグ（タグの効果検証・頻度分析）
- いいね数・保存数・コメント数（エンゲージメント指標）
- メディアタイプ（写真/動画の傾向比較）
- 投稿時間帯（時間帯の効果検証用）
- 使用フィルター（可能なら）

### 2. 競合アカウントの投稿分析・収集
**方法**: Instaloader（非公式スクレイピング）
- アカウント指定 or 投稿URL指定で、その人の投稿を遡って分析
- ログインが必要（BANリスク対策として遅延を入れる）

**収集項目**:
- 投稿URL
- 投稿日・時刻
- キャプション全文
- ハッシュタグ
- いいね数（ログイン状態で取得可能）
- コメント数
- メディアタイプ（写真 or 動画識別）
- 再生数（動画の場合、後述の方法で取得）

**注意点**:
- 一度に大量取得するとBANリスクがあるため、1分1投稿などのディレイが必要
- 非公開アカウント以外は安定して取得可能

### 3. 再生数の取得
**方法**: Seleniumを使った自動スクリーンショット
- Instagramの投稿画面で再生数が表示されている部分を自動キャプチャ
- 画像OCRでCSV化も後から可能

**取得できる情報**:
- 投稿日時（画面に表示されている日付）
- キャプション、ハッシュタグ
- 再生数（リール or 動画）
- いいね数・コメント数

**注意点**:
- Instagramにログインした状態で使う必要がある
- Selenium操作中はIPブロックを防ぐために適切な遅延を入れるのが必須
- PCブラウザ上で動かす必要がある（スマホ画面は不可）

### 4. 簡易分析機能
- 平均いいね数、文字数、タグ数の相関をグラフで表示
- 自分 vs 競合で比較用グラフを作成
- PNG/CSV形式で出力

### 5. 出力形式
**CSV形式**:
- 自分と競合で別シートまたは別ファイルで出力
- 以下のカラム構成:
  - 投稿タイプ（自分/競合）
  - 投稿日時
  - いいね数
  - 保存数
  - コメント数
  - 再生数（動画の場合）
  - キャプション
  - ハッシュタグ
  - 投稿時間帯
  - メディアタイプ
  - 投稿URL

**ChatGPT用プロンプトテンプレート**:
- 「このCSVをChatGPTに貼れば分析できる」テンプレートを自動生成
- TXT形式で出力

## 📊 想定CSVフォーマット

```
投稿タイプ,投稿日時,いいね数,保存数,コメント数,再生数,キャプション,ハッシュタグ,投稿時間帯,メディアタイプ,投稿URL
自分,2024-12-01 19:00,123,45,10,,〇〇な毎日…,"#副業 #集客",19:00,写真,https://...
競合A,2024-11-30 21:00,340,112,25,5000,～,"#集客術",21:00,動画,https://...
```

## 🧠 ChatGPT分析テンプレート例

```
以下は私と競合のInstagram投稿データです。
キャプション、タグ、投稿時間、反応（いいね・保存）などをもとに、
私の投稿の伸び悩みの原因を分析してください。

---ここにCSV貼り付け---
```

## ⚠️ 開発時の注意点

### 法的・倫理的リスク（非公式スクレイピング）
- 利用規約違反になる可能性あり
- 商用販売する場合、スクレイピングベースは避ける or 非公開で使うべき
- **改善案**: 「自分の投稿だけ」ならAPI連携を推奨。競合データは、ユーザーにURL貼ってもらい、その投稿1件だけ収集するようにする（セーフゾーン）

### API利用のハードル
- Meta開発者登録が面倒
- トークン管理やリフレッシュの仕組みが必要
- **改善案**: ツール内で「Meta API連携セットアップガイド」を付属。ノーコード化（Streamlit＋設定ファイル）すれば、エンジニアでなくても扱いやすくなる

### 自動分析の難易度
- 感情分析や構成の分類などは、簡易的な集計だけでは限界がある
- **改善案**: 「ChatGPTにCSVを貼れば分析してくれるプロンプト」をツール内に用意（人間の知能で補う）。将来的にOllama（ローカルLLM）連携で無料AI対応も検討

## 🔮 今後のアップグレード候補（Ver.2以降）

- Ollama等のローカルAI対応（オフラインでも分析できる無料AI連携）
- データから「次にバズる投稿案」自動提案（AIによるネクスト戦略提案：構成・タグ）
- 投稿ジャンル分類（AIで「howto系・共感系・体験談系」など分類可視化）

## 💡 利用シナリオ

1. ツールで「自分と競合の投稿データを収集」
2. 自動で「キャプション傾向・タグ・時間帯・構成の違い」をグラフに出力
3. ChatGPTにCSVとテンプレを貼って、「伸びる投稿を真似するヒント」を得る
4. 次の投稿で改善を試す

## 🎯 技術スタック

- **言語**: Python
- **API連携**: Instagram Graph API（自分の投稿）
- **スクレイピング**: Instaloader（競合投稿）
- **自動化**: Selenium（再生数取得）
- **データ処理**: pandas
- **可視化**: matplotlib
- **UI**: Streamlit（推奨）

- **UI**: Streamlit（推奨）

---

## 🏗️ 深層対話：バズを「設計」するアーキテクチャの真髄

**テーマ**: ツールを「命令」から「対話」へ、そして「自律（Autonomous）」へ

**参加者**:
*   **Architect**: システムの根幹を設計する構造思想家。美しく堅牢な設計を志向。
*   **UX Designer**: ユーザーの「感情」と「操作感」を設計する体験の魔術師。
*   **AI Specialist**: LLMの出力品質と「知能」の統合を担当する技術者。
*   **PM (Product Manager)**: 「今、何を作るべきか」を決定し、市場価値を担保する。

---

### 第1章：なぜ「収集」と「分析」を分離したのか

**Architect**: 
このツールの設計思想において最も議論を呼んだのが、`基本コンセプト` にある「収集に特化し、分析は外部に委ねる」という点でしたね。

**UX Designer**: 
最初は「AIに全自動でアドバイスまでさせてほしい」という意見もありました。でも、あえてそれを切り離した。

**PM**: 
理由は明確です。当時のAI開発速度は凄まじく、ツールの中に固いロジックを組み込むと、すぐに陳腐化するからです。ChatGPT側（GPT-4oなど）の進化を最大限に活かすには、**「最高品質のデータを、最高に貼り付けやすい形式（CSV）で渡す」**ことこそが最大のユーザー体験（UX）だと判断しました。

**Architect**: 
**【設計原則1】 変動の激しい「知能（AI）」と、普遍的な「事実（データ）」を疎結合にせよ。**
これにより、ユーザーは自分のお気に入りのAI（Claude, Gemini, ChatGPT等）を自由に選んで分析できるようになりました。

### 第2章：スクレイピングという「刃（やいば）」の扱い方

**AI Specialist**: 
`競合アカウントの収集` で Instaloader を採用した点は、BANリスクとの戦いでもありましたね。

**UX Designer**: 
ユーザーに「ログインが必要ですよ」「1分1投稿のディレイが入りますよ」と正直に伝える。この `注意点` の明記は、一見不便に見えますが、実は「プロの道具」としての信頼感に繋がっています。

**Architect**: 
技術的な妥協ではありません。Instagramという巨大なエコシステムの中で生き残るための「生存戦略」です。

**PM**: 
**【設計原則2】 速度よりも「生存」を優先せよ。**
一気に1000件収集してアカウントが飛ぶより、10件を確実に、毎日記録し続けること。それが `2025-12-15-ツール作成アイデア` で語られた「継続的な収益化」の基盤です。

### 第3章：「再生数」というブラックボックスへの挑戦

**Architect**: 
`再生数の取得` で Selenium を使った自動キャプチャと OCR を提案したのは、APIでは取得できない「生の市場反応」を掴むためでした。

**AI Specialist**: 
画像OCRはまだ発展途上ですが、将来的には `Ver.2以降` の「ジャンル分類」と組み合わせることで、「このサムネイルのデザインなら、再生数が伸びやすい」という視覚的トレンドの数値化が可能になります。

**PM**: 
これが `2025-12-22-インスタ動画解析結果` で発見された「視覚的フック」の正体を暴くための武器になります。

### 第4章：エピローグ：ツールは「脳」の鏡である

**Architect**: 
結局、この `会話内容整理` を通じて我々が作り上げたのは、単なるPythonスクリプトではありません。

**AI Specialist**: 
使い手の「問い（問いの解像度）」を映し出す、鏡のようなインターフェースですね。

**PM**: 
このツールを使い込み、CSVデータを毎日眺めているユーザーは、やがてツールを使わなくても「バズの法則」を脳内でシミュレートできるようになります。ツールはその修行をサポートするための**「補助脳」**なんです。

**UX Designer**: 
その時、この `会話内容整理` の冒頭に書かれた「目的」は、単なる問題解決を超えて、「ビジネスプロデューサーの育成」へと昇華されているでしょう。

---

## 関連リンク
- [[USAGE]]
- [[ツール説明書]]
- [[技術資産__インスタ分析ツール]]
- [[2026-01-13_ツール開発・改善知見バイブル_深層対話]]
- [[2025-12-22-ニッチGPTs案]]
- [[2025-12-15-ツール作成アイデア]]
- [[SNS運用代行・知識統合バイブル【深層対話録】]]
- [[在宅ワーク考察]]
- [[00 Rules]]






```

---

