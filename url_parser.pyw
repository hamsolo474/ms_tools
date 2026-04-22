import re
import tkinter as tk
from tkinter import ttk, messagebox
import urllib.parse
import pyperclip
import subprocess


class GUIDRow(ttk.Frame):
    def __init__(self, parent, row_num, label, guid, url_patterns, on_remove, default_url="Fabric Service Portal", **kwargs):
        super().__init__(parent, **kwargs)
        self.row_num = row_num
        self.guid = guid
        self.url_patterns = url_patterns
        self.on_remove = on_remove
        self.link_var = tk.StringVar(value=default_url)

        ttk.Label(self, text=str(row_num), width=4).pack(side=tk.LEFT, padx=2)

        self.label_entry = ttk.Entry(self, width=18)
        self.label_entry.insert(0, label)
        self.label_entry.pack(side=tk.LEFT, padx=2)
        self.label_entry.bind('<KeyRelease>', self._on_any_change)

        self.guid_entry = ttk.Entry(self, width=35)
        self.guid_entry.insert(0, guid)
        self.guid_entry.configure(state='readonly')
        self.guid_entry.pack(side=tk.LEFT, padx=2)

        self.anchor_entry = ttk.Entry(self, width=18)
        self.anchor_entry.insert(0, label)
        self.anchor_entry.pack(side=tk.LEFT, padx=2)
        self.anchor_entry.bind('<KeyRelease>', self._on_any_change)

        self.url_combo = ttk.Combobox(
            self,
            textvariable=self.link_var,
            values=list(url_patterns.keys()),
            state='readonly',
            width=20
        )
        self.url_combo.pack(side=tk.LEFT, padx=2)
        self.url_combo.bind('<<ComboboxSelected>>', self._on_any_change)

        self.remove_btn = ttk.Button(self, text="X", width=3, command=self._do_remove)
        self.remove_btn.pack(side=tk.LEFT, padx=2)

    def _do_remove(self):
        self.on_remove(self)

    def _on_any_change(self, event=None):
        pass

    def get_url(self):
        pattern = self.url_patterns.get(self.link_var.get(), "")
        return pattern.replace("%guid%", self.guid)

    def get_anchor_text(self):
        return self.anchor_entry.get().strip()

    def get_label(self):
        return self.label_entry.get().strip()

    def get_markdown_link(self):
        anchor = self.get_anchor_text() or self.get_label()
        url = self.get_url()
        return f'<a href="{url}">{anchor}</a>'

    def get_display_line(self):
        label = self.get_label()
        return f"{label}: {self.guid}"

    def get_html_for_word(self):
        anchor = self.get_anchor_text() or self.get_label()
        url = self.get_url()
        return f'{anchor}: {self.guid} <a href="{url}">{anchor}</a>'


