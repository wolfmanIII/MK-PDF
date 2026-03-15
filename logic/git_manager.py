import subprocess
import os

class GitManager:
    def __init__(self, root_path):
        self.root_path = root_path

    def is_repo(self):
        """Verifica se la directory è un repository git."""
        if not self.root_path: return False
        try:
            result = subprocess.run(
                ['git', '-C', self.root_path, 'rev-parse', '--is-inside-work-tree'],
                capture_output=True, text=True
            )
            return result.returncode == 0
        except Exception:
            return False

    def init_repo(self):
        """Inizializza un nuovo repository git."""
        try:
            subprocess.run(['git', '-C', self.root_path, 'init'], check=True)
            return True
        except Exception:
            return False

    def create_checkpoint(self, message):
        """Esegue git add . e git commit -m 'message'."""
        try:
            # Stage all changes
            subprocess.run(['git', '-C', self.root_path, 'add', '.'], check=True)
            # Commit
            subprocess.run(['git', '-C', self.root_path, 'commit', '-m', message], check=True)
            return True, "Checkpoint creato con successo"
        except subprocess.CalledProcessError as e:
            return False, f"Errore Git: {e.stderr if e.stderr else 'Nessuna modifica da salvare'}"
        except Exception as e:
            return False, str(e)

    def get_last_commit_msg(self):
        """Ritorna l'ultimo messaggio di commit."""
        try:
            result = subprocess.run(
                ['git', '-C', self.root_path, 'log', '-1', '--pretty=%B'],
                capture_output=True, text=True
            )
            return result.stdout.strip() if result.returncode == 0 else ""
        except Exception:
            return ""
