# bl_info = {
#     "name": "Find Replace Horizontal",
#     "description": "Show Find and Replace boxes on horizontal bar",
#     "author": "find_replace_author",
#     "version": (1, 0, 0),
#     "blender": (2, 80, 0),
#     "location": "Text Editor > horizontal bar",
#     "doc_url": "no_site.html",
#     "category": "Development",
# }

import bpy
from bpy.props import BoolProperty

# get preferences caller function
def get_prefs():
    return bpy.context.preferences.addons['weed'].preferences.find_replace


def draw_find_replace(self, context):
    layout = self.layout
    fnd_rplc = get_prefs() 
    wm = context.window_manager
    layout.use_property_decorate = False
    st = context.space_data
    text = st.text
    if not text:
        fnd_rplc.find_replace_toggle = False
    
    else:
        row = layout.row(align=True)
        row.prop(fnd_rplc, "find_replace_toggle", text="", icon='VIEWZOOM', toggle=True)
        if fnd_rplc.find_replace_toggle:
            # find
            # row = layout.row(align=True)
            row.prop(st, "find_text", text="")
            row.activate_init = True
            row.operator("text.find_set_selected", text="", icon='EYEDROPPER') 
            row.operator("text.find", text="", icon='VIEWZOOM')        
            
            # replace                        
            row = layout.row(align=True)
            row.prop(st, "replace_text", text="")
            row.operator("text.replace_set_selected", text="", icon='EYEDROPPER')
            row.operator("text.replace", text="", icon='DECORATE_OVERRIDE')        
            # row.operator("text.replace", text="All", icon='DECORATE_OVERRIDE')#.all = True
            # breakpoint.here
            
        
            # settings                   
            row = layout.row(align=True)      
            row.prop(st, "use_match_case", text="Case", toggle=True)    # case
            row.prop(st, "use_find_wrap", text="Wrap", toggle=True)  # warp
            row.prop(st, "use_find_all", text="All", toggle=True)  # all
            row.scale_x = 0.6
        

class WEED_OT_find_replace_popup(bpy.types.Operator):
    bl_idname = 'weed.find_replace_popup'
    bl_label = 'Find and Replace'
    bl_description = 'Find and Replace popup'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    def draw(self, context):
        layout = self.layout
        st = context.space_data

        # find
        col = layout.column()
        row = col.row(align=True)
        row.activate_init = True
        row.prop(st, "find_text", icon='VIEWZOOM', text="")
        row.operator("text.find_set_selected", text="", icon='EYEDROPPER')
        col.active_default = True
        col.operator("text.find")

        layout.separator()

        # replace
        col = layout.column()
        row = col.row(align=True)
        row.prop(st, "replace_text", icon='DECORATE_OVERRIDE', text="")
        row.operator("text.replace_set_selected", text="", icon='EYEDROPPER')

        row = col.row(align=True)
        row.operator("text.replace")
        # row.operator("text.replace", text="Replace All")#.all = True
        # breakpoint.here
        

        layout.separator()

        # settings
        row = layout.row(align=True)
        if not st.text:
            row.active = False
        row.prop(st, "use_match_case", text="Case", toggle=True)
        row.prop(st, "use_find_wrap", text="Wrap", toggle=True)
        row.prop(st, "use_find_all", text="All", toggle=True)

        layout.separator()

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        bpy.ops.text.find_set_selected()
        return context.window_manager.invoke_props_dialog(self, width=400)


class Preferences(bpy.types.PropertyGroup):
    find_replace_toggle : BoolProperty(
        name = 'show find footer',
        default = False,
        description = 'Show Find and Replace footer panel')


prefs_classes = (
    Preferences,
)

classes = (
    WEED_OT_find_replace_popup,
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

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TEXT_HT_footer.prepend(draw_find_replace)

    kc = bpy.context.window_manager.keyconfigs
    if kc.addon:
        km = kc.addon.keymaps.new(name='Text', space_type='TEXT_EDITOR')
        km.keymap_items.new('weed.find_replace_popup',
                            'F', 'PRESS', ctrl=True, shift=True)

def unregister(prefs=True):
    kc = bpy.context.window_manager.keyconfigs
    if kc.addon:
        km = kc.addon.keymaps['Text']
        kmi = km.keymap_items['weed.find_replace_popup']
        km.keymap_items.remove(kmi)

    bpy.types.TEXT_HT_footer.remove(draw_find_replace)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    if prefs:
        for cls in reversed(prefs_classes):
            bpy.utils.unregister_class(cls)
    
