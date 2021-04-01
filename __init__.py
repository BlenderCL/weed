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

if "bpy" in locals():
    import importlib
    importlib.reload(prefs)
    importlib.reload(bge_console_manager)
    importlib.reload(pudb_wrapper)
    importlib.reload(api_navigator)
    # importlib.reload(code_editor)
    # importlib.reload(code_tree)
    # importlib.reload(find_replace)
    # importlib.reload(icons_get)

else:
    from weed import prefs, ui
    
    from weed.console_tools import bge_console_manager
    
    from weed.debugger_tools import pudb_wrapper
         
    from weed.editor_tools import (
        api_navigator,
        # code_editor,
        code_tree,
        # find_replace,
        # icons_get
        )

modules = (
    prefs,
    ui,
    bge_console_manager,
    pudb_wrapper,
    api_navigator,
    code_tree
    # icons_get
)

def register():
    for mod in modules:
        mod.register()

def unregister():  # note how unregistering is done in reverse
    for mod in reversed(modules):
        mod.unregister()


# def _call_globals(attr_name):
#     for m in globals().values():
#         if hasattr(m, attr_name):
#             getattr(m, attr_name)()


# def register():
#     _call_globals("register")


# def unregister():
#     _call_globals("unregister")

# import bpy

# classes = (
#     prefs,
#     bge_console_manager,
#     pudb_wrapper,
#     # api_navigator,
#     icons_get
# )
# register, unregister = bpy.utils.register_classes_factory(classes)
