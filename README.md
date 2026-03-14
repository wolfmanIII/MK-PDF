# MK-PDF 🌌🚀

**MK-PDF** is a specialized, industrial-grade Markdown editor and professional PDF generator designed for the *Nemici tra le Stelle* hard sci-fi universe. It bridges the gap between raw technical writing and high-fidelity document production.

---

## 🛠️ Key Features

- **Industrial Editor**: Powered by EasyMDE, providing a clean, distraction-free Markdown experience.
- **Deep Space Aesthetics**: Uses the `Abyss` design system for a high-contrast, professional dark mode.
- **Data Visualization**: Native support for **Mermaid.js** diagrams, rendered directly into your documents and PDFs.
- **Professional PDF Output**: Seamless integration with Gotenberg (Chromium) for pixel-perfect A4 documents with automatic page numbering and standard industry margins.
- **Fileless Pipeline**: All PDF previews are streamed directly from memory (RAM) through a custom FastAPI bridge, leaving zero temporary files on your local storage.

---

## 🚀 Quick Start

### 1. Prerequisites
- **Python 3.12+**
- **Pipenv**
- **Gotenberg** (Running on `http://localhost:3000`)
  ```bash
  docker run -d -p 3000:3000 gotenberg/gotenberg:8
  ```

### 2. Installation
Clone the repository and install dependencies:
```bash
git clone <repository-url>
cd MK-PDF
pipenv install
```

### 3. Execution
Launch the application (optionally providing a target directory):
```bash
pipenv run python main.py /percorso/alla/tua/cartella
```
*If no path is provided, it defaults to the 'Nemici Tra Le Stelle' project folder.*

---

## 📂 Features & Dynamic Navigation
- **Dynamic Sector Selection**: Click the `folder_open` icon in the sidebar to change the root directory on the fly without restarting the app.
- **Breadcrumb Navigation**: Easily jump between subfolders of any local project.

- `main.py`: Core orchestrator and FastAPI server.
- `logic/converter.py`: Gotenberg integration and in-memory streaming logic.
- `components/`: UI modules (Navbar, Sidebar, Editor).
- `static/js/`: Modularized JavaScript assets for theme and editor lifecycle.
- `templates/`: Clean HTML/CSS templates for web and PDF rendering.
- `docs/`: Technical specifications and system analysis.

---

## 📄 Documentation
For a deep dive into the system architecture, check out:
- [Analisi Tecnica MK-PDF](file:///home/wolfman/projects/Pirates-Ancients-Corporations/MK-PDF/docs/Analisi-Tecnica-MK-PDF.md)

---
*Developed for the Pirates-Ancients-Corporations ecosystem.*
