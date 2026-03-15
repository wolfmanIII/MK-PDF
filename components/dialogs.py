from nicegui import ui
import os

class ModalSystem:
    @staticmethod
    def show_new_file_dialog(on_create):
        with ui.dialog() as dialog, ui.card().classes('q-pa-none overflow-hidden bg-[#0f172a]').style('width: 420px'):
            # Header con stile Quasar
            with ui.column().classes('w-full q-pa-md bg-primary text-white'):
                ui.label('NUOVO DOCUMENTO').classes('text-h6 text-weight-bold')
                ui.label('Inizializzazione sequenza dati markdown').classes('text-caption opacity-80 text-uppercase')
                
            with ui.column().classes('q-pa-lg w-full q-gutter-md'):
                ui.label('IDENTIFICATIVO FILE').classes('text-overline text-primary')
                name_input = ui.input(placeholder='es: rapporto_missione.md').props('outlined autofocus color=primary').classes('w-full')
                
                async def handle_create():
                    await on_create(name_input.value, dialog)
                with ui.row().classes('w-full justify-end q-gutter-sm'):
                    ui.button('Annulla', on_click=dialog.close).props('flat color=primary')
                    ui.button('Crea File', on_click=handle_create).props('unelevated color=primary').classes('q-px-md')
        dialog.open()


    @staticmethod
    def confirm_delete(filename, on_confirm):
        with ui.dialog() as dialog, ui.card().classes('q-pa-none overflow-hidden bg-[#0f172a]').style('width: 400px'):
            with ui.row().classes('q-pa-md bg-negative text-white items-center'):
                ui.icon('warning', size='md').classes('q-mr-sm')
                ui.label('ELIMINAZIONE DATI').classes('text-h6 text-weight-bold')
            
            with ui.column().classes('q-pa-md w-full items-center'):
                ui.label(f'Confermi l\'epurazione definitiva di "{filename}"?').classes('text-body1 text-center')
                
                async def handle_confirm():
                    await on_confirm(dialog)
                with ui.row().classes('q-gutter-md q-pt-md'):
                    ui.button('Annulla', on_click=dialog.close).props('flat color=grey')
                    ui.button('Epurazione', on_click=handle_confirm).props('unelevated color=negative')
        dialog.open()

    @staticmethod
    def folder_picker_dialog(current_path, min_root, on_select, navigate_logic):
        dialog = ui.dialog()
        state = {'path': current_path}
        
        async def update_ui():
            content_container.clear()
            # Forza il percorso a essere almeno min_root
            if not state['path'].startswith(min_root):
                state['path'] = min_root
                
            with content_container:
                # Breadcrumbs stile Quasar
                with ui.row().classes('w-full q-pa-sm bg-[#1e293b] rounded items-center'):
                    # Calcoliamo il path relativo a min_root per i breadcrumbs
                    rel = os.path.relpath(state['path'], min_root)
                    parts = [] if rel == "." else rel.split(os.sep)
                    
                    ui.icon('home', size='xs').classes('q-mr-xs')
                    async def go_home():
                        state.update({'path': min_root})
                        await update_ui()
                    ui.label('HOME').classes('cursor-pointer text-primary text-weight-medium').on('click', go_home)
                    
                    acc = min_root
                    for part in parts:
                        if not part: continue
                        acc = os.path.join(acc, part)
                        ui.label('/').classes('q-px-xs opacity-50')
                        async def mk_go(p=acc):
                            state['path'] = p
                            await update_ui()
                        ui.label(part).classes('cursor-pointer text-primary text-weight-medium').on('click', mk_go)

                # Lista items stile Premium (Compatto)
                with ui.scroll_area().style('height: 380px; width: 100%').classes('q-mt-md bg-[#0f172a] rounded-borders'):
                    items = await navigate_logic(state['path'])
                    with ui.column().classes('w-full q-pa-sm q-gutter-xs'):
                        # Il pulsante "torna indietro"
                        if state['path'] != min_root:
                            parent = os.path.dirname(state['path'])
                            async def go_back():
                                state.update({'path': parent})
                                await update_ui()
                            with ui.row().classes('w-full q-pa-xs items-center cursor-pointer hover:bg-white/5 rounded-borders transition-colors group') \
                                .on('click', go_back):
                                ui.icon('folder_open', color='grey-5', size='xs').classes('opacity-60 group-hover:opacity-100')
                                ui.label('.. / Parent Directory').classes('text-caption opacity-40 group-hover:opacity-80')

                        for item in items:
                            if item['is_dir']:
                                async def go_in(p=item['path']):
                                    state.update({'path': p})
                                    await update_ui()
                                with ui.row().classes('w-full q-pa-sm items-center cursor-pointer hover:bg-primary/10 rounded-borders transition-colors group border-b border-white/5') \
                                    .on('click', go_in):
                                    
                                    with ui.row().classes('items-center q-gutter-sm col-grow'):
                                        ui.icon('folder', color='warning', size='sm').classes('group-hover:scale-110 transition-transform')
                                        ui.label(item['name']).classes('text-weight-bold text-white text-body2')
                                    
                                    ui.icon('chevron_right', color='grey-5', size='xs').classes('opacity-0 group-hover:opacity-100 transition-opacity')

                # Input percorso
                with ui.column().classes('w-full q-mt-lg q-gutter-sm'):
                    ui.label('LOCALIZZAZIONE MANUALE').classes('text-overline text-primary letter-spacing-1')
                    with ui.input(value=state['path']).props('outlined dense color=primary bg-color=slate-900').classes('w-full shadow-inner') as path_input:
                        with path_input.add_slot('prepend'):
                            ui.icon('place', size='xs')
                    
                    async def on_path_change(e):
                        new_p = os.path.abspath(e.value)
                        if new_p.startswith(min_root):
                            state['path'] = new_p
                        else:
                            ui.notify('Accesso negato fuori dalla Home', type='warning')
                        await update_ui()
                    path_input.on('change', on_path_change)

        with dialog, ui.card().classes('q-pa-none overflow-hidden bg-[#0f172a]').style('width: 540px'):
            with ui.column().classes('w-full q-pa-md bg-primary text-white'):
                ui.label('Settore Operativo').classes('text-h6 text-weight-bold')
                ui.label('Navigazione sorgenti dati').classes('text-caption opacity-80')
            
            content_container = ui.column().classes('q-pa-md w-full')
            ui.timer(0.1, update_ui, once=True)
            
            with ui.row().classes('q-pa-md w-full justify-end q-gutter-sm border-t'):
                ui.button('Annulla', on_click=dialog.close).props('flat color=primary')
                async def submit():
                    await on_select(state['path'], dialog)
                ui.button('Connetti', on_click=submit).props('unelevated color=primary')
        
        dialog.open()
