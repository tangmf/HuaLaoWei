@echo off
setlocal enabledelayedexpansion

:: Default to current directory if no folder param provided
set "TARGET_DIR=%cd%"

:: Parse optional --folder="folder_name" argument
for %%A in (%*) do (
    echo %%~A | findstr /B /C:"--folder=" >nul
    if not errorlevel 1 (
        set "TARGET_DIR=%%~A"
        set "TARGET_DIR=!TARGET_DIR:--folder=!"
        set "TARGET_DIR=!TARGET_DIR:"=!"
    )
)

echo Target folder: %TARGET_DIR%
echo Decompressing all .gz files in the folder and its subdirectories...

for /R "%TARGET_DIR%" %%F in (*.gz) do (
    echo Processing: %%F
    gzip -dk "%%F"
)

echo All files have been decompressed!
pause
