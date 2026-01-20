---
tags:
  - デプロイ
  - Docker
  - SaaS化
  - AWS
  - GoogleCloud
  - 00ルール
date: 2026-01-15
source: Sales Automation Tool Deployment Strategy
---

# [[Sales_Automation_Tool_Deployment_Guide]]

[[2026-01-15_3大ツール完全操作マニュアル_深層解説|⬅️ 操作マニュアルへ]] | [[2026-01-15_営業オート化_技術・知識全書_深層対話|📚 技術バイブルへ]]

> [!TIP]
> **本書の位置づけ**
> このファイルは、開発した「Sales Automation Tool」をローカル環境だけでなく、**SaaS（Software as a Service）としてクラウド上に展開し、課金モデルで運用する** ための技術ガイドである。

---

## 1. 🏠 Local Run (基本操作)

まずはローカルで動作確認を行う。

```powershell
cd c:\Users\user\Desktop\保管庫\ユニコの脳みそ\03\Sales_Automation_Tool
pip install -r requirements.txt
streamlit run app.py
```

## 2. 🐳 Docker Run (SaaS化シミュレーション)

本ツールは `Dockerfile` を完備しており、どの環境でも「コンテナ」として独立動作する。
これにより、サーバー1台で複数の顧客用コンテナを立ち上げる「マルチテナント運用」が可能になる。

```bash
# Build Image
docker build -t sales-agent-v5 .

# Run Container (Port 8501)
docker run -p 8501:8501 sales-agent-v5
```

## 3. ☁️ Cloud Deployment (自動販売機化)

この `Dockerfile` をクラウドにアップロードすれば、URL一つで誰でも使えるWebアプリになる。

### Option A: Google Cloud Run (推奨)
*   **コスト**: 使った分だけ課金（待機時間ゼロ円）。
*   **メリット**: **「DuckDuckGo検索」や「スクレイピング」のIP分散** がしやすい。
*   **コマンド**:
    ```bash
    gcloud run deploy --source .
    ```

### Option B: AWS App Runner
*   **コスト**: 月額固定（少し高い）。
*   **メリット**: 設定不要でGitHubと連携して自動デプロイされる。

### Option C: Streamlit Community Cloud (無料)
*   **コスト**: 0円。
*   **デメリット**: スクレイピング規制が厳しいため、v5.0（検索機能付き）は動作しない可能性がある。

---

## 📋 v5.0 Features Recap
*   **Meta-Agent**: Finds "Jobs" (案件) automatically and drafts proposals.
*   **Auto-Prospecting**: Finds "Companies" automatically.
*   **SMTP Sending**: Sends real emails with Reputation Guardian.
*   **CRM**: Manages everything with SQLite.

[[2026-01-15_作業メモ|📝 本日の作業ログに戻る]]
