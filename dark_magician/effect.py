from typing import Literal, Callable

import customtkinter as ctk
import more_itertools as mit


class EffectBaseClass_Final:
    pass


class EffectBaseClass_Extender:
    pass


class EffectBaseClass_Root:
    pass


class Effect:
    def __init__(
        self, 
        master: ctk.CTk, options: list[str],
        repack_binding: Callable,  
        left: list['Effect'] = None, right: list['Effect'] = None,
        vartype: ctk.Variable = ctk.StringVar
    ) -> 'Effect':

        self.master = master
        self.repack_binding = repack_binding

        self.ctkvar: ctk.Variable = vartype(master, "")
        self.widget: ctk.CTkBaseClass = ctk.CTkOptionMenu(master, variable=self.ctkvar, values=options)
        
        self.left: list['Effect']  = left if isinstance(left, list) else ([left] if left else None)
        self.right: list['Effect'] = right if isinstance(right, list) else ([right] if right else None)


    def _render_tree(
        self, 
        get
    ) -> str | list['Effect']:

        tree = [self.ctkvar.get()] if get=="var_values" else [self]
                
        if self.left:
            for left in reversed(self.left):
                tree.insert(0, left._render_tree(get=get))
        if self.right:
            for right in self.right:
                tree.append(right._render_tree(get=get))
            
        return tree


    def render_tree(
        self, 
        get: Literal["var_values", "effect_class"] = "var_values",
        condense: bool = False,
        flatten: bool = False
    ) -> str | list['Effect']:
        
        tree = self._render_tree(get=get)
        if flatten:
            tree = [e for e in list(mit.collapse(tree, base_type=Effect)) if e]

            if get == "effect_class" and condense:

                right_pass = []
                ignoring = False
                for i, e in enumerate(reversed(tree)):
                    e: Effect
                    if isinstance(e, EffectBaseClass_Final) and e.ctkvar.get():
                        ignoring = True
                    if isinstance(e, EffectBaseClass_Root):
                        ignoring = False
                    if ignoring:
                        if isinstance(e, (EffectBaseClass_Extender, EffectBaseClass_Final)) and not e.ctkvar.get():
                            print(f"skipping: {e=}, {e.ctkvar.get()=}")
                            continue
                        
                    right_pass.append(e)

                left_pass = []
                ignoring = False
                for e in reversed(right_pass):
                    e: Effect
                    if isinstance(e, EffectBaseClass_Final) and e.ctkvar.get():
                        ignoring = True
                    if isinstance(e, EffectBaseClass_Root) and e.ctkvar.get():
                        ignoring = False
                    if ignoring:
                        if isinstance(e, (EffectBaseClass_Extender, EffectBaseClass_Final)) and not e.ctkvar.get():
                            print(f"skipping: {e=}, {e.ctkvar.get()=}")
                            continue

                    left_pass.append(e)

                tree = list(left_pass)        
                    
        return tree


    def set_left(self, left: list['Effect'] = None) -> None:
        if self.left:
            for sleft in self.left:
                sleft.destroy()

        self.left = None  
        self.left = left if isinstance(left, list) else ([left] if left else None)
        
        self.repack_binding()


    def set_right(self, right: list['Effect'] = None) -> None:
        if self.right:
            for sright in self.right:
                sright.destroy()

        self.right = None  
        self.right = right if isinstance(right, list) else ([right] if right else None)

        self.repack_binding()


    def destroy(self)  -> None:
        if self.left:
            for left in self.left:
                left.destroy()
            self.left = None

        if self.right:
            for right in self.right:
                right.destroy()
            self.right = None
            
        if self.widget:
            self.widget.destroy()


class Effect_Root(Effect, EffectBaseClass_Root):
    def __init__(self, master: ctk.CTk, repack_binding: Callable) -> 'Effect_Root':
        super().__init__(
            master = master,
            repack_binding = repack_binding,
            options = [
                "when ", 
                "if ", 
                "at any time ",
            ]
        )
        
        self.widget.configure(
            command = lambda _: [
                self.set_left(Effect_RootConditionalRoot(master=master, repack_binding=self.repack_binding)), 
                self.set_right()
            ]
        )


class Effect_RootConditionalRoot(Effect):
    def __init__(self, master: ctk.CTk, repack_binding: Callable) -> None:
        super().__init__(
            master = master,
            repack_binding = repack_binding,
            options = [
                "during ", 
                "after ",
                "before ",
            ]
        )

        self.widget.configure(
            command = lambda _: [
                self.set_left(), 
                self.set_right([
                    Effect_RootConditionalPlayerOwnership(master=master, repack_binding=self.repack_binding),
                    EffectAndOr(master=master, repack_binding=self.repack_binding, extend_with=Effect_RootConditionalRoot)
                ])
            ]
        )


class Effect_RootConditionalPlayerOwnership(Effect):
    def __init__(self, master: ctk.CTk, repack_binding: Callable) -> None:
        super().__init__(
            master = master,
            repack_binding = repack_binding,
            options = [
                "your ", 
                "your opponent's ",
                "either player's ",
            ]
        )

        self.widget.configure(
            command = lambda _: [
                self.set_left(), 
                self.set_right([
                    Effect_RootConditionalPhase(master=master, repack_binding=self.repack_binding),
                    EffectAndOr(master=master, repack_binding=self.repack_binding, extend_with=Effect_RootConditionalPlayerOwnership)
                ])
            ]
        )


class Effect_RootConditionalPhase(Effect):
    def __init__(self, master: ctk.CTk, repack_binding: Callable) -> None:
        super().__init__(
            master = master,
            repack_binding=repack_binding,
            options = [
                "turn(s) ",
                "Draw Phase(s) ",
                "Main Phase(s) ",
                "Battle Phase(s) ",
                "End Phase(s) ",
            ]
        )

        self.widget.configure(
            command = lambda _: [
                self.set_left(), 
                self.set_right([
                    EffectAndOr(master=master, repack_binding=self.repack_binding, extend_with=Effect_RootConditionalPhase),
                    Effect_RootConditionalFinal(master=master, repack_binding=self.repack_binding),
                ])
            ]
        )


class Effect_RootConditionalFinal(Effect, EffectBaseClass_Final):
    def __init__(self, master: ctk.CTk, repack_binding: Callable) -> None:
        super().__init__(
            master = master,
            repack_binding = repack_binding,
            options = [
                "",
                " : ",
            ]
        )

        self.widget.configure(
            command = lambda _: [
                self.set_left(), 
                self.set_right()
            ]
        )


class EffectAndOr(Effect, EffectBaseClass_Extender):
        def __init__(self, master: ctk.CTk, repack_binding: Callable, extend_with: Effect) -> None:
            super().__init__(
                master = master,
                repack_binding = repack_binding,
                options = [
                    "",
                    "or ",
                    "and ",
                ]
            )

            self.widget.configure(
                command = lambda _: [
                    self.set_left(), 
                    self.set_right(extend_with(master=master, repack_binding=self.repack_binding)) if self.ctkvar.get() else self.set_right(),
                ]
            )

