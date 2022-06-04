import bpy

def footer_spacer(self, context):
    layout = self.layout
    layout.separator_spacer()

def weed_menu(self, context):
    layout = self.layout
    layout.menu('WEED_MT_main_menu', text=' Weed', icon='FILE_SCRIPT')
    layout.separator()


class WEED_MT_main_menu(bpy.types.Menu):
    bl_label = 'Weed Menu'
    bl_idname = 'WEED_MT_main_menu'
    bl_options = {'REGISTER'}

    def draw(self, context):
        layout = self.layout
        layout.label(text='Weed tools')
        layout.separator()


class WEED_PT_main_panel(bpy.types.Panel):
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_label = "IDE Tools"
    bl_category = "Weed IDE"
    bl_options = {'DEFAULT_CLOSED'}
    quick_prefs_layout = None
    modules_layout = None

    def draw(self, context):
        self.layout.label(text='Quick preferences: ')
        self.quick_prefs_layout = self.layout.grid_flow(columns=2, even_columns=1)
        self.layout.separator()
        self.layout.label(text='Tools: ')
        self.modules_layout = self.layout.grid_flow(columns=2, even_columns=1)   # .box()


def register():
    bpy.utils.register_class(WEED_MT_main_menu)
    bpy.utils.register_class(WEED_PT_main_panel)
    bpy.types.TEXT_MT_context_menu.append(weed_menu)
    bpy.types.TEXT_MT_view.append(weed_menu)
    bpy.types.TEXT_HT_footer.append(footer_spacer)

    # if bpy.context.preferences.addons.get('development_icon_get'):
    #     bpy.types.TEXT_MT_context_menu.append(icon_get_menu)
    #     bpy.types.TEXT_MT_view.append(icon_get_menu)
    #     bpy.types.TEXT_HT_footer.append(icon_get_menu)

def unregister():
    # if bpy.context.preferences.addons.get('development_icon_get'):
    #     bpy.types.TEXT_MT_context_menu.remove(icon_get_menu)
    #     bpy.types.TEXT_MT_view.remove(icon_get_menu)
    #     bpy.types.TEXT_HT_footer.remove(icon_get_menu)

    bpy.types.TEXT_HT_footer.remove(footer_spacer)
    bpy.types.TEXT_MT_view.remove(weed_menu)
    bpy.types.TEXT_MT_context_menu.remove(weed_menu)
    bpy.utils.unregister_class(WEED_PT_main_panel)
    bpy.utils.unregister_class(WEED_MT_main_menu)




