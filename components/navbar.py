from nicegui import ui

def create_navbar():
    # Usando pure Quasar/NiceGUI props e classes
    with ui.header().props('elevated').classes('q-pa-md items-center justify-between'):
        with ui.row().classes('items-center'):
            ui.icon('satellite_alt', size='md').props('color=white')
            ui.label('MK-PDF').classes('text-h5 text-weight-bold q-ml-md')
        
        with ui.row().classes('items-center'):
            ui.button(icon='settings', on_click=lambda: ui.notify('Impostazioni non implementate')).props('flat round color=white')
