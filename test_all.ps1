# MyManaBox Test Script
Write-Host "Testing MyManaBox Card Sorter" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan

Set-Location "c:\Users\Petro\repos\MyManaBox"
$python = "C:\Users\Petro\repos\MyManaBox\.venv\Scripts\python.exe"

Write-Host "`n1. Testing Summary:" -ForegroundColor Yellow
& $python mymanabox.py --summary

Write-Host "`n2. Testing Search for 'Abrade':" -ForegroundColor Yellow
& $python mymanabox.py --search "Abrade"

Write-Host "`n3. Testing Duplicates:" -ForegroundColor Yellow
& $python mymanabox.py --duplicates

Write-Host "`n4. Testing Color Sort:" -ForegroundColor Yellow
& $python mymanabox.py --sort color

Write-Host "`nAll tests completed!" -ForegroundColor Green
