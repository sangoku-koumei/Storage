# セットアップガイド

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





