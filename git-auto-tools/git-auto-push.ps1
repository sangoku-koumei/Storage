# Git自動同期スクリプト (仮想脳専用)
param([switch]$autoCommit, [string]$message = "", [int]$interval = 300)
$ErrorActionPreference = "Stop"

function Log-Message($msg) {
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] $msg"
}

Log-Message "--- 仮想脳 同期システム 起動 (監視モード) ---"

while ($true) {
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
            Log-Message "警告: リモート(origin)が設定されていません。同期をスキップします。"
        }
        else {
            # 変更の検知
            $status = git status --short
            if ($status) {
                Log-Message "変更を検知しました。同期を開始します..."
                git add .
                
                if ($autoCommit) {
                    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
                    $commitMessage = if ($message) { $message } else { "自動同期: $timestamp" }
                    
                    Log-Message "コミット実行中: $commitMessage"
                    git commit -m $commitMessage
                    
                    Log-Message "プッシュ実行中..."
                    $retryCount = 0
                    $currentBranch = git branch --show-current
                    while ($retryCount -lt 3) {
                        git push origin $currentBranch 2>$null
                        if ($LASTEXITCODE -eq 0) {
                            Log-Message "✅ 同期が正常に完了しました。"
                            break
                        } else {
                            $retryCount++
                            Log-Message "再試行中 ($retryCount/3)..."
                            Start-Sleep -Seconds 5
                        }
                    }
                }
            } else {
                # 変更がない場合でも、定期的にプルして最新を確認するなどの処理も検討可能
                # 今回はログを汚さないよう静止
            }
        }
    }
    catch {
        Log-Message "警告: 同期中にエラーが発生しました。次回の実行を待ちます。($_)"
    }
    
    # 次の同期まで待機
    Start-Sleep -Seconds $interval
}
