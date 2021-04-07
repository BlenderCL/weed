import bpy

def footer_spacer(self, context):
    layout = self.layout
    layout.separator_spacer()

def weed_menu(self, context):
    layout = self.layout
    layout.menu('WEED_MT_main_menu', text=' Weed', icon='FILE_SCRIPT')
    layout.separator()

def icon_get_menu(self, context):
    # iv.icons_show
    layout = self.layout
    layout.operator_context = 'INVOKE_DEFAULT'
    icon_show = layout.operator('iv.icons_show', text='get icon ID', icon='IMAGE_DATA')
    # icon_show.instance = icon_show

class WEED_MT_main_menu(bpy.types.Menu):
    bl_label = 'Weed Menu'
    # bl_idname = 'OBJECT_MT_custom_menu'
    bl_idname = 'WEED_MT_main_menu'
    # bl_idname = 'weed.main_menu'
    bl_options = {'REGISTER'}

    def draw(self, context):
        layout = self.layout


class WEED_PT_main_panel(bpy.types.Panel):
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_label = "Weed IDE"
    bl_category = "Weed"
    bl_options = {'DEFAULT_CLOSED'}

def register():
    bpy.utils.register_class(WEED_MT_main_menu)
    bpy.types.TEXT_MT_context_menu.append(weed_menu)
    bpy.types.TEXT_MT_view.append(weed_menu)
    bpy.types.TEXT_HT_footer.append(footer_spacer)

    if bpy.context.preferences.addons.get('development_icon_get'):
        bpy.types.TEXT_MT_context_menu.append(icon_get_menu)
        bpy.types.TEXT_MT_view.append(icon_get_menu)

def unregister():
    if bpy.context.preferences.addons.get('development_icon_get'):
        bpy.types.TEXT_MT_context_menu.remove(icon_get_menu)
        bpy.types.TEXT_MT_view.remove(icon_get_menu)

    bpy.types.TEXT_HT_footer.remove(footer_spacer)
    bpy.types.TEXT_MT_view.remove(weed_menu)
    bpy.types.TEXT_MT_context_menu.remove(weed_menu)
    bpy.utils.unregister_class(WEED_MT_main_menu)




