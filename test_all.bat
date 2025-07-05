@echo off
echo Testing MyManaBox Card Sorter
echo ==============================

echo.
echo 1. Testing Summary:
C:\Users\Petro\repos\MyManaBox\.venv\Scripts\python.exe mymanabox.py --summary

echo.
echo 2. Testing Search for "Abrade":
C:\Users\Petro\repos\MyManaBox\.venv\Scripts\python.exe mymanabox.py --search "Abrade"

echo.
echo 3. Testing Duplicates:
C:\Users\Petro\repos\MyManaBox\.venv\Scripts\python.exe mymanabox.py --duplicates

echo.
echo 4. Testing Color Sort:
C:\Users\Petro\repos\MyManaBox\.venv\Scripts\python.exe mymanabox.py --sort color

echo.
echo All tests completed!
pause
