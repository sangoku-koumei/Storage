
PROPOSAL_TEMPLATES = {
    "default": """
【提案文】
はじめまして。{name}と申します。

募集要項を拝見し、{genre}ジャンルにおける貴社のプロジェクトに大変魅力を感じ、応募いたしました。
私は現在、AIを活用した高度なリサーチ業務を専門としており、特に「質の高い情報収集」と「独自の切り口」による提案を得意としています。

【私の強み】
1. **スピードと質の並立**: 独自のリサーチAIツールを活用し、通常の3倍のスピードで深堀りした情報を提供可能です。
2. **多角的な視点**: 競合分析、口コミ分析、隠れたニーズの発掘など、多角的な視点からリサーチを行います。
3. **継続的な改善**: 納品後もフィードバックを元に、より貴社のターゲットに刺さるリサーチへとチューニングいたします。

【提案内容】
今回、{genre}に関するリサーチに加え、以下の付加価値を提供させていただきます。
- 競合チャンネル/競合サービスの上位3社の徹底分析レポート
- ターゲット層の潜在ニーズ（サイコグラフィック）分析
- 次回の企画出しに使えるプロンプト/キーワード集

【稼働可能時間】
週{hours}時間程度

まずはトライアルとして、1本リサーチをさせていただければ幸いです。
貴社の事業拡大に貢献できることを楽しみにしております。

よろしくお願いいたします。
"""
}

RESEARCH_PROMPTS = {
    "competitor": """
あなたはプロのマーケットリサーチャーです。
以下のジャンルにおける競合上位3社（またはチャンネル）を分析してください。

【ジャンル】
{genre}

【分析項目】
1. **ターゲット層の属性**: 年齢、性別、悩み、価値観
2. **強み・差別化ポイント**: なぜ顧客に選ばれているのか？
3. **弱み・改善点**: 顧客が不満に思っているポイント（口コミなどから推測）
4. **オファー内容**: 商品構成、価格帯、特典
5. **デザイン・世界観**: 配色、フォント、使用画像の傾向

出力はマークダウン形式の表でまとめてください。
""",
    "review": """
あなたはユーザー心理を読み解くプロのサイコロジストです。
以下の商品・サービスに対する「口コミ/レビュー」を分析し、潜在的なニーズと言語化されていない不満を洗い出してください。

【対象】
{target}

【分析ステップ】
1. ポジティブな意見から「ユーザーが真に求めていた価値」を特定する。
2. ネガティブな意見から「ユーザーが許せなかったポイント（地雷）」を特定する。
3. 上記を踏まえ、このターゲットに刺さる「キラーワード」を10個提案してください。
""",
    "idea": """
あなたは売れる企画を生み出す敏腕プロデューサーです。
現在、以下のジャンルで新しいコンテンツ（動画/記事/商品）を企画しています。

【ジャンル】
{genre}

競合がまだ手をつけていない、しかしターゲットが潜在的に求めている「穴場的な企画アイデア」を10個出してください。
それぞれのアイデアについて、以下の要素を記載してください。
- **タイトル案**: クリックしたくなる魅力的なタイトル
- **ターゲット**: 誰に向けたものか
- **お楽しみポイント**: ユーザーが得られるベネフィット（感情的価値）
"""
}

CHECKLIST_QUESTIONS = [
    {
        "id": "q1",
        "question": "Q1. そのリサーチは「客観的なデータ」に基づくものですか？（No=個人の感想や主観が必要な場合）",
        "good_answer": "yes"
    },
    {
        "id": "q2",
        "question": "Q2. 必要な情報はWeb上にテキストとして存在しますか？（No=足で稼ぐ現地調査や、非公開情報の取得が必要）",
        "good_answer": "yes"
    },
    {
        "id": "q3",
        "question": "Q3. リサーチ結果に「正解」はありますか、あるいは「ファクト」が重視されますか？（No=芸術的なセンスや、完全にオリジナルの創作が必要）",
        "good_answer": "yes"
    }
]

