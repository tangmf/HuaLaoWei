@echo off
echo Compressing all .csv files to .gz using 7-Zip...

for /R %%F in (*.csv) do (
    echo Processing: %%F
    "C:\Program Files\7-Zip\7z.exe" a -tgzip "%%F.gz" "%%F"
)

echo Done!
pause
