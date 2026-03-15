# MK-PDF 🌌🚀

**MK-PDF** is a specialized, industrial-grade Markdown editor and professional PDF generator designed for the *Nemici tra le Stelle* hard sci-fi universe. It bridges the gap between raw technical writing and high-fidelity document production.

---

## 🛠️ Key Features

- **Industrial Editor**: Powered by EasyMDE, providing a clean, distraction-free Markdown experience with professional **Hotkeys** (Ctrl+S, Ctrl+P, Ctrl+F).
- **Deep Space Aesthetics**: Uses the `Human Slate` design system (Zen Mode) for a minimalist, high-contrast dark mode.
- **Local Versioning**: Integrated **Git Abstraction** for simplified document checkpoints and history management.
- **Global Search**: High-speed, recursive full-text search across the entire workspace.
- **Data Visualization**: Native support for **Mermaid.js** diagrams, rendered directly into your documents and PDFs.
- **Professional PDF Output**: Support for multiple templates (`clean`, `industrial`) with automatic page numbering and professional headers/footers.
- **Adaptive UI**: Switch between **Page Focus** (sticky header) and **Editor Focus** (internal scroll) to suit your workflow.

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
Launch the application:
```bash
pipenv run python main.py
```
*Note: By default, the application starts in the user's home directory. Use the **Cambia Root** button inside the app to navigate to your project workspace.*

---

## 📂 Features & Dynamic Navigation
- **Dynamic Sector Selection**: Click the `folder_open` icon in the sidebar to change the root directory on the fly without restarting the app.
- **Breadcrumb Navigation**: Easily jump between subfolders of any local project.

- `main.py`: Core orchestrator and FastAPI server.
- `logic/`: Business logic for file management, Git abstraction, and PDF conversion.
- `components/`: Modular UI components (Editor, Dialogs).
- `static/`: Frontend assets (JavaScript, CSS).
- `templates/`: HTML/CSS templates for web rendering and PDF exports (Headers/Footers).
- `docs/`: Technical specifications and system analysis.

---

## 📄 Documentation
For a deep dive into the system architecture, check out:
- [Analisi Tecnica MK-PDF](file:///home/wolfman/projects/Pirates-Ancients-Corporations/MK-PDF/docs/Analisi-Tecnica-MK-PDF.md)

---
*Developed for the Pirates-Ancients-Corporations ecosystem.*
