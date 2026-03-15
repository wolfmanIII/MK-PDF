# Analisi Tecnica: Progetto MK-PDF
**Versione:** 1.1.0  
**Data di Analisi:** 2026-03-15  
**Classificazione:** Documentazione Tecnica di Sistema

---

## 1. Introduzione ed Obiettivi
MK-PDF è un'applicazione web-based modulare scritta in Python, progettata per la gestione, l'editing e la conversione professionale di documenti Markdown in formati PDF ad alta fedeltà. L'architettura è stata ottimizzata per il lore "Hard Sci-Fi" di *Nemici tra le Stelle*, integrando strumenti di visualizzazione dati avanzati (Mermaid.js) e un'estetica ispirata al tema "Abyss".

## 2. Stack Tecnologico

### Backend (Python Core)
- **Framework UI:** [NiceGUI](https://nicegui.io/) (basato su FastAPI, Vue.js e Quasar).
- **Dependency Management:** `pipenv`.
- **Async I/O:** `aiofiles` per la gestione non-bloccante del filesystem.
- **Markdown Processing:** `python-markdown` con estensioni per tabelle, TOC e blocchi di codice recintati.
- **Comunicazione HTTP:** `requests` per il payload verso l'istanza Docker Gotenberg.

### Frontend & Rendering
- **Design System:** Custom CSS (Human Slate / Zen Mode) basato su variabili statiche e Design Tokens.
- **Local Assets:** Dipendenze JS/CSS (EasyMDE, Mermaid, FontAwesome) ospitate localmente nella directory `static/`.
- **Web Editor:** [EasyMDE](https://github.com/Ionaru/easy-markdown-editor) con integrazione di Hotkeys personalizzate e override CodeMirror.
- **Grafici e Diagrammi:** [Mermaid.js](https://mermaid.js.org/) con inizializzazione asincrona e supporto al rendering PDF.
- **Template System:** Jinja2-style per l'iniezione dinamica di Header/Footer HTML nei documenti PDF.

## 3. Architettura dei Componenti (Frontend-Bridges)

Il sistema segue un pattern a componenti per massimizzare la manutenibilità:

1.  **Dialogs (`dialogs.py`):** Gestisce tutte le modali (Nuovo File, Delete, Root Picker) con uno stile premium unificato, feedback Quasar e supporto nativo per callback asincroni.
2.  **FileManager Logic (`file_manager.py`):** Modulo core per la navigazione e ricerca ricorsiva. Migrato integralmente ad **Asyncio** per garantire che le operazioni su disco non blocchino il loop dell'interfaccia.
3.  **Editor Bridge (`editor.py`):** Interfaccia Python/JS per EasyMDE. Gestisce il ciclo di vita dell'editor e la sincronizzazione del contenuto tramite `run_javascript`.
4.  **Main App (`main.py`):** Orchestratore dello stato (Scroll Mode, Search State) e Server API per PDF streaming. Gestisce il montaggio degli asset statici locali.

## 4. Pipeline di Conversione PDF

Il processo di generazione PDF è gestito dal modulo `logic/converter.py` e segue questo flusso:

1.  **Preprocessing:** Il Markdown viene convertito in HTML semantico.
2.  **Iniezione di Asset:** Viene generato un documento HTML di trasporto che include:
    - Tailwind CSS (configurazione `prose`).
    - Script di inizializzazione Mermaid.js.
    - Metadati per il rendering dei font.
3.  **Gotenberg Request:** Il payload viene inviato all'endpoint `/forms/chromium/convert/html`.
4.  **Wait Logic:** Gotenberg è istruito con un parametro `waitDelay` (2 secondi) e margini standard A4 (1 pollice) definiti esplicitamente in unità imperiali (`1in`) per una precisione millimetrica.
5.  **Memory Streaming:** Il PDF generato viene catturato come stream di byte, salvato in una cache volatile (`pdf_cache`) e servito tramite l'endpoint `/pdf_preview`. Questo elimina la necessità di file temporanei su disco, garantendo privacy e pulizia del filesystem.

## 5. Decisioni Tecniche Fondamentali (Analisi delle Scelte)

### WYSIWYG vs EasyMDE
È stata preferita la soluzione EasyMDE rispetto a Quill/TinyMCE per eliminare la "perdita di fedeltà" durante la conversione bidirezionale HTML-Markdown. EasyMDE lavora sul testo grezzo, garantendo che i file disk rimangano tecnicamente puri e privi di artefatti HTML.

### Sincronizzazione On-Demand
Inizialmente progettato con un sistema di sincronizzazione continua (messaggistica JS), il sistema è stato migrato a una sincronizzazione asincrona attivata solo al Save/Print. Questo riduce il carico sulla pipeline di rete locale e previene race conditions durante l'input veloce dell'utente.

### Gestione dello Stato UX (Page vs Editor Focus)
Per bilanciare l'ergonomia su diversi monitor, l'app implementa un toggle di stato per il container dell'editor. In modalità "Focus su Pagina", l'header diventa `sticky` e il container scala con il contenuto. In modalità "Focus su Editor", il container viene bloccato a `100vh` e lo scroll viene delegato internamente. Questo switch avviene senza re-rendering del DOM per preservare il cursore (cursor persistence).

### In-Memory PDF Streaming & Templates
A differenza delle utility standard che creano file di spool, MK-PDF utilizza un approccio "fileless" integrando Jinja2 per supportare template multipli (`clean`, `industrial`). La pipeline di conversione comunica via streaming con Gotenberg e serve il risultato tramite un buffer RAM. Questo approccio è stato scelto per eliminare frammenti di dati nel volume del progetto e velocizzare l'apertura nel browser attraverso rotte FastAPI dedicate.

## 6. Limitazioni Conosciute e Sviluppi Futuri
- [x] **Rendering Offline:** Supporto locale per tutti gli asset JS/CSS (EasyMDE, Mermaid, FontAwesome).
- **Multi-Tab Mode:** Gestione di più file Markdown aperti simultaneamente.
- **AI Integration:** Supporto per il completamento contestuale (IUNO API).

---
