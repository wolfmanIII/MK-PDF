import os
import datetime
import shutil

class FileManager:
    def __init__(self, project_root):
        self.project_root = os.path.abspath(project_root)

    def list_items(self, current_dir):
        """Ritorna una lista ordinata di cartelle e file markdown."""
        try:
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
        except Exception as e:
            raise Exception(f"Errore nella lettura della directory: {e}")

    def create_markdown(self, directory, name):
        """Crea un nuovo file markdown con template base."""
        if not name.endswith('.md'):
            name += '.md'
        file_path = os.path.join(directory, name)
        
        if os.path.exists(file_path):
            raise FileExistsError(f"Il file {name} esiste già.")
            
        content = f'# {name.replace(".md", "")}\n\nNuovo documento creato il {datetime.datetime.now().strftime("%d/%m/%Y")}'
        with open(file_path, 'w') as f:
            f.write(content)
        return file_path

    def delete_item(self, path):
        """Rimuove un file o una cartella (se vuota)."""
        if not os.path.exists(path):
            raise FileNotFoundError("Risorsa non trovata.")
        
        if os.path.isdir(path):
            os.rmdir(path) # Sicurezza: solo se vuota
        else:
            os.remove(path)

    def get_breadcrumbs(self, current_path):
        """Genera le parti del percorso per la navigazione."""
        try:
            rel_path = os.path.relpath(current_path, self.project_root)
        except ValueError:
            return []
            
        if rel_path == ".": return []
        return rel_path.split(os.sep)

    def read_file(self, path):
        with open(path, 'r') as f:
            return f.read()

    def save_file(self, path, content):
        with open(path, 'w') as f:
            f.write(content)
