#!/usr/bin/env python3
"""
Vulnerability Scanner - Scannt Nachbar-Webseiten nach Sicherheitslücken
Verwendung: python scanner.py

Ablauf:
1. Besucht alle URLs in TARGET_URLS mit Selenium (headless)
2. Lädt Page Source und sucht nach .py Dateien
3. Führt Bandit und Semgrep Scans durch
4. Sucht nach hartcodierten Credentials
5. Generiert einen Report
"""

import os
import re
import json
import shutil
import subprocess
from datetime import datetime
from urllib.parse import urljoin, urlparse

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import requests

# === KONFIGURATION ===
# Trage hier die URLs deiner Nachbarn ein
# Unterstützt: HTTP-URLs und GitHub-Repos
TARGET_URLS = [
    "http://192.168.178.198:5001",
    #"http://192.168.1.11:5001",
    #"http://192.168.1.12:5001",
    #"http://192.168.1.13:5001",
    #"https://github.com/username/repo",  # GitHub-Repos werden geklont
]

DOWNLOADS_DIR = "./downloads"
REPORT_FILE = "./scan_report.txt"

# Pfade zu den Security-Tools (falls nicht im PATH)
SEMGREP_PATH = os.path.expanduser("~/.local/bin/semgrep")
if not os.path.exists(SEMGREP_PATH):
    SEMGREP_PATH = os.path.expanduser("~/Library/Python/3.9/bin/semgrep")
if not os.path.exists(SEMGREP_PATH):
    SEMGREP_PATH = "semgrep"  # Fallback auf PATH

# Regex-Patterns für Credential-Suche
CREDENTIAL_PATTERNS = [
    (r'password\s*[=:]\s*["\']([^"\']+)["\']', "Hardcoded Password"),
    (r'passwd\s*[=:]\s*["\']([^"\']+)["\']', "Hardcoded Password"),
    (r'api[_-]?key\s*[=:]\s*["\']([^"\']+)["\']', "API Key"),
    (r'secret[_-]?key\s*[=:]\s*["\']([^"\']+)["\']', "Secret Key"),
    (r'token\s*[=:]\s*["\']([^"\']+)["\']', "Token"),
    (r'db[_-]?password\s*[=:]\s*["\']([^"\']+)["\']', "Database Password"),
    (r'mysql://[^:]+:([^@]+)@', "MySQL Connection String"),
    (r'postgresql://[^:]+:([^@]+)@', "PostgreSQL Connection String"),
]


