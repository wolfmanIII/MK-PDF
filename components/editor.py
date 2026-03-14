import json
from nicegui import ui

class Editor:
    def create(self):
        with ui.column().classes('w-full h-full p-0 bg-base-100 items-stretch'):
            # Textarea nuda per EasyMDE
            ui.html('<textarea id="chronos-editor"></textarea>').classes('w-full flex-grow')

    def set_content(self, content):
        # Usiamo json.dumps per compatibilità totale con JavaScript
        content_json = json.dumps(content)
        ui.run_javascript(f'if (window.MKEditor) window.MKEditor.setValue({content_json})')

    async def get_content(self):
        return await ui.run_javascript('window.MKEditor.getValue()')
