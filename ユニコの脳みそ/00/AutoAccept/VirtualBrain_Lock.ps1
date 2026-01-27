# VirtualBrain_Lock.ps1
# Usage:
# .\VirtualBrain_Lock.ps1 -Lock    (Sets folder to Read-Only)
# .\VirtualBrain_Lock.ps1 -Unlock  (Allows writing for maintenance)

param(
    [Parameter(Mandatory = $false)]
    [switch]$Lock,
    
    [Parameter(Mandatory = $false)]
    [switch]$Unlock
)

$targetDir = "C:\Users\user\Desktop\保管庫\ユニコの脳みそ\00"

if ($Lock) {
    Write-Host "Locking Virtual Brain (00 folder)..." -ForegroundColor Yellow
    # Set +R (Read-only) attribute recursively
    # Note: attrib +r only affects files, directories are more about permissions
    # We use icacls for more robust protection
    icacls $targetDir /deny "Everyone:(DE,DC)" /t /c /q
    Write-Host "Lock complete. Deletion and Directory modification are now restricted." -ForegroundColor Green
}
elseif ($Unlock) {
    Write-Host "Unlocking Virtual Brain for maintenance..." -ForegroundColor Cyan
    icacls $targetDir /remove:deny "Everyone" /t /c /q
    Write-Host "Unlock complete. You may now perform updates." -ForegroundColor Green
}
else {
    Write-Host "Please specify -Lock or -Unlock" -ForegroundColor Red
}
