# Skinport Monitor Bot

Ein Bot, der die Skinport API überwacht und Discord-Benachrichtigungen für neue Items sendet.

## Setup

1. Erstelle eine `.env` Datei im Projektverzeichnis mit folgenden Variablen:
```
SKINPORT_API_KEY=dein_api_key
SKINPORT_API_SECRET=dein_api_secret
DISCORD_WEBHOOK_URL=deine_discord_webhook_url
```

2. Installiere die benötigten Abhängigkeiten:
```bash
pip install -r requirements.txt
```

3. Konfiguriere den Bot in `config.py`:
- Passe `TARGET_ITEM` an, um nach anderen Items zu suchen
- Ändere `CHECK_INTERVAL`, um die Häufigkeit der Überprüfungen anzupassen

## Verwendung

Starte den Bot mit:
```bash
python main.py
```

Der Bot wird alle 5 Minuten (Standard-Einstellung) die Skinport API nach dem gewünschten Item durchsuchen und bei einem Fund eine Benachrichtigung an Discord senden.

## Features

- Automatische Überwachung der Skinport API
- Discord Webhook Integration
- Konfigurierbare Suchintervalle
- Detaillierte Preisinformationen in den Benachrichtigungen 