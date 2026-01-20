---
tags: [Manual_Creation_Tool, Agency_Grade, Manual, Usage_Guide, AI_Tool]
date: 2026-01-16
source: Manual_Creation_Tool_v6.0
aliases: [Agency_Architect_Manual, ツール利用ガイド, AIマニュアル作成ツール操作説明書]
---

# [[Manual_Creation_Tool_Usage_Guide]]
# AI Manual Architect v6.0 (Agency Edition) 利用ガイド

本文書は、**AI Manual Architect v6.0 (Agency Grade)** の操作方法を解説する公式ガイドである。
本ツールは、単なるテキスト生成ツールではない。「コンサルタントが30時間かけて行うマニュアル作成業務」を、AIと協働して30分で完了させるための **"Agency Operation System"** である。

Backlink: [[03_Manual_Creation_Tool]]

---

## 🚀 0. クイック起動 (Quick Launch)

ツールを起動するには、以下のコマンドをターミナルで実行してください。

*   **Tool Location**: `c:\Users\user\Desktop\保管庫\ユニコの脳みそ\00\Manual_Creation_Tool`
*   **Launch Command**:
    ```bash
    cd c:\Users\user\Desktop\保管庫\ユニコの脳みそ\00\Manual_Creation_Tool
    streamlit run app.py
    ```

## 🚀 1. 導入と準備 (Getting Started)

### 1-1. コンセプト
本ツールは **「Human-in-the-Loop (人間参加型)」** アーキテクチャを採用している。
AIに「丸投げ」するのではなく、要所要所で人間（あなた）が **意思決定（Review/Critique）** を行うことで、プロ品質の成果物を生み出す。

### 1-2. 起動方法
1.  **Terminal** を開く。
2.  以下のコマンドを実行する。
    ```bash
    streamlit run app.py
    ```
3.  ブラウザが立ち上がり、ダッシュボードが表示される。

### 1-3. API Keyの設定
*   **Sidebar (左メニュー)** の "OpenAI API Key" 欄にキーを入力する。
*   キーは自動的に `StateManager` に保存され、セッション中は維持される。

---

## 🛠️ 2. 基本ワークフロー (Core Workflow)

画面上部のタブに従って、左から右へ作業を進める。

### Step 1: 🏗️ Architect (構成設計)
マニュアルの「骨子（Skeleton）」を定義するフェーズ。

1.  **Input Source**:
    *   **Raw Text**: クライアントからの雑多なメモや要望をそのまま貼り付ける。
    *   **Questionnaire Wizard**: フォームに従って「目的」「対象読者」「スコープ」を入力し、構造化された指示書を作る。
2.  **Service Tier**:
    *   上部のセレクトボックスで「Volume / Depth」を決定する。
    *   **Normal**: 要約版。
    *   **Detailed**: 徹底した深掘りと事例（Agency推奨）。
3.  **Generate Skeleton**:
    *   ボタンを押すと、AIが章立て（JSON）を提案する。
    *   **Structure Editor**: 生成されたJSONを直接編集し、章の追加・削除が可能。

### Step 2: 📝 Production (執筆 & 構造化)
骨子に基づき、本文を執筆するフェーズ。

1.  **Manual Type Selection** (重要/New!):
    *   サイドバーの **"Config"** で定義したプリセット、または標準プリセット（SOP, System, Training等）が適用される。
    *   選択された型に基づき、AIは「トーン＆マナー」や「必須セクション」を強制的に挿入する。
2.  **Generate Full Draft**:
    *   ボタンを押すと、AIが数分かけて長文ドラフトを執筆する。
    *   この時点ではまだ「下書き（Draft）」である。

### Step 3: 🧐 Review (Human-in-the-Loop)
**v6.0 最大の変更点**。AIの生成フローを一時停止し、人間の介入を強制する。

1.  **AI Critique**:
    *   AI編集長がドラフトを読み、「論理の飛躍」「具体性の欠如」などを辛辣に指摘する。
2.  **Human Critique (追加指示)**:
    *   あなた自身の目でドラフトとAI指摘を確認する。
    *   **"Your Additional Instructions"** 欄に、修正指示（例：「もっと語り口を柔らかく」「第2章の事例を具体的に」）を入力する。
3.  **Proceed to Final Polish**:
    *   このボタンを押すと、AI指摘＋人間指示を統合して、最終生成（Polishing）が開始される。

### Step 4: 🚀 Publishing (最終化 & 出力)
納品物の最終確認と微調整を行う。

1.  **Format Check**:
    *   Markdownが正しくレンダリングされているか確認する。
    *   [[Mermaid記法]] による図解（フローチャート等）が表示されているか確認する。
2.  **Section-Level Refinement (部分修正)**:
    *   **"🛠️ Section Refinement"** タブを開く。
    *   修正したいセクション（見出し）を選択する。
    *   修正指示を送り、**その部分だけ** をリライトさせる。全体再生成の手間が不要になる。
3.  **Download**:
    *   "Download Markdown" で `.md` ファイルを取得し、納品する。

---

## ⚙️ 3. Agency Operation Pack (高度な機能)

プロのエージェンシー業務を支える補助機能群。

### 💾 3-1. Project Save/Load (プロジェクト保存)
作業を中断・再開するための機能。
*   **Save**: Sidebarの "Download Project JSON" をクリック。現在の全状態（入力、設定、ドラフト、最終稿）が1ファイルに保存される。
*   **Load**: "Load Project" にファイルをアップロードすると、瞬時に作業状態が復元される。
*   **Use Case**: クライアント確認待ちの間に保存し、翌日再開する。

### 🛠️ 3-2. Custom Preset Builder (独自型定義)
自社独自の「売れるマニュアルの型」を作る機能。
1.  **"⚙️ Config"** タブを開く。
2.  **New Preset Definition**:
    *   **Name**: 管理名（例：採用面接マニュアル）。
    *   **Focus**: 重視するポイント（例：見極めと魅力付け）。
    *   **Sections**: 必須の見出しリスト。
    *   **Instruction**: AIへの具体的な振る舞い指示（System Prompt）。
3.  保存すると、以降の生成プロセスでこのプリセットが使用可能になる。

---

## ⚠️ 4. Troubleshooting & Tips

*   **Q: 生成が途中で止まる**
    *   A: OpenAI APIのタイムアウトの可能性があります。リロードせず、少し待ってから再実行してください。
*   **Q: 図解（Mermaid）が表示されない**
    *   A: MarkdownビューワーがMermaidに対応していない場合があります。本ツール上では表示されますが、納品先（Notion等）の仕様を確認してください。
*   **Q: 独自の型を作ったが、AIが従わない**
    *   A: "Instruction" をより強力な言葉（例：「絶対に〜せよ」「〜は禁止」）で記述してください。AIは曖昧な指示を無視する傾向があります。

---

## 📚 5. 関連資料 (References)
*   [[Manual_Creation_Bible_Master]]: ツールの設計思想と詳細仕様書。
*   [[Improvement_Strategy]]: 開発の経緯と改善戦略。
*   [[Original_Request_Memo_Deep_Log]]: 初期の開発要望ログ。

**End of Guide**
