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
                
                with ui.row().classes('w-full justify-end q-gutter-sm'):
                    ui.button('Annulla', on_click=dialog.close).props('flat color=primary')
                    ui.button('Crea File', on_click=lambda: on_create(name_input.value, dialog)).props('unelevated color=primary').classes('q-px-md')
        dialog.open()

    @staticmethod
    def confirm_delete(filename, on_confirm):
        with ui.dialog() as dialog, ui.card().classes('q-pa-none overflow-hidden bg-[#0f172a]').style('width: 400px'):
            with ui.row().classes('q-pa-md bg-negative text-white items-center'):
                ui.icon('warning', size='md').classes('q-mr-sm')
                ui.label('ELIMINAZIONE DATI').classes('text-h6 text-weight-bold')
            
            with ui.column().classes('q-pa-md w-full items-center'):
                ui.label(f'Confermi l\'epurazione definitiva di "{filename}"?').classes('text-body1 text-center')
                
                with ui.row().classes('q-gutter-md q-pt-md'):
                    ui.button('Annulla', on_click=dialog.close).props('flat color=grey')
                    ui.button('Epurazione', on_click=lambda: on_confirm(dialog)).props('unelevated color=negative')
        dialog.open()

    @staticmethod
    def folder_picker_dialog(current_path, project_root, on_select, navigate_logic):
        dialog = ui.dialog()
        state = {'path': current_path}
        
        def update_ui():
            content_container.clear()
            with content_container:
                # Breadcrumbs stile Quasar
                with ui.row().classes('w-full q-pa-sm bg-[#1e293b] rounded items-center'):
                    parts = state['path'].strip('/').split('/')
                    acc = '/'
                    ui.icon('folder', size='xs').classes('q-mr-xs')
                    for part in parts:
                        if not part: continue
                        acc = os.path.join(acc, part)
                        def mk_go(p=acc):
                            state['path'] = p
                            update_ui()
                        ui.label(part).classes('cursor-pointer text-primary text-weight-medium').on('click', mk_go)
                        ui.label('/').classes('q-px-xs opacity-50')

                # Lista items stile Quasar
                with ui.scroll_area().style('height: 300px; width: 100%').classes('border border-white/10 q-mt-md bg-[#0f172a]'):
                    items = navigate_logic(state['path'])
                    with ui.list().props('bordered separator'):
                        for item in items:
                            if item['is_dir']:
                                with ui.item(on_click=lambda p=item['path']: (state.update({'path': p}), update_ui())).props('clickable'):
                                    with ui.item_section().props('avatar'):
                                        ui.icon('folder', color='warning')
                                    with ui.item_section():
                                        ui.label(item['name']).classes('text-weight-bold')

                # Input percorso
                with ui.column().classes('w-full q-mt-md q-gutter-sm'):
                    ui.label('PERCORSO MANUALE').classes('text-overline text-primary')
                    path_input = ui.input(value=state['path']).props('outlined dense color=primary').classes('w-full')
                    path_input.on('change', lambda e: (state.update({'path': e.value}), update_ui()))

        with dialog, ui.card().classes('q-pa-none overflow-hidden bg-[#0f172a]').style('width: 540px'):
            with ui.column().classes('w-full q-pa-md bg-primary text-white'):
                ui.label('Settore Operativo').classes('text-h6 text-weight-bold')
                ui.label('Navigazione sorgenti dati').classes('text-caption opacity-80')
            
            content_container = ui.column().classes('q-pa-md w-full')
            update_ui()
            
            with ui.row().classes('q-pa-md w-full justify-end q-gutter-sm border-t'):
                ui.button('Annulla', on_click=dialog.close).props('flat color=primary')
                ui.button('Connetti', on_click=lambda: on_select(state['path'], dialog)).props('unelevated color=primary')
        
        dialog.open()
