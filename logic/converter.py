import requests
import markdown
import os

class GotenbergClient:
    def __init__(self, host='http://localhost:3000'):
        self.host = host

    def convert_markdown(self, md_content):
        # Convert MD to HTML with Tailwind/Mermaid support
        html_content = self._wrap_html(md_content)
        
        try:
            # Save temporary HTML for Gotenberg (still needed as a file for the multipart request)
            temp_html = 'temp_print.html'
            with open(temp_html, 'w') as f:
                f.write(html_content)

            url = f'{self.host}/forms/chromium/convert/html'

            # Carichiamo il template del footer
            footer_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'pdf_footer.html')
            with open(footer_path, 'r') as f_footer:
                footer_content = f_footer.read()

            with open(temp_html, 'rb') as f:
                files = {
                    'index.html': ('index.html', f, 'text/html'),
                    'footer.html': ('footer.html', footer_content, 'text/html')
                }
                data = {
                    'waitDelay': '2s',
                    'displayHeaderFooter': 'true',
                    'paperWidth': '8.27', 
                    'paperHeight': '11.69',
                    'marginTop': '1in',
                    'marginBottom': '1in',
                    'marginLeft': '1in',
                    'marginRight': '1in'
                }

                response = requests.post(url, files=files, data=data)
            
            if response.status_code == 200:
                return response.content
            else:
                print(f"Gotenberg error ({response.status_code}): {response.text}")
                return None
        except Exception as e:
            print(f"Conversion error: {e}")
            return None
        finally:
            if os.path.exists(temp_html):
                os.remove(temp_html)

    def _wrap_html(self, md_content):
        # Convert MD to HTML using python-markdown
        body_html = markdown.markdown(md_content, extensions=['fenced_code', 'tables', 'toc'])
        
        # Load template and script
        base_dir = os.path.dirname(__file__)
        template_path = os.path.join(base_dir, '..', 'templates', 'pdf_wrapper.html')
        script_path = os.path.join(base_dir, '..', 'static', 'js', 'pdf_init.js')
        
        with open(template_path, 'r') as f:
            template = f.read()
        with open(script_path, 'r') as f:
            script = f.read()
            
        # Replacement
        rendered = template.replace('{{ body }}', body_html)
        return rendered.replace('{{ script }}', script)
