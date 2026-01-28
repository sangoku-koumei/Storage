# Git自動プッシュスクリプト for Cursor
# 使い方: .\git-auto-push.ps1 [-autoCommit] [-message "コミットメッセージ"]

param(
    [switch]$autoCommit,
    [string]$message = ""
)

# エラーが発生した場合は即座に停止
$ErrorActionPreference = "Stop"

# カラー出力用
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-ColorOutput Cyan "=========================================="
Write-ColorOutput Cyan "  Git自動プッシュツール"
Write-ColorOutput Cyan "=========================================="
Write-Output ""

# 現在のディレクトリを確認
$currentDir = Get-Location
Write-Output "作業ディレクトリ: $currentDir"
Write-Output ""

# Gitリポジトリの確認
try {
    $gitRoot = git rev-parse --show-toplevel 2>$null
    if (-not $gitRoot) {
        Write-ColorOutput Yellow "警告: Gitリポジトリが見つかりません。初期化しますか？ (Y/N)"
        $response = Read-Host
        if ($response -eq "Y" -or $response -eq "y") {
            git init
            Write-ColorOutput Green "Gitリポジトリを初期化しました。"
        } else {
            Write-ColorOutput Red "処理を中止しました。"
            exit 1
        }
    }
} catch {
    Write-ColorOutput Red "エラー: Gitリポジトリの確認に失敗しました。"
    exit 1
}

# リモートリポジトリの確認
$remoteUrl = git remote get-url origin 2>$null
if (-not $remoteUrl) {
    Write-ColorOutput Yellow "警告: リモートリポジトリが設定されていません。"
    Write-ColorOutput Yellow "リモートリポジトリのURLを入力してください（例: https://github.com/user/repo.git）:"
    $newRemote = Read-Host
    if ($newRemote) {
        git remote add origin $newRemote
        Write-ColorOutput Green "リモートリポジトリを追加しました: $newRemote"
    }
}

# 変更されたファイルを確認
Write-ColorOutput Cyan "変更を確認中..."
$status = git status --short
if (-not $status) {
    Write-ColorOutput Yellow "変更されたファイルがありません。"
    exit 0
}

Write-Output ""
Write-ColorOutput Cyan "変更されたファイル:"
git status --short
Write-Output ""

# ステージング（git add .）
Write-ColorOutput Cyan "ステージング中..."
try {
    git add .
    Write-ColorOutput Green "✓ ステージング完了"
} catch {
    Write-ColorOutput Red "✗ ステージングエラー: $_"
    exit 1
}
Write-Output ""

# コミット
if ($autoCommit) {
    if (-not $message) {
        # コミットメッセージを自動生成（日時 + 変更されたファイル数）
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
        $fileCount = (git status --short | Measure-Object -Line).Lines
        $message = "自動コミット: $timestamp ($fileCount ファイル)"
    }
    
    Write-ColorOutput Cyan "コミット中..."
    Write-Output "メッセージ: $message"
    try {
        git commit -m $message
        Write-ColorOutput Green "✓ コミット完了"
    } catch {
        Write-ColorOutput Red "✗ コミットエラー: $_"
        exit 1
    }
    Write-Output ""
}

# プッシュ
Write-ColorOutput Cyan "プッシュ中..."
try {
    # 現在のブランチを取得
    $branch = git branch --show-current
    if (-not $branch) {
        $branch = "main"
        git branch -M main 2>$null
    }
    
    # リモートが設定されているか確認
    $remoteExists = git remote get-url origin 2>$null
    if ($remoteExists) {
        git push -u origin $branch
        Write-ColorOutput Green "✓ プッシュ完了 ($branch ブランチ)"
        
        # 最終確認: git log で最新のコミットが反映されているか
        Write-ColorOutput Cyan "プッシュの最終確認中..."
        $latestCommit = git log -1 --pretty=format:"%h - %s (%cr)"
        Write-Output "最新のコミット: $latestCommit"
    } else {
        Write-ColorOutput Yellow "警告: リモートリポジトリが設定されていません。プッシュをスキップします。"
    }
} catch {
    Write-ColorOutput Red "✗ プッシュエラー: $_"
    # ネットワークエラーなどの場合はリトライのヒント
    Write-ColorOutput Yellow "ネットワーク接続を確認してください。"
}

# --- デスクトップファイルのバックアップ (追加) ---
Write-Output ""
Write-ColorOutput Cyan "------------------------------------------"
Write-ColorOutput Cyan "  デスクトップファイルのバックアップ開始"
Write-ColorOutput Cyan "------------------------------------------"

$desktopPath = [Environment]::GetFolderPath("Desktop")
$destDesktopBackup = Join-Path $currentDir "Desktop_Backup"

if (-not (Test-Path $destDesktopBackup)) {
    New-Item -ItemType Directory -Path $destDesktopBackup -Force | Out-Null
}

Write-Output "コピー中: $desktopPath -> $destDesktopBackup"
try {
    # .git フォルダなどは除外してコピー (Robocopyを使用すると効率的)
    robocopy $desktopPath $destDesktopBackup /MIR /XD .git .vscode .gemini /R:1 /W:1 /NFL /NDL /NJH /NJS /nc /ns /np
    Write-ColorOutput Green "✓ デスクトップのバックアップ完了"
    
    # 変更があればコミット
    git add $destDesktopBackup
    $status = git status --short $destDesktopBackup
    if ($status) {
        git commit -m "Desktop auto backup: $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
        git push origin $branch
        Write-ColorOutput Green "✓ デスクトップの変更をGitに反映しました"
    }
} catch {
    Write-ColorOutput Red "✗ デスクトップバックアップ中にエラーが発生しました"
}

Write-Output ""
Write-ColorOutput Green "=========================================="
Write-ColorOutput Green "  処理が完了しました！"
Write-ColorOutput Green "=========================================="

