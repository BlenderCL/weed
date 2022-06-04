import bpy

addons = bpy.context.preferences.addons

# get preferences caller function
def get_prefs():
    return bpy.context.preferences.addons['weed'].preferences.icons_get_wrapper


def icon_get_menu(self, context):
    if addons.get('development_icon_get'):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        icon_show = layout.operator('iv.icons_show', text='get icon ID', icon='IMAGE_DATA')


def update_prefs(self, context):
    if not addons.get('development_icon_get'):
        bpy.ops.preferences.addon_enable(module="development_icon_get")
    if self.hide_panel:
        addons['development_icon_get'].preferences.show_panel = False
    else:
        addons['development_icon_get'].preferences.show_panel = True
    

class Preferences(bpy.types.PropertyGroup):
    """Code Editor Preferences Panel"""
    bl_idname = __name__

    hide_panel: bpy.props.BoolProperty(
        name="icon viewer hide panel",
        description="enable icons viewer addon without panel on 'Dev' tab",
        default=False, update=update_prefs
    )

    def quick_prefs(self, context):
        prefs = get_prefs()
        layout = self.quick_prefs_layout
        layout.prop(prefs, 'hide_panel')


prefs_classes = (
    Preferences,
)

def register(prefs=True):
    if prefs:
        for cls in prefs_classes:
            try:
                bpy.utils.unregister_class(cls)
            except:
                print(f'{cls} already unregistered')
                #pass
            bpy.utils.register_class(cls)

    bpy.types.TEXT_MT_context_menu.append(icon_get_menu)
    bpy.types.TEXT_MT_view.append(icon_get_menu)
    bpy.types.TEXT_HT_footer.append(icon_get_menu)
    bpy.types.WEED_PT_main_panel.append(Preferences.quick_prefs)



def unregister(prefs=True):
    bpy.types.WEED_PT_main_panel.remove(Preferences.quick_prefs)
    bpy.types.TEXT_MT_context_menu.remove(icon_get_menu)
    bpy.types.TEXT_MT_view.remove(icon_get_menu)
    bpy.types.TEXT_HT_footer.remove(icon_get_menu)
    if prefs:
        for cls in reversed(prefs_classes):
            bpy.utils.unregister_class(cls)

