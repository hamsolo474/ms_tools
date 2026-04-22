import tkinter as tk
from tkinter import ttk
import pyperclip

class StringToolsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("StringTools")
        self.original_text = ""
        self.current_text = ""

        self.create_widgets()
        self.load_clipboard()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        row = 0
        ttk.Label(main_frame, text="Text:").grid(row=0, column=0, sticky=tk.W)
        text_frame = ttk.Frame(main_frame)
        row +=1
        text_frame.grid(row=row, column=0, columnspan=4, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.text_area = tk.Text(text_frame, height=15, width=50, wrap=tk.WORD)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_area.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.config(yscrollcommand=scrollbar.set)

        row += 1
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=4, pady=5)
        
        ttk.Button(button_frame, text="UPPERCASE", command=self.to_uppercase)      .grid(row=0, column=0, padx=2)
        ttk.Button(button_frame, text="lowercase", command=self.to_lowercase)      .grid(row=0, column=1, padx=2)
        ttk.Button(button_frame, text="Strip Whitespace", command=self.strip_lines).grid(row=0, column=2, padx=2)
        
        row += 1
        ttk.Label(main_frame, text="Prefix:").grid(row=row, column=0, sticky=tk.W)
        self.prefix_entry = ttk.Entry(main_frame, width=15)
        self.prefix_entry.grid(row=row, column=1, pady=5, sticky=tk.W)
        ttk.Button(main_frame, text="Add Prefix", command=self.add_prefix).grid(row=row, column=2, padx=2)

        row += 1
        ttk.Label(main_frame, text="Suffix:")                             .grid(row=row, column=0, sticky=tk.W)
        self.suffix_entry = ttk.Entry(main_frame, width=15)
        self.suffix_entry                                                 .grid(row=row, column=1, pady=5, sticky=tk.W)
        ttk.Button(main_frame, text="Add Suffix", command=self.add_suffix).grid(row=4, column=2, padx=2)

        row += 1
        ttk.Label(main_frame, text="Delimiter:")                               .grid(row=row, column=0, sticky=tk.W)
        self.delimiter_entry = ttk.Entry(main_frame, width=15)
        self.delimiter_entry                                                   .grid(row=row, column=1, pady=5, sticky=tk.W)
        ttk.Button(main_frame, text="Split to Lines", command=self.split_lines).grid(row=row, column=2, padx=2)

        row += 1
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=row, column=0, columnspan=4, pady=10)

        ttk.Button(action_frame, text="Restore Original", command=self.restore_original).grid(row=0, column=0, padx=5)
        ttk.Button(action_frame, text="Copy Modified", command=self.copy_modified)      .grid(row=0, column=1, padx=5)

    def load_clipboard(self):
        try:
            self.original_text = pyperclip.paste()
            self.current_text = self.original_text
            self.update_text_area()
        except:
            self.original_text = ""
            self.current_text = ""

    def update_text_area(self):
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", self.current_text)

    def to_uppercase(self):
        self.current_text = self.current_text.upper()
        self.update_text_area()

    def to_lowercase(self):
        self.current_text = self.current_text.lower()
        self.update_text_area()

    def split_lines(self):
        delimiter = self.delimiter_entry.get()
        if delimiter:
            lines = self.current_text.split(delimiter)
            self.current_text = "\n".join(line for line in lines if line)
            self.update_text_area()

    def strip_lines(self):
        lines = self.current_text.split("\n")
        self.current_text = "\n".join(line.strip() for line in lines)
        self.update_text_area()

    def add_prefix(self):
        prefix = self.prefix_entry.get()
        if prefix:
            lines = self.current_text.split("\n")
            self.current_text = "\n".join(prefix + line for line in lines)
            self.update_text_area()

    def add_suffix(self):
        suffix = self.suffix_entry.get()
        if suffix:
            lines = self.current_text.split("\n")
            self.current_text = "\n".join(line + suffix for line in lines)
            self.update_text_area()

    def restore_original(self):
        self.current_text = self.original_text
        self.update_text_area()

    def copy_modified(self):
        pyperclip.copy(self.current_text)

if __name__ == "__main__":
    root = tk.Tk()
    root.attributes('-topmost', True)
    root.resizable(True, True)
    root.minsize(400, 300)
    root.bind('<Escape>', lambda e: root.destroy())
    app = StringToolsApp(root)
    root.mainloop()