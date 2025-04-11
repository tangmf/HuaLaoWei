@echo off
echo Compressing all .csv and .geojson files to .gz using 7-Zip...

REM Compress .csv files
for /R %%F in (*.csv) do (
    echo Processing CSV: %%F
    "C:\Program Files\7-Zip\7z.exe" a -tgzip "%%F.gz" "%%F"
)

REM Compress .geojson files
for /R %%F in (*.geojson) do (
    echo Processing GEOJSON: %%F
    "C:\Program Files\7-Zip\7z.exe" a -tgzip "%%F.gz" "%%F"
)

echo Done!
pause
