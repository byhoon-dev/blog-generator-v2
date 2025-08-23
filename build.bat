@echo off
chcp 65001 >nul
echo Blog Generator v2.0 Build Started...
echo.

python build_exe.py

echo.
echo Build completed successfully!
echo Check BlogGenerator_Distribution folder.
echo.
pause