import bpy
from bpy.props import *

class WeedToolsPanel(bpy.types.Panel):
    """Docstring of WeedToolsPanel"""
    bl_idname = "TEXTEDITOR_PT_weed_tools_panel"
    bl_label = "Weed Tools"
    #bl_options =  {'DEFAULT_CLOSED'}

    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'
    
    
    #Panels in ImageEditor are using .poll() instead of bl_context.
    #@classmethod
    #def poll(cls, context):
    #    return context.space_data.show_paint
    
    def draw(self, context):
        settings = context.window_manager
        layout = self.layout
        col = layout.column()
        row = col.row()
        row.alignment = 'RIGHT'
        row.prop(settings, 'subPanel', expand=True, icon_only=True)
        #layout.operator(WeedToolsOperator.bl_idname, text = "Weed Tools", icon = 'BLENDER')
        box = col.box()
        if settings.subPanel == 'code_tree':
            self.draw_codeTree(box)
        elif settings.subPanel == 'debugger':
            self.draw_debugger(box)
        elif settings.subPanel == 'develop':
            self.draw_develop(box)


    def draw_codeTree(self, layout):
        layout.label('Code tree')  

    def draw_debugger(self, layout):
        layout.label('Debugger tools')  

    def draw_develop(self, layout):
        layout.label('Addon development')   


        
def register():
    #bpy.utils.register_class(WeedToolsOperator)
    bpy.utils.register_class(WeedToolsPanel)
    bpy.types.WindowManager.subPanel = EnumProperty(
            name = 'panel',
            default = 'code_tree',
            items = [('debugger',  'Debugger tools',    '', 'RECOVER_AUTO', 0),
                     ('code_tree', 'Code tree',         '', 'OOPS',         1),
                     ('develop',   'Addon development', '', 'SCRIPT',       2)])

    #bpy.utils.register_class(WeedToolsMenu)
    #bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    del bpy.types.WindowManager.subPanels
    #bpy.utils.unregister_class(WeedToolsOperator)
    bpy.utils.unregister_class(WeedToolsPanel)
    #bpy.utils.unregister_class(WeedToolsMenu)
    #bpy.types.VIEW3D_MT_object.remove(menu_func)
    
if __name__ == "__main__":
    register()
