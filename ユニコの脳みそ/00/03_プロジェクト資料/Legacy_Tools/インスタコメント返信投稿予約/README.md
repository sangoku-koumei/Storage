# Instagram自動投稿・自動返信ツール (Meta Graph API版)

Tags: #Instagram #Python #自動化 #FastAPI #マーケティング #リード獲得 #Zettelkasten #SNS運用
Links: [[TOOL_DESCRIPTION]] [[FEATURES]] [[PROJECT_DESIGN]] [[CONVERSATION_SUMMARY]] [[技術資産__インスタコメント返信投稿予約ツール]] [[2026-01-09_SNS運用代行_知識統合バイブル_深層対話]] [[2026-01-13_ツール開発・改善知見バイブル_深層対話]]

---

ElgramやIstepのようなInstagram自動化ツールの自作版です。

## 機能

- ✅ **予約投稿**: Feed、Reel、Storyの予約投稿に対応
- ✅ **コメント自動返信**: キーワードベースの自動返信ルール
- ✅ **DM自動返信**: 24時間ルールを考慮したDM自動返信
- ✅ **テンプレート管理**: コメント/DM/キャプション用のテンプレート
- ✅ **ルール優先度**: ドラッグ&ドロップでルールの優先度を変更
- ✅ **インボックス**: コメントとDMの一元管理
- ✅ **イベントログ**: アプリケーションイベントの記録とデバッグ
- ✅ **Google Sheets連携**: ログのエクスポート（オプション）

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env.example`をコピーして`.env`を作成し、必要な値を設定してください。

```bash
cp .env.example .env
```

特に以下を設定：
- `META_APP_ID`: MetaアプリのApp ID
- `META_APP_SECRET`: MetaアプリのApp Secret
- `META_WEBHOOK_VERIFY_TOKEN`: Webhook検証用トークン

### 3. データベースの初期化

アプリ起動時に自動的にデータベーステーブルが作成されます。

### 4. アプリケーションの起動

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

APIドキュメントは `http://localhost:8000/docs` で確認できます。

## Meta Graph APIの設定

