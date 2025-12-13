#!/usr/bin/env python3
"""
Vulnerability Scanner - Scannt Nachbar-Webseiten nach SicherheitslÃ¼cken
Verwendung: python scanner.py

Ablauf:
1. Besucht alle URLs in TARGET_URLS mit Selenium (headless)
2. LÃ¤dt Page Source und sucht nach .py Dateien
3. FÃ¼hrt Bandit und Semgrep Scans durch
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
# UnterstÃ¼tzt: HTTP-URLs und GitHub-Repos
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

# Regex-Patterns fÃ¼r Credential-Suche
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
    """LÃ¤dt den HTML Page Source einer URL herunter."""
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
    """Sucht nach .py und .zip Dateien und lÃ¤dt diese herunter."""
    downloaded_files = []

    try:
        # ZUERST: PrÃ¼fe ob /source Endpoint existiert
        source_url = urljoin(base_url, "/source")
        print(f"  [*] PrÃ¼fe /source Endpoint: {source_url}")
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
                            pre_match = re.search(r'<pre>(.*?)