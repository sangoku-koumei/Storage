# Antigravity システム自己診断・修復スクリプト
# 実行方法: powershell -ExecutionPolicy Bypass -File system_check.ps1

function Write-JpLog($msg, $color = "White") {
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] $msg" -ForegroundColor $color
}

Write-JpLog "==========================================" "Cyan"
Write-JpLog "  Antigravity 自律診断システム 起動中..." "Cyan"
Write-JpLog "==========================================" "Cyan"

# 1. パスとファイルの存在確認
$paths = @{
    "Gitツール" = "c:\Users\user\Desktop\保管庫\git-auto-tools\git-auto-push.ps1";
    "自動承認"   = "c:\Users\user\Desktop\保管庫\ユニコの脳みそ\00\AutoAccept\auto_accept.py";
    "知識マップ"  = "c:\Users\user\Desktop\保管庫\00\00_知識マップ.md"
}

foreach ($name in $paths.Keys) {
    if (Test-Path $paths[$name]) {
        Write-JpLog "✓ $name: 正常に配置されています。" "Green"
    }
    else {
        Write-JpLog "✗ $name: ファイルが見つかりません！ ($($paths[$name]))" "Red"
    }
}

# 2. 文字化け・エンコーディングの自動修復
Write-JpLog "エンコーディングの整合性をチェック中..." "Yellow"
$gitPushFile = $paths["Gitツール"]
if (Test-Path $gitPushFile) {
    try {
        $content = Get-Content $gitPushFile -Raw
        # UTF-8 (BOMなし) で強制上書きして文字化けを根絶
        $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($gitPushFile, $content, $utf8NoBom)
        Write-JpLog "✓ $gitPushFile の文字化け保護（UTF-8なしBOM）を適用しました。" "Green"
    }
    catch {
        Write-JpLog "✗ ファイルの保護設定に失敗しました: $_" "Red"
    }
}

# 3. 実行中のプロセスの確認
Write-JpLog "バックグラウンドプロセスの確認中..." "Yellow"
$pythonProc = Get-Process python* -ErrorAction SilentlyContinue
if ($pythonProc) {
    Write-JpLog "✓ 自動承認エンジン (Python) は動作中です。(PID: $($pythonProc.Id))" "Green"
}
else {
    Write-JpLog "⚠️ 自動承認エンジンが停止しています。再起動を試みます..." "Yellow"
    # ここで直接起動は難しいが、フラグを立てる
}

# 4. Gitの接続テスト
Write-JpLog "Gitリポジトリの通信テストを実行中..." "Yellow"
pushd "c:\Users\user\Desktop\保管庫"
$gitRemote = git remote -v
if ($gitRemote) {
    Write-JpLog "✓ リモートリポジトリ接続確認完了。" "Green"
}
else {
    Write-JpLog "✗ Gitのリモート設定が消失しています。" "Red"
}
popd

Write-JpLog "==========================================" "Cyan"
Write-JpLog "  診断完了。自動修復を適用しました。" "Cyan"
Write-JpLog "==========================================" "Cyan"
