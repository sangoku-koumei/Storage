# Git自動プッシュツール 使い方

## 概要
このツールは、CursorでGit操作を簡単に自動化するためのツールです。
「Run」ボタンを何度も押す必要がなくなります！

## クイックスタート 🚀

**最も簡単な使い方（3ステップ）:**

1. **Ctrl + Shift + P** を押す
2. 「**task**」と入力して「**Tasks: Run Task**」を選択
3. 「**Git: すべてをプッシュ（add + commit + push）**」を選択

これだけで、すべての変更が自動的にGitHubにプッシュされます！

## 使い方

### 方法1: タスクランナーを使用（推奨）

1. **Ctrl + Shift + P** を押してコマンドパレットを開く
2. 「**Tasks: Run Task**」と入力してEnter
3. 以下のタスクから選択：
   - **「Git: すべてをプッシュ（add + commit + push）」** ← これが最も便利！
   - 「Git: ステージングのみ（add）」
   - 「Git: コミット（commit）」
   - 「Git: プッシュ（push）」
   - 「Git: ステータス確認（status）」

### 方法2: キーボードショートカットを設定（最も速い！）

**推奨ショートカット: Ctrl + Shift + G**

設定手順：
1. **Ctrl + K, Ctrl + S** でキーボードショートカット設定を開く
2. 右上の「**{}**」アイコンをクリックして`keybindings.json`を開く
3. 以下のJSONをコピー＆ペースト：

```json
[
  {
    "key": "ctrl+shift+g",
    "command": "workbench.action.tasks.runTask",
    "args": "Git: すべてをプッシュ（add + commit + push）"
  }
]
```

4. 保存して、**Ctrl + Shift + G**を押すだけでGitプッシュが実行されます！

**注意:** `git-auto-tools/keybindings.json.example`も参考にしてください。

### 方法3: コマンドラインから直接実行

PowerShellで以下のコマンドを実行：

```powershell
.\git-auto-tools\git-auto-push.ps1 -autoCommit
```

カスタムメッセージを指定する場合：

```powershell
.\git-auto-tools\git-auto-push.ps1 -autoCommit -message "今日の作業完了"
```

## 機能

### 自動プッシュタスク
- すべての変更ファイルを自動的にステージング（`git add .`）
- 自動的にコミット（メッセージは日時が自動挿入）
- GitHubに自動プッシュ

### 手動操作タスク
- ステージングのみ
- コミットのみ（メッセージを入力可能）
- プッシュのみ
- ステータス確認

## トラブルシューティング

### リモートリポジトリが設定されていない場合
初回実行時に、リモートリポジトリのURLの入力を求められます。
以下を入力してください：
```
https://github.com/sangoku-koumei/Storage.git
```

### 認証エラーが出る場合
GitHubの認証が必要な場合は、事前に認証を設定してください：
```powershell
git config --global credential.helper wincred
```

### エラーが発生した場合
- PowerShellの実行ポリシーを確認
- Gitがインストールされているか確認
- ネットワーク接続を確認

## カスタマイズ

`git-auto-tools/git-auto-push.ps1`を編集することで、以下のカスタマイズが可能です：
- コミットメッセージの形式を変更
- 自動プッシュの動作を変更
- 追加のGit操作を追加

## 注意事項

- このツールは変更を自動的にコミット・プッシュします
- 重要な変更の前に、必ず`git status`で確認することをお勧めします
- プッシュ前にコミットメッセージを確認したい場合は、「Git: コミット（commit）」タスクを個別に使用してください

