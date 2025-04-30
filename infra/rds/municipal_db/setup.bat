@echo off
REM Load .env variables manually
for /f "tokens=1,2 delims==" %%A in (.env) do (
    set %%A=%%B
)

REM Run psql using those env vars
psql -h %PGHOST% -U %PGUSER% -d %PGDATABASE% -p %PGPORT% -f init_all.sql