SOP_TEMPLATES = {
    "basic": """
# 基本リサーチ作業手順書 (SOP)

## 1. 目的
{task_name} に関する情報を収集し、クライアントが意思決定できる状態にする。

## 2. 準備するもの
- Webブラウザ (Chrome推奨)
- ChatGPT / Perplexity / Gemini などのAIツール
- スプレッドシート（納品用フォーマット）

## 3. 手順

### STEP 1: キーワード選定
1. 対象テーマに関連するキーワードを5〜10個リストアップする。
2. 「サジェストキーワード」や「関連語」も含める。

### STEP 2: AIによる予備調査
1. AIツールに以下のプロンプトを入力する。
   > 「{task_name}について、市場規模、主要なプレイヤー、現在のトレンドを教えてください。」
2. 出力された内容をざっと読み、全体像を把握する。

### STEP 3: 詳細リサーチ & 裏取り
1. STEP 2で出てきた固有名詞や数字について、Google検索で裏取りを行う。
2. 信頼できるソース（公式サイト、大手メディア、論文など）のURLを控える。
3. 情報が古い場合（3年以上前）は、最新情報を探し直す。

### STEP 4: まとめ & 品質チェック
1. 指定のフォーマットに情報を入力する。
2. **出典URLがリンク切れしていないか確認する。**
3. 誤字脱字がないか確認する。
4. 「個人の感想」ではなく「事実」に基づいているか最終確認する。

## 4. エラー対応
- 情報が見つからない場合は、無理に埋めず「情報なし」と記載し、その理由をメモする。
- 判断に迷う場合は、必ず管理者に相談する。
"""
}

HTML_REPORT_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - AI Research Report</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Helvetica+Neue:wght@300;400;700&family=Noto+Sans+JP:wght@300;400;700&display=swap');
        
        body {
            font-family: 'Helvetica Neue', 'Noto Sans JP', sans-serif;
            line-height: 1.8;
            color: #333;
            background-color: #f4f7f6;
            margin: 0;
            padding: 40px;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            background-color: #fff;
            padding: 60px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.05);
            border-radius: 8px;
        }
        
        header {
            border-bottom: 2px solid #eaeaea;
            padding-bottom: 20px;
            margin-bottom: 40px;
            text-align: center;
        }
        
        h1 {
            font-size: 28px;
            margin-bottom: 10px;
            color: #2c3e50;
        }
        
        .meta {
            font-size: 14px;
            color: #7f8c8d;
        }
        
        h2 {
            font-size: 22px;
            color: #2980b9;
            border-left: 5px solid #2980b9;
            padding-left: 15px;
            margin-top: 40px;
            margin-bottom: 20px;
        }
        
        h3 {
            font-size: 18px;
            color: #34495e;
            margin-top: 30px;
        }
        
        p {
            margin-bottom: 20px;
            text-align: justify;
        }
        
        ul, ol {
            margin-bottom: 20px;
            padding-left: 20px;
        }
        
        li {
            margin-bottom: 10px;
        }
        
        .box {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
        }
        
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        
        th {
            background-color: #f2f2f2;
            color: #333;
        }
        
        .footer {
            margin-top: 60px;
            padding-top: 20px;
            border-top: 1px solid #eaeaea;
            text-align: center;
            font-size: 12px;
            color: #aaa;
        }
        
        .highlight {
            background-color: #fff3cd;
            padding: 2px 5px;
            border-radius: 3px;
        }
        
        a {
            color: #3498db;
            text-decoration: none;
        }
        
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{{ title }}</h1>
            <div class="meta">Generated by Research Business Tool AI | {{ generated_date }}</div>
        </header>
        
        <section class="summary">
            <h2>Search Summary</h2>
            <div class="box">
                {{ ai_analysis | replace('\n', '<br>') | safe }}
            </div>
        </section>
        
        <section class="sources">
            <h2>Source References</h2>
            <p>The following top search results were analyzed:</p>
            <ul>
            {% for result in search_results %}
                <li>
                    <strong><a href="{{ result.href }}" target="_blank">{{ result.title }}</a></strong>
                    <br>
                    <span style="font-size: 0.9em; color: #666;">{{ result.body[:150] }}...</span>
                </li>
            {% endfor %}
            </ul>
        </section>
        
        <div class="footer">
            CONFIDENTIAL - Internal Use Only <br>
            Powered by OpenAI & DuckDuckGo
        </div>
    </div>
</body>
</html>
"""
