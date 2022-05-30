bl_info = {
    "name": "Weed Blender IDE",
    "author": "Cristian Hasbun",
    "version": (2022, 5, 1),
    "blender": (2, 80, 0),
    "location": "Text Editor | Interactive Console | Terminal Console",
    "description": "WEED Enhances Empowered Developers!  *recursive acronym",
    "warning": "",
    "doc_url": "http://www.blender.cl/weed_IDE",
    "tracker_url": "",
    "category": "Development",
}


_modules = [
#   ('module',          'path',        has_prefs )#
    ('find_replace',    'editor_tools',   True  ),
    ('pudb_wrapper',    'debugger_tools', False ),
    ('bge_console',     'console_tools',  False ),
    ('scripts_manager', 'editor_tools',   True  ),
    ('code_editor',     'editor_tools',   True  ),
    ('api_navigator',   'editor_tools',   True  ),
    ('code_tree',       'editor_tools',   True  ),
#   ('icons_get',       'editor_tools',   False )
#   ('ui',              '',               False ),
]

# _modules = [
# #   ('module',          'path',        has_prefs )#
#     ('find_replace',    'editor_tools'),
#     ('pudb_wrapper',    'debugger_tools'),
#     ('bge_console',     'console_tools'),
#     ('scripts_manager', 'editor_tools'),
#     ('code_editor',     'editor_tools'),
#     ('api_navigator',   'editor_tools'),
#     ('code_tree',       'editor_tools'),
# #   ('icons_get',     'editor_tools'),
# #   ('ui',            ''),
# ]

_icon_types = {
    'py'    : 'FILE_SCRIPT',
    'txt'   : 'TEXT',
    'blend' : 'FILE_BLEND',
    'jpg'   : 'FILE_IMAGE',
    'png'   : 'FILE_IMAGE',
    'bmp'   : 'FILE_IMAGE',
    'gif'   : 'FILE_IMAGE',
    'tga'   : 'FILE_IMAGE',
    'jpeg'  : 'FILE_IMAGE',
    'avi'   : 'FILE_MOVIE',
    'mov'   : 'FILE_MOVIE',
    'mp4'   : 'FILE_MOVIE',
    'mp3'   : 'FILE_SOUND',
    'ogg'   : 'FILE_SOUND',
    'sh'    : 'CONSOLE',
    'bin'   : 'FILE_VOLUME',
    'pyc'   : 'SCRIPT',
    'pyd'   : 'SCRIPT',
    'exe'   : 'FILE_VOLUME',
}


from bpy.props import *
from inspect import cleandoc

if "bpy" in locals():
    import importlib
    importlib.reload(ui)
    for module, path, has_prefs in _modules:
        exec(f"importlib.reload({module})")

else:
    import bpy
    from weed import ui
    for module, path, has_prefs in _modules:
        exec(f"from weed.{path} import {module}")


def module_toggle(self, context):
    for module, path, has_prefs in _modules:
        if eval(f"self.{module}_enabled != self.{module}_last_state"):
            #self.report({'DEBUG'}, f'{module} change state')
            execute_code = f"""
                if self.{module}_enabled:
                    try:
                        {module}.register(prefs=True)
                        #self.report({'DEBUG'}, f'{module}.register()')
                    except:
                        #self.report({'DEBUG'}, f'{module}.register() fail !')
                else:
                    try:
                        {module}.unregister(prefs=False)
                        #self.report({'DEBUG'}, f'{module}.unregister()')
                    except:
                        #self.report({'DEBUG'}, f'{module}.unregister() fail !')
                self.{module}_last_state = self.{module}_enabled        
            """
            exec(cleandoc(execute_code))
            break



class WeedPreferences(bpy.types.AddonPreferences):
    bl_idname = 'weed'

    for module, path, has_prefs in _modules:
        pref_generator = f"""
            {module}_enabled: BoolProperty(name='{module}'.replace('_',' ').title(),                    
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
        layout = self.layout
        no_prefs_modules = layout.box().grid_flow(columns=2, even_columns=1)
        layout.separator()
        prefs_modules = layout.column(align=False)
        prefs_modules.alignment = 'RIGHT'
        for module, path, has_prefs in _modules:
            draw_generator = f"""
                if ({has_prefs} and hasattr(self,'{module}') and 
                    hasattr(self.{module}, 'draw')):
                    #pref_module = prefs_modules.split(factor=0.2)
                    #pref_module = prefs_modules.split(factor=0.2)
                    prefs_modules.prop(self, "{module}_enabled")
                    subbox = prefs_modules.box()
                    subbox.enabled = self.{module}_enabled    
                    if self.{module}_enabled:
                        self.{module}.draw(subbox)
                    else:
                        subbox.label()
                    prefs_modules.separator()
                else:
                    no_prefs_modules.prop(self, "{module}_enabled")
                    #layout.separator()
           """
            exec(cleandoc(draw_generator))
    #del cleandoc


def register():
    ui.register()
    for module, path, has_prefs in _modules:
        execute_code = f"""
            try:
                {module}.register() 
                #self.report({'DEBUG'}, f'{module} registered')    
            except:
                pass
                #self.report({'DEBUG'}, f'{module} except registering')    
        """
        
        exec(cleandoc(execute_code))
    bpy.utils.register_class(WeedPreferences)


def unregister():  # note how unregistering is done in reverse
    bpy.utils.unregister_class(WeedPreferences)
    for module, path, has_prefs in reversed(_modules):
        execute_code = f"""
            try:
                {module}.unregister() 
                #self.report({'DEBUG'}, f'{module} unregistered')    
            except:
                pass
                #self.report({'DEBUG'}, f'{module} except unregistering')    
        """
        exec(cleandoc(execute_code))
    ui.unregister()