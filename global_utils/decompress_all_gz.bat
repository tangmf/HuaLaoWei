@echo off
setlocal enabledelayedexpansion

:: Default to current directory
set "TARGET_DIR=%cd%"
set "NEXT_IS_FOLDER="

:: Parse optional --folder= syntax
for %%A in (%*) do (
    if defined NEXT_IS_FOLDER (
        set "TARGET_DIR=%%~A"
        set "NEXT_IS_FOLDER="
    ) else (
        echo %%~A | findstr /B /C:"--folder=" >nul
        if not errorlevel 1 (
            set "ARG=%%~A"
            set "ARG=!ARG:--folder=!"
            set "ARG=!ARG:"=!"
            set "TARGET_DIR=!ARG!"
        ) else if "%%~A"=="--folder" (
            set "NEXT_IS_FOLDER=1"
        )
    )
)

:: Resolve to absolute path
pushd "!TARGET_DIR!" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Cannot access folder: !TARGET_DIR!
    exit /b 1
)
set "TARGET_DIR=%cd%"
popd

echo.
echo Target folder: !TARGET_DIR!
echo Decompressing all .gz files recursively...
echo.

:: Decompress .gz files
pushd "!TARGET_DIR!" >nul
set /a count=0
for /R %%F in (*.gz) do (
    echo Decompressing: %%F
    gzip -dk "%%F"
    set /a count+=1
)
popd

echo.
echo Total .gz files decompressed: !count!
echo Done. Press any key to exit.
pause
