@echo off
setlocal

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
echo Compressing .csv and .geojson files to .gz using 7-Zip...

:: Compress .csv files
for /R "%TARGET_DIR%" %%F in (*.csv) do (
    echo Processing CSV: %%F
    "C:\Program Files\7-Zip\7z.exe" a -tgzip "%%F.gz" "%%F"
)

:: Compress .geojson files
for /R "%TARGET_DIR%" %%F in (*.geojson) do (
    echo Processing GEOJSON: %%F
    "C:\Program Files\7-Zip\7z.exe" a -tgzip "%%F.gz" "%%F"
)

echo All files have been compressed!
pause
