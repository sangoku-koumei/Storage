# ファイルの文字コード検出ツール
# 指定されたファイルの文字コードを検出します

param(
    [Parameter(Mandatory=$true)]
    [string]$FilePath
)

# ファイルが存在するか確認
if (-not (Test-Path $FilePath)) {
    Write-Host "エラー: ファイルが見つかりません: $FilePath" -ForegroundColor Red
    exit 1
}

Write-Host "ファイルの文字コードを検出中..." -ForegroundColor Cyan
Write-Host "ファイル: $FilePath" -ForegroundColor Gray
Write-Host ""

# ファイルの先頭部分を読み込んで文字コードを推測
try {
    $bytes = [System.IO.File]::ReadAllBytes($FilePath)
    $text = [System.IO.File]::ReadAllText($FilePath, [System.Text.Encoding]::Default)
    
    # BOMの検出
    $hasBOM = $false
    $detectedEncoding = "不明"
    
    if ($bytes.Length -ge 3) {
        # UTF-8 BOM: EF BB BF
        if ($bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
            $detectedEncoding = "UTF-8 (BOM付き)"
            $hasBOM = $true
        }
        # UTF-16 LE BOM: FF FE
        elseif ($bytes[0] -eq 0xFF -and $bytes[1] -eq 0xFE) {
            $detectedEncoding = "UTF-16 LE (BOM付き)"
            $hasBOM = $true
        }
        # UTF-16 BE BOM: FE FF
        elseif ($bytes[0] -eq 0xFE -and $bytes[1] -eq 0xFF) {
            $detectedEncoding = "UTF-16 BE (BOM付き)"
            $hasBOM = $true
        }
    }
    
    if (-not $hasBOM) {
        # 文字コードを試行錯誤で検出
        $encodings = @(
            [System.Text.Encoding]::UTF8,
            [System.Text.Encoding]::GetEncoding("Shift_JIS"),
            [System.Text.Encoding]::GetEncoding("EUC-JP"),
            [System.Text.Encoding]::Default
        )
        
        foreach ($enc in $encodings) {
            try {
                $decoded = $enc.GetString($bytes)
                # 日本語文字が含まれているか確認
                if ($decoded -match '[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]') {
                    $detectedEncoding = $enc.EncodingName
                    break
                }
            } catch {
                continue
            }
        }
        
        if ($detectedEncoding -eq "不明") {
            $detectedEncoding = "UTF-8 (BOMなし) または その他"
        }
    }
    
    Write-Host "検出された文字コード: " -NoNewline
    Write-Host "$detectedEncoding" -ForegroundColor Green
    Write-Host ""
    
    # ファイルサイズ情報
    $fileInfo = Get-Item $FilePath
    Write-Host "ファイルサイズ: $($fileInfo.Length) バイト" -ForegroundColor Gray
    Write-Host ""
    
    # 推奨アクション
    if ($detectedEncoding -notlike "*UTF-8*") {
        Write-Host "推奨: UTF-8に変換することをお勧めします" -ForegroundColor Yellow
        Write-Host "      convert-to-utf8.ps1 を使用してください" -ForegroundColor Yellow
    } else {
        Write-Host "✓ 文字コードは適切です（UTF-8）" -ForegroundColor Green
    }
    
} catch {
    Write-Host "エラー: ファイルの読み込みに失敗しました: $_" -ForegroundColor Red
    exit 1
}

