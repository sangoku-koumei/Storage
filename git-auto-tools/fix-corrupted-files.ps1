# 文字化けしたファイルを検出・修復するツール
# Gitリポジトリ内の文字化けファイルを検出し、修復を試みます

param(
    [string]$TargetDir = ".",
    [switch]$AutoFix
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  文字化けファイル検出・修復ツール" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 対象ディレクトリを確認
$targetPath = Resolve-Path $TargetDir
Write-Host "対象ディレクトリ: $targetPath" -ForegroundColor Gray
Write-Host ""

# .md ファイルを検索
Write-Host "Markdownファイルを検索中..." -ForegroundColor Cyan
$mdFiles = Get-ChildItem -Path $targetPath -Filter "*.md" -Recurse | Where-Object { $_.FullName -notlike "*\.git\*" }

$corruptedFiles = @()
$totalFiles = $mdFiles.Count
Write-Host "  検出されたファイル数: $totalFiles" -ForegroundColor Gray
Write-Host ""

# 各ファイルをチェック
$checkedCount = 0
foreach ($file in $mdFiles) {
    $checkedCount++
    Write-Progress -Activity "ファイルをチェック中" -Status "$checkedCount / $totalFiles" -PercentComplete (($checkedCount / $totalFiles) * 100)
    
    try {
        $bytes = [System.IO.File]::ReadAllBytes($file.FullName)
        
        # 文字化けの可能性があるパターンをチェック
        $isCorrupted = $false
        $reason = ""
        
        # パターン1: 不正なバイト列が含まれている
        # 文字化けしている場合、ASCII範囲外の不正なバイトが含まれることがある
        $invalidBytes = 0
        foreach ($byte in $bytes) {
            # UTF-8として無効なバイトパターン
            if ($byte -gt 0x7F -and $byte -lt 0xC0 -or $byte -gt 0xF4) {
                $invalidBytes++
            }
        }
        
        # パターン2: UTF-8として読み込めない
        try {
            $utf8Content = [System.IO.File]::ReadAllText($file.FullName, [System.Text.Encoding]::UTF8)
            # 日本語が含まれているか確認
            if ($utf8Content -match '[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]') {
                # Shift_JISとしても試してみる
                try {
                    $sjisContent = [System.Text.Encoding]::GetEncoding("Shift_JIS").GetString($bytes)
                    # 両方で日本語が読み取れる場合、Shift_JISの可能性
                    if ($sjisContent -match '[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]' -and 
                        $sjisContent.Length -gt $utf8Content.Length) {
                        $isCorrupted = $true
                        $reason = "Shift_JISとして保存されている可能性"
                    }
                } catch {
                    # Shift_JISとして読めない場合は問題なし
                }
            }
        } catch {
            $isCorrupted = $true
            $reason = "UTF-8として読み込めない"
        }
        
        if ($isCorrupted) {
            $corruptedFiles += [PSCustomObject]@{
                File = $file.FullName
                Reason = $reason
            }
        }
        
    } catch {
        # ファイル読み込みエラー
        $corruptedFiles += [PSCustomObject]@{
            File = $file.FullName
            Reason = "読み込みエラー: $_"
        }
    }
}

Write-Progress -Activity "ファイルをチェック中" -Completed

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  検出結果" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

if ($corruptedFiles.Count -eq 0) {
    Write-Host "✓ 文字化けしたファイルは見つかりませんでした" -ForegroundColor Green
} else {
    Write-Host "文字化けの可能性があるファイル: $($corruptedFiles.Count) 件" -ForegroundColor Yellow
    Write-Host ""
    
    foreach ($item in $corruptedFiles) {
        Write-Host "  [×] $($item.File)" -ForegroundColor Red
        Write-Host "      理由: $($item.Reason)" -ForegroundColor Gray
        Write-Host ""
    }
    
    if ($AutoFix) {
        Write-Host "自動修復を開始します..." -ForegroundColor Cyan
        Write-Host ""
        
        foreach ($item in $corruptedFiles) {
            Write-Host "修復中: $($item.File)" -ForegroundColor Yellow
            & "$PSScriptRoot\convert-to-utf8.ps1" -FilePath $item.File -Backup
            Write-Host ""
        }
        
        Write-Host "==========================================" -ForegroundColor Green
        Write-Host "  修復が完了しました！" -ForegroundColor Green
        Write-Host "==========================================" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "修復するには、以下のコマンドを実行してください:" -ForegroundColor Yellow
        Write-Host "  .\fix-corrupted-files.ps1 -AutoFix" -ForegroundColor White
        Write-Host ""
        Write-Host "または、個別に変換する場合:" -ForegroundColor Yellow
        foreach ($item in $corruptedFiles) {
            Write-Host "  .\convert-to-utf8.ps1 -FilePath `"$($item.File)`" -Backup" -ForegroundColor White
        }
    }
}

