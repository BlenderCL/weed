bl_info = {
    "name": "Weed Blender IDE",
    "author": "Cristian Hasbun",
    "version": (2020, 10, 1),
    "blender": (2, 80, 0),
    "location": "Text Editor | Interactive Console | Terminal Console",
    "description": "WEED Enhances Empowered Developers!  *recursive acronym",
    "warning": "",
    #"warning": "like in the butchery, not expect to be free of bugs...",
    "wiki_url": "http://www.blender.cl/weed_IDE",
    "tracker_url": "",
    "category": "Development",
}

#import bpy
from bpy.props import *

_modules = [
#  active,  has_prefs, 'module',        'path'
    (True,  False,     'ui',            ''),
    (True,  False,     'bge_console',   '.console_tools'),
    (True,  False,     'pudb_wrapper',  '.debugger_tools'),
    (True,  True,      'api_navigator', '.editor_tools'),
    (True,  False,     'code_tree',     '.editor_tools'),
    (True,  True,      'find_replace',  '.editor_tools'),
    (False, False,     'code_editor',   '.editor_tools'),
    (False, False,     'icons_get',     '.editor_tools')
]

if "bpy" in locals():
    import importlib
    for active, has_prefs, module, path in _modules:
        if active:
            exec(f"importlib.reload({module})")

else:
    import bpy
    for active, has_prefs, module, path in _modules:
        if active:
            exec(f"from weed{path} import {module}")


# from bpy.types import AddonPreferences
class WeedPreferences(bpy.types.AddonPreferences):
    bl_idname = 'weed'

    for active, has_prefs, module, path in _modules:
        if active and has_prefs:
            exec(f"{module}: PointerProperty(type={module}.Preferences)")


def register():
    for active, has_prefs, module, path in _modules:
        if active:
            exec(f"{module}.register()")
    bpy.utils.register_class(WeedPreferences)

def unregister():  # note how unregistering is done in reverse
    bpy.utils.unregister_class(WeedPreferences)
    for active, has_prefs, module, path in reversed(_modules):
        if active:
            exec(f"{module}.unregister()")
