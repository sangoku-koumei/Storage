import streamlit as st

# KEYWORDS: [Automation_Hub, Dashboard, Multi-Tool, Strategy_Integration]
# DESCRIPTION: ユニコ脳自動化スイートの総合ダッシュボード。各ツールへの入り口であり、帝国の自動化資産を一括管理する中心地。

st.set_page_config(
    page_title="Unico Brain Automation Suite",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 ユニコの脳みそ Automation Suite")
st.markdown("""
# Welcome to the Automation Hub

「00」フォルダの知識と戦略をコード化した、最強の自動化ツール群です。
左側のサイドバーからツールを選択してください。

## 🛠 収録ツール一覧

### 📊 リサーチ・戦略
- **01 全コンテンツ競合リサーチ (Naked Strategy)**: YouTube、SNS、ココナラの競合を丸裸にする分析ツール。
- **07 自動鑑定書・商品作成 (Fortune Product Forge)**: マルチエージェント会議で「売れる占い商品」を自動生成。

### ✍️ コンテンツ制作
- **02 投稿作成ツール**: リサーチ結果に基づき、インフルエンサー的な投稿（Instagram/Note）を作成。
- **05 画像自動生成**: DALL-E 3を用いた高クオリティなサムネイル生成。

### 🤖 自動化・運用
- **03 自動投稿ツール (Instagram)**: Instagramへの投稿を自動化（API連携）。
- **04 自動コメント返信**: ファン化を促進する神対応レスポンス生成。
- **06 画像自動リネーム**: 乱雑な画像ファイルを整理・リネーム。

> [!TIP]
> **Phantom Note Genesis (Note専用ツール)** は、専用フォルダ `Phantom_Note_Genesis_Suite` へ統合・独立しました。
""")


st.markdown("---")
with st.expander("📖 詳しい使い方はこちら（クリックして開く）"):
    st.markdown("""
    ### 🔰 はじめの一歩
    1. 画面左上の **">"** アイコンをクリックして、サイドバーメニューを開きます。
    2. 使いたいツールを選択してください（例：`01 Competitor Research`）。
    
    ### 🔑 必要なもの
    各ツールの実行には **APIキー** が必要です。
    - **OpenAI API Key**: ChatGPT連携用。これがないとAIが喋りません。
    - **YouTube Data API Key**: YouTubeリサーチ用。
    
    APIキーは各ツールのサイドバーにある入力欄に入れてください。
    
    ### 困ったときは？
    同封の `README.md` を読むか、開発者（AI）にチャットで聞いてください。

