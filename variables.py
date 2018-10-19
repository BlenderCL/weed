""" addon_development """
# creada en  : __init.py__ linea 157
# ubicada en : bpy.types.Scene.addon_development
# usada como : bpy.context.scene.addon_development
# usada en   : addon_development_manager.py
# contiene   : lista de addons [('ruta','nombre','tooltip'), (...]


""" code_editors """
# creada en  : __init.py__ linea 154
# ubicada en : bpy.types.WindowManager.code_editors
# usada como : context.window_manager.code_editors
# usada en   : quick_operators.py, code_editor.py, ui.py
# contiene   : lista de addons [('ruta','nombre','tooltip'), (...]

# tal vez probar algo como

    # import bpy
    # from bpy.props import PointerProperty, StringProperty
    #
    # class codeEditorsList(bpy.types.PropertyGroup):
    #     code_editor = StringProperty(default="")
    #
    #     bpy.types.WindowManager.code_editors = PointerProperty(
    #                                 type=codeEditorsList)


""" code_tree """
# creada en  : __init.py__ linea 157
# ubicada en : bpy.types.Scene.addon_development
# usada como : bpy.context.scene.addon_development
# usada en   : addon_development_manager.py
# contiene   : lista de addons [('ruta','nombre','tooltip'), (...]


