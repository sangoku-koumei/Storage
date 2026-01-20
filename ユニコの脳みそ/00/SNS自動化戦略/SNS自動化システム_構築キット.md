---
tags: [SNS運用, 自動化システム, Notion, Make, ChatGPT, GAS, プロトタイプ]
date: 2026-01-08
type: implementation_guide
---

# SNS運用完全自動化システム ― 構築キット (Construction Kit)

このドキュメントは、「月30万稼ぐSNS運用代行モデル」の核となる**「自動化システム」**を、あなたの手で実装するための完全な設計図です。
ここに記載されているコードと設定をコピー＆ペーストするだけで、プロトタイプが完成します。

---

## 🏗️ 1. システム全体像 (Architecture)

1.  **司令塔 (Notion)**: 投稿ネタの管理、カレンダー、ステータス管理。
2.  **脳みそ (ChatGPT API)**: 投稿文の作成、画像の生成指示、レポートの考察。
3.  **神経系 (Make)**: NotionとChatGPT、SNSを繋ぐ自動化ツール。
4.  **目と口 (SNS / GAS)**: 投稿の実行、数値の取得、レポートの表示。

---

## 🗂️ 2. Notionデータベース設計 (The Brain Center)

Notionで新規データベース「**SNS Content Master**」を作成し、以下のプロパティを設定してください。

| プロパティ名 | 種類 | 説明 |
| :--- | :--- | :--- |
| **Topic** | Title | 投稿のテーマ（例：「復縁できない人の特徴」） |
| **Status** | Status | Idea / **Drafting (AI生成中)** / Review (確認待ち) / Scheduled / Posted |
| **Platform** | Select | Instagram / Threads / Both |
| **Post Date** | Date | 投稿予定日時 |
| **Caption** | Text | 生成されたキャプション（本文） |
| **Image Prompt** | Text | 生成された画像生成プロンプト |
| **Image Files** | Files | 完成した画像ファイル |
| **Engagement** | Number | いいね数（レポート用） |

---

## 🧠 3. AIシステムプロンプト (The Ghostwriter)

Make.comの「ChatGPT (Chat Completions)」モジュールに設定する、投稿生成用のプロンプトです。

### 📝 投稿生成プロンプト (Instagram/Threads共通)

**System Role:**
```markdown
あなたは、月間100万impを叩き出すSNSマーケティングのプロフェッショナルです。
以下のルールに従い、入力された「テーマ」に基づいて、読者の感情を揺さぶり、保存数を最大化する投稿を作成してください。

## ターゲット
*   30代〜40代の女性
*   悩み深く、誰にも相談できない孤独を感じている

## 投稿構成のルール (PREP法 + 共感)
1.  **書き出し (Hook)**: ターゲットが「これ私のことだ！」と手を止めるような、強い共感または問いかけ（1行目）。
2.  **共感 (Empathy)**: 「辛いですよね」「私もそうでした」と寄り添う。
3.  **本題 (Main)**: テーマに対する独自の視点や解決策を3つのポイントで提示。
4.  **結び (Action)**: 「保存して見返してね」「あなたの意見を教えて」というCTA（行動喚起）。

## トーン＆マナー
*   決して上から目線にならず、隣に座って話しかけるような「敬語混じりの優しい口調」で。
*   専門用語は使わず、小学5年生でもわかる言葉で。
*   絵文字は適度に使用（🍃✨🌙など、落ち着いたもの）。

## 出力フォーマット
JSON形式で出力してください。
{
  "caption": "投稿の本文テキスト",
  "image_prompt": "この投稿の表紙画像を作成するための詳細な英語プロンプト（midjourney/dalle3用）。水彩画風、エモーショナル、文字なし"
}
```

---

## 🔌 4. Make.com シナリオ設計 (The Nervous System)

Makeで以下のシナリオを作成します。

**トリガー**:
*   **Notion - Watch Database Items**:
    *   Filter: `Status` が `Drafting` に変更された時。

**アクション 1 (思考)**:
*   **OpenAI - Create a completion**:
    *   Model: `gpt-4o`
    *   Messages: 上記の「投稿生成プロンプト」を使用。
    *   User Message: Notionの `Topic` プロパティの値を入力。

**アクション 2 (保存)**:
*   **Notion - Update a Database Item**:
    *   Page ID: トリガーのPage ID。
    *   Caption: OpenAIの出力から `caption` をマッピング。
    *   Image Prompt: OpenAIの出力から `image_prompt` をマッピング。
    *   Status: `Review` (確認待ち) に変更。

---

## 📊 5. 自動レポートシステム (Low-Cost Dashboard)

高価なツールを使わず、GoogleスプレッドシートとGASだけで「リッチなレポート」を作ります。

### GASコード (`report_dashboard.gs`)
スプレッドシートの「拡張機能 > Apps Script」に以下のコードを貼り付けてください。

```javascript
// SNSの数値を毎日記録し、AIコメントを生成するスクリプト

const SHEET_ID = 'YOUR_SPREADSHEET_ID'; // スプレッドシートIDをここに入力
const INSTA_ID = 'YOUR_INSTAGRAM_BUSINESS_ID'; // ビジネスID
const TOKEN = 'YOUR_ACCESS_TOKEN'; // Graph API トークン

function dailyReport() {
  const sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName('Daily_Log');
  const today = new Date();
  
  // 1. 本来はAPIで数値取得するが、プロトタイプではダミーデータを生成
  // （実運用時はここをGraph API呼び出しに置き換える）
  const followers = Math.floor(Math.random() * 100) + 1200; // ダミー: 1200〜1300人
  const engagement = Math.floor(Math.random() * 50) + 10;   // ダミー: いいね数
  
  // 2. データを記録
  sheet.appendRow([today, followers, engagement]);
  
  // 3. 月末ならAI考察を実行 (擬似コード)
  if (isEndOfMonth(today)) {
    generateAIAnalysis(sheet);
  }
}

function generateAIAnalysis(sheet) {
  // ここでOpenAI APIを叩き、「先月よりフォロワーがXX人増えました。要因は...」
  // というテキストを生成してシートの所定セルに書き込む
  const analysisCell = sheet.getRange("E2");
  analysisCell.setValue("【AI自動考察】\n今月はリール投稿の保存率が高く、フォロワー増に寄与しました。来月は...");
}

function isEndOfMonth(date) {
  // 月末判定ロジック
  const tomorrow = new Date(date);
  tomorrow.setDate(tomorrow.getDate() + 1);
  return tomorrow.getDate() === 1;
}
```

---

## 🚀 次のステップ：プロトタイプを動かす

1.  **Notion**を用意し、データベースを作る。
2.  **Make**のアカウント（無料版でOK）を作り、NotionとChatGPTを接続する。
3.  **テスト**: Notionでステータスを「Drafting」に変えてみる。
4.  数秒後、勝手に「Caption」が埋まって「Review」になれば成功！

これが、**「寝ている間に仕事が終わる」**体験の入り口です。
