import bpy

class PopupFindReplace(bpy.types.Operator):
    bl_idname = 'weed.popup_find_replace'
    bl_label = 'Popup Find and Replace'
    bl_description = 'popup with Find and Replace'
    bl_options = {'REGISTER', 'UNDO'}

    # Needed hack for repeat operator
    find_hack = bpy.props.BoolProperty(default=False)
    replace_hack = bpy.props.BoolProperty(default=False)

    # set_selected_hack = bpy.props.BoolProperty(default = False)

    def draw(self, context):
        layout = self.layout
        st = context.space_data
        # find
        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(st, "find_text", text="")
        # row.operator("text.find_set_selected", text="", icon='TEXT')
        # row.prop(self, "set_selected_hack", text="", icon='TEXT', toggle=True)
        # col.operator("text.find")
        col.prop(self, "find_hack", text="Find Next", toggle=True)

        # replace
        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(st, "replace_text", text="")
        # row.operator("text.replace_set_selected", text="", icon='TEXT')
        # col.operator("text.replace")
        col.prop(self, "replace_hack", text="Replace", toggle=True)

        # settings
        row = layout.row(align=True)
        row.prop(st, "use_match_case")
        row.prop(st, "use_find_wrap", text="Wrap")
        row.prop(st, "use_find_all", text="All")

    def execute(self, context):
        # if self.set_selected_hack:
        #    bpy.ops.text.find_set_selected()
        #    self.set_selected_hack = False
        try:
            if self.find_hack:
                bpy.ops.text.find()
            if self.replace_hack:
                bpy.ops.text.replace()
        except:
            self.report({'WARNING'}, 'Not Found')
        self.find_hack = False
        self.replace_hack = False
        return {'FINISHED'}

    def invoke(self, context, event):
        # return context.window_manager.invoke_props_dialog(self, width=400)
        # return context.window_manager.invoke_popup(self, width=200)
        try:
            #bpy.ops.text.find_set_selected()
            bpy.ops.text.selection_set(select=True)
        except:
            pass
        return context.window_manager.invoke_props_popup(self, event)


def register_keymaps():
    kc = bpy.context.window_manager.keyconfigs
    if kc.addon:
        km = kc.addon.keymaps.new(name='Text', space_type='TEXT_EDITOR')
        km.keymap_items.new('weed.popup_find_replace', 'F', 'PRESS', ctrl=True)
        # km.keymap_items.new('weed.popup_find_replace', 'H', 'PRESS', ctrl=True)
        dkm = kc.default.keymaps['Text Generic']
        dkm.keymap_items['text.start_find'].active = False
        dkm.keymap_items['text.replace'].active = False


def unregister_keymaps():
    kc = bpy.context.window_manager.keyconfigs
    if kc.addon:
        km = kc.addon.keymaps['Text']
        kmi = km.keymap_items['weed.popup_find_replace']
        km.keymap_items.remove(kmi)
        # kmi = km.keymap_items['weed.popup_replace']
        # km.keymap_items.remove(kmi)
        dkm = kc.default.keymaps['Text Generic']
        dkm.keymap_items['text.start_find'].active = True
        dkm.keymap_items['text.replace'].active = True


def register():
    bpy.utils.register_class(PopupFindReplace)
    register_keymaps()


def unregister():
    bpy.utils.unregister_class(PopupFindReplace)
    unregister_keymaps()


if __name__ == '__main__':
    # unregister()
    register()
