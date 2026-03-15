# MK-PDF: Stato dell'Arte e Architettura Tecnica

## 1. Visione d'Insieme
**MK-PDF** è un editor Markdown di classe industriale progettato per la massima efficienza produttiva. Non è solo un semplice editor, ma un sistema integrato di composizione documentale che unisce la flessibilità del Markdown alla precisione della generazione PDF professionale tramite motori di rendering enterprise.

---

## 2. Architettura del Core

### 2.1 Backend (Python & FastAPI)
Il cuore pulsante dell'applicazione è basato su **FastAPI** integrato in **NiceGUI**. 
- **Gestione Asincrona**: Tutte le operazioni pesanti (I/O su disco tramite `aiofiles`, chiamate API Gotenberg) sono gestite in modo asincrono per garantire che l'interfaccia utente rimanga sempre fluida (60 FPS).
- **File Management**: Implementazione di un `FileManager` asincrono che gestisce la navigazione, la ricerca ricorsiva (Full-text) e la creazione di file Markdown con template predefiniti.
- **Root Secrecy & Security**: Il sistema è blindato per operare esclusivamente all'interno della `HOME` dell'utente o della directory esplicita di progetto.

### 2.2 Generatore PDF (Gotenberg Integration)
La conversione da Markdown a PDF avviene tramite un'architettura a microservizi:
1. **Gotenberg Client**: Un client Python dedicato interagisce con un'istanza Docker di Gotenberg.
2. **Pipeline di Conversione**: Markdown -> HTML (con supporto Mermaid) -> PDF (Chrome Headless).
3. **Ghost Cache**: Il PDF generato viene memorizzato in una cache volatile (`pdf_cache`) e servito tramite una rotta FastAPI dedicata (`/pdf_preview`).
4. **Header Inline**: La rotta PDF è configurata con `Content-Disposition: inline`, forzando i browser moderni alla visualizzazione immediata invece del download.

---

## 3. Frontend & User Experience (UX)

### 3.1 Design System "Zen Mode" (Human Slate)
L'evoluzione v3.0 di MK-PDF adotta il paradigma **Zen Mode**, eliminando ogni sovrastruttura convenzionale:
- **Zero-UI Distraction**: Rimozione della Navbar e del Sidebar Drawer per massimizzare lo spazio di lavoro.
- **Header Adattivo (Sticky)**: Toolbar di navigazione che rimane fissa durante lo scroll o si ancora all'editor in base alla modalità selezionata.
- **Distrazione Zero**: La barra breadcrumb viene automaticamente occultata in modalità Fullscreen tramite monitoraggio attivo (MutationObserver) per pulire l'area di lavoro.
- **Dual Focus Mode**: Supporto per "Focus su Pagina" (sticky) e "Focus su Editor" (scroll interno) per adattarsi a diversi hardware e preferenze.
- **Palette**: Slate 950/800 per gli sfondi e Indigo 500/400 per accenti e focus.
- **Tipografia**: Utilizzo di font monospazio ad alta leggibilità (Fira Code/JetBrains Mono) per l'editing e sans-serif professionali per il browser dei file.

### 3.2 L'Editor (EasyMDE & CodeMirror)
L'integrazione di EasyMDE è stata personalizzata a livello atomico:
- **Toolbar Industriale**: Una barra degli strumenti a contrasto calcolato in overlay.
- **Mermaid Support**: Supporto nativo per diagrammi e grafici direttamente nel Markdown, renderizzati in tempo reale nell'anteprima.
- **Monolitical View**: L'editor occupa il 100% dell'area utile, nascondendo automaticamente tutti i controlli di file management durante la scrittura.
- **Hotkeys Professionali**: Integrazione di scorciatoie da tastiera (Ctrl+S, Ctrl+P, Ctrl+F, Esc) per un'operatività senza mouse.

---

## 4. Soluzioni Tecniche di Rilievo

### 4.1 Il Problema del PDF Preview
Dopo diverse iterazioni, la soluzione definitiva per l'anteprima PDF implementata prevede:
- **Timestamp Anti-Cache**: Ogni richiesta verso `/pdf_preview` include un parametro `t` (Unix timestamp) per forzare il refresh del browser.
- **Nuovo Tab Garantito**: Utilizzo di `window.open` via Javascript iniettato per superare le limitazioni di redirect di alcuni framework UI.
- **Notification Lifecycle**: Le notifiche di stato ("Generazione PDF in corso...") vengono gestite tramite blocchi `try...finally` per assicurarne la scomparsa immediata al termine dell'operazione.

### 4.2 Navigazione e Breadcrumbs (Centralizzati)
In assenza di Sidebar, la navigazione è stata integrata nel "Browser Centrale":
- **Breadcrumbs Dinamici**: Permettono salti rapidi tra le directory e la Root del progetto direttamente dall'area di lavoro.
- **Gestione Root**: Il comando "Cambia Root" permette di ricalibrare istantaneamente lo scope del progetto. Si è scelto di rimuovere l'integrazione Git diretta per favorire l'uso di client esterni specializzati e aumentare la robustezza del nucleo di editing.
- **Search Engine**: Motore di ricerca ricorsivo ad alta velocità con anteprima del contesto e salto diretto alla riga.

---

## 5. Stack Tecnologico Finale
- **Backend**: Python 3.12+, FastAPI, NiceGUI, aiofiles.
- **Editor**: EasyMDE (Local), CodeMirror 5 (Local).
- **Rendering PDF**: Gotenberg 8.x (Docker/API).
- **Styling**: Vanilla CSS con variabili custom (Design Tokens).
- **Grafici**: Mermaid.js (Local).

---

## 6. Prossimi Passi e Roadmap
- [x] Implementazione di scorciatoie da tastiera (Hotkeys) personalizzate.
- [x] Supporto per template PDF (Header/Footer personalizzati tramite Gotenberg).
- [x] Ricerca full-text all'interno della directory di lavoro.
- [x] Localizzazione completa degli asset (Offline support).
- [x] Transizione ad architettura asincrona (`aiofiles`).

---
**Ultimo Aggiornamento**: 15 Marzo 2026 (Roadmap v3.0 Completata)
**Stato**: Stabile / In Produzione
