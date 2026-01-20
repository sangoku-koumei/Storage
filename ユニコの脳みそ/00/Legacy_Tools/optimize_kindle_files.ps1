# Batch File Optimization Script
# This script adds tags and related links to all remaining isolated files

$files = @(
    @{Path="c:\Users\user\Desktop\保管庫\2025-12-03-Kindleアイデア_05_浦島太郎.md"; Tags="#Kindle #Idea #WIP #恋愛 #陰陽術"; Links="[[2025-12-03-Kindle本アイデア-全体構想]]`n- [[2025-12-03-Kindleアイデア_00_全体的な事]]`n`n### シリーズ他作品`n- [[2025-12-03-Kindleアイデア_04_一寸法師]]`n- [[2025-12-03-Kindleアイデア_06_赤ずきん]]"},
    @{Path="c:\Users\user\Desktop\保管庫\2025-12-03-Kindleアイデア_06_赤ずきん.md"; Tags="#Kindle #Idea #WIP #恋愛 #陰陽術"; Links="[[2025-12-03-Kindle本アイデア-全体構想]]`n- [[2025-12-03-Kindleアイデア_00_全体的な事]]`n`n### シリーズ他作品`n- [[2025-12-03-Kindleアイデア_05_浦島太郎]]`n- [[2025-12-03-Kindleアイデア_07_ブレーメンの音楽隊]]"},
    @{Path="c:\Users\user\Desktop\保管庫\2025-12-03-Kindleアイデア_07_ブレーメンの音楽隊.md"; Tags="#Kindle #Idea #WIP #恋愛 #陰陽術"; Links="[[2025-12-03-Kindle本アイデア-全体構想]]`n- [[2025-12-03-Kindleアイデア_00_全体的な事]]`n`n### シリーズ他作品`n- [[2025-12-03-Kindleアイデア_06_赤ずきん]]`n- [[2025-12-03-Kindleアイデア_08_醜いアヒルの子]]"},
    @{Path="c:\Users\user\Desktop\保管庫\2025-12-03-Kindleアイデア_08_醜いアヒルの子.md"; Tags="#Kindle #Idea #WIP #恋愛 #陰陽術"; Links="[[2025-12-03-Kindle本アイデア-全体構想]]`n- [[2025-12-03-Kindleアイデア_00_全体的な事]]`n`n### シリーズ他作品`n- [[2025-12-03-Kindleアイデア_07_ブレーメンの音楽隊]]`n- [[2025-12-03-Kindleアイデア_09_王様の耳はロバの耳]]"},
    @{Path="c:\Users\user\Desktop\保管庫\2025-12-03-Kindleアイデア_09_王様の耳はロバの耳.md"; Tags="#Kindle #Idea #WIP #恋愛 #陰陽術"; Links="[[2025-12-03-Kindle本アイデア-全体構想]]`n- [[2025-12-03-Kindleアイデア_00_全体的な事]]`n`n### シリーズ他作品`n- [[2025-12-03-Kindleアイデア_08_醜いアヒルの子]]`n- [[2025-12-03-Kindleアイデア_10_ハーメルンの笛吹き男]]"},
    @{Path="c:\Users\user\Desktop\保管庫\2025-12-03-Kindleアイデア_10_ハーメルンの笛吹き男.md"; Tags="#Kindle #Idea #WIP #恋愛 #陰陽術"; Links="[[2025-12-03-Kindle本アイデア-全体構想]]`n- [[2025-12-03-Kindleアイデア_00_全体的な事]]`n`n### シリーズ他作品`n- [[2025-12-03-Kindleアイデア_09_王様の耳はロバの耳]]`n- [[2025-12-03-Kindleアイデア_11_桃太郎]]"},
    @{Path="c:\Users\user\Desktop\保管庫\2025-12-03-Kindleアイデア_11_桃太郎.md"; Tags="#Kindle #Idea #WIP #恋愛 #陰陽術"; Links="[[2025-12-03-Kindle本アイデア-全体構想]]`n- [[2025-12-03-Kindleアイデア_00_全体的な事]]`n`n### シリーズ他作品`n- [[2025-12-03-Kindleアイデア_10_ハーメルンの笛吹き男]]`n- [[2025-12-03-Kindleアイデア_01_かぐや姫]]"}
)

foreach ($file in $files) {
    if (Test-Path $file.Path) {
        $content = Get-Content $file.Path -Raw -Encoding UTF8
        
        # Add tags at the beginning if not present
        if ($content -notmatch "^#") {
            $content = $file.Tags + "`r`n`r`n" + $content
        }
        
        # Add related links section at the end if not present
        if ($content -notmatch "## 関連リンク") {
            $content = $content.TrimEnd() + "`r`n`r`n---`r`n`r`n## 関連リンク`r`n`r`n### 親プロジェクト`r`n- " + $file.Links + "`r`n"
        }
        
        Set-Content -Path $file.Path -Value $content -Encoding UTF8 -NoNewline
        Write-Host "✓ Processed: $($file.Path)"
    }
}

Write-Host "`nKindle files optimization complete!"
