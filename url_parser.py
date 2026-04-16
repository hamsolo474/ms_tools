import re
import tkinter as tk
from tkinter import ttk, messagebox
import urllib.parse
import pyperclip


class GUIDRow(ttk.Frame):
    def __init__(self, parent, row_num, label, guid, url_patterns, on_remove, 
    #on_update, 
    **kwargs):
        super().__init__(parent, **kwargs)
        self.row_num = row_num
        self.guid = guid
        self.url_patterns = url_patterns
        self.on_remove = on_remove
    #    self.on_update = on_update
        self.link_var = tk.StringVar(value="Fabric Service Portal")

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
        #self.on_update(self)

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
        return f"[{anchor}]({url})"

    def get_display_line(self):
        label = self.get_label()
        return f"{label}: {self.guid}"

    def update_preview(self):
        pass


class URLParserApp:
    GUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
    
    URL_PATTERNS = {
        "Fabric Service Portal": "https://serviceportal.fabric.microsoft-int.com/object-viewer?oid=%guid%",
    }

    LABEL_MAPPINGS = {
        "groups": "Workspace",
        "lakehouses": "Lakehouse",
        "lakehouse": "Lakehouse",
        "lakewarehouses": "Lakehouse",
        "lakewarehouse": "Lakehouse",
        "warehouse": "Warehouse",
        "warehouses": "Warehouse",
        "pipelines": "Data Pipeline",
        "pipeline": "Data Pipeline",
        "notebooks": "Notebook",
        "notebook": "Notebook",
        "datasets": "Dataset",
        "dataset": "Dataset",
        "reports": "Report",
        "report": "Report",
        "dashboards": "Dashboard",
        "dashboard": "Dashboard",
        "dataflows": "Dataflow",
        "dataflow": "Dataflow",
        "kqldatabases": "KQL Database",
        "kqldatabase": "KQL Database",
        "kqldashboards": "KQL Dashboard",
        "kqldashboard": "KQL Dashboard",
        "eventhouses": "Eventhouse",
        "eventhouse": "Eventhouse",
        "eventstreams": "Eventstream",
        "eventstream": "Eventstream",
        "mlExperiments": "ML Experiment",
        "mlexperiment": "ML Experiment",
        "mlModels": "ML Model",
        "mlmodel": "ML Model",
        "datamarts": "Datamart",
        "datamart": "Datamart",
        "databricks": "Databricks",
        "sqlEndpoints": "SQL Endpoint",
        "sqlendpoint": "SQL Endpoint",
        "capacity": "Capacity",
        "ctid": "Tenant ID",
        "clientSideAuth": "Client Auth",
    }

    def __init__(self, root):
        self.root = root
        self.root.title("PBI URL Splitter")
        self.root.geometry("900x150")

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

    def _add_row(self, detected_label, display_label, guid):
        row = GUIDRow(
            self.rows_frame,
            len(self.guid_rows) + 1,
            display_label,
            guid,
            self.URL_PATTERNS,
            on_remove=self._remove_row,
            #on_update=self._update_row
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

    #def _update_row(self, row):
    #    pass

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
        return self.LABEL_MAPPINGS.get(detected_label, detected_label)

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
                mapped_label = self._get_mapped_label(detected_label)
                self._add_row(detected_label, mapped_label, part.lower())

        query_params = urllib.parse.parse_qsl(parsed.query)
        for param_name, param_value in query_params:
            if self.GUID_PATTERN.match(param_value):
                mapped_label = self._get_mapped_label(param_name)
                self._add_row(param_name, mapped_label, param_value.lower())

        if not self.guid_rows:
            messagebox.showinfo("No GUIDs", "No GUIDs found in URL")

    def copy_all(self):
        if not self.guid_rows:
            messagebox.showwarning("No Output", "No GUIDs parsed. Please parse a URL first.")
            return
        parts = []
        for row in self.guid_rows:
            parts.append(f"{row.get_display_line()} {row.get_markdown_link()}")
        text = "\n".join(parts)
        pyperclip.copy(text)
        #messagebox.showinfo("Copied", "All data copied to clipboard!")


def main():
    root = tk.Tk()
    app = URLParserApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
