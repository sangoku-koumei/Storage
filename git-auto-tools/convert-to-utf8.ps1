# ファイルをUTF-8に変換するツール
# 指定されたファイルをUTF-8（BOMなし）に変換します

param(
    [Parameter(Mandatory=$true)]
    [string]$FilePath,
    [switch]$Backup
)

# ファイルが存在するか確認
if (-not (Test-Path $FilePath)) {
    Write-Host "エラー: ファイルが見つかりません: $FilePath" -ForegroundColor Red
    exit 1
}

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  ファイルをUTF-8に変換" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# バックアップを作成
if ($Backup) {
    $backupPath = "$FilePath.bak"
    Copy-Item -Path $FilePath -Destination $backupPath -Force
    Write-Host "バックアップを作成しました: $backupPath" -ForegroundColor Yellow
    Write-Host ""
}

# 現在の文字コードを検出（簡易版）
Write-Host "現在の文字コードを検出中..." -ForegroundColor Cyan
$originalEncoding = "UTF-8"
$bytes = [System.IO.File]::ReadAllBytes($FilePath)

# BOMを確認
if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
    $originalEncoding = "UTF-8 (BOM付き)"
} elseif ($bytes.Length -ge 2 -and $bytes[0] -eq 0xFF -and $bytes[1] -eq 0xFE) {
    $originalEncoding = "UTF-16 LE"
} elseif ($bytes.Length -ge 2 -and $bytes[0] -eq 0xFE -and $bytes[1] -eq 0xFF) {
    $originalEncoding = "UTF-16 BE"
} else {
    # 日本語が含まれている場合はShift_JISの可能性が高い
    try {
        $sjisText = [System.Text.Encoding]::GetEncoding("Shift_JIS").GetString($bytes)
        if ($sjisText -match '[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]') {
            $originalEncoding = "Shift_JIS (推測)"
        }
    } catch {
        $originalEncoding = "不明 (UTF-8として処理)"
    }
}

Write-Host "  検出された文字コード: $originalEncoding" -ForegroundColor Gray
Write-Host ""

# ファイルを読み込んで変換
Write-Host "UTF-8に変換中..." -ForegroundColor Cyan
try {
    # 複数のエンコーディングで試行
    $encodings = @(
        [System.Text.Encoding]::UTF8,
        [System.Text.Encoding]::GetEncoding("Shift_JIS"),
        [System.Text.Encoding]::GetEncoding("EUC-JP"),
        [System.Text.Encoding]::Default
    )
    
    $content = $null
    $usedEncoding = $null
    
    foreach ($enc in $encodings) {
        try {
            $testContent = [System.IO.File]::ReadAllText($FilePath, $enc)
            # 文字化けしていないか確認（日本語文字が含まれているか）
            if ($testContent -match '[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]' -or 
                $enc -eq [System.Text.Encoding]::UTF8) {
                $content = $testContent
                $usedEncoding = $enc.EncodingName
                break
            }
        } catch {
            continue
        }
    }
    
    if ($null -eq $content) {
        # UTF-8で強制読み込み
        $content = [System.IO.File]::ReadAllText($FilePath, [System.Text.Encoding]::UTF8)
        $usedEncoding = "UTF-8 (強制)"
    }
    
    Write-Host "  読み込みに使用したエンコーディング: $usedEncoding" -ForegroundColor Gray
    
    # UTF-8（BOMなし）で保存
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($FilePath, $content, $utf8NoBom)
    
    Write-Host "  ✓ 変換完了: UTF-8 (BOMなし)" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "  変換が完了しました！" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    
} catch {
    Write-Host "エラー: 変換に失敗しました: $_" -ForegroundColor Red
    exit 1
}

