# Desktop Git Upload Tool
# 使い方: powershell -File desktop-git.ps1 -Source "C:\Users\user\Desktop\AI_TEMP" -AutoCommit

param(
    [string]$Source = "",
    [switch]$AutoCommit
)

$ErrorActionPreference = "Stop"

function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) { Write-Output $args }
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-ColorOutput Cyan "=========================================="
Write-ColorOutput Cyan "  デスクトップ Git アップロードツール"
Write-ColorOutput Cyan "=========================================="

# デフォルトのソース（指定がない場合）
if (-not $Source) {
    $Source = [Environment]::GetFolderPath("Desktop")
}

Write-Output "ソースディレクトリ: $Source"

# 保存先のベース（保管庫内のバックアップ用リポジトリ）
$CurrentRepo = git rev-parse --show-toplevel
$DestBackup = Join-Path $CurrentRepo "Desktop_Backup"

if (-not (Test-Path $DestBackup)) {
    New-Item -ItemType Directory -Path $DestBackup -Force | Out-Null
}

Write-Output "転送先: $DestBackup"

# コピー (MIRでミラーリング)
try {
    Write-ColorOutput Cyan "同期中..."
    # 一時ファイルや巨大ファイルを除外
    robocopy $Source $DestBackup /MIR /XD .git .vscode .gemini tmp /R:1 /W:1 /NFL /NDL /NJH /NJS /nc /ns /np /XF *.tmp *.log
    Write-ColorOutput Green "✓ 同期完了"
}
catch {
    Write-ColorOutput Red "✗ 同期に失敗しました"
    exit 1
}

# Git への反映
if ($AutoCommit) {
    Set-Location $CurrentRepo
    git add $DestBackup
    $status = git status --short $DestBackup
    if ($status) {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
        git commit -m "Desktop manual backup: $timestamp"
        git push
        Write-ColorOutput Green "✓ Gitにバックアップをプッシュしました"
    }
    else {
        Write-ColorOutput Yellow "変更はありませんでした。"
    }
}
