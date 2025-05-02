@echo off
setlocal enabledelayedexpansion

:: Default to current directory
set "TARGET_DIR=%cd%"
set "NEXT_IS_FOLDER="

:: Parse command-line arguments
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

:: Resolve full absolute path to the folder
pushd "!TARGET_DIR!" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Could not change directory to !TARGET_DIR!
    exit /b 1
)
set "TARGET_DIR=%cd%"
popd

echo.
echo Target folder resolved to: !TARGET_DIR!
echo.

:: Compress .csv files recursively
pushd "!TARGET_DIR!" >nul
set /a count_csv=0
for /R %%F in (*.csv *.CSV) do (
    echo Compressing CSV: %%F
    "C:\Program Files\7-Zip\7z.exe" a -tgzip -y "%%F.gz" "%%F"
    set /a count_csv+=1
)
echo.
echo Total CSV files compressed: !count_csv!
echo.

:: Compress .geojson files recursively
set /a count_geo=0
for /R %%F in (*.geojson *.GEOJSON) do (
    echo Compressing GEOJSON: %%F
    "C:\Program Files\7-Zip\7z.exe" a -tgzip -y "%%F.gz" "%%F"
    set /a count_geo+=1
)
popd

echo.
echo Total GEOJSON files compressed: !count_geo!
echo.
echo All done. Press any key to exit.
pause
