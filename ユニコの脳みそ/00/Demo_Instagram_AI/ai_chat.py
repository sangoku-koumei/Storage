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
