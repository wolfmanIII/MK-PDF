from nicegui import ui, app
from components.editor import Editor
from components.dialogs import ModalSystem
from logic.file_manager import FileManager
from logic.converter import GotenbergClient
from fastapi import Response
from fastapi.staticfiles import StaticFiles
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

app.mount('/static', StaticFiles(directory='static'), name='static')

class MKPDFApp:
    def __init__(self):
        self.fm = FileManager(PROJECT_ROOT) if PROJECT_ROOT else None
        self.editor = Editor()
        self.client = GotenbergClient(GOTENBERG_URL)
        
        self.current_file = None
        self.current_dir = self.fm.project_root if self.fm else USER_HOME
        
        self.active_pdf_template = 'industrial'
        self.available_templates = ['clean', 'industrial']
        
        # Search State
        self.search_query = ""
        self.is_searching = False
        
        # UI Options
        self.internal_scroll = False
        
        # UI Elements
        self.file_list_container = None
        self.breadcrumb_container = None
        self.editor_breadcrumb_container = None

    def start(self):
        @ui.page('/')
        async def main_page():
            ui.dark_mode().enable()
            # Tema "Umano": Slate & Indigo (Più morbido e professionale)
            ui.colors(primary='#6366f1', secondary='#1e293b', accent='#818cf8')
            
            ui.add_head_html(read_template('base_head.html'))
            ui.add_head_html(read_template('editor_head.html'))
            
            with ui.column().classes('w-full bg-[#0f172a] min-h-screen'):
                self.browser_view = ui.column().classes('w-full q-pa-lg q-gutter-md')
                self.browser_view.visible = True
                with self.browser_view:
                    await self._render_browser_view()
                
                self.editor_view = ui.column().classes('w-full')
                self.editor_view.visible = False
                with self.editor_view:
                    await self._render_editor_view()
            
            # Caricamento iniziale
            ui.timer(0.1, self.update_ui, once=True)


    async def _render_browser_view(self):
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
                
                with ui.row().classes('items-center q-gutter-md'):
                    # Search Bar
                    with ui.input(placeholder='Cerca nei testi...', on_change=self.on_search_change).props('outlined dense color=primary').classes('w-64 bg-[#1e293b]') as self.search_input:
                        with self.search_input.add_slot('prepend'):
                            ui.icon('search')
                        with self.search_input.add_slot('append'):
                            ui.icon('close').classes('cursor-pointer').on('click', self.clear_search)
                    
                    with ui.row().classes('q-gutter-sm'):
                        pass
                            
                        ui.button('Cambia Root', icon='folder_open', on_click=self.open_root_picker).props('flat dense color=primary')
                        ui.button('Nuovo File', icon='add', on_click=self.open_new_file_dialog).props('unelevated color=primary')
            
            with ui.card().props('bordered flat').classes('w-full q-pa-none bg-[#0f172a]'):
                with ui.row().classes('w-full q-pa-sm bg-[#1e293b] items-center text-overline'):
                    ui.label('Nome').classes('col-grow q-pl-md')
                    ui.label('Dimensione').classes('col-2 text-right')
                    ui.label('Modificato').classes('col-3 text-right q-pr-md')
                
                self.file_list_container = ui.column().classes('w-full')
            
            await self.update_ui()

    async def _render_editor_view(self):
        header_classes = 'w-full q-pa-md items-center justify-between bg-[#1e293b] z-50 shadow-lg editor-header'
        if not self.internal_scroll:
            header_classes += ' sticky top-0'
        
        with ui.row().classes(header_classes).props('id=editor-header-bar') as self.editor_header:
            with ui.row().classes('items-center q-gutter-sm'):
                ui.icon('edit_note', size='sm', color='primary').classes('opacity-50')
                self.editor_breadcrumb_container = ui.row().classes('items-center q-gutter-xs')
            
            with ui.row().classes('q-gutter-sm items-center'):
                # Toggle Scroll Mode
                icon = 'unfold_less' if self.internal_scroll else 'unfold_more'
                self.scroll_toggle_btn = ui.button(icon=icon, on_click=self.toggle_scroll_mode) \
                    .props('flat dense color=primary') \
                    .tooltip('Cambia modalità di scorrimento') \
                    .classes('opacity-50 hover:opacity-100')
                
                ui.button(icon='fullscreen', on_click=lambda: ui.run_javascript('if(window.MKEditor) window.MKEditor.instance.toggleFullScreen()')).props('flat color=primary id=btn-fullscreen').tooltip('Fullscreen')
                ui.button('Chiudi', icon='close', on_click=self.close_file).props('flat text-color=grey id=btn-close')
                ui.button('Salva', icon='save', on_click=self.save_file).props('unelevated color=primary id=btn-save')
                ui.select(options=self.available_templates, value=self.active_pdf_template, on_change=lambda e: setattr(self, 'active_pdf_template', e.value)).props('flat dense options-dark').classes('text-caption opacity-70 w-24')
                ui.button('PDF', icon='picture_as_pdf', on_click=self.print_pdf).props('unelevated color=secondary id=btn-pdf')
        
        editor_card_classes = 'w-full q-pa-none'
        if not self.internal_scroll:
            editor_card_classes += ' q-mt-md'
            
        with ui.column().classes('w-full q-pa-lg') \
            .style('height: calc(100vh - 100px)' if self.internal_scroll else '') as self.editor_container:
            with ui.card().props('flat bordered').classes(f'{editor_card_classes} col-grow overflow-hidden') as self.editor_card:
                self.editor.create()

    # --- UI Logic ---

    async def update_ui(self):
        if not self.fm: return
        if self.is_searching:
            await self._update_search_results()
        else:
            await self._update_file_list()
        self._update_breadcrumbs(self.breadcrumb_container, self.current_dir)

    async def _update_file_list(self):
        self.file_list_container.clear()
        try:
            items = await self.fm.list_items(self.current_dir)
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
                await self.go_to_dir(path)
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

    def _render_search_match(self, match):
        async def handle_click():
            await self.load_file(match['path'])

        with ui.row().classes('w-full q-pa-md border-b border-white/5 items-center cursor-pointer hover:bg-[#1e293b] transition-colors') \
            .on('click', handle_click):
            
            with ui.column().classes('col-grow'):
                with ui.row().classes('items-center q-gutter-xs'):
                    ui.icon('description', size='xs', color='primary').classes('opacity-50')
                    ui.label(match['name']).classes('text-weight-bold text-primary')
                    ui.label(f"linea {match['line']}").classes('text-caption monospace opacity-40')
                
                ui.label(match['excerpt']).classes('text-caption text-grey-4 truncate-2-lines q-pl-md border-l-2 border-primary/20')

    async def _update_search_results(self):
        self.file_list_container.clear()
        results = await self.fm.search_content(self.search_query)
        
        with self.file_list_container:
            if not results:
                with ui.column().classes('w-full items-center q-pa-xl opacity-30'):
                    ui.icon('search_off', size='4rem')
                    ui.label('Nessun risultato trovato')
                return
            
            ui.label(f'Trovati {len(results)} match').classes('q-pa-md text-overline text-accent opacity-70')
            for match in results:
                self._render_search_match(match)

    def _update_breadcrumbs(self, container, target_path, is_file=False):
        container.clear()
        parts = self.fm.get_breadcrumbs(target_path)
        with container:
            ui.icon('account_tree', size='xs', color='primary').classes('opacity-50')
            async def go_root():
                await self.close_file()
                await self.go_to_dir(self.fm.project_root)
            ui.label(os.path.basename(self.fm.project_root)).classes('text-primary text-weight-bold cursor-pointer') \
                .on('click', go_root)
            
            acc = self.fm.project_root
            for p in parts:
                ui.label('/').classes('opacity-30')
                acc = os.path.join(acc, p)
                async def mk_go(p_auto=acc):
                    await self.close_file()
                    await self.go_to_dir(p_auto)
                ui.label(p).classes('cursor-pointer text-weight-medium').on('click', mk_go)
            
            if is_file and self.current_file:
                ui.label('/').classes('opacity-30')
                ui.label(os.path.basename(self.current_file)).classes('text-primary text-weight-bold')

    # --- Actions ---

    async def go_to_dir(self, path):
        self.current_dir = path
        await self.update_ui()

    async def go_to_root(self):
        await self.close_file()
        await self.go_to_dir(self.fm.project_root)

    def toggle_scroll_mode(self):
        self.internal_scroll = not self.internal_scroll
        
        if self.internal_scroll:
            # Modalità Editor (Fisso)
            self.editor_header.classes(remove='sticky top-0')
            self.editor_container.style('height: calc(100vh - 100px)')
            self.editor_card.classes(remove='q-mt-md')
            self.scroll_toggle_btn.props('icon=unfold_less')
            ui.notify('Focus su Editor (Scroll Interno)', color='primary')
        else:
            # Modalità Pagina (Sticky)
            self.editor_header.classes(add='sticky top-0')
            self.editor_container.style('height: auto')
            self.editor_card.classes(add='q-mt-md')
            self.scroll_toggle_btn.props('icon=unfold_more')
            ui.notify('Focus su Pagina (Header Sticky)', color='primary')

    async def on_search_change(self, e):
        self.search_query = e.value
        self.is_searching = len(self.search_query) >= 2
        await self.update_ui()

    async def clear_search(self):
        self.search_input.value = ""
        self.search_query = ""
        self.is_searching = False
        await self.update_ui()

    async def load_file(self, path):
        self.current_file = path
        content = await self.fm.read_file(path)
        self.browser_view.visible = False
        self.editor_view.visible = True
        await asyncio.sleep(0.1) 
        await ui.run_javascript('if (window.MKEditor) window.MKEditor.init()')
        self.editor.set_content(content)
        self._update_breadcrumbs(self.editor_breadcrumb_container, os.path.dirname(path), True)

    async def close_file(self):
        self.current_file = None
        self.browser_view.visible = True
        self.editor_view.visible = False
        await self.update_ui()

    async def save_file(self):
        if not self.current_file: return
        content = await self.editor.get_content()
        await self.fm.save_file(self.current_file, content)
        ui.notify('Dati salvati', type='positive')

    async def print_pdf(self):
        if not self.current_file: return
        ui.notify('Generazione PDF in corso...', spinner=True)
        try:
            content = await self.editor.get_content()
            
            # Caricamento template dinamico
            template_path = os.path.join(os.path.dirname(__file__), 'templates', 'export', self.active_pdf_template)
            header_html = None
            footer_html = None
            
            h_file = os.path.join(template_path, 'header.html')
            f_file = os.path.join(template_path, 'footer.html')
            
            if os.path.exists(h_file):
                with open(h_file, 'r') as f: header_html = f.read()
            if os.path.exists(f_file):
                with open(f_file, 'r') as f: footer_html = f.read()

            pdf_bytes = await asyncio.to_thread(self.client.convert_markdown, content, header_html, footer_html)
            if pdf_bytes:
                pdf_cache['latest'] = pdf_bytes
                ui.notify('PDF pronto', type='positive')
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
                path = await self.fm.create_markdown(self.current_dir, name)
                dialog.close()
                await self.load_file(path)
            except Exception as e: ui.notify(str(e), type='negative')
        ModalSystem.show_new_file_dialog(on_create)

    def open_confirm_delete(self, path):
        async def on_confirm(dialog):
            try:
                await self.fm.delete_item(path)
                ui.notify("Epurato")
                dialog.close()
                await self.update_ui()
                if self.current_file == path: await self.close_file()
            except Exception as e: ui.notify(str(e), type='negative')
        ModalSystem.confirm_delete(os.path.basename(path), on_confirm)

    def open_root_picker(self):
        start_dir = self.current_dir if self.fm else USER_HOME
        ModalSystem.folder_picker_dialog(start_dir, USER_HOME, self._on_root_selected, self.fm.list_items if self.fm else FileManager(USER_HOME).list_items)

    async def _on_root_selected(self, path, dialog):
        self.fm = FileManager(path)
        self.current_dir = path
        await self._render_browser_view()
        dialog.close()


app_obj = MKPDFApp()
app_obj.start()

@app.get('/pdf_preview')
def pdf_preview():
    return Response(
        content=pdf_cache['latest'], 
        media_type='application/pdf',
        headers={'Content-Disposition': 'inline; filename="preview.pdf"'}
    )

ui.run(title='MK-PDF', port=8080, reload=True, show=False)
