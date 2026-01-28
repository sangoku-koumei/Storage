# Git自動同期スクリプト (仮想脳専用)
param([switch]$autoCommit, [string]$message = "")
$ErrorActionPreference = "Stop"

function Log-Message($msg) {
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] $msg"
}

Log-Message "--- 仮想脳 同期システム 起動 ---"

try {
    # Gitルートの確認
    $gitRoot = git rev-parse --show-toplevel 2>$null
    if (-not $gitRoot) {
        Log-Message "初期化中..."
        git init
    }

    # リモート設定の確認
    $remoteUrl = git remote get-url origin 2>$null
    if (-not $remoteUrl) {
        Log-Message "警告: リモート(origin)が設定されていません。"
        exit 0
    }

    # 変更の検知
    $status = git status --short
    if (-not $status) {
        Log-Message "変更はありません。"
        exit 0
    }

    # 同期プロセス
    Log-Message "変更をステージング中..."
    git add .
    
    if ($autoCommit) {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
        $commitMessage = if ($message) { $message } else { "自動同期: $timestamp" }
        
        Log-Message "コミット実行中: $commitMessage"
        git commit -m $commitMessage
        
        Log-Message "プッシュ実行中..."
        $retryCount = 0
        while ($retryCount -lt 3) {
            git push origin (git branch --show-current) 2>$null
            if ($LASTEXITCODE -eq 0) {
                Log-Message "✅ 同期が正常に完了しました。"
                break
            } else {
                $retryCount++
                Log-Message "再試行中 ($retryCount/3)..."
                Start-Sleep -Seconds 5
            }
        }
        if ($retryCount -eq 3) {
            Log-Message "❌ 同期に失敗しました。ネットワークやコンフリクトを確認してください。"
        }
    }
}
catch {
    Log-Message "致命的エラー: $_"
}
