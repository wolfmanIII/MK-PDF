import os
import datetime
import shutil
import asyncio
import aiofiles
from typing import List, Dict, Any, Optional

class FileManager:
    """
    Gestore del filesystem per il progetto MK-PDF.
    Gestisce operazioni di lettura, scrittura, ricerca e navigazione in modo asincrono.
    """
    
    def __init__(self, project_root: str):
        """
        Inizializza il gestore con la root del progetto.
        
        :param project_root: Percorso assoluto della directory radice del progetto.
        """
        self.project_root = os.path.abspath(project_root)

    async def list_items(self, current_dir: str) -> List[Dict[str, Any]]:
        """
        Ritorna una lista ordinata di cartelle e file markdown nella directory specificata.
        
        :param current_dir: Directory da scansionare.
        :return: Lista di dizionari contenenti i metadati degli elementi.
        """
        def _scan():
            items = os.listdir(current_dir)
            folders = []
            files = []
            
            for item in items:
                if item.startswith('.'): continue
                full_path = os.path.join(current_dir, item)
                stats = os.stat(full_path)
                
                info = {
                    'name': item,
                    'path': full_path,
                    'size': f"{stats.st_size / 1024:.1f} KB",
                    'mtime': datetime.datetime.fromtimestamp(stats.st_mtime).strftime('%d %b %Y %H:%M'),
                    'is_dir': os.path.isdir(full_path)
                }
                
                if info['is_dir']:
                    folders.append(info)
                elif item.endswith('.md'):
                    files.append(info)
            return sorted(folders, key=lambda x: x['name'].lower()) + sorted(files, key=lambda x: x['name'].lower())

        try:
            return await asyncio.to_thread(_scan)
        except Exception as e:
            raise Exception(f"Errore nella lettura della directory: {e}")

    async def create_markdown(self, directory: str, name: str) -> str:
        """
        Crea un nuovo file markdown con un template di base.
        
        :param directory: Directory di destinazione.
        :param name: Nome del file (con o senza estensione .md).
        :return: Percorso completo del file creato.
        """
        if not name.endswith('.md'):
            name += '.md'
        file_path = os.path.join(directory, name)
        
        if await asyncio.to_thread(os.path.exists, file_path):
            raise FileExistsError(f"Il file {name} esiste già.")
            
        content = f'# {name.replace(".md", "")}\n\nNuovo documento creato il {datetime.datetime.now().strftime("%d/%m/%Y")}'
        
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(content)
        return file_path

    async def delete_item(self, path: str) -> None:
        """
        Rimuove un file o una cartella (solo se vuota).
        
        :param path: Percorso dell'elemento da eliminate.
        """
        if not await asyncio.to_thread(os.path.exists, path):
            raise FileNotFoundError("Risorsa non trovata.")
        
        def _delete():
            if os.path.isdir(path):
                os.rmdir(path) # Sicurezza: solo se vuota
            else:
                os.remove(path)
        
        await asyncio.to_thread(_delete)

    def get_breadcrumbs(self, current_path: str) -> List[str]:
        """
        Genera i segmenti del percorso relativi alla root del progetto per la navigazione.
        
        :param current_path: Percorso attuale.
        :return: Lista di stringhe rappresentanti i livelli della directory.
        """
        try:
            rel_path = os.path.relpath(current_path, self.project_root)
        except ValueError:
            return []
            
        if rel_path == ".": return []
        return rel_path.split(os.sep)

    async def read_file(self, path: str) -> str:
        """
        Legge il contenuto di un file in modo asincrono.
        
        :param path: Percorso del file.
        :return: Contenuto testuale del file.
        """
        async with aiofiles.open(path, 'r', encoding='utf-8') as f:
            return await f.read()

    async def save_file(self, path: str, content: str) -> None:
        """
        Salva il contenuto in un file in modo asincrono.
        
        :param path: Percorso del file.
        :param content: Testo da salvare.
        """
        async with aiofiles.open(path, 'w', encoding='utf-8') as f:
            await f.write(content)

    async def search_content(self, query: str) -> List[Dict[str, Any]]:
        """
        Cerca ricorsivamente una stringa in tutti i file .md del progetto.
        
        :param query: Stringa di ricerca.
        :return: Lista di risultati con percorso, riga ed estratto.
        """
        results = []
        if not query or len(query) < 2: return results
        
        query = query.lower()

        def _search():
            local_results = []
            for root, _, files in os.walk(self.project_root):
                for file in files:
                    if file.endswith('.md'):
                        full_path = os.path.join(root, file)
                        try:
                            with open(full_path, 'r', encoding='utf-8') as f:
                                for i, line in enumerate(f, 1):
                                    if query in line.lower():
                                        local_results.append({
                                            'path': full_path,
                                            'name': file,
                                            'line': i,
                                            'excerpt': line.strip()
                                        })
                                        if len(local_results) > 50: return local_results
                        except Exception:
                            continue
            return local_results

        return await asyncio.to_thread(_search)
