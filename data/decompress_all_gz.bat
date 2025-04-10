@echo off
echo Decompressing all .gz files in the current directory and subdirectories...

for /R %%F in (*.gz) do (
    echo Processing: %%F
    gzip -dk "%%F"
)

echo Done!
pause
