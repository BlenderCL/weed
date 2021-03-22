# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8-80 compliant>
import bpy
from bpy.types import Header, Menu, Panel
from bpy.app.translations import pgettext_iface as iface_


class TEXT_HT_header(Header):
    bl_space_type = 'TEXT_EDITOR'

    def draw(self, context):
        layout = self.layout

        st = context.space_data
        text = st.text

        layout.template_header()

        TEXT_MT_editor_menus.draw_collapsible(context, layout)

        if text and text.is_modified:
            row = layout.row(align=True)
            row.alert = True
            row.operator("text.resolve_conflict", text="", icon='HELP')

        layout.separator_spacer()

        row = layout.row(align=True)
        row.template_ID(st, "text", new="text.new", unlink="text.unlink", open="text.open")

        layout.separator_spacer()

        if text:
            is_osl = text.name.endswith((".osl", ".osl"))

            row = layout.row()
            if is_osl:
                row = layout.row()
                row.operator("node.shader_script_update")
            else:
                row = layout.row()
                row.active = text.name.endswith(".py")
                row.prop(text, "use_module")

                row = layout.row()
                row.operator("text.run_script")
    
        
bpy.types.WindowManager.toggle_find_search = bpy.props.BoolProperty()


class TEXT_OT_toggle_find(bpy.types.Operator):
    """Toogle Find & Search"""
    bl_idname = "text.toggle_find_search"
    bl_label = "Find & Search"

    def execute(self, context):
        wm = context.window_manager
        if wm.toggle_find_search == False:
            wm.toggle_find_search = True
        else:
            wm.toggle_find_search = False   
            st = context.space_data
            s = self.get_selected_text(st.text)
            if s is not None:
                bpy.context.space_data.find_text = s
                 
        bpy.context.space_data.text = bpy.context.space_data.text #  Refresh footer

        return {'FINISHED'}


    def get_selected_text(self, text):
        """"""
        current_line = text.current_line
        select_end_line = text.select_end_line

        current_character = text.current_character
        select_end_character = text.select_end_character

        # if there is no selected text return None
        if current_line == select_end_line:
            if current_character == select_end_character:
                return None
            else:
                return current_line.body[min(current_character, select_end_character):max(current_character, select_end_character)]

        text_return = None
        writing = False
        normal_order = True  # selection from top to bottom

        for line in text.lines:
            if not writing:
                if line == current_line:
                    text_return = current_line.body[current_character:] + "\n"
                    writing = True
                    continue
                elif line == select_end_line:
                    text_return = select_end_line.body[select_end_character:] + "\n"
                    writing = True
                    normal_order = False
                    continue
            else:
                if normal_order:
                    if line == select_end_line:
                        text_return += select_end_line.body[:select_end_character]
                        break
                    else:
                        text_return += line.body + "\n"
                        continue
                else:
                    if line == current_line:
                        text_return += current_line.body[:current_character]
                        break
                    else:
                        text_return += line.body + "\n"
                        continue

        return text_return


class TEXT_HT_footer(Header):
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'FOOTER'

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        layout.use_property_decorate = False
        st = context.space_data
        text = st.text
        if text:
            if wm.toggle_find_search:
                row = layout.row()
                if text.filepath:
                    if text.is_dirty:
                        row.label(
                            text=iface_(f"File: *{text.filepath:s} (unsaved)"),
                            translate=False,
                        )
                    else:
                        row.label(
                            text=iface_("File: {text.filepath:s}"),
                            translate=False,
                        )
                else:
                    row.label(
                        text="Text: External"
                        if text.library
                        else "Text: Internal",
                    )
            else:                    
                layout = self.layout              
                st = context.space_data

                # find
                col = layout.column()
                #col = col.scale_x = 1.6
                row = col.row(align=True)

                row.operator("text.find_set_selected", text="", icon='EYEDROPPER') 
                subrow = row.split()
                subrow.scale_x = 1.6     
                subrow.prop(st, "find_text", text="")
                subrow.activate_init = True
                row.operator("text.find", text="Find Next")        

                layout.separator_spacer()

                # replace                        
                col = layout.column()
                row = col.row(align=True)
                row.operator("text.replace_set_selected", text="", icon='EYEDROPPER')
                subrow = row.split()
                subrow.scale_x = 1.6         
                subrow.prop(st, "replace_text", text="")
                row.operator("text.replace", text="Replace")        

                layout.separator_spacer()

                # settings                   
                row = layout.row(align=False)      
                if not st.text:
                    row.active = False
                row.prop(st, "use_match_case", text="", toggle=True, icon="SMALL_CAPS")    # case
                row.prop(st, "use_find_wrap", text="", toggle=True, icon="LOOP_BACK")  # warp
                row.prop(st, "use_find_all", text="", toggle=True, icon="DUPLICATE")  # all

                layout.separator_spacer()

                col = layout.column()
                row = col.row(align=False)       
                row.prop(wm, 'toggle_find_search', text="", icon="X", toggle=True)


