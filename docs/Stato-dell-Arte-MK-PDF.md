# MK-PDF: Stato dell'Arte e Architettura Tecnica

## 1. Visione d'Insieme
**MK-PDF** è un editor Markdown di classe industriale progettato per la massima efficienza produttiva. Non è solo un semplice editor, ma un sistema integrato di composizione documentale che unisce la flessibilità del Markdown alla precisione della generazione PDF professionale tramite motori di rendering enterprise.

---

## 2. Architettura del Core

### 2.1 Backend (Python & FastAPI)
Il cuore pulsante dell'applicazione è basato su **FastAPI** integrato in **NiceGUI**. 
- **Gestione Asincrona**: Tutte le operazioni pesanti (I/O su disco, chiamate API Gotenberg) sono gestite in modo asincrono per garantire che l'interfaccia utente rimanga sempre fluida (60 FPS).
- **File Management**: Implementazione di un `FileManager` personalizzato che gestisce la navigazione, la lettura/scrittura e la creazione di file Markdown con template predefiniti.
- **Root Secrecy & Security**: Il sistema è blindato per operare esclusivamente all'interno della `HOME` dell'utente, prevenendo navigazioni accidentali in directory di sistema.

### 2.2 Generatore PDF (Gotenberg Integration)
La conversione da Markdown a PDF avviene tramite un'architettura a microservizi:
1. **Gotenberg Client**: Un client Python dedicato interagisce con un'istanza Docker di Gotenberg.
2. **Pipeline di Conversione**: Markdown -> HTML (con supporto Mermaid) -> PDF (Chrome Headless).
3. **Ghost Cache**: Il PDF generato viene memorizzato in una cache volatile (`pdf_cache`) e servito tramite una rotta FastAPI dedicata (`/pdf_preview`).
4. **Header Inline**: La rotta PDF è configurata con `Content-Disposition: inline`, forzando i browser moderni alla visualizzazione immediata invece del download.

---

## 3. Frontend & User Experience (UX)

### 3.1 Design System "Human Slate"
Abbandonata l'estetica estrema di Abyss Elite, MK-PDF adotta il tema **Human Slate**:
- **Palette**: Slate 950/800 per gli sfondi e Indigo 500/400 per accenti e focus.
- **Tipografia**: Utilizzo di font monospazio ad alta leggibilità (Fira Code/JetBrains Mono) per l'editing e sans-serif professionali per l'interfaccia.
- **Quasar Framework**: Sfrutta la potenza dei componenti Vue di Quasar per breadcrumbs, card e dialoghi, garantendo un look nativo e coerente.

### 3.2 L'Editor (EasyMDE & CodeMirror)
L'integrazione di EasyMDE è stata personalizzata a livello atomico:
- **Toolbar Industriale**: Una barra degli strumenti a contrasto calcolato. Gli stati attivi sono indicati da bordi bianchi nitidi (1px solid white) su sfondo trasparente, garantendo che l'icona rimanga sempre visibile.
- **Mermaid Support**: Supporto nativo per diagrammi e grafici direttamente nel Markdown, renderizzati in tempo reale nell'anteprima.
- **Fullscreen & Side-by-Side**: Modalità ottimizzate che nascondono dinamicamente i drawer e gli header di sistema per una concentrazione totale.

---

## 4. Soluzioni Tecniche di Rilievo

### 4.1 Il Problema del PDF Preview
Dopo diverse iterazioni, la soluzione definitiva per l'anteprima PDF implementata prevede:
- **Timestamp Anti-Cache**: Ogni richiesta verso `/pdf_preview` include un parametro `t` (Unix timestamp) per forzare il refresh del browser.
- **Nuovo Tab Garantito**: Utilizzo di `window.open` via Javascript iniettato per superare le limitazioni di redirect di alcuni framework UI.
- **Notification Lifecycle**: Le notifiche di stato ("Generazione PDF in corso...") vengono gestite tramite blocchi `try...finally` per assicurarne la scomparsa immediata al termine dell'operazione.

### 4.2 Navigazione e Breadcrumbs
Navigazione multi-livello con gestione automatica dei percorsi relativi e assoluti. L'UI riflette dinamicamente la posizione attuale nel filesystem, permettendo salti rapidi verso la Root del progetto o cartelle intermedie senza perdita di contesto.

---

## 5. Stack Tecnologico Finale
- **Backend**: Python 3.12+, FastAPI, NiceGUI (Quasar/Vue inside).
- **Editor**: EasyMDE (JS), CodeMirror 5 (JS).
- **Rendering PDF**: Gotenberg 8.x (Docker/API).
- **Styling**: Vanilla CSS con variabili custom (Design Tokens).
- **Grafici**: Mermaid.js integrato.

---

## 6. Prossimi Passi e Roadmap
- [ ] Implementazione di scorciatoie da tastiera (Hotkeys) personalizzate.
- [ ] Supporto per template PDF (Header/Footer personalizzati tramite Gotenberg).
- [ ] Sistema di versionamento locale (Git abstraction).
- [ ] Ricerca full-text all'interno della directory di lavoro.

---
**Ultimo Aggiornamento**: 15 Marzo 2026
**Stato**: Stabile / In Produzione
