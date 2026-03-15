from nicegui import ui, app
from components.editor import Editor
from components.editor import Editor
from components.dialogs import ModalSystem
from logic.file_manager import FileManager
from logic.converter import GotenbergClient
from fastapi import Response
import os
import argparse
import asyncio

# --- Configuration ---
GOTENBERG_URL = os.getenv('GOTENBERG_URL', 'http://localhost:3000')
USER_HOME = os.path.expanduser('~')

# --- Arguments ---
parser = argparse.ArgumentParser(description='MK-PDF: Industrial Markdown Editor')
parser.add_argument('path', nargs='?', default=None)
args, _ = parser.parse_known_args()
PROJECT_ROOT = os.path.abspath(args.path) if args.path else None

# Cache per il PDF
pdf_cache = {'latest': b''}

def read_template(filename):
    path = os.path.join(os.path.dirname(__file__), 'templates', filename)
    with open(path, 'r') as f: return f.read()

class ChronosApp:
    def __init__(self):
        self.fm = FileManager(PROJECT_ROOT) if PROJECT_ROOT else None
        self.editor = Editor()
        self.client = GotenbergClient(GOTENBERG_URL)
        
        self.current_file = None
        self.current_dir = self.fm.project_root if self.fm else USER_HOME
        
        # UI Elements
        self.file_list_container = None
        self.breadcrumb_container = None
        self.editor_breadcrumb_container = None

    def start(self):
        @ui.page('/')
        def main_page():
            ui.dark_mode().enable()
            # Tema "Umano": Slate & Indigo (Più morbido e professionale)
            ui.colors(primary='#6366f1', secondary='#1e293b', accent='#818cf8')
            
            ui.add_head_html(read_template('base_head.html'))
            ui.add_head_html(read_template('editor_head.html'))
            
            with ui.column().classes('w-full q-pa-lg bg-[#0f172a] min-h-screen'):
                self.browser_view = ui.column().classes('w-full q-gutter-md')
                self.browser_view.visible = True
                with self.browser_view:
                    self._render_browser_view()
                
                self.editor_view = ui.column().classes('w-full').style('height: calc(100vh - 150px)')
                self.editor_view.visible = False
                with self.editor_view:
                    self._render_editor_view()


    def _render_browser_view(self):
        self.browser_view.clear()
        with self.browser_view:
            if not self.fm:
                with ui.column().classes('w-full items-center q-pa-xl q-gutter-md'):
                    ui.icon('folder_open', size='5rem', color='primary').classes('opacity-20')
                    ui.label('NESSUNA DIRECTORY SELEZIONATA').classes('text-h6 opacity-50')
                    ui.button('Seleziona Directory di Lavoro', icon='search', on_click=self.open_root_picker).props('unelevated color=primary')
                return

            with ui.row().classes('w-full items-center justify-between q-mb-md'):
                with ui.row().classes('items-center q-gutter-md'):
                    ui.label('MK-PDF').classes('text-h5 text-weight-bold text-primary')
                    self.breadcrumb_container = ui.row().classes('items-center q-gutter-xs')
                
                with ui.row().classes('q-gutter-sm'):
                    ui.button('Cambia Root', icon='folder_open', on_click=self.open_root_picker).props('flat dense color=primary')
                    ui.button('Nuovo File', icon='add', on_click=self.open_new_file_dialog).props('unelevated color=primary')
            
            with ui.card().props('bordered flat').classes('w-full q-pa-none bg-[#0f172a]'):
                with ui.row().classes('w-full q-pa-sm bg-[#1e293b] items-center text-overline'):
                    ui.label('Nome').classes('col-grow q-pl-md')
                    ui.label('Dimensione').classes('col-2 text-right')
                    ui.label('Modificato').classes('col-3 text-right q-pr-md')
                
                self.file_list_container = ui.column().classes('w-full')
            
            self.update_ui()

    def _render_editor_view(self):
        with ui.row().classes('w-full q-pa-md items-center justify-between bg-[#1e293b] rounded-borders q-mb-md'):
            with ui.row().classes('items-center q-gutter-sm'):
                ui.icon('edit_note', size='sm', color='primary').classes('opacity-50')
                self.editor_breadcrumb_container = ui.row().classes('items-center q-gutter-xs')
            
            with ui.row().classes('q-gutter-sm'):
                ui.button(icon='fullscreen', on_click=lambda: ui.run_javascript('if(window.MKEditor) window.MKEditor.instance.toggleFullScreen()')).props('flat round color=primary')
                ui.button('Chiudi', icon='close', on_click=self.close_file).props('flat text-color=grey')
                ui.button('Salva', icon='save', on_click=self.save_file).props('unelevated color=primary')
                ui.button('PDF', icon='picture_as_pdf', on_click=self.print_pdf).props('unelevated color=secondary')
        
        with ui.card().props('flat bordered').classes('w-full col-grow q-pa-none'):
            self.editor.create()

    # --- UI Logic ---

    def update_ui(self):
        if not self.fm: return
        self._update_file_list()
        self._update_breadcrumbs(self.breadcrumb_container, self.current_dir)

    def _update_file_list(self):
        self.file_list_container.clear()
        try:
            items = self.fm.list_items(self.current_dir)
            with self.file_list_container:
                if self.current_dir != self.fm.project_root:
                    parent = os.path.dirname(self.current_dir)
                    self._render_file_row(".. (Cartella Superiore)", True, parent)
                for item in items:
                    self._render_file_row(item['name'], item['is_dir'], item['path'], item)
        except Exception as e:
            ui.notify(str(e), type='negative')

    def _render_file_row(self, name, is_dir, path, info=None):
        async def handle_click():
            if is_dir: 
                self.go_to_dir(path)
            else: 
                await self.load_file(path)

        with ui.row().classes('w-full q-pa-sm border-b border-white/5 items-center cursor-pointer hover:bg-[#1e293b] transition-colors') \
            .on('click', handle_click):
            
            icon = 'folder' if is_dir else 'description'
            icon_color = 'warning' if is_dir else 'primary'
            ui.icon(icon, size='sm', color=icon_color).classes('opacity-70')
            ui.label(name).classes('col-grow truncate text-weight-medium')
            
            if info and name != ".. (Cartella Superiore)":
                ui.label(info['size']).classes('col-2 text-right text-caption monospace opacity-60')
                ui.label(info['mtime']).classes('col-3 text-right q-pr-md text-caption monospace opacity-60')
                if not is_dir:
                    ui.button(icon='delete', on_click=lambda: self.open_confirm_delete(path)).props('flat round dense color=negative').classes('q-ml-sm')

    def _update_breadcrumbs(self, container, target_path, is_file=False):
        container.clear()
        parts = self.fm.get_breadcrumbs(target_path)
        with container:
            ui.icon('account_tree', size='xs', color='primary').classes('opacity-50')
            ui.label(os.path.basename(self.fm.project_root)).classes('text-primary text-weight-bold cursor-pointer') \
                .on('click', lambda: (self.close_file(), self.go_to_dir(self.fm.project_root)))
            
            acc = self.fm.project_root
            for p in parts:
                ui.label('/').classes('opacity-30')
                acc = os.path.join(acc, p)
                def mk_go(p_auto=acc): return lambda: (self.close_file(), self.go_to_dir(p_auto))
                ui.label(p).classes('cursor-pointer text-weight-medium').on('click', mk_go())
            
            if is_file and self.current_file:
                ui.label('/').classes('opacity-30')
                ui.label(os.path.basename(self.current_file)).classes('text-primary text-weight-bold')

    # --- Actions ---

    def go_to_dir(self, path):
        self.current_dir = path
        self.update_ui()

    def go_to_root(self):
        self.close_file()
        self.go_to_dir(self.fm.project_root)

    async def load_file(self, path):
        self.current_file = path
        content = self.fm.read_file(path)
        self.browser_view.visible = False
        self.editor_view.visible = True
        await asyncio.sleep(0.1) 
        await ui.run_javascript('if (window.MKEditor) window.MKEditor.init()')
        self.editor.set_content(content)
        self._update_breadcrumbs(self.editor_breadcrumb_container, os.path.dirname(path), True)

    def close_file(self):
        self.current_file = None
        self.browser_view.visible = True
        self.editor_view.visible = False
        self.update_ui()

    async def save_file(self):
        if not self.current_file: return
        content = await self.editor.get_content()
        self.fm.save_file(self.current_file, content)
        ui.notify('Dati salvati', type='positive')

    async def print_pdf(self):
        if not self.current_file: return
        ui.notify('Generazione PDF in corso...', spinner=True)
        try:
            content = await self.editor.get_content()
            pdf_bytes = await asyncio.to_thread(self.client.convert_markdown, content)
            if pdf_bytes:
                pdf_cache['latest'] = pdf_bytes
                ui.notify('PDF pronto', type='positive')
                # Riga corretta
                await ui.run_javascript('window.open("/pdf_preview?t=" + Date.now(), "_blank"); null;')
            else:
                ui.notify('Errore nella conversione PDF', type='negative')
        except Exception as e:
            ui.notify(f'Errore: {str(e)}', type='negative')
        finally:
            ui.notify('Generazione PDF completata', type='positive')

    def open_new_file_dialog(self):
        async def on_create(name, dialog):
            try:
                path = self.fm.create_markdown(self.current_dir, name)
                dialog.close()
                await self.load_file(path)
            except Exception as e: ui.notify(str(e), type='negative')
        ModalSystem.show_new_file_dialog(on_create)

    def open_confirm_delete(self, path):
        def on_confirm(dialog):
            try:
                self.fm.delete_item(path)
                ui.notify("Epurato")
                dialog.close()
                self.update_ui()
                if self.current_file == path: self.close_file()
            except Exception as e: ui.notify(str(e), type='negative')
        ModalSystem.confirm_delete(os.path.basename(path), on_confirm)

    def open_root_picker(self):
        start_dir = self.current_dir if self.fm else USER_HOME
        ModalSystem.folder_picker_dialog(start_dir, USER_HOME, self._on_root_selected, self.fm.list_items if self.fm else FileManager(USER_HOME).list_items)

    def _on_root_selected(self, path, dialog):
        self.fm = FileManager(path)
        self.current_dir = path
        self._render_browser_view()
        dialog.close()

app_obj = ChronosApp()
app_obj.start()

@app.get('/pdf_preview')
def pdf_preview():
    return Response(
        content=pdf_cache['latest'], 
        media_type='application/pdf',
        headers={'Content-Disposition': 'inline; filename="preview.pdf"'}
    )

ui.run(title='MK-PDF', port=8080, reload=True, show=False)
