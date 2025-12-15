#!/usr/bin/env python3
"""
GitHub Security Scanner - Crawlt GitHub Repos und scannt auf Schwachstellen

Verwendung:
    python github_scanner.py

Logik:
    A) Selenium besucht GitHub Repo-Seite
    B) Crawlt rekursiv durch alle Ordner
    C) Findet alle interessanten Dateien (.py, .json, .env, etc.)
    D) Laedt Raw-Content herunter
    E) Bandit/Semgrep/Safety scannen den heruntergeladenen Code
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
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
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


class GitHubScanner:
    """GitHub Repository Security Scanner"""

    # Interessante Dateiendungen
    INTERESTING_EXTENSIONS = ['.py', '.json', '.env', '.yml', '.yaml', '.sql', '.txt', '.cfg', '.ini', '.conf', '.sh']

    def __init__(self, config_path="config.json"):
        self.script_dir = Path(__file__).parent
        self.config = self._load_config(config_path)
        self.results_dir = self.script_dir / self.config.get("output_dir", "results")
        self.download_dir = self.results_dir / "downloaded_code"
        self.driver = None
        self.all_findings = []
        self.downloaded_files_log = []

        # Ordner erstellen
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.download_dir.mkdir(parents=True, exist_ok=True)

        # File extensions aus config oder default
        self.file_extensions = self.config.get("file_extensions", self.INTERESTING_EXTENSIONS)

    def _load_config(self, config_path):
        """Konfiguration aus JSON laden"""
        config_file = self.script_dir / config_path
        if not config_file.exists():
            print(f"ERROR: Config-Datei nicht gefunden: {config_file}")
            print("       Erstelle config.json mit deinen GitHub Repo URLs!")
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
        # GitHub braucht manchmal User-Agent
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

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

    def _parse_github_url(self, repo_url):
        """
        Parst GitHub URL und extrahiert owner, repo, branch.

        Beispiel:
            https://github.com/Gandalss/Hacking_with_python_2
            -> owner: Gandalss, repo: Hacking_with_python_2, branch: main
        """
        parsed = urlparse(repo_url)
        path_parts = parsed.path.strip('/').split('/')

        if len(path_parts) >= 2:
            owner = path_parts[0]
            repo = path_parts[1]
            # Branch ist standardmaessig main (oder master bei aelteren Repos)
            branch = path_parts[3] if len(path_parts) > 3 else None
            return owner, repo, branch

        return None, None, None

    def _get_default_branch(self, owner, repo):
        """Ermittelt den Default-Branch des Repos (main oder master)"""
        try:
            api_url = f"https://api.github.com/repos/{owner}/{repo}"
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("default_branch", "main")
        except:
            pass
        return "main"

    def _is_interesting_file(self, filename):
        """Prueft ob die Datei interessant ist basierend auf Endung"""
        return any(filename.endswith(ext) for ext in self.file_extensions)

    def _convert_to_raw_url(self, github_url):
        """
        Konvertiert GitHub blob URL zu Raw URL.

        Von: https://github.com/user/repo/blob/main/file.py
        Nach: https://raw.githubusercontent.com/user/repo/main/file.py
        """
        if '/blob/' in github_url:
            raw_url = github_url.replace('github.com', 'raw.githubusercontent.com')
            raw_url = raw_url.replace('/blob/', '/')
            return raw_url
        return github_url

    def _download_raw_file(self, raw_url, target_dir, filename):
        """Laedt eine Datei von GitHub Raw herunter"""
        try:
            response = requests.get(raw_url, timeout=15)

            if response.status_code == 200:
                # Sanitize filename
                safe_filename = re.sub(r'[^\w\-_\.]', '_', filename)
                if '/' in filename:
                    # Bei verschachtelten Pfaden Ordner erstellen
                    safe_filename = filename.replace('/', '_')

                filepath = target_dir / safe_filename

                with open(filepath, 'w', encoding='utf-8', errors='ignore') as f:
                    f.write(response.text)

                return True, filepath

        except Exception as e:
            print(f"          Fehler beim Download: {e}")

        return False, None

    def _crawl_github_repo(self, repo_url, target_dir):
        """
        Crawlt ein GitHub Repository und laedt alle interessanten Dateien herunter.
        Verwendet GitHub API als primaere Methode (zuverlaessiger als Selenium).
        """
        result = {
            "repo": repo_url,
            "status": "pending",
            "files": [],
            "folders_crawled": [],
            "error": None
        }

        owner, repo, _ = self._parse_github_url(repo_url)
        if not owner or not repo:
            result["error"] = "Ungueltige GitHub URL"
            result["status"] = "error"
            return result

        # Default Branch ermitteln
        default_branch = self._get_default_branch(owner, repo)
        print(f"          Default Branch: {default_branch}")

        # Verwende GitHub API fuer zuverlaessiges Crawling
        print(f"          Verwende GitHub API...")

        # Queue fuer zu crawlende Pfade (BFS)
        paths_to_crawl = [""]  # Start mit Root
        crawled_paths = set()

        while paths_to_crawl:
            current_path = paths_to_crawl.pop(0)

            if current_path in crawled_paths:
                continue
            crawled_paths.add(current_path)

            # GitHub Contents API
            if current_path:
                api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{current_path}?ref={default_branch}"
                print(f"          Crawle: /{current_path}")
            else:
                api_url = f"https://api.github.com/repos/{owner}/{repo}/contents?ref={default_branch}"
                print(f"          Crawle: / (Root)")

            result["folders_crawled"].append(current_path or "/")

            try:
                response = requests.get(api_url, timeout=15)

                if response.status_code == 403:
                    print(f"          API Rate Limit - wechsle zu Selenium...")
                    # Fallback zu Selenium bei Rate Limit
                    return self._crawl_github_repo_selenium(repo_url, target_dir, owner, repo, default_branch)

                if response.status_code != 200:
                    print(f"          API Fehler: {response.status_code}")
                    continue

                contents = response.json()

                # Kann eine Liste (Ordner) oder ein Objekt (Datei) sein
                if isinstance(contents, dict):
                    contents = [contents]

                for item in contents:
                    item_type = item.get("type", "")
                    item_name = item.get("name", "")
                    item_path = item.get("path", "")

                    if item_type == "file":
                        # Pruefe ob interessante Datei
                        if self._is_interesting_file(item_name):
                            download_url = item.get("download_url")
                            if download_url:
                                print(f"          -> Lade: {item_path}")
                                success, filepath = self._download_raw_file(download_url, target_dir, item_path)
                                if success:
                                    result["files"].append(str(filepath))

                    elif item_type == "dir":
                        # Ignoriere uninteressante Ordner
                        if item_name.startswith('.') and item_name not in ['.github']:
                            continue
                        if item_name in ['node_modules', '__pycache__', 'venv', '.git', 'dist', 'build']:
                            continue

                        if item_path not in crawled_paths:
                            paths_to_crawl.append(item_path)

            except Exception as e:
                print(f"          FEHLER: {e}")
                continue

        # Status aktualisieren
        if result["files"]:
            result["status"] = "success"
        else:
            result["status"] = "no_files"

        return result

    def _crawl_github_repo_selenium(self, repo_url, target_dir, owner, repo, default_branch):
        """Fallback: Selenium-basiertes Crawling wenn API nicht verfuegbar"""
        result = {
            "repo": repo_url,
            "status": "pending",
            "files": [],
            "folders_crawled": [],
            "error": None
        }

        paths_to_crawl = [""]
        crawled_paths = set()

        while paths_to_crawl:
            current_path = paths_to_crawl.pop(0)

            if current_path in crawled_paths:
                continue
            crawled_paths.add(current_path)

            if current_path:
                page_url = f"https://github.com/{owner}/{repo}/tree/{default_branch}/{current_path}"
                print(f"          [Selenium] Crawle: /{current_path}")
            else:
                page_url = f"https://github.com/{owner}/{repo}"
                print(f"          [Selenium] Crawle: / (Root)")

            result["folders_crawled"].append(current_path or "/")

            try:
                self.driver.get(page_url)
                time.sleep(3)  # Mehr Zeit fuer dynamisches Laden

                # Finde alle Links auf der Seite
                all_links = self.driver.find_elements(By.TAG_NAME, 'a')

                for link in all_links:
                    try:
                        href = link.get_attribute('href')
                        if not href:
                            continue

                        # Nur Links zum gleichen Repo
                        if f"/{owner}/{repo}/" not in href:
                            continue

                        if '/blob/' in href:
                            # Datei
                            filename = href.split('/')[-1]
                            if self._is_interesting_file(filename):
                                raw_url = self._convert_to_raw_url(href)
                                rel_path = href.split(f'/blob/{default_branch}/')[-1] if f'/blob/{default_branch}/' in href else filename

                                print(f"          -> Lade: {rel_path}")
                                success, filepath = self._download_raw_file(raw_url, target_dir, rel_path)
                                if success:
                                    result["files"].append(str(filepath))

                        elif '/tree/' in href and f'/tree/{default_branch}/' in href:
                            # Ordner
                            folder_path = href.split(f'/tree/{default_branch}/')[-1]
                            folder_name = folder_path.split('/')[-1] if folder_path else ""

                            if folder_name.startswith('.') and folder_name not in ['.github']:
                                continue
                            if folder_name in ['node_modules', '__pycache__', 'venv', '.git']:
                                continue

                            if folder_path and folder_path not in crawled_paths:
                                paths_to_crawl.append(folder_path)

                    except:
                        continue

            except TimeoutException:
                print(f"          TIMEOUT bei {current_path}")
            except Exception as e:
                print(f"          FEHLER bei {current_path}: {e}")

        if result["files"]:
            result["status"] = "success"
        else:
            result["status"] = "no_files"

        return result

    def _run_bandit(self, target_dir):
        """Bandit Security Scanner ausfuehren"""
        findings = []

        python_files = list(target_dir.glob("**/*.py"))
        if not python_files:
            return findings

        try:
            cmd = [
                sys.executable, "-m", "bandit",
                "-r", str(target_dir),
                "-f", "json",
                "-ll",
                "-ii"
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

        req_file = target_dir / "requirements.txt"
        if not req_file.exists():
            # Suche auch nach requirements_txt (durch Umbenennung)
            for f in target_dir.glob("*requirements*"):
                if f.is_file():
                    req_file = f
                    break
            else:
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
        """Einfacher Secret-Scanner - sucht nach Passwoertern in Dateien."""
        findings = []

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
            "GITHUB SECURITY SCANNER REPORT",
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

        findings_by_repo = {}
        for finding in self.all_findings:
            repo = finding.get("repo", "unknown")
            if repo not in findings_by_repo:
                findings_by_repo[repo] = []
            findings_by_repo[repo].append(finding)

        for repo, findings in findings_by_repo.items():
            report_lines.append(f"\nREPO: {repo}")
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
        print("       GITHUB SECURITY SCANNER")
        print("       Repository Crawler Edition")
        print("=" * 60)
        print()

        repos = self.config.get("repos", [])
        if not repos:
            print("ERROR: Keine Repos in config.json definiert!")
            return

        # Filtere Platzhalter heraus
        valid_repos = [r for r in repos if "KOLLEGE" not in r and "REPO" not in r.split('/')[-1]]

        if len(valid_repos) < len(repos):
            print(f"HINWEIS: {len(repos) - len(valid_repos)} Platzhalter-URLs uebersprungen")

        if not valid_repos:
            print("ERROR: Keine gueltigen Repo-URLs gefunden!")
            print("       Ersetze die Platzhalter in config.json mit echten GitHub URLs")
            return

        print(f"Zu scannende Repos: {len(valid_repos)}")
        for repo in valid_repos:
            print(f"  - {repo}")
        print()

        # WebDriver initialisieren
        print("Initialisiere Browser...")
        if not self._init_webdriver():
            return

        scanners_config = self.config.get("scanners", {})

        try:
            for idx, repo_url in enumerate(valid_repos, 1):
                print(f"\n{'='*60}")
                print(f"[{idx}/{len(valid_repos)}] REPO: {repo_url}")
                print("=" * 60)

                # Zielordner
                owner, repo, _ = self._parse_github_url(repo_url)
                target_dir = self.download_dir / f"repo_{idx}_{owner}_{repo}"
                target_dir.mkdir(parents=True, exist_ok=True)

                # ===== SCHRITT A-D: GitHub Crawling =====
                print("\n      [A-D] GitHub Crawling:")
                crawl_result = self._crawl_github_repo(repo_url, target_dir)

                # Log
                self.downloaded_files_log.append({
                    "repo": repo_url,
                    "files": crawl_result["files"],
                    "folders_crawled": crawl_result["folders_crawled"]
                })

                print(f"\n      Download: {len(crawl_result['files'])} Dateien gespeichert")
                print(f"      Ordner gecrawlt: {len(crawl_result['folders_crawled'])}")

                if not crawl_result["files"]:
                    print("      Keine interessanten Dateien gefunden!")
                    continue

                # ===== SCHRITT E: Security Scans =====
                print("\n      [E] Security Scans:")
                repo_findings = []

                # Secret Scanner
                print("          Secret Scanner...", end=" ")
                secret_findings = self._check_for_secrets(target_dir)
                for f in secret_findings:
                    f["repo"] = repo_url
                repo_findings.extend(secret_findings)
                print(f"{len(secret_findings)} findings")

                # Bandit
                if scanners_config.get("bandit", True):
                    print("          Bandit...", end=" ")
                    bandit_findings = self._run_bandit(target_dir)
                    for f in bandit_findings:
                        f["repo"] = repo_url
                    repo_findings.extend(bandit_findings)
                    print(f"{len(bandit_findings)} findings")

                # Semgrep
                if scanners_config.get("semgrep", True):
                    print("          Semgrep...", end=" ")
                    semgrep_findings = self._run_semgrep(target_dir)
                    for f in semgrep_findings:
                        f["repo"] = repo_url
                    repo_findings.extend(semgrep_findings)
                    print(f"{len(semgrep_findings)} findings")

                # Safety
                if scanners_config.get("safety", True):
                    print("          Safety...", end=" ")
                    safety_findings = self._run_safety(target_dir)
                    for f in safety_findings:
                        f["repo"] = repo_url
                    repo_findings.extend(safety_findings)
                    print(f"{len(safety_findings)} findings")

                self.all_findings.extend(repo_findings)

                print(f"\n      REPO Total: {len(repo_findings)} findings")

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
                repo = finding.get("repo", "")
                code = finding.get("code", "")[:50]
                print(f"  [{severity}] {ftype} ({scanner})")
                print(f"         Repo: {repo}")
                if code:
                    print(f"         Code: {code}...")


def main():
    """Hauptfunktion"""
    import warnings
    warnings.filterwarnings('ignore')

    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    scanner = GitHubScanner()
    scanner.run()


if __name__ == "__main__":
    main()
