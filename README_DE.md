[English](README.md) | [中文](README_CN.md) | [한국어](README_KO.md) | [日本語](README_JP.md) | [Français](README_FR.md) | [Deutsch](README_DE.md) | [Español](README_ES.md)

<img width="3836" height="2026" alt="image" src="https://github.com/user-attachments/assets/d86c3d6b-6fd4-4cfe-b64f-67c465bb3d3c" /><img width="3832" height="2024" alt="image" src="https://github.com/user-attachments/assets/a91d2b13-07ac-4cae-ab33-506f1fa3bca6" />

# Everything by mdfind

Ein leistungsstarkes und effizientes Dateisuch-Tool für macOS, das die native Spotlight-Engine für blitzschnelle Ergebnisse nutzt.

## Hauptfunktionen

*   **Blitzschnelle Suche:** Nutzt den macOS Spotlight-Index für nahezu sofortige Dateisuche.
*   **Flexible Suchoptionen:** Suchen Sie nach Dateiname oder Inhalt, um die benötigten Dateien schnell zu finden.
*   **Erweiterte Filterung:** Verfeinern Sie Ihre Suchen mit einer Vielzahl von Filtern:
    *   Dateigrößenbereich (minimale und maximale Größe in Bytes)
    *   Spezifische Dateierweiterungen (z. B. `pdf`, `docx`)
    *   Groß-/Kleinschreibung beachten
    *   Vollständige oder teilweise Übereinstimmungsoptionen
*   **Verzeichnisspezifische Suche:** Beschränken Sie Ihre Suche auf ein bestimmtes Verzeichnis für gezielte Ergebnisse.
*   **Umfangreiche Vorschau:** Zeigen Sie verschiedene Dateitypen direkt in der Anwendung in der Vorschau an:
    *   Textdateien mit Kodierungserkennung
    *   Bilder (JPEG, PNG, GIF mit Animationsunterstützung, BMP, WEBP, HEIC)
    *   SVG-Dateien mit angemessener Skalierung und Zentrierung
    *   Videodateien mit Wiedergabesteuerung
    *   Audiodateien
*   **Integrierter Mediaplayer:**
    *   Video- und Audiowiedergabe mit Standardsteuerelementen
    *   Eigenständiges Player-Fenster für Mediendateien
    *   Kontinuierlicher Wiedergabemodus
    *   Lautstärkeregelung und Stummschaltungsoption
*   **Lesezeichen:** Schneller Zugriff auf häufige Suchen:
    *   Große Dateien (>50 MB)
    *   Videodateien
    *   Audiodateien
    *   Bilder
    *   Archive
    *   Anwendungen
*   **Sortierbare Ergebnisse:** Organisieren Sie Suchergebnisse nach Name, Größe, Änderungsdatum oder Pfad.
*   **Mehrfachdatei-Operationen:** Führen Sie Aktionen an mehreren Dateien gleichzeitig aus:
    *   Wählen Sie mehrere Dateien mit den Umschalt- oder Befehlstasten (⌘) aus
    *   Stapeloperationen: Öffnen, Löschen, Kopieren, Verschieben, Umbenennen
    *   Kontextmenü für zusätzliche Operationen
*   **Multi-Tab-Suchoberfläche:** Arbeiten Sie gleichzeitig mit mehreren Suchsitzungen:
    *   Erstellen Sie neue Tabs für verschiedene Suchanfragen
    *   Schließen, neu anordnen und verwalten Sie Tabs mit dem Rechtsklick-Kontextmenü
    *   Unabhängige Suchergebnisse und Einstellungen pro Tab
    *   Chrome-ähnliches Tab-Erlebnis mit Scroll-Schaltflächen für viele Tabs
*   **Anpassbare Oberfläche:**
    *   6 schöne Designs zur Auswahl:
        *   Hell und Dunkel (Systemstandard)
        *   Tokyo Night und Tokyo Night Storm
        *   Chinolor Dark und Chinolor Light (chinesische traditionelle Farben)
    *   Titelleisten-Thematisierung des Systems, die zu Ihrem ausgewählten Design passt
    *   Vorschaufenster ein-/ausblenden
    *   Konfigurierbarer Suchverlauf
*   **Multi-Format-Export:** Exportieren Sie Suchergebnisse in mehrere Formate:
    *   JSON - Strukturiertes Datenformat
    *   Excel (.xlsx) - Tabelle mit Formatierung
    *   HTML - Webfertiges Tabellenformat
    *   Markdown - Dokumentationsfreundliches Format
    *   CSV - Klassisches durch Kommas getrenntes Werteformat
*   **Lazy Loading:** Verarbeitet große Ergebnismengen effizient, indem Elemente beim Scrollen in Chargen geladen werden.
*   **Drag & Drop:** Ziehen Sie Dateien direkt in externe Anwendungen.
*   **Pfadoperationen:** Kopieren Sie Dateipfad, Verzeichnispfad oder Dateinamen in die Zwischenablage.

## Installation

1.  **Voraussetzungen:**
    *   Python 3.6+
    *   PyQt6

2.  **Repository klonen:**

    ```bash
    git clone https://github.com/appledragon/everythingByMdfind
    cd everythingByMdfind
    ```

3.  **Abhängigkeiten installieren:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Anwendung ausführen:**

    ```bash
    python everything.py
    ```

## Erstellen einer eigenständigen Anwendung (Optional)

Sie können py2app verwenden, um eine eigenständige macOS-Anwendung zu erstellen:

1.  **py2app installieren:**

    ```bash
    pip install py2app
    ```

2.  **setup.py erstellen:**

    ```bash
    cat > setup.py << 'EOF'
    from setuptools import setup

    APP = ['everything.py']
    DATA_FILES = [
        ('', ['LICENSE.md', 'README.md']),
    ]
    OPTIONS = {
        'argv_emulation': False,
        'packages': ['PyQt6'],
        'excludes': [],
        'plist': {
            'CFBundleName': 'Everything',
            'CFBundleDisplayName': 'Everything',
            'CFBundleVersion': '1.3.6',
            'CFBundleShortVersionString': '1.3.6',
            'CFBundleIdentifier': 'com.appledragon.everythingbymdfind',
            'LSMinimumSystemVersion': '10.14',
            'NSHighResolutionCapable': True,
        }
    }

    setup(
        app=APP,
        data_files=DATA_FILES,
        options={'py2app': OPTIONS},
        setup_requires=['py2app'],
    )
    EOF
    ```

3.  **Anwendung erstellen:**

    ```bash
    python setup.py py2app
    ```

    Das macOS-App-Bundle wird sich im Verzeichnis `dist` befinden.

## Mitwirken

Beiträge sind willkommen! Bitte zögern Sie nicht, Pull Requests einzureichen oder Issues für Fehlerbehebungen, Funktionsanfragen oder allgemeine Verbesserungen zu öffnen.

## Lizenz

Dieses Projekt ist unter der [MIT]-Lizenz lizenziert - siehe die Datei [LICENSE.md](LICENSE.md) für Details.

## Autor

Apple Dragon

## Version

1.3.6

## Danksagungen

*   Dank an das PyQt6-Team für die Bereitstellung eines leistungsstarken und vielseitigen GUI-Frameworks.
*   Inspiration von anderen großartigen Dateisuch-Tools.
