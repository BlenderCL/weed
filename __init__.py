bl_info = {
    "name": "Weed Blender IDE",
    "author": "Cristian Hasbun",
    "version": (2021, 5, 1),
    "blender": (2, 80, 0),
    "location": "Text Editor | Interactive Console | Terminal Console",
    "description": "WEED Enhances Empowered Developers!  *recursive acronym",
    "warning": "",
    "wiki_url": "http://www.blender.cl/weed_IDE",
    "tracker_url": "",
    "category": "Development",
}

#import bpy
from bpy.props import *
from inspect import cleandoc

_modules = [
#  #('module',        'path',        has_prefs )#
    # ('ui',            '',                False ),
    ('bge_console',   '.console_tools',  False ),
    ('pudb_wrapper',  '.debugger_tools', False ),
    ('api_navigator', '.editor_tools',   True  ),
    ('code_tree',     '.editor_tools',   False ),
    ('find_replace',  '.editor_tools',   True  ),
    ('code_editor',   '.editor_tools',   True  ),
    # ('file_manager',  '.editor_tools',   False ),
    # ('icons_get',     '.editor_tools',   False )
]

if "bpy" in locals():
    import importlib
    importlib.reload(ui)
    for module, path, has_prefs in _modules:
        exec(f"importlib.reload({module})")

else:
    import bpy
    from weed import ui
    for module, path, has_prefs in _modules:
        exec(f"from weed{path} import {module}")


def module_toggle(self, context):
    from inspect import cleandoc
    #prefs = context.preferences.addons['weed'].preferences
    #breakpoint.here
    for module, path, has_prefs in _modules:
        if eval(f"self.{module}_enabled != self.{module}_last_state"):
            execute_code = f"""
                if not {has_prefs}:
                    if self.{module}_enabled:
                        {module}.register()
                    else:
                        {module}.unregister()
                else:
                    if self.{module}_enabled:
                        {module}.register(prefs=False)
                    else:
                        {module}.unregister(prefs=False)
                self.{module}_last_state = self.{module}_enabled        

            """
            exec(cleandoc(execute_code))
            break
    #bpy.utils.unregister_class(WeedPreferences)
    #bpy.utils.register_class(WeedPreferences)




# from bpy.types import AddonPreferences
class WeedPreferences(bpy.types.AddonPreferences):
    # agregar codigo para presentar en el panel de preferencias
    #     agregar codigo para integrar preferencias
    #     en el panel principal de la UI (tal vez no aca)
    bl_idname = 'weed'

    for module, path, has_prefs in _modules:
        pref_generator = f"""
            {module}_enabled: BoolProperty(name='{module}',                    
                        default=True, update=module_toggle)
            {module}_last_state: BoolProperty(name='{module}',                    
                        default=True)
        """
        if has_prefs:
            pref_generator += f"""
            {module}: PointerProperty(type={module}.Preferences)
            """
        exec(cleandoc(pref_generator))

    def draw(self, context):
        #prefs = context.preferences.addons['weed'].preferences
        layout = self.layout
        col = layout.column(align=False)
        for module, path, has_prefs in _modules:
            draw_generator = f"""
                if hasattr(self, "{module}_enabled"):
                    box = col.box()
                    box.prop(self, "{module}_enabled")
                    subbox = box.box()
                    if {has_prefs} and hasattr(self,'{module}') and hasattr(self.{module}, 'draw'):
                        self.{module}.draw(subbox)
                    else:
                        subbox.label(text="module {module} doesn't have an attribute panel")
                else:
                    subbox.label(text="module {module} disabled")
            """
            exec(cleandoc(draw_generator))

    #del cleandoc


def register():
    from inspect import cleandoc
    ui.register()
    for module, path, has_prefs in _modules:
        exec(f"{module}.register()")
    bpy.utils.register_class(WeedPreferences)

    prefs = bpy.context.preferences.addons['weed'].preferences
    for module, path, has_prefs in _modules:
        # if active: # and eval(f"{module} in prefs"):
        execute_code = f"""
            if not {has_prefs} and not prefs.{module}_enabled:
                {module}.unregister()     
        """
        exec(cleandoc(execute_code))


def unregister():  # note how unregistering is done in reverse
    bpy.utils.unregister_class(WeedPreferences)
    for module, path, has_prefs in _modules:
        execute_code = f"""
            try:
                {module}.unregister()     
            except:
                if hasattr({module}, 'prefs_classes'):
                    for pref_cls in {module}.prefs_classes:
                        bpy.utils.unregister_class(pref_cls)
                        print('module {module}, unregister pref:', pref_cls)
        """
        exec(cleandoc(execute_code))
    ui.unregister()