# Git Auto-Sync Script
param([switch]$autoCommit, [string]$message = "", [int]$interval = 300)
$ErrorActionPreference = "Stop"

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function LogMsg($m) {
    $t = Get-Date -Format "HH:mm:ss"
    Write-Host "[$t] $m"
}

LogMsg "SYNC_SYSTEM_START"

while ($true) {
    try {
        if (-not (git rev-parse --show-toplevel 2>$null)) {
            LogMsg "GIT_INIT"
            git init
        }
        $remote = git remote get-url origin 2>$null
        if (-not $remote) {
            LogMsg "WARN_NO_REMOTE"
        } else {
            if (git status --short) {
                LogMsg "CHANGE_DETECTED"
                git add .
                if ($autoCommit) {
                    $commitMsg = if ($message) { $message } else { "AutoSync: $(Get-Date -Format 'yyyyMMddHHmm')" }
                    LogMsg "COMMIT_START"
                    git commit -m $commitMsg
                    LogMsg "PUSH_START"
                    $b = git branch --show-current
                    git push origin $b 2>$null
                    if ($LASTEXITCODE -eq 0) {
                        LogMsg "SUCCESS_SYNC"
                    } else {
                        LogMsg "ERROR_SYNC_FAILED"
                    }
                }
            }
        }
    } catch {
        LogMsg "FATAL_ERROR"
    }
    Start-Sleep -Seconds $interval
}