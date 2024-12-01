@echo off

:: Ask for MySQL credentials
set MYSQL_USER=root
set  MYSQL_PASSWORD=2001053597Rex?
set LOCAL_DATABASE_NAME=CoralClientSeller 
set BACKUP_PATH= ./SQLStuff/Backup.sql

:: Create a backup of the local database
echo Creating backup of the local database...
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe" -u %MYSQL_USER% -p%MYSQL_PASSWORD% %LOCAL_DATABASE_NAME% > %BACKUP_PATH%

:: Check if the backup was created successfully
if exist %BACKUP_PATH% (
    echo Backup created successfully at %BACKUP_PATH%.
) else (
    echo Backup failed. Please check the provided path or credentials.
    pause
    exit /b
)

