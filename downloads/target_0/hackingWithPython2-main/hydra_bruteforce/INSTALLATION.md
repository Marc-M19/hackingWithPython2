# Hydra Installation Guide

## Status: Hydra ist nicht installiert

Hydra wurde auf diesem System nicht gefunden. Folge der Anleitung unten, um es zu installieren.

## Installation nach Betriebssystem

### macOS

#### Option 1: Homebrew (empfohlen)
```bash
# Installiere Homebrew falls noch nicht vorhanden
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Installiere Hydra
brew install hydra

# Prüfe Installation
hydra -h
```

#### Option 2: Kompilieren von Source
```bash
# Abhängigkeiten installieren
brew install pkg-config libssh openssl

# Hydra herunterladen
git clone https://github.com/vanhauser-thc/thc-hydra.git
cd thc-hydra

# Kompilieren
./configure
make
sudo make install

# Prüfe Installation
hydra -h
```

### Linux (Debian/Ubuntu)

```bash
# System aktualisieren
sudo apt-get update

# Hydra installieren
sudo apt-get install hydra

# Prüfe Installation
hydra -h
```

### Linux (Arch/Manjaro)

```bash
# Hydra installieren
sudo pacman -S hydra

# Prüfe Installation
hydra -h
```

### Linux (Fedora/RHEL)

```bash
# Hydra installieren
sudo dnf install hydra

# Prüfe Installation
hydra -h
```

### Kali Linux

Hydra ist standardmäßig vorinstalliert auf Kali Linux.

```bash
# Falls nicht vorhanden
sudo apt-get install hydra

# Prüfe Installation
hydra -h
```

## Optionale Abhängigkeiten

### jq (JSON-Parser für Bash-Script)

#### macOS
```bash
brew install jq
```

#### Linux (Debian/Ubuntu)
```bash
sudo apt-get install jq
```

#### Linux (Arch)
```bash
sudo pacman -S jq
```

### Python requests (für Credential-Verifizierung)

```bash
pip install requests

# oder mit pip3
pip3 install requests
```

## Verifizierung der Installation

Nach der Installation führe folgende Befehle aus:

```bash
# Prüfe Hydra-Version
hydra -V

# Zeige verfügbare Module
hydra -U

# Teste HTTP-POST-Form Modul
hydra -U http-post-form
```

### Erwartete Ausgabe

```
Hydra v9.5 (c) 2023 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes.

...
```

## Fehlerbehebung

### macOS: "command not found: hydra"

Nach Installation mit Homebrew:
```bash
# Prüfe ob Homebrew-Pfad in PATH ist
echo $PATH

# Falls nicht, füge zu ~/.zshrc hinzu
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Linux: "E: Unable to locate package hydra"

```bash
# Repositories aktualisieren
sudo apt-get update

# Alternative: Installiere aus source
git clone https://github.com/vanhauser-thc/thc-hydra.git
cd thc-hydra
./configure
make
sudo make install
```

### Permission Denied

```bash
# Prüfe ob mit sudo installiert
sudo which hydra

# Falls ja, füge User zu entsprechender Gruppe hinzu
sudo usermod -aG admin $USER
```

## Nach der Installation

Nach erfolgreicher Installation kannst du das Hydra-Tool verwenden:

```bash
cd /Users/luisvincentstiller/Documents/GitHub/Hacking_with_python_2/hackingWithPython2-main/hydra_bruteforce

# Führe das Script aus
./run_hydra_attack.sh
```

## Weitere Ressourcen

- [THC-Hydra GitHub Repository](https://github.com/vanhauser-thc/thc-hydra)
- [Hydra Official Documentation](https://github.com/vanhauser-thc/thc-hydra/blob/master/README.md)
- [Hydra Man Page](https://www.kali.org/tools/hydra/)

## Quick Start nach Installation

```bash
# 1. Installiere Hydra (siehe oben)
brew install hydra  # macOS

# 2. Optional: Installiere jq
brew install jq

# 3. Optional: Installiere Python requests
pip3 install requests

# 4. Navigiere zum Projekt
cd hydra_bruteforce

# 5. Starte Flask-App (in separatem Terminal)
cd ..
python3 app.py

# 6. Führe Hydra-Angriff aus
cd hydra_bruteforce
./run_hydra_attack.sh
```

## Systemanforderungen

- **RAM**: Mindestens 512 MB
- **CPU**: Beliebig (mehr Kerne = mehr Threads möglich)
- **Disk**: ca. 50 MB für Hydra Binary
- **Python**: 3.6+ für Analyzer-Script

## Unterstützte Protokolle

Hydra unterstützt über 50 Protokolle:

- HTTP/HTTPS (POST/GET)
- FTP
- SSH
- Telnet
- MySQL/PostgreSQL
- SMB
- RDP
- SMTP
- POP3
- IMAP
- und viele mehr

Zeige alle Module mit:
```bash
hydra -U
```
