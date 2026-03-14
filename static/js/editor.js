/**
 * MK-PDF Editor - Core Logic
 */

console.log("MK-PDF Editor System Initializing...");

window.MKEditor = {
    instance: null,

    init: function() {
        console.log("MKEditor: init() called");
        const target = document.getElementById('chronos-editor');
        
        if (!target) {
            console.error("MKEditor: Target textarea #chronos-editor NOT FOUND in DOM");
            return;
        }

        if (typeof EasyMDE === 'undefined') {
            console.error("MKEditor: EasyMDE library NOT LOADED. Retrying in 500ms...");
            setTimeout(() => this.init(), 500);
            return;
        }
        
        // Se l'istanza esiste già ed è nel DOM, refresh e stop
        if (this.instance && document.body.contains(this.instance.element)) {
            console.log("MKEditor: Instance exists, refreshing...");
            this.hidePlaceholder();
            this.instance.codemirror.refresh();
            return;
        }

        // Cleanup istanze orfane
        if (this.instance) {
            console.log("MKEditor: Cleaning up detached instance...");
            try { this.instance.toTextArea(); } catch(e) {}
            this.instance = null;
        }

        console.log("MKEditor: Creating new EasyMDE instance");
        try {
            target.style.display = 'block'; 
            
            this.instance = new EasyMDE({
                element: target,
                spellChecker: false,
                minHeight: "500px",
                forceSync: true,
                autoDownloadFontAwesome: false,
                toolbar: [
                    "bold", "italic", "heading", "|", 
                    "quote", "unordered-list", "ordered-list", "|", 
                    "link", "image", "table", "|", 
                    "preview", "side-by-side", "|", 
                    "guide"
                ],
                previewRender: (plainText) => {
                    const rendered = this.instance.markdown(plainText);
                    this.renderMermaid();
                    return rendered;
                }
            });
            
            console.log("MKEditor: EasyMDE initialized successfully");
            this.hidePlaceholder();
            
            setTimeout(() => {
                if (this.instance) this.instance.codemirror.refresh();
            }, 250);
            
        } catch (e) {
            console.error("MKEditor: Initialization failed", e);
        }
    },

    hidePlaceholder: function() {
        const p = document.querySelector('.mk-editor-placeholder');
        if (p) p.style.display = 'none';
    },

    setValue: function(content) {
        console.log("MKEditor: setValue() called");
        
        const doSet = () => {
            if (this.instance) {
                console.log("MKEditor: Setting value");
                this.instance.value(content || "");
                this.hidePlaceholder();
                this.instance.codemirror.refresh();
                setTimeout(() => this.instance.codemirror.refresh(), 100);
            } else {
                console.log("MKEditor: Instance null in setValue, init and retry...");
                this.init();
                setTimeout(() => this.setValue(content), 400);
            }
        };

        if (!this.instance || !document.body.contains(this.instance.element)) {
            this.init();
            setTimeout(doSet, 400);
        } else {
            doSet();
        }
    },

    getValue: function() {
        return this.instance ? this.instance.value() : "";
    },

    renderMermaid: function() {
        if (!window.mermaid) return;
        setTimeout(() => {
            const containers = document.querySelectorAll(".editor-preview pre code.language-mermaid, .editor-preview-side pre code.language-mermaid");
            containers.forEach((c, i) => {
                const parent = c.parentElement;
                if (parent.getAttribute('data-mermaid-processed')) return;
                
                const id = 'mermaid-svg-' + i + '-' + Date.now();
                const code = c.textContent;
                try {
                    mermaid.render(id, code).then(({svg}) => {
                        parent.innerHTML = svg;
                        parent.setAttribute('data-mermaid-processed', 'true');
                        parent.style.background = 'transparent';
                    });
                } catch (e) { console.error("Mermaid error:", e); }
            });
        }, 200);
    }
};
