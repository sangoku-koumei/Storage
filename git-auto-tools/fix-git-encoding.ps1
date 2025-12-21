# Git文字化け修正ツール
# Gitのエンコーディング設定を修正して、日本語ファイル名やコミットメッセージの文字化けを防ぎます

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Git文字化け修正ツール" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 現在の設定を確認
Write-Host "現在のGitエンコーディング設定を確認中..." -ForegroundColor Yellow
$currentQuotepath = git config --get core.quotepath
$currentCommitEncoding = git config --get i18n.commitencoding
$currentLogEncoding = git config --get i18n.logoutputencoding

Write-Host "  core.quotepath: $currentQuotepath" -ForegroundColor Gray
Write-Host "  i18n.commitencoding: $currentCommitEncoding" -ForegroundColor Gray
Write-Host "  i18n.logoutputencoding: $currentLogEncoding" -ForegroundColor Gray
Write-Host ""

# 設定を適用
Write-Host "Gitエンコーディング設定を適用中..." -ForegroundColor Cyan

# core.quotepathをfalseに設定（日本語ファイル名を正しく表示）
git config --global core.quotepath false
Write-Host "  ✓ core.quotepath = false" -ForegroundColor Green

# コミットメッセージのエンコーディングをUTF-8に設定
git config --global i18n.commitencoding utf-8
Write-Host "  ✓ i18n.commitencoding = utf-8" -ForegroundColor Green

# ログ出力のエンコーディングをUTF-8に設定
git config --global i18n.logoutputencoding utf-8
Write-Host "  ✓ i18n.logoutputencoding = utf-8" -ForegroundColor Green

# Windowsの場合、自動変換を無効化（オプション）
if ($IsWindows -or $env:OS -like "*Windows*") {
    git config --global core.autocrlf false
    Write-Host "  ✓ core.autocrlf = false (Windows改行コード自動変換を無効化)" -ForegroundColor Green
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  設定が完了しました！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "注意: 既存のコミット履歴の文字化けは修正されません。" -ForegroundColor Yellow
Write-Host "      新しいコミットから文字化けが改善されます。" -ForegroundColor Yellow

