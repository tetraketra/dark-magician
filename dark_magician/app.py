import json
import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk

import ttkwidgets.autocomplete as ttkwa

from logging_utils import *
from settings import *


@dataclass
class tkinterAppSettings:
    root: tk.Tk
    theme: tk.StringVar = None


    def __post_init__(self):
        self.theme = tk.StringVar(self.root)

        try:
            with open(APP_RUNTIME_SETTINGS['settings_file'], "r") as f:
                json_converted: dict = json.load(f)
                self.set_theme(json_converted['theme'])
                
        except FileNotFoundError:
            self.set_theme("forest-dark")
            


    def __repr__(self):
        return str({
            key:val.get() for key, val in self.__dict__.items() \
            if key != "root"
        })


    def write_on_call(func):
        def wrapper(self, value):
            func(self, value)
            self.write_settings()
        return wrapper


    @add_logging(log_level=logging.INFO)
    def write_settings(self):
        with open(APP_RUNTIME_SETTINGS['settings_file'], "w") as f:
            json_converted = {
                key:val.get() for key, val in self.__dict__.items() \
                if key != "root"
            }
            json.dump(json_converted, f)


    @write_on_call
    @add_logging(log_level=logging.DEBUG)
    def set_theme(self, theme: str) -> None:
        self.theme.set(theme)
        if theme in ("forest-dark", "forest-light"):
            ttk.Style().theme_use(theme)
        if theme in ("azure-dark", "azure-light"):
            self.root.tk.call("set_theme", theme.split("-")[1])

        
class tkinterApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Dark Magician")
        self.geometry("400x400")
        
        self.tk.call("source", "../themes/azure.tcl")
        self.tk.call("source", "../themes/forest-dark.tcl")
        self.tk.call("source", "../themes/forest-light.tcl")

        self.settings = tkinterAppSettings(self)

        bg = ttk.Frame(self)
        bg.pack(fill="both", expand=True)

        self.configure_button = ttk.Button(
            bg, text="⚙️", width=len("⚙️"),
            command=lambda: ConfigureWindow(root=self), 
        )
        self.configure_button.pack(anchor="ne")


class ConfigureWindow(tk.Toplevel):
    def __init__(self, root: tkinterApp, *args, **kwargs):
        super().__init__(root, *args, **kwargs)

        self.title("Configure")
        self.geometry(f"300x200+{root.winfo_x() + 10}+{root.winfo_y() + 10}")
        
        bg = ttk.Frame(self)
        bg.pack(fill="both", expand=True)

        themes = ["forest-dark", "forest-light", "azure-dark", "azure-light"]
        theme_selector = ttkwa.AutocompleteCombobox(
            bg, themes, width=len(max(themes, key=len)),
            textvariable=root.settings.theme
        )
        theme_selector.bind(
            "<<ComboboxSelected>>", 
            lambda _: [root.settings.set_theme(theme_selector.get())],
        )

        labeled_options = {
            "Select Theme":theme_selector
        }

        for index, (label, widget) in enumerate(labeled_options.items()):
            label = ttk.Label(bg, text=label)
            label.grid(row=index, column=0, sticky="w", padx=5)
            widget.grid(row=index, column=1, sticky="e", padx=5)

        self.update_idletasks()
        self.geometry(f"{self.winfo_width()}x{self.winfo_reqheight()}")