class TEXT_MT_editor_menus(Menu):
    bl_idname = "TEXT_MT_editor_menus"
    bl_label = ""

    def draw(self, context):
        layout = self.layout
        st = context.space_data
        text = st.text

        layout.menu("TEXT_MT_view")
        layout.menu("TEXT_MT_text")

        if text:
            layout.menu("TEXT_MT_edit")
            layout.menu("TEXT_MT_format")

        layout.menu("TEXT_MT_templates")


class TEXT_PT_properties(Panel):
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Text"
    bl_label = "Properties"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        st = context.space_data

        flow = layout.column_flow()
        if not st.text:
            flow.active = False
        row = flow.row(align=True)
        st = context.space_data
        row.prop(st, "show_margin", text = "Margin")
        rowsub = row.row()
        rowsub.active = st.show_margin
        rowsub.prop(st, "margin_column", text = "")

        flow.prop(st, "font_size")
        flow.prop(st, "tab_width")


#class TEXT_PT_find(Panel):
#    bl_space_type = 'TEXT_EDITOR'
#    bl_region_type = 'UI'
#    bl_category = "Text"
#    bl_label = "Find & Replace"

#    def draw(self, context):
#        layout = self.layout
#        st = context.space_data

#        # settings
#        row = layout.row(align=True)
#        if not st.text:
#            row.active = False
#        row.prop(st, "use_match_case", text="Case", toggle=True)
#        row.prop(st, "use_find_wrap", text="Wrap", toggle=True)
#        row.prop(st, "use_find_all", text="All", toggle=True)

#        # find
#        col = layout.column()
#        row = col.row(align=True)
#        row.prop(st, "find_text", icon='VIEWZOOM', text="")
#        row.operator("text.find_set_selected", text="", icon='IMPORT')
#        col.operator("text.find")

#        # replace
#        col = layout.column()
#        row = col.row(align=True)
#        row.prop(st, "replace_text", icon='DECORATE_OVERRIDE', text="")
#        row.operator("text.replace_set_selected", text="", icon='IMPORT')
#        col.operator("text.replace")


class TEXT_MT_view(Menu):
    bl_label = "View"

    def draw(self, context):
        layout = self.layout

        st = context.space_data

        layout.prop(st, "show_region_ui")

        layout.separator()

        layout.prop(st, "show_line_numbers")
        layout.prop(st, "show_word_wrap")
        layout.prop(st, "show_syntax_highlight")
        layout.prop(st, "show_line_highlight")

        layout.separator()

        layout.operator("text.move",
                        text="Top of File",
                        ).type = 'FILE_TOP'
        layout.operator("text.move",
                        text="Bottom of File",
                        ).type = 'FILE_BOTTOM'

        layout.separator()

        layout.menu("INFO_MT_area")


class TEXT_MT_text(Menu):
    bl_label = "Text"

    def draw(self, context):
        layout = self.layout

        st = context.space_data
        text = st.text

        layout.operator("text.new", text="New")
        layout.operator("text.open", text="Open...", icon='FILE_FOLDER')

        if text:
            layout.separator()
            layout.operator("text.reload")

            layout.separator()
            layout.operator("text.save", icon='FILE_TICK')
            layout.operator("text.save_as", text="Save As...")

            if text.filepath:
                layout.operator("text.make_internal")

            layout.separator()
            layout.operator("text.run_script")


