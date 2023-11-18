import tkinter as tk
import customtkinter as ctk
import more_itertools as mit

from logging_utils import *
from settings import *
from effect import *

MAX_COLS = 5


class TextboxEffectPlaintext(ctk.CTkTextbox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure(state="disabled")

    def set_text(self, text: str) -> None:
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.insert("1.0", text)
        self.configure(state="disabled")


class TabviewEffectsConstructor(ctk.CTkTabview):
    def __init__(self, text_render_binding: Callable, abilities: int = 0, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.text_render_binding = text_render_binding
        self.effect_count: int = abilities
        self.effects: list[Effect] = []
        self.add_effect()
        


    def get_effect(self) -> Effect:
        return self.effects[int(self.get().split("#")[1]) - 1]

    
    def add_effect(self) -> None:
        self.effect_count += 1
        
        self.add(f"Effect #{self.effect_count}")
        self.set(f"Effect #{self.effect_count}")
        
        self.effects.append(Effect_Root(master=self.tab(self.get()), repack_binding=self.repack))

        self.repack()
        
        
    def repack(self) -> None:
        render_tree: list[Effect] = self.get_effect().render_tree(get="effect_class", flatten=True, condense=False)
        for index, effect in enumerate(render_tree):
            effect: Effect
            effect.widget.grid_remove()
        
        render_tree: list[Effect] = self.get_effect().render_tree(get="effect_class", flatten=True, condense=True)
        for index, effect in enumerate(render_tree):
            effect: Effect
            effect.widget.grid(row = index // MAX_COLS, column = index % MAX_COLS)
                
        render_tree: list[str] = self.get_effect().render_tree(get="var_values", flatten=True)
        self.text_render_binding("".join(render_tree).replace("  ", "") or "~ effectless ~")


    def remove_Effect(self) -> None:
        deleted_tab = self.get()
        deleted_tab_num = int(deleted_tab.split("#")[1])

        self.effect_count -= 1
        self.effects.pop(deleted_tab_num - 1)
        self.delete(deleted_tab)
        
        for tab_num in range(deleted_tab_num + 1, self.effect_count + 2):
            self.rename(
                old_name=f"Effect #{tab_num}", 
                new_name=f"Effect #{tab_num - 1}"
            )

        if self.effect_count > 1:
            self.set(f"Effect #{max(deleted_tab_num - 1, 1)}")
            if self.index(self.get()) + 1 != self.effect_count:
                self.set(f"Effect #{deleted_tab_num}")


class tkinterApp(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        self.title("Dark Magician")
        self.geometry("800x800")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # background
        bg = ctk.CTkFrame(self)
        bg.grid(row=0, column=0, sticky="nsew") 
        bg.grid_columnconfigure(0, weight=1)
        bg.grid_rowconfigure(1, weight=1) # button area (0) is min size, the rest stretches to fit

        # buttons
        buttons = {
            " ":ctk.CTkButton(bg, text = " ", state="disabled"),
            "-":ctk.CTkButton(bg, text = "-", width=80),
            "+":ctk.CTkButton(bg, text = "+", width=80),
            "Import":ctk.CTkButton(bg, text="Import"),
            "Export":ctk.CTkButton(bg, text="Export")
        }
        for i, (label, button) in enumerate(buttons.items()):
            button.grid(row=0, column=i, sticky="nsew")
        
        # main content
        main_content = ctk.CTkFrame(bg)
        main_content.grid(row=1, column=0, columnspan=len(buttons), sticky="nswe")
        main_content.grid_columnconfigure(0, weight=1)
        main_content.grid_rowconfigure(0, weight=5)

        effect_plaintext = TextboxEffectPlaintext(master=main_content, wrap=tk.WORD)
        effect_plaintext.grid(row=1, column=0, columnspan=len(buttons), sticky="nsew")
        effect_plaintext.set_text("~ nothing here yet ~")

        abilities_constructor = TabviewEffectsConstructor(master=main_content, text_render_binding=effect_plaintext.set_text)
        abilities_constructor.grid(row=0, column=0, columnspan=len(buttons), sticky="nsew")
        buttons["-"].configure(command=abilities_constructor.remove_Effect)
        buttons["+"].configure(command=abilities_constructor.add_effect)
        

        
            