class URLParserApp:
    GUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
    
    URL_PATTERNS = {
        "Fabric Service Portal": "https://serviceportal.fabric.microsoft-int.com/object-viewer?oid=%guid%",
    }

    LABEL_MAPPINGS = {
        "groups": ("Workspace", "Fabric Service Portal"),
        "lakehouses": ("Lakehouse", "Fabric Service Portal"),
        "lakehouse": ("Lakehouse", "Fabric Service Portal"),
        "lakewarehouses": ("Lakehouse", "Fabric Service Portal"),
        "lakewarehouse": ("Lakehouse", "Fabric Service Portal"),
        "warehouse": ("Warehouse", "Fabric Service Portal"),
        "warehouses": ("Warehouse", "Fabric Service Portal"),
        "pipelines": ("Data Pipeline", "Fabric Service Portal"),
        "pipeline": ("Data Pipeline", "Fabric Service Portal"),
        "notebooks": ("Notebook", "Fabric Service Portal"),
        "notebook": ("Notebook", "Fabric Service Portal"),
        "datasets": ("Dataset", "Fabric Service Portal"),
        "dataset": ("Dataset", "Fabric Service Portal"),
        "reports": ("Report", "Fabric Service Portal"),
        "report": ("Report", "Fabric Service Portal"),
        "dashboards": ("Dashboard", "Fabric Service Portal"),
        "dashboard": ("Dashboard", "Fabric Service Portal"),
        "dataflows": ("Dataflow", "Fabric Service Portal"),
        "dataflow": ("Dataflow", "Fabric Service Portal"),
        "dataflow-gen2": ("Dataflow", "Fabric Service Portal"),
        "dataflows-gen2": ("Dataflow", "Fabric Service Portal"),
        "kqldatabases": ("KQL Database", "Fabric Service Portal"),
        "kqldatabase": ("KQL Database", "Fabric Service Portal"),
        "kqldashboards": ("KQL Dashboard", "Fabric Service Portal"),
        "kqldashboard": ("KQL Dashboard", "Fabric Service Portal"),
        "eventhouses": ("Eventhouse", "Fabric Service Portal"),
        "eventhouse": ("Eventhouse", "Fabric Service Portal"),
        "eventstreams": ("Eventstream", "Fabric Service Portal"),
        "eventstream": ("Eventstream", "Fabric Service Portal"),
        "mlExperiments": ("ML Experiment", "Fabric Service Portal"),
        "mlexperiment": ("ML Experiment", "Fabric Service Portal"),
        "mlModels": ("ML Model", "Fabric Service Portal"),
        "mlmodel": ("ML Model", "Fabric Service Portal"),
        "datamarts": ("Datamart", "Fabric Service Portal"),
        "datamart": ("Datamart", "Fabric Service Portal"),
        "databricks": ("Databricks", "Fabric Service Portal"),
        "sqlEndpoints": ("SQL Endpoint", "Fabric Service Portal"),
        "sqlendpoint": ("SQL Endpoint", "Fabric Service Portal"),
        "capacity": ("Capacity", "Fabric Service Portal"),
        "ctid": ("Tenant ID", "Fabric Service Portal"),
        "clientSideAuth": ("Client Auth", "Fabric Service Portal"),
    }

    def __init__(self, root):
        self.root = root
        self.root.title("PBI URL Splitter")
        self.root.geometry("900x150")
        self.root.attributes('-topmost', True)
        self.root.bind('<Escape>', lambda e: self.root.destroy())

        self.guid_rows = []
        self.max_visible_rows = 5

        self._setup_ui()
        self.root.update_idletasks()

        try:
            clipboard_url = pyperclip.paste()
            if clipboard_url and clipboard_url.startswith(('http://', 'https://')):
                self.url_entry.insert(0, clipboard_url)
                self.parse_url()
        except Exception:
            pass

    def _setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="URL:").pack(anchor=tk.W)
        url_frame = ttk.Frame(main_frame)
        url_frame.pack(fill=tk.X, pady=(0, 5))
        self.url_entry = ttk.Entry(url_frame, width=100)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.url_entry.bind('<Return>', lambda e: self.parse_url())
        self.parse_btn = ttk.Button(url_frame, text="Parse URL", command=self.parse_url)
        self.parse_btn.pack(side=tk.LEFT, padx=(5, 0))

        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(10, 5))
        ttk.Label(header_frame, text="#", width=4).pack(side=tk.LEFT, padx=2)
        ttk.Label(header_frame, text="Label", width=18).pack(side=tk.LEFT, padx=2)
        ttk.Label(header_frame, text="GUID", width=35).pack(side=tk.LEFT, padx=2)
        ttk.Label(header_frame, text="Anchor", width=18).pack(side=tk.LEFT, padx=2)
        ttk.Label(header_frame, text="URL", width=22).pack(side=tk.LEFT, padx=2)
        ttk.Label(header_frame, text="", width=14).pack(side=tk.LEFT, padx=2)

        self.rows_frame = ttk.Frame(main_frame)
        self.rows_frame.pack(fill=tk.X, pady=(0, 5))

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))

        self.copy_btn = ttk.Button(btn_frame, text="Copy All", command=self.copy_all)
        self.copy_btn.pack(side=tk.LEFT)

    def _clear_rows(self):
        for row in self.guid_rows:
            row.destroy()
        self.guid_rows = []
        self._resize_window()

    def _add_row(self, detected_label, display_label, guid, default_url="Fabric Service Portal"):
        row = GUIDRow(
            self.rows_frame,
            len(self.guid_rows) + 1,
            display_label,
            guid,
            self.URL_PATTERNS,
            on_remove=self._remove_row,
            default_url=default_url
        )
        row.pack(fill=tk.X, pady=2)
        self.guid_rows.append(row)
        self._resize_window()

    def _remove_row(self, row):
        self.guid_rows.remove(row)
        row.destroy()
        for i, r in enumerate(self.guid_rows):
            r.row_num = i + 1
        self._resize_window()

    def _resize_window(self):
        self.root.update_idletasks()
        row_height = 30
        base_height = 140
        num_rows = len(self.guid_rows)
        height = min(num_rows, self.max_visible_rows) * row_height + base_height
        width = self.root.winfo_width()
        if width < 100:
            width = 900
        self.root.geometry(f"{width}x{height}")

    def _get_mapped_label(self, detected_label):
        mapping = self.LABEL_MAPPINGS.get(detected_label)
        if mapping:
            return mapping[0], mapping[1]
        return detected_label, "Fabric Service Portal"

    def parse_url(self):
        self._clear_rows()

        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Input Required", "Please enter a URL")
            return

        if not url.startswith(('http://', 'https://')):
            messagebox.showwarning("Invalid URL", "Please enter a valid URL starting with http:// or https://")
            return

        try:
            parsed = urllib.parse.urlparse(url)
        except Exception as e:
            messagebox.showerror("Parse Error", f"Failed to parse URL: {e}")
            return

        path_parts = [p for p in parsed.path.split('/') if p]

        for i, part in enumerate(path_parts):
            if self.GUID_PATTERN.match(part):
                detected_label = path_parts[i - 1] if i > 0 else "path"
                mapped_label, default_url = self._get_mapped_label(detected_label)
                self._add_row(detected_label, mapped_label, part.lower(), default_url)

        query_params = urllib.parse.parse_qsl(parsed.query)
        for param_name, param_value in query_params:
            if self.GUID_PATTERN.match(param_value):
                mapped_label, default_url = self._get_mapped_label(param_name)
                self._add_row(param_name, mapped_label, param_value.lower(), default_url)

        if not self.guid_rows:
            messagebox.showinfo("No GUIDs", "No GUIDs found in URL")

    def copy_all(self):
        if not self.guid_rows:
            messagebox.showwarning("No Output", "No GUIDs parsed. Please parse a URL first.")
            return

        html_parts = []
        for row in self.guid_rows:
            html_parts.append(row.get_html_for_word())
        html_content = "<br>".join(html_parts)

        self._copy_html_to_clipboard(html_content)

    def _copy_html_to_clipboard(self, content):
        import subprocess
        
        cf_header = 'Version:0.9\n'
        cf_header += 'StartHTML:00000000\n'
        cf_header += 'EndHTML:00000000\n'
        cf_header += 'StartFragment:00000000\n'
        cf_header += 'EndFragment:00000000\n'
        
        html_prefix = '<html><head><meta charset="UTF-8"></head><body>'
        html_suffix = '</body></html>'
        
        start_frag_tag = '<!--StartFragment-->'
        end_frag_tag = '<!--EndFragment-->'
        
        start_html_offset = len(cf_header)
        start_frag_offset = start_html_offset + len(html_prefix) + len(start_frag_tag)
        end_frag_offset = start_frag_offset + len(content)
        end_html_offset = end_frag_offset + len(end_frag_tag) + len(html_suffix)
        
        cf_header = (f'Version:0.9\n'
                   f'StartHTML:{start_html_offset:08d}\n'
                   f'EndHTML:{end_html_offset:08d}\n'
                   f'StartFragment:{start_frag_offset:08d}\n'
                   f'EndFragment:{end_frag_offset:08d}\n')
        
        cf_html = cf_header + html_prefix + start_frag_tag + content + end_frag_tag + html_suffix
        
        cmd = f'''$html = @'
{cf_html}
'@; Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Clipboard]::SetText($html, [System.Windows.Forms.TextDataFormat]::Html)'''
        
        subprocess.run(['powershell', '-Command', cmd], capture_output=True)


def main():
    root = tk.Tk()
    app = URLParserApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
