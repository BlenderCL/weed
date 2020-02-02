import bpy

def draw_code_tree_box(self, context, layout):
    code_editors = context.window_manager.code_editors
    col = layout.column(align=False)
    row = col.row(align=False)
    row.prop(get_addon_preferences(), 'user_site_packages',
             icon = 'RECOVER_LAST', text = '')
    selector = row.row(align=True)
    selector.prop(context.scene, 'explorer_root_folder', text='')
    selector.operator('weed.open_addon_menu',
                 icon = 'COLLAPSEMENU', text = '')
    row.enabled = False
    col.prop(get_addon_preferences(), 'show_code_tree',
             icon = 'OOPS', text = 'view code tree')
    if str(context.area) not in code_editors.keys():
        layout.label(text='to activate Code tree,', icon='INFO')
        #layout.label(text='Start code editor here')
        layout.operator('weed.code_editor_start', icon = 'SYNTAX_ON',
                        text = 'Start Code Editor here', emboss = True)
        return {'FINISHED'}

    icons = { 'imports' : 'OUTLINER_OB_GROUP_INSTANCE',
              'imports_off' : 'GROUP',
              'import' : 'OUTLINER_OB_GROUP_INSTANCE',
              'toggle_open' : 'DISCLOSURE_TRI_RIGHT',
              'toggle_close' : 'DISCLOSURE_TRI_DOWN',
              'class' : 'OBJECT_DATA', 'class_off' : 'MATCUBE',
              'def' : 'LAYER_ACTIVE', 'def_off' : 'FONT_DATA'}
    #layout.operator_context = 'EXEC_DEFAULT'
    col = layout.column(align=True)


def code_tree_popup(self, context):
    icons = { 'imports' : 'OUTLINER_OB_GROUP_INSTANCE',
              'imports_off' : 'GROUP',
              'import' : 'OUTLINER_OB_GROUP_INSTANCE',
              'toggle_open' : 'DISCLOSURE_TRI_RIGHT',
              'toggle_close' : 'DISCLOSURE_TRI_DOWN',
              'class' : 'OBJECT_DATA', 'class_off' : 'MATCUBE',
              'def' : 'LAYER_ACTIVE', 'def_off' : 'FONT_DATA'}
    layout = self.layout
    layout.operator_context = 'EXEC_DEFAULT'
    layout.alignment = 'LEFT'
    layout.label(icon = 'FILE_TEXT', text = context.space_data.text.name)
    
    for i, node in enumerate(bpy.types.Text.code_tree[1:]):
        type = '' if node.type == 'import' else node.type + ' '
        prop = layout.operator('text.jump',
                            text = '     '*node.indnt + type + node.name,
                            icon = icons[node.type],
                            emboss = True)
        prop.line = node.line_n + 1

    

    

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