1. [Meta for Developers](https://developers.facebook.com/)でアプリを作成
2. Instagram Graph APIを有効化
3. OAuthリダイレクトURIを設定
4. Webhookを設定（コメントとDM用）
5. 必要な権限をリクエスト：
   - `instagram_basic`
   - `instagram_content_publish`
   - `instagram_manage_comments`
   - `instagram_manage_messages`

## 使用方法

### アカウント登録

```bash
POST /accounts
{
  "name": "アカウント名",
  "ig_user_id": "Instagram Business Account ID",
  "access_token": "アクセストークン"
}
```

### 予約投稿の作成

```bash
POST /posts
{
  "ig_account_id": 1,
  "post_type": "feed",  # feed, reel, story
  "media_type": "image",  # image, video
  "image_url": "https://example.com/image.jpg",
  "caption": "キャプション",
  "scheduled_at": "2024-01-01T12:00:00Z"
}
```

### コメント自動返信ルールの作成

```bash
POST /comment-rules
{
  "ig_account_id": 1,
  "keyword": "ありがとう",
  "reply_text": "どういたしまして！",
  "priority": 1
}
```

### DM自動返信ルールの作成

```bash
POST /dm-rules
{
  "ig_account_id": 1,
  "keyword": "こんにちは",
  "reply_text": "こんにちは！",
  "priority": 1
}
```

## Webhook設定

### ngrokを使用したローカル開発

```bash
ngrok http 8000
```

ngrokのURLをMetaアプリのWebhook設定に登録してください。

### Webhookエンドポイント

- **コメント**: `GET/POST /webhook/instagram`
- **DM**: `POST /webhook/instagram-messages`

## デバッグモード

`.env`で`DEBUG=true`に設定すると、詳細なリクエストログが出力されます。

## Google Sheets連携（オプション）

1. Google Cloud Consoleでサービスアカウントを作成
2. サービスアカウントのJSONキーをダウンロード
3. スプレッドシートにサービスアカウントのメールアドレスを共有
4. `.env`に設定を追加

## 注意事項

- **24時間ルール**: DM自動返信は、ユーザーからの最後のメッセージから24時間以内のみ可能です
- **アクセストークン**: 現在は平文で保存されています。本番環境では暗号化を推奨します
- **Webhookペイロード**: MetaのWebhookペイロード構造は実際のAPIに合わせて調整が必要な場合があります

## ライセンス

MIT

---

## 🌪️ 深層対話：自動化が解き放つ「真のクリエイティビティ」

**テーマ**: ツールを「作業の代行」から「売上の自動生成エンジン」へピボットさせる

**参加者**:
*   **Strategist**: ビジネスモデルの構築者。ROI（投資対効果）を最優先する。
*   **Developer**: 本ツールの設計者。APIの制約を超えた「機能的体験」を追求。
*   **Growth Hacker**: ユーザー行動を分析し、CVR（成約率）を極限まで高める。
*   **Unico (PM)**: プロジェクトの統合担当。技術とビジネスの橋渡しを行う。

---

### 第1章：なぜ「便利」なだけのツールは捨てられるのか

**Strategist**: 
この `README.md` を見て最初に思うのは、「予約投稿ができて便利そうだな」という感想です。でも、それでは3ヶ月で飽きられます。

**Developer**: 
厳しいですね。でも、その通りです。予約投稿なんて、今やMetaの公式ツール（Meta Business Suite）でも無料でできますから。

**Growth Hacker**: 
このツールの真価は、そこ（予約投稿）にはありません。`機能` にある「キーワードベースの自動返信」と、それを 「リード獲得（リスト取り）」に直結させる思想にあります。

**Unico**: 
つまり、**「自動化を効率化に使うな。増収に使え」**ということですね。

**Strategist**: 
**【提言1】 ツールは「コストセンター（経費）」ではなく「プロフィットセンター（収益源）」として設計せよ。**
コメント欄を単なるコミュニケーションの場ではなく、LINE登録や商品購入への「入り口」に変える。この目的意識が README から滲み出ている必要があります。

### 第2章：24時間ルールという「制約」の中で踊る

**Developer**: 
`注意事項` にある「24時間ルール」。これはMetaの厳格なポリシーです。ユーザーからの反応がない限り、こちらからDMを送り続けることはできません。

**Growth Hacker**: 
でも、それは「制限」ではなく、最高の「フック」になります。24時間しか会話できないからこそ、その1往復の密度を極限まで上げる。

**Strategist**: 
具体的には、コメントに「詳細」と書かれた瞬間に、条件反射で魅力的なリードマグネット（特典）をDMで飛ばす。この `Webhookイベント` の即時性が、有料ツール（Elgram等）に数万円を払う最大の理由です。

**Developer**: 
そのために `ngrok` を使ったローカル開発やデバッグモードを README に厚く書きました。1秒の遅れがCVRを下げますから。

### 第3章：Google Sheets連携：情報の「墓場」にするな

**Unico**: 
`Google Sheets連携` ですが、単にログを残すだけでは、データが「墓場」になってしまいます。

**Strategist**: 
そのシートは、次の「商品開発」の種であるべきです。どのキーワードが最も多く叩かれたか（＝ユーザーの最大の悩みは何か）。

**Growth Hacker**: 
「ありがとう」というルールよりも、「どうすればいいですか？」という質問キーワードを拾い上げるルールの方が価値が高い。それをスプレッドシートで見える化し、次の `2026-01-13_ツール開発知見バイブル` にフィードバックする。

**Developer**: 
ツールを「独立したプログラム」と見なさず、`技術資産__インスタコメント返信投稿予約ツール` という大きなナレッジの一部として捉える設計。これが Zettelkasten 連携の真髄ですね。

### 第4章：エピローグ：ロボットアームに「魂」を乗せる

**Strategist**: 
自動返信に「人格（トーン）」を持たせろ、というのが `2026-01-09_SNS運用代行バイブル` の教えでした。

**Developer**: 
README の `テンプレート管理` 機能は、その「人格」を切り替えるためのOS（オペレーティング・システム）です。

**Unico**: 
このツールを起動する時、あなたは単にコードを走らせているのではありません。あなたの代わりに24時間戦い、ファンを作り、リストを集め続ける「自動分身」を生み出しているのです。

**Strategist**: 
さあ、`依存関係のインストール` から始めましょう。そこが、あなたの「不労所得エンジン」の最初のネジ締めになります。

---

## 関連リンク
- [[TOOL_DESCRIPTION]]
- [[FEATURES]]
- [[PROJECT_DESIGN]]
- [[CONVERSATION_SUMMARY]]
- [[技術資産__インスタコメント返信投稿予約ツール]]
- [[2026-01-09_SNS運用代行_知識統合バイブル_深層対話]]
- [[2026-01-13_ツール開発・改善知見バイブル_深層対話]]
- [[在宅ワーク考察]]
- [[リード獲得・自動返信戦略]]
- [[00 Rules]]