class TEXT_MT_templates_py(Menu):
    bl_label = "Python"

    def draw(self, _context):
        self.path_menu(
            bpy.utils.script_paths("templates_py"),
            "text.open",
            props_default={"internal": True},
        )


class TEXT_MT_templates_osl(Menu):
    bl_label = "Open Shading Language"

    def draw(self, _context):
        self.path_menu(
            bpy.utils.script_paths("templates_osl"),
            "text.open",
            props_default={"internal": True},
        )


class TEXT_MT_templates(Menu):
    bl_label = "Templates"

    def draw(self, _context):
        layout = self.layout
        layout.menu("TEXT_MT_templates_py")
        layout.menu("TEXT_MT_templates_osl")


class TEXT_MT_edit_select(Menu):
    bl_label = "Select"

    def draw(self, _context):
        layout = self.layout

        layout.operator("text.select_all")
        layout.operator("text.select_line")


class TEXT_MT_format(Menu):
    bl_label = "Format"

    def draw(self, _context):
        layout = self.layout
        st = _context.space_data
        text = st.text

        layout.operator("text.indent")
        layout.operator("text.unindent")

        layout.separator()

        layout.operator("text.comment_toggle")

        layout.separator()

        layout.operator_menu_enum("text.convert_whitespace", "type")


class TEXT_MT_edit_to3d(Menu):
    bl_label = "Text To 3D Object"

    def draw(self, _context):
        layout = self.layout

        layout.operator("text.to_3d_object",
                        text="One Object",
                        ).split_lines = False
        layout.operator("text.to_3d_object",
                        text="One Object Per Line",
                        ).split_lines = True


class TEXT_MT_edit(Menu):
    bl_label = "Edit"

    @classmethod
    def poll(cls, context):
        return (context.space_data.text)

    def draw(self, _context):
        layout = self.layout
        st = _context.space_data
        text = st.text

        layout.operator("ed.undo")
        layout.operator("ed.redo")

        layout.separator()

        layout.operator("text.cut")
        layout.operator("text.copy", icon='COPYDOWN')
        layout.operator("text.paste", icon='PASTEDOWN')
        layout.operator("text.duplicate_line")

        layout.separator()

        layout.prop(st, "use_live_edit")

        layout.separator()

        layout.operator("text.move_lines",
                        text="Move line(s) up").direction = 'UP'
        layout.operator("text.move_lines",
                        text="Move line(s) down").direction = 'DOWN'

        layout.separator()

        layout.menu("TEXT_MT_edit_select")

        layout.separator()

        layout.operator("text.jump")
        layout.operator("text.find")
        layout.operator("text.toggle_find_search")
        layout.operator("text.start_find", text="Find...")
        layout.operator("text.autocomplete")

        layout.separator()

        layout.menu("TEXT_MT_edit_to3d")


class TEXT_MT_context_menu(Menu):
    bl_label = ""

    def draw(self, _context):
        layout = self.layout

        layout.operator_context = 'INVOKE_DEFAULT'

        layout.operator("text.cut")
        layout.operator("text.copy")
        layout.operator("text.paste")

        layout.separator()

        layout.operator("text.run_script")


classes = (
    TEXT_HT_header,
    TEXT_HT_footer,
    TEXT_MT_edit,
    TEXT_MT_editor_menus,
    TEXT_PT_properties,
    TEXT_OT_toggle_find,
#    TEXT_PT_find,
    TEXT_MT_view,
    TEXT_MT_text,
    TEXT_MT_templates,
    TEXT_MT_templates_py,
    TEXT_MT_templates_osl,
    TEXT_MT_edit_select,
    TEXT_MT_format,
    TEXT_MT_edit_to3d,
    TEXT_MT_context_menu,
)

if __name__ == "__main__":  # only for live edit.
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
