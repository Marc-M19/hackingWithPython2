#!/usr/bin/env python3
"""
Security Scanner - Scannt Webseiten auf Schwachstellen

Verwendung:
    python scanner.py

Logik:
    A) Selenium besucht URL, prueft auf Directory Listing
       -> Wenn Directory Listing: Alle .py, .json, .txt, .env Dateien laden
    B) Brute Force: Probiert immer bekannte Pfade durch
       -> /app.py, /.env, /.git/config, etc.
    C) Alles mit Status 200 wird gespeichert
    D) Bandit/Semgrep/Safety scannen den heruntergeladenen Code
"""

import json
import os
import subprocess
import sys
import time
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, urljoin

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import TimeoutException, WebDriverException
except ImportError:
    print("ERROR: Selenium nicht installiert!")
    print("       pip install selenium")
    sys.exit(1)

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: requests oder beautifulsoup4 nicht installiert!")
    print("       pip install requests beautifulsoup4")
    sys.exit(1)


class SecurityScanner:
    """Haupt-Scanner-Klasse"""

    # Brute Force Liste - diese Pfade werden IMMER probiert
    BRUTE_FORCE_PATHS = [
        # Python Files
        "app.py",
        "main.py",
        "server.py",
        "index.py",
        "wsgi.py",
        "manage.py",
        "config.py",
        "settings.py",
        "database.py",
        "models.py",
        "views.py",
        "routes.py",
        "utils.py",
        "helpers.py",
        "auth.py",
        "api.py",

        # Config & Secrets (WICHTIG!)
        ".env",
        ".env.local",
        ".env.production",
        ".env.development",
        "config.json",
        "config.yaml",
        "config.yml",
        "secrets.json",
        "credentials.json",
        ".htpasswd",

        # Git (Klassiker!)
        ".git/config",
        ".git/HEAD",
        ".git/index",
        ".gitignore",

        # Dependencies
        "requirements.txt",
        "Pipfile",
        "Pipfile.lock",
        "package.json",
        "package-lock.json",
        "composer.json",

        # Backups & Logs
        "backup.sql",
        "dump.sql",
        "database.sql",
        "debug.log",
        "error.log",
        "app.log",

        # Docker
        "Dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",

        # Andere
        "README.md",
        "TODO.txt",
        "notes.txt",
        ".DS_Store",
        "Makefile",
        "schema.sql",
    ]

    # Dateiendungen fuer Directory Listing
    INTERESTING_EXTENSIONS = ['.py', '.json', '.txt', '.env', '.yml', '.yaml', '.sql', '.sh', '.conf', '.cfg', '.ini']

    def __init__(self, config_path="config.json"):
        self.script_dir = Path(__file__).parent
        self.config = self._load_config(config_path)
        self.results_dir = self.script_dir / self.config.get("output_dir", "results")
        self.download_dir = self.results_dir / "downloaded_code"
        self.driver = None
        self.all_findings = []
        self.downloaded_files_log = []  # Track what was downloaded

        # Ordner erstellen
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.download_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self, config_path):
        """Konfiguration aus JSON laden"""
        config_file = self.script_dir / config_path
        if not config_file.exists():
            print(f"ERROR: Config-Datei nicht gefunden: {config_file}")
            print("       Erstelle config.json mit deinen URLs!")
            sys.exit(1)

        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _init_webdriver(self):
        """Selenium WebDriver initialisieren"""
        options = ChromeOptions()

        selenium_config = self.config.get("selenium", {})
        if selenium_config.get("headless", True):
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--ignore-certificate-errors")

        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(selenium_config.get("timeout", 30))
            return True
        except WebDriverException as e:
            print(f"ERROR: Chrome WebDriver konnte nicht gestartet werden!")
            print(f"       Stelle sicher, dass Chrome und ChromeDriver installiert sind.")
            print(f"       Details: {e}")
            return False

    def _close_webdriver(self):
        """WebDriver schliessen"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None

    def _is_directory_listing(self, page_source):
        """
        Prueft ob die Seite ein Directory Listing ist.

        Typische Merkmale:
        - Viele <a> Tags mit Dateiendungen
        - "Index of" im Titel oder Body
        - Apache/Nginx Directory Listing Struktur
        """
        soup = BeautifulSoup(page_source, 'html.parser')

        # Check 1: "Index of" im Titel oder h1
        title = soup.find('title')
        h1 = soup.find('h1')

        if title and 'index of' in title.text.lower():
            return True
        if h1 and 'index of' in h1.text.lower():
            return True

        # Check 2: Viele Links mit Dateiendungen
        all_links = soup.find_all('a', href=True)
        file_links = 0

        for link in all_links:
            href = link['href']
            # Ignoriere Parent-Directory und Anker-Links
            if href in ['../', '../', '#', '/']:
                continue
            # Zaehle Links die auf Dateien zeigen
            if any(href.endswith(ext) for ext in self.INTERESTING_EXTENSIONS):
                file_links += 1
            # Oder die wie Dateien aussehen (mit Punkt und Endung)
            if re.match(r'.*\.\w{1,5}$', href):
                file_links += 1

        # Wenn mehr als 3 Datei-Links -> wahrscheinlich Directory Listing
        if file_links >= 3:
            return True

        # Check 3: Typische Apache/Nginx Directory Listing Elemente
        if soup.find('pre') and len(all_links) > 5:
            return True

        return False

    def _extract_files_from_directory_listing(self, page_source, base_url):
        """
        Extrahiert alle interessanten Datei-Links aus einem Directory Listing.
        """
        soup = BeautifulSoup(page_source, 'html.parser')
        files_to_download = []

        for link in soup.find_all('a', href=True):
            href = link['href']

            # Ignoriere Navigation
            if href in ['../', '../', '#', '/', './', '.']:
                continue

            # Pruefe auf interessante Endungen
            is_interesting = any(href.endswith(ext) for ext in self.INTERESTING_EXTENSIONS)

            # Oder .py Dateien explizit
            if href.endswith('.py') or href.endswith('.env') or href.endswith('.json'):
                is_interesting = True

            if is_interesting:
                # Vollstaendige URL erstellen
                full_url = urljoin(base_url, href)
                files_to_download.append({
                    'url': full_url,
                    'filename': href.split('/')[-1]
                })

        return files_to_download

    def _download_file(self, url, target_dir, filename=None):
        """
        Laedt eine einzelne Datei herunter wenn Status 200.
        Returns: (success, filepath, content_type)
        """
        try:
            response = requests.get(url, timeout=10, verify=False, allow_redirects=True)

            if response.status_code == 200:
                # Pruefe ob es nicht eine HTML-Fehlerseite ist
                content = response.text
                content_type = response.headers.get('Content-Type', '')

                # Wenn es HTML ist aber wir eine .py Datei erwartet haben -> skip
                if filename and filename.endswith('.py'):
                    if content.strip().startswith('<!DOCTYPE') or content.strip().startswith('<html'):
                        return False, None, 'html-redirect'

                # Dateiname bestimmen
                if not filename:
                    filename = Path(urlparse(url).path).name or "unknown"

                # Sanitize filename (behalte aber Punkte fuer Endungen)
                safe_filename = re.sub(r'[^\w\-_\.]', '_', filename)
                if not safe_filename or safe_filename == '_':
                    safe_filename = f"file_{hash(url) % 10000}"

                # Spezialfall: .git/config -> git_config
                if '/' in filename:
                    safe_filename = filename.replace('/', '_')

                filepath = target_dir / safe_filename

                # Speichern
                with open(filepath, 'w', encoding='utf-8', errors='ignore') as f:
                    f.write(content)

                return True, filepath, content_type

        except Exception as e:
            pass

        return False, None, None

    def _download_source(self, url, target_dir):
        """
        Neue Download-Logik:
        A) Selenium besucht URL, prueft auf Directory Listing
        B) Brute Force bekannte Pfade
        C) Alles mit Status 200 speichern
        """
        result = {
            "url": url,
            "status": "pending",
            "files": [],
            "directory_listing": False,
            "brute_force_hits": [],
            "error": None
        }

        base_url = url.rstrip('/')
        parsed = urlparse(url)
        base_origin = f"{parsed.scheme}://{parsed.netloc}"

        # ===== SCHRITT A: Selenium besucht URL =====
        print("\n      [A] Selenium: Besuche URL...", end=" ")
        try:
            self.driver.get(url)
            time.sleep(2)
            page_source = self.driver.page_source

            # Speichere HTML
            html_file = target_dir / "index.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(page_source)
            result["files"].append(str(html_file))

            # Pruefe auf Directory Listing
            if self._is_directory_listing(page_source):
                print("DIRECTORY LISTING GEFUNDEN!")
                result["directory_listing"] = True

                # Alle interessanten Dateien extrahieren und herunterladen
                files_to_download = self._extract_files_from_directory_listing(page_source, url)
                print(f"          Gefunden: {len(files_to_download)} interessante Dateien")

                for file_info in files_to_download:
                    success, filepath, _ = self._download_file(
                        file_info['url'],
                        target_dir,
                        file_info['filename']
                    )
                    if success:
                        result["files"].append(str(filepath))
                        print(f"          -> {file_info['filename']}")
            else:
                print("OK (kein Directory Listing)")

        except TimeoutException:
            print("TIMEOUT")
            result["error"] = "Timeout beim Laden"
        except Exception as e:
            print(f"FEHLER: {e}")
            result["error"] = str(e)

        # ===== SCHRITT B: Brute Force bekannte Pfade =====
        print("      [B] Brute Force: Probiere bekannte Pfade...")
        hits = 0

        for path in self.BRUTE_FORCE_PATHS:
            # Versuche verschiedene Varianten
            urls_to_try = [
                f"{base_origin}/{path}",
                f"{base_url}/{path}",
            ]

            for try_url in urls_to_try:
                success, filepath, content_type = self._download_file(try_url, target_dir, path)

                if success and filepath:
                    # Pruefe ob Datei nicht leer ist
                    if filepath.stat().st_size > 0:
                        result["files"].append(str(filepath))
                        result["brute_force_hits"].append(path)
                        hits += 1

                        # Markiere besonders interessante Funde
                        if path in ['.env', '.git/config', 'credentials.json', 'secrets.json']:
                            print(f"          !!! KRITISCH: {path} gefunden !!!")
                        else:
                            print(f"          -> {path}")
                        break  # Naechster Pfad

        print(f"          Brute Force Treffer: {hits}")

        # ===== SCHRITT C: Zusammenfassung =====
        # Dedupliziere Dateien
        result["files"] = list(set(result["files"]))

        if result["files"]:
            result["status"] = "success"
        else:
            result["status"] = "no_files"

        return result

    def _run_bandit(self, target_dir):
        """Bandit Security Scanner ausfuehren"""
        findings = []

        # Pruefen ob Python-Dateien existieren
        python_files = list(target_dir.glob("**/*.py"))
        if not python_files:
            return findings

        try:
            cmd = [
                sys.executable, "-m", "bandit",
                "-r", str(target_dir),
                "-f", "json",
                "-ll",  # Low severity
                "-ii"   # Low confidence
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.stdout:
                try:
                    output = json.loads(result.stdout)
                    for issue in output.get("results", []):
                        findings.append({
                            "scanner": "bandit",
                            "severity": issue.get("issue_severity", "LOW").lower(),
                            "confidence": issue.get("issue_confidence", "MEDIUM").lower(),
                            "type": issue.get("test_id", "unknown"),
                            "file": issue.get("filename", ""),
                            "line": issue.get("line_number", 0),
                            "code": issue.get("code", ""),
                            "description": issue.get("issue_text", "")
                        })
                except json.JSONDecodeError:
                    pass

        except subprocess.TimeoutExpired:
            print("      Bandit: Timeout")
        except FileNotFoundError:
            print("      Bandit: Nicht installiert (pip install bandit)")
        except Exception as e:
            print(f"      Bandit: Fehler - {e}")

        return findings

    def _run_semgrep(self, target_dir):
        """Semgrep Security Scanner ausfuehren"""
        findings = []

        try:
            cmd = [
                "semgrep",
                "--config", "auto",
                "--json",
                "--quiet",
                str(target_dir)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=180
            )

            if result.stdout:
                try:
                    output = json.loads(result.stdout)
                    for match in output.get("results", []):
                        severity = match.get("extra", {}).get("severity", "INFO")
                        severity_map = {"INFO": "low", "WARNING": "medium", "ERROR": "high"}

                        findings.append({
                            "scanner": "semgrep",
                            "severity": severity_map.get(severity.upper(), "low"),
                            "confidence": "high",
                            "type": match.get("check_id", "unknown"),
                            "file": match.get("path", ""),
                            "line": match.get("start", {}).get("line", 0),
                            "code": match.get("extra", {}).get("lines", ""),
                            "description": match.get("extra", {}).get("message", "")
                        })
                except json.JSONDecodeError:
                    pass

        except subprocess.TimeoutExpired:
            print("      Semgrep: Timeout")
        except FileNotFoundError:
            print("      Semgrep: Nicht installiert (pip install semgrep)")
        except Exception as e:
            print(f"      Semgrep: Fehler - {e}")

        return findings

    def _run_safety(self, target_dir):
        """Safety Dependency Scanner ausfuehren"""
        findings = []

        # Pruefen ob requirements.txt existiert
        req_file = target_dir / "requirements.txt"
        if not req_file.exists():
            return findings

        try:
            cmd = [
                sys.executable, "-m", "safety", "check",
                "-r", str(req_file),
                "--json"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            output_text = result.stdout or result.stderr
            if output_text:
                try:
                    output = json.loads(output_text)
                    vulnerabilities = []
                    if isinstance(output, dict):
                        vulnerabilities = output.get("vulnerabilities", [])
                    elif isinstance(output, list):
                        vulnerabilities = output

                    for vuln in vulnerabilities:
                        if isinstance(vuln, dict):
                            findings.append({
                                "scanner": "safety",
                                "severity": "high",
                                "confidence": "high",
                                "type": f"CVE-{vuln.get('vulnerability_id', 'unknown')}",
                                "file": "requirements.txt",
                                "line": 0,
                                "code": f"{vuln.get('package_name', '')}=={vuln.get('analyzed_version', '')}",
                                "description": vuln.get('advisory', '')[:200] if vuln.get('advisory') else ''
                            })
                except json.JSONDecodeError:
                    pass

        except subprocess.TimeoutExpired:
            print("      Safety: Timeout")
        except FileNotFoundError:
            print("      Safety: Nicht installiert (pip install safety)")
        except Exception as e:
            print(f"      Safety: Fehler - {e}")

        return findings

    def _check_for_secrets(self, target_dir):
        """
        Einfacher Secret-Scanner - sucht nach Passwoertern in Dateien.
        """
        findings = []

        # Patterns fuer Secrets
        secret_patterns = [
            (r'password\s*[=:]\s*["\']([^"\']+)["\']', 'Hardcoded Password'),
            (r'passwd\s*[=:]\s*["\']([^"\']+)["\']', 'Hardcoded Password'),
            (r'api[_-]?key\s*[=:]\s*["\']([^"\']+)["\']', 'API Key'),
            (r'secret[_-]?key\s*[=:]\s*["\']([^"\']+)["\']', 'Secret Key'),
            (r'token\s*[=:]\s*["\']([^"\']+)["\']', 'Token'),
            (r'aws[_-]?access[_-]?key', 'AWS Access Key'),
            (r'private[_-]?key', 'Private Key'),
            (r'DB_PASSWORD\s*=\s*(.+)', 'Database Password'),
            (r'DATABASE_URL\s*=\s*(.+)', 'Database URL'),
        ]

        # Durchsuche alle Textdateien
        for filepath in target_dir.glob("**/*"):
            if filepath.is_file() and filepath.suffix in ['.py', '.env', '.json', '.txt', '.yml', '.yaml', '.cfg', '.ini', '.conf', '']:
                try:
                    content = filepath.read_text(encoding='utf-8', errors='ignore')

                    for pattern, secret_type in secret_patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            line_num = content[:match.start()].count('\n') + 1
                            findings.append({
                                "scanner": "secret-scanner",
                                "severity": "high",
                                "confidence": "medium",
                                "type": secret_type,
                                "file": str(filepath),
                                "line": line_num,
                                "code": match.group(0)[:100],
                                "description": f"Moegliches Secret gefunden: {secret_type}"
                            })
                except:
                    pass

        return findings

    def _generate_report(self):
        """Report generieren (Text + JSON)"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        stats = {"high": 0, "medium": 0, "low": 0}
        for finding in self.all_findings:
            severity = finding.get("severity", "low")
            if severity in stats:
                stats[severity] += 1

        report_lines = [
            "=" * 60,
            "SECURITY SCANNER REPORT",
            f"Erstellt: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}",
            "=" * 60,
            "",
            f"Gesamt Findings: {len(self.all_findings)}",
            f"  HIGH:   {stats['high']}",
            f"  MEDIUM: {stats['medium']}",
            f"  LOW:    {stats['low']}",
            "",
            "-" * 60,
            "DETAILS",
            "-" * 60,
            ""
        ]

        findings_by_url = {}
        for finding in self.all_findings:
            url = finding.get("url", "unknown")
            if url not in findings_by_url:
                findings_by_url[url] = []
            findings_by_url[url].append(finding)

        for url, findings in findings_by_url.items():
            report_lines.append(f"\nURL: {url}")
            report_lines.append("-" * 40)

            for f in findings:
                severity = f.get("severity", "low").upper()
                scanner = f.get("scanner", "unknown")
                ftype = f.get("type", "unknown")
                file_path = f.get("file", "")
                line = f.get("line", 0)
                desc = f.get("description", "")[:100]
                code = f.get("code", "")[:80]

                report_lines.append(f"  [{severity}] {ftype}")
                report_lines.append(f"    Scanner: {scanner}")
                if file_path:
                    report_lines.append(f"    Datei: {file_path}:{line}")
                if code:
                    report_lines.append(f"    Code: {code}")
                if desc:
                    report_lines.append(f"    {desc}")
                report_lines.append("")

        report_file = self.results_dir / f"scan_report_{timestamp}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(report_lines))

        latest_report = self.results_dir / "scan_report.txt"
        with open(latest_report, 'w', encoding='utf-8') as f:
            f.write("\n".join(report_lines))

        json_data = {
            "timestamp": datetime.now().isoformat(),
            "statistics": stats,
            "total_findings": len(self.all_findings),
            "findings": self.all_findings,
            "downloaded_files": self.downloaded_files_log
        }

        json_file = self.results_dir / f"scan_results_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        latest_json = self.results_dir / "scan_results.json"
        with open(latest_json, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        return report_file, json_file, stats

    def run(self):
        """Haupt-Scan durchfuehren"""
        print("=" * 60)
        print("       SECURITY SCANNER")
        print("       Directory Listing + Brute Force Edition")
        print("=" * 60)
        print()

        urls = self.config.get("urls", [])
        if not urls:
            print("ERROR: Keine URLs in config.json definiert!")
            return

        if len(urls) < 4:
            print(f"WARNUNG: Nur {len(urls)} URLs definiert (empfohlen: min. 4)")

        print(f"Zu scannende URLs: {len(urls)}")
        print(f"Brute Force Pfade: {len(self.BRUTE_FORCE_PATHS)}")
        print()

        # WebDriver initialisieren
        print("Initialisiere Browser...")
        if not self._init_webdriver():
            return

        scanners_config = self.config.get("scanners", {})

        try:
            for idx, url in enumerate(urls, 1):
                print(f"\n{'='*60}")
                print(f"[{idx}/{len(urls)}] TARGET: {url}")
                print("=" * 60)

                # Zielordner
                url_hash = re.sub(r'[^\w]', '_', url)[:50]
                target_dir = self.download_dir / f"url_{idx}_{url_hash}"
                target_dir.mkdir(parents=True, exist_ok=True)

                # Download (A + B + C)
                download_result = self._download_source(url, target_dir)

                # Log
                self.downloaded_files_log.append({
                    "url": url,
                    "files": download_result["files"],
                    "directory_listing": download_result["directory_listing"],
                    "brute_force_hits": download_result["brute_force_hits"]
                })

                print(f"\n      [C] Download: {len(download_result['files'])} Dateien gespeichert")

                if download_result["directory_listing"]:
                    print("          (via Directory Listing)")
                if download_result["brute_force_hits"]:
                    print(f"          Brute Force Hits: {', '.join(download_result['brute_force_hits'])}")

                if not download_result["files"]:
                    print("          Keine Dateien zum Scannen!")
                    continue

                # ===== SCHRITT D: Scans =====
                print("\n      [D] Security Scans:")
                url_findings = []

                # Secret Scanner (eigener, immer aktiv)
                print("          Secret Scanner...", end=" ")
                secret_findings = self._check_for_secrets(target_dir)
                for f in secret_findings:
                    f["url"] = url
                url_findings.extend(secret_findings)
                print(f"{len(secret_findings)} findings")

                # Bandit
                if scanners_config.get("bandit", True):
                    print("          Bandit...", end=" ")
                    bandit_findings = self._run_bandit(target_dir)
                    for f in bandit_findings:
                        f["url"] = url
                    url_findings.extend(bandit_findings)
                    print(f"{len(bandit_findings)} findings")

                # Semgrep
                if scanners_config.get("semgrep", True):
                    print("          Semgrep...", end=" ")
                    semgrep_findings = self._run_semgrep(target_dir)
                    for f in semgrep_findings:
                        f["url"] = url
                    url_findings.extend(semgrep_findings)
                    print(f"{len(semgrep_findings)} findings")

                # Safety
                if scanners_config.get("safety", True):
                    print("          Safety...", end=" ")
                    safety_findings = self._run_safety(target_dir)
                    for f in safety_findings:
                        f["url"] = url
                    url_findings.extend(safety_findings)
                    print(f"{len(safety_findings)} findings")

                self.all_findings.extend(url_findings)

                print(f"\n      URL Total: {len(url_findings)} findings")

        finally:
            self._close_webdriver()

        # Report
        print("\n" + "=" * 60)
        print("ERGEBNISSE")
        print("=" * 60)

        report_file, json_file, stats = self._generate_report()

        print(f"\nGesamt Findings: {len(self.all_findings)}")
        print(f"  HIGH:   {stats['high']}")
        print(f"  MEDIUM: {stats['medium']}")
        print(f"  LOW:    {stats['low']}")
        print()
        print(f"Report: {report_file}")
        print(f"JSON:   {json_file}")

        # Top Findings
        if self.all_findings:
            print("\n" + "-" * 60)
            print("TOP FINDINGS (max 10)")
            print("-" * 60)

            sorted_findings = sorted(
                self.all_findings,
                key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x.get("severity", "low"), 3)
            )

            for finding in sorted_findings[:10]:
                severity = finding.get("severity", "low").upper()
                scanner = finding.get("scanner", "?")
                ftype = finding.get("type", "unknown")
                url = finding.get("url", "")
                code = finding.get("code", "")[:50]
                print(f"  [{severity}] {ftype} ({scanner})")
                print(f"         URL: {url}")
                if code:
                    print(f"         Code: {code}...")


def main():
    """Hauptfunktion"""
    import warnings
    warnings.filterwarnings('ignore')

    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    scanner = SecurityScanner()
    scanner.run()


if __name__ == "__main__":
    main()
