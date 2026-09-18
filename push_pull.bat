@echo off
cd /d "%~dp0"
git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
    echo ERROR: This folder is not a Git repository
    pause
    exit /b
)

set "evil=false"
set "invalid=false"
:menu
cls
set "choice="
if "%invalid%"=="true" (
    echo Invalid input
    set "invalid=false"
)
for /f "delims=" %%B in ('git branch --show-current') do set "branch=%%B"
echo ===================================
echo      GIT auto commit pull push
echo ===================================
echo Running on branch: %branch%
echo ===================================
if "%evil%"=="false" (
    echo [1] Commit, Pull, Push
) else echo [1] Commit, Pull, Push       \ /
echo [2] Pull, Push              ^|   ^|  
echo [3] Quit                   \_____/
echo ===================================
echo.
set /p choice="Choose an option (1-3): "
if "%choice%"=="1" goto full_sync
if "%choice%"=="2" goto pull_push
if "%choice%"=="3" goto end
if "%choice%"=="4" (
    if "%evil%"=="true" (set "evil=false") else (set "evil=true")
    goto menu
)
set "invalid=true"
goto menu

:full_sync

echo Checking for changes...
for /f %%T in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss_fffffff"') do set "timestamp=%%T"
set "statusFile=%TEMP%\git_status_308198fb8342141930293f7ffc50ed3b19ff73af0f6ed6226db95fb53e92348d_%timestamp%_%RANDOM%.txt"
git status --porcelain --untracked-files=all > "%statusFile%"
set /a changeCount=0
for /f "usebackq delims=" %%A in ("%statusFile%") do (
    set /a changeCount+=1
)
del "%statusFile%"
if %changeCount% EQU 0 (
    echo No changes to commit found.
    goto pull_push
)

if %changeCount% EQU 1 (
    echo Found 1 changed file to commit.
) else (
    echo Found %changeCount% changed files to commit.
)

set /p summary="Enter commit summary (Short. Characters < 50): "
set /p description="Enter commit description (Detailed. Can be left empty for minor commits): "
echo Adding all changed files to commit...
git add .
if errorlevel 1 (
    echo ERROR: Git add failed.
    pause
    goto menu
)
echo Committing changes...
git commit -m "%summary%" -m "%description%"
if errorlevel 1 (
    echo ERROR: Commit failed.
    pause
    goto menu
)
goto pull_push


:pull_push
if "%evil%"=="true" (
    rundll32.exe user32.dll,LockWorkStation
)
echo Pulling latest changes from remote...
git pull
if errorlevel 1 (
    echo ERROR: Pull failed.
    pause
    goto menu
)
echo Pushing changes to remote...
git push
if errorlevel 1 (
    echo ERROR: Push failed.
    pause
    goto menu
)
echo FINISHED
timeout /t 60
if "%evil%"=="true" (
    shutdown /s /t 300
)
goto menu

:end
exit /b