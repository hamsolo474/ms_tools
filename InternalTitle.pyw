import re
import sys
import subprocess
import tkinter as tk
import datetime as dt
from tkinter import ttk
try:
    import pyperclip
except ModuleNotFoundError: 
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyperclip"])
    import pyperclip


# Example string
dateformat = "%b/%d"
today = dt.datetime.today().strftime(dateformat)
nc = (dt.datetime.today()+dt.timedelta(days=2)).strftime(dateformat)
example = f"Responded | LC: {today} NC: {nc} (Email)| Copilot: Yes | ASC: No | ActionOn: CSS | Region: APAC"

# Dropdown options
ActionOnL = ["CSS", "Collab", "PG", "Customer"]
BoolsD = {'1': "Yes", '0': "No", "Yes": "Yes", "No": "No"}
StatusL = ["Pending PG", "Pending Collab", "Responded", "FQR", "Solution given", "FU1", "FU2", "FU3", "Pending Closure", "Case closure checklist complete"]
ContactMethodL = ["Email", "Teams", "Phone call"]
RegionL = ['APAC', 'NAM', 'EMEA', 'IST']

# Regex patterns for editable fields
patterns = {
    "LC": r"LC:\s*(.../\d{1,2})",
    "NC": r"NC:\s*(.../\d{1,2})",
    "Copilot": r"Copilot:\s*(Yes|No)",
    "ASC": r"ASC:\s*(Yes|No)",
    "ActionOn": r"ActionOn:\s*(\w+)",
    "Region": r"Region:\s*(\w+)",
    "ContactMethod": r"(\(\w+\))",
    "Status": r'(^[^|]*)'
}

def reset():
    text_box.delete("1.0", tk.END)
    text_box.insert(tk.END, example)

def copy():
    pyperclip.copy(text_box.get('1.0', tk.END))

def close_on_escape(event=None):
    root.destroy()

# Extract initial values
def extract_values(text):
    values = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            values[key] = match.group(1)
    return values

# Update text box when dropdown changes
def update_text(*args):
    new_text = example
    new_text = re.sub(patterns["ActionOn"],      f"ActionOn: {actionon_var.get()}",         new_text+" ")
    new_text = re.sub(patterns["Region"],        f"Region: {region_var.get()}",             new_text+" ")
    new_text = re.sub(patterns["Copilot"],       f"Copilot: {BoolsD[copilot_var.get()]}",   new_text+" ")
    new_text = re.sub(patterns["ASC"],           f"ASC: {BoolsD[asc_var.get()]}",           new_text+" ")
    new_text = re.sub(patterns["NC"],            f"NC: {nc_var.get()}",                     new_text+" ")
    new_text = re.sub(patterns["LC"],            f"LC: {lc_var.get()}",                     new_text+" ")
    new_text = re.sub(patterns["ContactMethod"], f"({cm_var.get()})",                       new_text+" ")
    new_text = re.sub(patterns["Status"],        f"{status_var.get()}",                     new_text+" ")
    text_box.delete("1.0", tk.END)
    text_box.insert(tk.END, new_text)

# GUI setup
root = tk.Tk()
root.withdraw()
 # Get mouse loc
x = root.winfo_pointerx()-300
y = root.winfo_pointery()-50
top = tk.Toplevel(root)
top.geometry(f"+{x}+{y}") 

top.title("Internal Title tool")
top.attributes("-topmost", True)
top.bind("<Escape>", close_on_escape)

# Extract initial values
initial_values = extract_values(example)

# Frame for dropdowns
frame = tk.Frame(top)
frame.pack(pady=10)

def widgets(label, value, default, wtype, row, col, ddvals=None):
    tk.Label(frame, text=label).grid(row=row, column=col, padx=5)
    var = tk.StringVar(value=initial_values.get(value, default))
    if wtype == 'dd':
        widget = ttk.Combobox(frame, textvariable=var, values=ddvals)
        var.trace("w", update_text)
    elif wtype == 'cb':
        widget = ttk.Checkbutton(frame, variable=var, command=update_text)
        var.trace("w", update_text)
    else:
        assert(wtype in ['dd','cb'])
    widget.grid(row=row, column=col+1, padx=5)
    return var

row = 0
# LC Dropdown
col = 0
lc_var = widgets(label="LC Date:", 
                 value="LC", 
                 default=today, 
                 wtype="dd", 
                 row=row, col=col, 
                 ddvals=[(dt.datetime.today()-dt.timedelta(days=i)).strftime(dateformat) for i in range(3)])

# NC Dropdown
col = 2
nc_var = widgets(label="NC Date:", 
                 value="NC", 
                 default=nc,
                 wtype="dd", 
                 row=row, col=col, 
                 ddvals=[(dt.datetime.today()+dt.timedelta(days=i+1)).strftime(dateformat) for i in range(7)])


row+=1 
#Status Dropdown
col = 0
status_var = widgets(label="Status:", 
                 value="Status", 
                 default="FQR",
                 wtype="dd", 
                 row=row, col=col, 
                 ddvals=StatusL)
# ActionOn Dropdown
col = 2
actionon_var = widgets(label="ActionOn", 
                 value="ActionOn", 
                 default="CSS",
                 wtype="dd", 
                 row=row, col=col, 
                 ddvals=ActionOnL)

row+=1
# Region Dropdown
col = 0
region_var = widgets(label="Region", 
                 value="Region", 
                 default="APAC",
                 wtype="dd", 
                 row=row, col=col, 
                 ddvals=RegionL)

# Contact Method Dropdown
col = 2
cm_var = widgets(label="Contact Method", 
                 value="ContactMethod", 
                 default="Email",
                 wtype="dd", 
                 row=row, col=col, 
                 ddvals=ContactMethodL)

row+=1
# Copilot CB
col = 0
copilot_var = widgets(label="Copilot:", 
                 value="Copilot", 
                 default='1',
                 wtype="cb", 
                 row=row, col=col)

# ASC CB
col = 2
asc_var = widgets(label="ASC:", 
                 value="ASC", 
                 default='0',
                 wtype="cb", 
                 row=row, col=col)



row+=1
# Reset button
col = 1
tk.Button(frame, text="Reset String", command=reset).grid(row=row, column=col, padx=5)

# Reset button
col = 3
tk.Button(frame, text="Copy String", command=copy).grid(row=row, column=col, padx=5)

# Editable text box
text_box = tk.Text(top, height=4, width=70)
text_box.pack(pady=10)
text_box.insert(tk.END, example)

root.mainloop()
