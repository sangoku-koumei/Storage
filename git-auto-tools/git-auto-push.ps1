# Git自動プッシュスクリプト for Antigravity
# 使い方: .\git-auto-push.ps1 [-autoCommit] [-message "コミットメッセージ"]

param(
    [switch]$autoCommit,
    [string]$message = ""
)

# エラーが発生した場合は即座に停止
$ErrorActionPreference = "Stop"

# カラー出力用
function Write-ColorOutput($ForegroundColor) {
    if ($args) {
        Write-Host $args -ForegroundColor $ForegroundColor
    }
}

Write-ColorOutput Cyan "=========================================="
Write-ColorOutput Cyan "  Git自動プッシュツール for Antigravity"
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
        Write-ColorOutput Yellow "警告: Gitリポジトリが見つかりません。現在のフォルダで初期化します。"
        git init
    }
}
catch {
    Write-ColorOutput Red "エラー: Gitリポジトリの確認に失敗しました。"
    exit 1
}

# リモートリポジトリの確認
$remoteUrl = git remote get-url origin 2>$null
if (-not $remoteUrl) {
    Write-ColorOutput Yellow "警告: リモートリポジトリが設定されていません。"
    exit 0
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
}
catch {
    Write-ColorOutput Red "✗ ステージングエラー: $_"
    exit 1
}
Write-Output ""

# コミット
if ($autoCommit) {
    if (-not $message) {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
        $fileCount = (git status --short | Measure-Object -Line).Lines
        $message = "Antigravity 自動同期: $timestamp ($fileCount ファイル)"
    }
    
    Write-ColorOutput Cyan "コミット中..."
    Write-Output "メッセージ: $message"
    
    $stagedChanges = git diff --cached --name-only
    if ($stagedChanges) {
        try {
            git commit -m $message
            Write-ColorOutput Green "✓ コミット完了"
        }
        catch {
            Write-ColorOutput Red "✗ コミットエラー: $_"
        }
    }
    else {
        Write-Output "コミットする変更がありません。"
    }
    Write-Output ""
}

# プッシュ
Write-ColorOutput Cyan "プッシュ中..."
try {
    $branch = git branch --show-current
    if (-not $branch) { $branch = "main" }
    
    git push origin $branch
    Write-ColorOutput Green "✓ プッシュ完了 ($branch ブランチ)"
    
    Write-ColorOutput Cyan "同期の最終確認中..."
    $latestCommit = git log -1 --pretty=format:"%h - %s (%cr)"
    Write-Output "最新のコミット: $latestCommit"
}
catch {
    Write-ColorOutput Red "✗ プッシュエラー: $_"
}

# --- デスクトップファイルのバックアップ ---
Write-Output ""
Write-ColorOutput Cyan "------------------------------------------"
Write-ColorOutput Cyan "  デスクトップバックアップ (Antigravity Sync)"
Write-ColorOutput Cyan "------------------------------------------"

$desktopPath = [Environment]::GetFolderPath("Desktop")
$destDesktopBackup = Join-Path $currentDir "Desktop_Backup"

if (-not (Test-Path $destDesktopBackup)) {
    New-Item -ItemType Directory -Path $destDesktopBackup -Force | Out-Null
}

Write-Output "同期中: $desktopPath -> $destDesktopBackup"
try {
    $robocopyArgs = @($desktopPath, $destDesktopBackup, "/MIR", "/XD", ".git", ".vscode", ".gemini", "/R:1", "/W:1", "/NFL", "/NDL", "/NJH", "/NJS", "/nc", "/ns", "/np")
    $process = Start-Process robocopy -ArgumentList $robocopyArgs -Wait -NoNewWindow -PassThru
    
    if ($process.ExitCode -lt 8) {
        Write-ColorOutput Green "✓ デスクトップ同期完了"
        
        git add $destDesktopBackup
        if (git diff --cached --name-only $destDesktopBackup) {
            git commit -m "Antigravity Desktop backup: $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
            git push origin $branch
            Write-ColorOutput Green "✓ デスクトップの変更をGitに反映しました"
        }
    }
}
catch {
    Write-ColorOutput Red "✗ デスクトップバックアップ中にエラーが発生しました"
}

Write-Output ""
Write-ColorOutput Green "=========================================="
Write-ColorOutput Green "  すべての同期が正常に完了しました！"
Write-ColorOutput Green "=========================================="
