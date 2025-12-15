-- Datenbank-Schema für "Hebeln Mit Kopf" - Börsenanalyse-Plattform
-- Diese Tabelle speichert Autoren/Analysten-Accounts
-- HINWEIS: Dies ist eine Demo-Implementierung für Lernzwecke!
-- In Produktion würde man Posts in einer separaten Tabelle speichern.

CREATE DATABASE IF NOT EXISTS hackingdb CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE hackingdb;

DROP TABLE IF EXISTS users;
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(150) NOT NULL UNIQUE,  -- Autor-Name
  password VARCHAR(255) NOT NULL,         -- Passwort (in Demo plain-text, in Produktion gehasht!)
  bio VARCHAR(512) DEFAULT '',            -- Trading-Fokus / Über den Autor
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Registrierungsdatum
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Demo-Benutzer für SQL Injection Tests
INSERT INTO users (username, password, bio) VALUES
('admin', 'SecureP@ssw0rd!', 'Administrator - Full access to platform'),
('trader_max', 'MyPassword123', 'Spezialisiert auf DAX-Analysen und technische Indikatoren'),
('crypto_lisa', 'Bitcoin2024!', 'Fokus auf Kryptowährungen, DeFi und Blockchain-Technologie'),
('value_investor', 'WarrenB123', 'Value Investing, Fundamentalanalyse und langfristige Strategien'),
('swing_trader', 'TradeIt99', 'Swing Trading mit Fokus auf US-Aktien und Momentum-Strategien');

-- Optional: Beispiel für zukünftige Posts-Tabelle (aktuell nicht verwendet)
-- CREATE TABLE posts (
--   id INT AUTO_INCREMENT PRIMARY KEY,
--   author_id INT NOT NULL,
--   title VARCHAR(255) NOT NULL,
--   content TEXT,
--   category VARCHAR(100),
--   market_status ENUM('bullish', 'bearish', 'neutral') DEFAULT 'neutral',
--   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--   FOREIGN KEY (author_id) REFERENCES users(id)
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