def setup_selenium():
    """Initialisiert Selenium WebDriver im Headless-Modus."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(30)
    return driver


def download_page_source(driver, url, target_dir):
    """Lädt den HTML Page Source einer URL herunter."""
    try:
        driver.get(url)
        page_source = driver.page_source

        # Speichere Page Source
        html_path = os.path.join(target_dir, "page.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(page_source)

        print(f"  [+] Page Source gespeichert: {html_path}")
        return page_source
    except Exception as e:
        print(f"  [-] Fehler beim Laden von {url}: {e}")
        return None


def clone_github_repo(github_url, target_dir):
    """Klont ein GitHub-Repository."""
    try:
        # Konvertiere GitHub-URL zu git-URL
        if "github.com" in github_url:
            git_url = github_url.rstrip('/') + ".git"
            if not git_url.startswith("https://"):
                git_url = "https://" + git_url.split("://")[-1]
        else:
            git_url = github_url

        print(f"  [*] Klone Repository: {git_url}")
        cmd = ["git", "clone", "--depth", "1", git_url, target_dir]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode == 0:
            print(f"  [+] Repository erfolgreich geklont")
            return True
        else:
            print(f"  [-] Git clone Fehler: {result.stderr}")
            return False
    except Exception as e:
        print(f"  [-] Fehler beim Klonen: {e}")
        return False


def find_and_download_files(driver, base_url, target_dir):
    """Sucht nach .py und .zip Dateien und lädt diese herunter."""
    downloaded_files = []

    try:
        # ZUERST: Prüfe ob /source Endpoint existiert
        source_url = urljoin(base_url, "/source")
        print(f"  [*] Prüfe /source Endpoint: {source_url}")
        try:
            driver.get(source_url)
            page_source = driver.page_source

            if "Index of" in page_source or "source" in driver.current_url:
                print("  [+] /source Endpoint gefunden!")
                # Extrahiere alle .py Links
                py_links = re.findall(r'href="([^"]*\.py[^"]*)"', page_source)
                py_links += re.findall(r'href="(/source/[^"]+)"', page_source)

                for py_link in py_links:
                    try:
                        full_url = urljoin(base_url, py_link)
                        filename = os.path.basename(urlparse(py_link).path)
                        if not filename.endswith('.py'):
                            filename += '.py'

                        response = requests.get(full_url, timeout=10)
                        if response.status_code == 200:
                            # Extrahiere Code aus <pre> Tags falls vorhanden
                            content = response.text
                            pre_match = re.search(r'<pre>(.*?)</pre>', content, re.DOTALL)
                            if pre_match:
                                content = pre_match.group(1)
                            # HTML-Entities dekodieren
                            content = content.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')

                            file_path = os.path.join(target_dir, filename)
                            with open(file_path, "w", encoding="utf-8") as f:
                                f.write(content)
                            downloaded_files.append(file_path)
                            print(f"  [+] Source heruntergeladen: {filename}")
                    except Exception as e:
                        print(f"  [-] Fehler beim Download von {py_link}: {e}")
        except Exception as e:
            print(f"  [-] /source Endpoint nicht verfügbar: {e}")

        # Zurück zur Hauptseite
        driver.get(base_url)

        # Finde alle Links auf der Seite
        links = driver.find_elements(By.TAG_NAME, "a")
        hrefs = []

        for link in links:
            href = link.get_attribute("href")
            if href:
                hrefs.append(href)

        # Suche nach interessanten Dateien
        for href in hrefs:
            if href.endswith(('.py', '.zip', '.tar.gz', '.txt')):
                try:
                    full_url = urljoin(base_url, href)
                    filename = os.path.basename(urlparse(href).path)

                    # Download via requests
                    response = requests.get(full_url, timeout=10)
                    if response.status_code == 200:
                        file_path = os.path.join(target_dir, filename)
                        with open(file_path, "wb") as f:
                            f.write(response.content)
                        downloaded_files.append(file_path)
                        print(f"  [+] Datei heruntergeladen: {filename}")
                except Exception as e:
                    print(f"  [-] Fehler beim Download von {href}: {e}")

        # Prüfe auf Directory Listing (Apache/nginx Style)
        page_source = driver.page_source
        if "Index of" in page_source or "Directory listing" in page_source:
            print("  [!] Directory Listing gefunden!")
            # Extrahiere alle .py Dateien aus dem Listing
            py_files = re.findall(r'href="([^"]+\.py)"', page_source)
            for py_file in py_files:
                try:
                    full_url = urljoin(base_url, py_file)
                    response = requests.get(full_url, timeout=10)
                    if response.status_code == 200:
                        file_path = os.path.join(target_dir, os.path.basename(py_file))
                        with open(file_path, "wb") as f:
                            f.write(response.content)
                        downloaded_files.append(file_path)
                        print(f"  [+] Python-Datei heruntergeladen: {py_file}")
                except Exception as e:
                    print(f"  [-] Fehler: {e}")

    except Exception as e:
        print(f"  [-] Fehler beim Suchen nach Dateien: {e}")

    return downloaded_files


def run_bandit(target_dir):
    """Führt Bandit Security Scanner auf dem Zielverzeichnis aus."""
    results = {"tool": "bandit", "findings": [], "error": None}

    # Prüfe ob Python-Dateien vorhanden sind
    py_files = [f for f in os.listdir(target_dir) if f.endswith('.py')]
    if not py_files:
        results["error"] = "Keine Python-Dateien gefunden"
        return results

    try:
        cmd = ["bandit", "-r", target_dir, "-f", "json", "-q"]
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if process.stdout:
            bandit_output = json.loads(process.stdout)
            results["findings"] = bandit_output.get("results", [])
            results["metrics"] = bandit_output.get("metrics", {})
    except FileNotFoundError:
        results["error"] = "Bandit nicht installiert (pip install bandit)"
    except subprocess.TimeoutExpired:
        results["error"] = "Bandit Timeout"
    except json.JSONDecodeError:
        results["error"] = "Bandit Output konnte nicht geparst werden"
    except Exception as e:
        results["error"] = str(e)

    return results


def run_semgrep(target_dir):
    """Führt Semgrep Security Scanner auf dem Zielverzeichnis aus."""
    results = {"tool": "semgrep", "findings": [], "error": None}

    # Prüfe ob Dateien vorhanden sind
    files = os.listdir(target_dir)
    if not files:
        results["error"] = "Keine Dateien gefunden"
        return results

    try:
        cmd = [
            SEMGREP_PATH,
            "--config", "auto",
            "--json",
            "--quiet",
            target_dir
        ]
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if process.stdout:
            semgrep_output = json.loads(process.stdout)
            results["findings"] = semgrep_output.get("results", [])
    except FileNotFoundError:
        results["error"] = "Semgrep nicht installiert (pip install semgrep)"
    except subprocess.TimeoutExpired:
        results["error"] = "Semgrep Timeout"
    except json.JSONDecodeError:
        results["error"] = "Semgrep Output konnte nicht geparst werden"
    except Exception as e:
        results["error"] = str(e)

    return results


def scan_for_credentials(target_dir):
    """Sucht nach hartcodierten Credentials in allen Dateien."""
    findings = []

    for filename in os.listdir(target_dir):
        file_path = os.path.join(target_dir, filename)
        if not os.path.isfile(file_path):
            continue

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            for pattern, finding_type in CREDENTIAL_PATTERNS:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Finde Zeilennummer
                    line_num = content[:match.start()].count('\n') + 1
                    findings.append({
                        "type": finding_type,
                        "file": filename,
                        "line": line_num,
                        "match": match.group(0)[:100]  # Truncate für Ausgabe
                    })
        except Exception as e:
            print(f"  [-] Fehler beim Scannen von {filename}: {e}")

    return findings


def generate_report(all_results):
    """Generiert einen zusammenfassenden Report."""
    report_lines = []
    report_lines.append("=" * 70)
    report_lines.append("VULNERABILITY SCAN REPORT")
    report_lines.append(f"Generiert: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 70)
    report_lines.append("")

    total_findings = 0

    for target_result in all_results:
        url = target_result["url"]
        report_lines.append(f"\n{'='*70}")
        report_lines.append(f"TARGET: {url}")
        report_lines.append(f"{'='*70}")

        if target_result.get("error"):
            report_lines.append(f"[ERROR] {target_result['error']}")
            continue

        # Bandit Findings
        bandit = target_result.get("bandit", {})
        report_lines.append(f"\n[BANDIT SCAN]")
        if bandit.get("error"):
            report_lines.append(f"  Error: {bandit['error']}")
        else:
            findings = bandit.get("findings", [])
            report_lines.append(f"  Findings: {len(findings)}")
            for f in findings[:10]:  # Maximal 10 anzeigen
                report_lines.append(f"    - [{f.get('severity', 'UNKNOWN')}] {f.get('issue_text', 'N/A')}")
                report_lines.append(f"      File: {f.get('filename', 'N/A')}:{f.get('line_number', '?')}")
            total_findings += len(findings)

        # Semgrep Findings
        semgrep = target_result.get("semgrep", {})
        report_lines.append(f"\n[SEMGREP SCAN]")
        if semgrep.get("error"):
            report_lines.append(f"  Error: {semgrep['error']}")
        else:
            findings = semgrep.get("findings", [])
            report_lines.append(f"  Findings: {len(findings)}")
            for f in findings[:10]:
                report_lines.append(f"    - [{f.get('extra', {}).get('severity', 'UNKNOWN')}] {f.get('check_id', 'N/A')}")
                report_lines.append(f"      File: {f.get('path', 'N/A')}:{f.get('start', {}).get('line', '?')}")
            total_findings += len(findings)

        # Credential Findings
        creds = target_result.get("credentials", [])
        report_lines.append(f"\n[CREDENTIAL SCAN]")
        report_lines.append(f"  Findings: {len(creds)}")
        for c in creds[:10]:
            report_lines.append(f"    - [{c['type']}] {c['file']}:{c['line']}")
            report_lines.append(f"      Match: {c['match']}")
        total_findings += len(creds)

    report_lines.append(f"\n{'='*70}")
    report_lines.append(f"ZUSAMMENFASSUNG: {total_findings} Schwachstellen gefunden")
    report_lines.append(f"{'='*70}")

    report_text = "\n".join(report_lines)

    # Ausgabe in Konsole
    print(report_text)

    # Speichere Report
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(report_text)

    print(f"\n[+] Report gespeichert: {REPORT_FILE}")

    return total_findings


def main():
    """Hauptfunktion - führt den kompletten Scan durch."""
    print("=" * 70)
    print("VULNERABILITY SCANNER")
    print("Scannt Nachbar-Webseiten nach Sicherheitslücken")
    print("=" * 70)
    print(f"\nZiele: {len(TARGET_URLS)} URLs")
    print(f"Downloads: {DOWNLOADS_DIR}")
    print("")

    # Erstelle/Leere Downloads-Verzeichnis
    if os.path.exists(DOWNLOADS_DIR):
        shutil.rmtree(DOWNLOADS_DIR)
    os.makedirs(DOWNLOADS_DIR)

    # Initialisiere Selenium
    print("[*] Initialisiere Selenium WebDriver...")
    driver = setup_selenium()

    all_results = []

    try:
        for idx, url in enumerate(TARGET_URLS):
            print(f"\n[{idx+1}/{len(TARGET_URLS)}] Scanne: {url}")
            print("-" * 50)

            target_result = {"url": url}
            target_dir = os.path.join(DOWNLOADS_DIR, f"target_{idx}")
            os.makedirs(target_dir, exist_ok=True)

            # Prüfe ob es eine GitHub-URL ist
            if "github.com" in url:
                print("  [*] GitHub-Repository erkannt")
                if clone_github_repo(url, target_dir):
                    # Zähle heruntergeladene Python-Dateien
                    py_count = sum(1 for root, dirs, files in os.walk(target_dir)
                                   for f in files if f.endswith('.py'))
                    print(f"  [*] {py_count} Python-Dateien im Repository")
                else:
                    target_result["error"] = "Konnte Repository nicht klonen"
                    all_results.append(target_result)
                    continue
            else:
                # 1. Download Page Source (für normale URLs)
                page_source = download_page_source(driver, url, target_dir)
                if not page_source:
                    target_result["error"] = "Konnte Seite nicht laden"
                    all_results.append(target_result)
                    continue

                # 2. Suche und downloade .py Dateien
                downloaded = find_and_download_files(driver, url, target_dir)
                print(f"  [*] {len(downloaded)} Dateien heruntergeladen")

            # 3. Bandit Scan
            print("  [*] Führe Bandit Scan durch...")
            target_result["bandit"] = run_bandit(target_dir)

            # 4. Semgrep Scan
            print("  [*] Führe Semgrep Scan durch...")
            target_result["semgrep"] = run_semgrep(target_dir)

            # 5. Credential Scan
            print("  [*] Suche nach Credentials...")
            target_result["credentials"] = scan_for_credentials(target_dir)

            all_results.append(target_result)

    finally:
        driver.quit()
        print("\n[*] Selenium beendet")

    # Generiere Report
    print("\n" + "=" * 70)
    total = generate_report(all_results)

    print(f"\n{'='*70}")
    print(f"SCAN ABGESCHLOSSEN - {total} Schwachstellen gefunden")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
