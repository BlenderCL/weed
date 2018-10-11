import bpy

def code_tree_popup(self, context):
    icons = { 'import' : 'LAYER_ACTIVE',
               'class' : 'OBJECT_DATA',
                 'def' : 'SCRIPTPLUGINS' }
    layout = self.layout
    layout.operator_context = 'EXEC_DEFAULT'
    col = layout.column(align=True)
    tot_imports = len(bpy.types.Text.code_tree['imports'])
    for i, (idx, indnt, (keyword, name, args)) in enumerate(
                                    bpy.types.Text.code_tree['imports']):
        #row = row if i%2 else layout.row(align=True)
        prop = col.operator('text.jump',
                            text = name,
                            icon = icons[keyword],
                            emboss = True)
        prop.line = idx + 1

    for idx, indnt, (keyword, name, args) in bpy.types.Text.code_tree['class_def']:
        #if not indnt:
        #    col.separator()
        prop = col.operator('text.jump',
                            text = '·   '*indnt + name,
                            icon = icons[keyword] if not indnt else 'NONE',
                            emboss = True)
        prop.line = idx + 1
        prev_indnt = indnt
    

class WEED_OT_ViewCodeTree(bpy.types.Operator):
    bl_idname = 'weed.view_code_tree'
    bl_label = 'View Code Tree'
    bl_description = 'Show code tree in a popup'
    bl_options = {'REGISTER', 'INTERNAL'}
    
    def execute(self, context):
        context.window_manager.popup_menu(code_tree_popup,
                                          title='View Code Tree',
                                          icon='OOPS')
        return {'FINISHED'} 


# REGISTER
#############

# def register():
#     bpy.utils.register_class(WEED_OT_ViewCodeTree)

# def unregister():
#     bpy.utils.unregister_class(WEED_OT_ViewCodeTree)
