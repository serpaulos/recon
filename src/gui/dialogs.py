import tkinter as tk
from tkinter import ttk


def ask_string(root: tk.Tk, title: str, prompt: str, initialvalue: str | None = None) -> str | None:
    result = {"value": None}

    win = tk.Toplevel(root)
    win.title(title)
    win.resizable(False, False)
    win.transient(root)
    win.grab_set()
    win.attributes("-topmost", True)

    frm = ttk.Frame(win, padding=12)
    frm.pack(fill="both", expand=True)

    ttk.Label(frm, text=prompt).pack(anchor="w", pady=(0, 6))

    entry = ttk.Entry(frm, width=45)
    entry.pack(fill="x")
    if initialvalue is not None:
        entry.insert(0, initialvalue)
        entry.select_range(0, tk.END)

    btns = ttk.Frame(frm)
    btns.pack(fill="x", pady=(10, 0))

    def on_ok(event=None):
        result["value"] = entry.get()
        win.destroy()

    def on_cancel(event=None):
        result["value"] = None
        win.destroy()

    ttk.Button(btns, text="OK", command=on_ok).pack(side="right", padx=(6, 0))
    ttk.Button(btns, text="Cancel", command=on_cancel).pack(side="right")

    win.bind("<Return>", on_ok)
    win.bind("<Escape>", on_cancel)

    win.update_idletasks()
    x = root.winfo_rootx() + 60
    y = root.winfo_rooty() + 60
    win.geometry(f"+{x}+{y}")

    win.lift()
    entry.focus_set()
    entry.focus_force()

    root.wait_window(win)
    return result["value"]
