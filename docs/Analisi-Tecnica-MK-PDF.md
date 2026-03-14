# Analisi Tecnica: Progetto MK-PDF
**Versione:** 1.0.0  
**Data di Analisi:** 2026-03-14  
**Classificazione:** Documentazione Tecnica di Sistema

---

## 1. Introduzione ed Obiettivi
MK-PDF è un'applicazione web-based modulare scritta in Python, progettata per la gestione, l'editing e la conversione professionale di documenti Markdown in formati PDF ad alta fedeltà. L'architettura è stata ottimizzata per il lore "Hard Sci-Fi" di *Nemici tra le Stelle*, integrando strumenti di visualizzazione dati avanzati (Mermaid.js) e un'estetica ispirata al tema "Abyss".

## 2. Stack Tecnologico

### Backend (Python Core)
- **Framework UI:** [NiceGUI](https://nicegui.io/) (basato su FastAPI, Vue.js e Quasar).
- **Dependency Management:** `pipenv`.
- **Markdown Processing:** `python-markdown` con estensioni per tabelle, TOC e blocchi di codice recintati.
- **Comunicazione HTTP:** `requests` per il payload verso l'istanza Docker Gotenberg.

### Frontend & Rendering
- **Design System:** [DaisyUI](https://daisyui.com/) (Tema `abyss`).
- **CSS Framework:** Tailwind CSS (via CDN con plugin Typography).
- **Web Editor:** [EasyMDE](https://github.com/Ionaru/easy-markdown-editor) con logic bridge modulare in `static/js/editor.js`.
- **Grafici e Diagrammi:** [Mermaid.js](https://mermaid.js.org/) con inizializzazione asincrona.
- **Asset Management:** Logica JS esternata per massimizzare la velocità di caricamento e la pulizia del DOM.

## 3. Architettura dei Componenti (Frontend-Bridges)

Il sistema segue un pattern a componenti per massimizzare la manutenibilità:

1.  **Navbar (`navbar.py`):** Gestisce l'identità visiva e i metadati globali dell'app utilizzando classi DaisyUI puriste (`bg-base-300`, `text-primary`).
2.  **Sidebar (`sidebar.py`):** Sistema di esplorazione file ricorsivo. Implementa una logica di "Middle-Truncation" per i nomi file lunghi, garantendo la visibilità costante dell'estensione `.md` e fornendo tooltips dinamici per il nome completo.
3.  **Editor (`editor.py`):** Bridge Python/JS che interfaccia l'app con `static/js/editor.js`. Gestisce il ciclo di vita di EasyMDE e l'iniezione sicura dei dati tramite `window.setMKEditorValue`, garantendo la sincronizzazione anche in caso di latenza del browser.
4.  **Main App (`main.py`):** Orchestratore dello stato e Server API. Implementa rotte dinamiche FastAPI per lo streaming di asset volatili (PDF) direttamente dalla memoria.

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

### Integrazione Deep-Theme (Abyss)
La UI non utilizza semplici override di colore, ma sfrutta le variabili CSS esposte da DaisyUI (`var(--b1)`, `var(--p)`, etc.). Questo approccio garantisce che ogni componente, incluso l'editor di terze parti, rispetti matematicamente la palette definita dal brand.

### In-Memory PDF Streaming
A differenza delle utility standard che creano file di spool, MK-PDF utilizza un approccio "fileless". La pipeline di conversione comunica via streaming con Gotenberg e serve il risultato tramite un buffer RAM. Questo approccio è stato scelto per eliminare frammenti di dati nel volume del progetto e velocizzare l'apertura nel browser attraverso rotte FastAPI dedicate.

## 6. Limitazioni Conosciute e Sviluppi Futuri
- **Rendering Offline:** Attualmente lo stack richiede una connessione internet per le CDN di Tailwind e Mermaid. Per una versione "Air-gapped", i file dovrebbero essere serviti localmente.
- **Multi-Tab:** L'app attualmente visualizza un file alla volta (Design Single-Document Interface).

---
