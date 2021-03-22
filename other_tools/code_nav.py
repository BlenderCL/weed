# BEGIN GPL LICENSE BLOCK #####
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
# END GPL LICENSE BLOCK #####

# <pep8 compliant>

# Tintwotin: Couldn't get Edit Externally to work, so that code is commented out

bl_info = {
    'name': 'Code Navigation',
    'author': 'Greg Zaal, Tintwotin',
    'version': (1, 3),
    "blender": (2, 80, 0),
    'location': 'Text Editor > Sidebar',
    'warning': '',
    'description': 'Show all classes and functions and jump to them. Switch to an external editor and reload+run the script',
    'wiki_url': '',
    'tracker_url': '',
    'category': 'Development'}


import bpy
from subprocess import Popen
from os.path import exists

built_in_functions = ['execute', 'invoke', 'modal', 'cancel', 'poll', 'draw', 'check', 'register', 'unregister', '__init__', '__del__']

# Addon prefs
class CodeNavigation(bpy.types.AddonPreferences):
    bl_idname = __name__

    ext_text_editor: bpy.props.StringProperty(
        name="External text editor executable",
        subtype='FILE_PATH',
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "ext_text_editor")


class TEXT_OT_code_nav_edit_externally(bpy.types.Operator):

    'Edit the text file with an external editor'
    bl_idname = 'codenav.edit_ext'
    bl_label = 'Edit Externally'

    @classmethod
    def poll(cls, context):
        if context.area.spaces[0].text.filepath != '':
            return True
        else:
            return False

    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons[__name__].preferences
        if exists(addon_prefs.ext_text_editor):
            Popen([addon_prefs.ext_text_editor, context.area.spaces[0].text.filepath])
        else:
            self.report({'ERROR'}, "Text editor path is invalid, specify in addon preferences")
        return {'FINISHED'}


class TEXT_OT_code_nav_reload_run(bpy.types.Operator):

    'Reload the file from disk and run it (use when editing in an external text editor)'
    bl_idname = 'codenav.reload_run'
    bl_label = 'Reload & Run'

    @classmethod
    def poll(cls, context):
        if context.area.spaces[0].text.filepath != '':
            return True
        else:
            return False

    def execute(self, context):
        unregister()
        bpy.ops.text.reload()
        bpy.ops.text.run_script()
        return {'FINISHED'}


class TEXT_OT_code_nav_scroll(bpy.types.Operator):

    'Go to and select this code block'
    bl_idname = 'codenav.scroll'
    bl_label = 'Jump Here'
    line: bpy.props.IntProperty()
    last_line: bpy.props.IntProperty()
    do_nothing: bpy.props.BoolProperty(default = False)

    def execute(self, context):
        if self.do_nothing:
            return {'CANCELLED'}

        if self.last_line:
            self.line = self.last_line
        if context.area.spaces[0].text.lines[self.line - 1].body:
            oldfind = context.area.spaces[0].find_text
            oldwrap = bpy.context.space_data.use_find_wrap
            oldcase = bpy.context.space_data.use_match_case
            context.space_data.use_find_wrap = True
            context.space_data.use_match_case = True
            while context.area.spaces[0].text.current_line_index+1 != self.line:
                context.area.spaces[0].find_text = context.area.spaces[0].text.lines[self.line - 1].body
                bpy.ops.text.find()

            context.area.spaces[0].find_text = oldfind
            context.space_data.use_find_wrap = oldwrap
            context.space_data.use_match_case = oldcase

        self.last_line = 0
        context.scene.CodeNavLineNum = self.line
        return {'FINISHED'}


class OBJECT_PT_code_nav(bpy.types.Panel):
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_label = "Code Navigation"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        col = layout.column(align=True)
        text = context.area.spaces[0].text
        linenum = 0
#        row = col.row()
#        row.label(text="Type  Name")
#        row.prop(scene, 'CodeNavIgnoreBuiltIn', toggle=True)
        for line in text.lines:
            linenum += 1
            linetext = line.body.strip()
            if linetext.startswith('class ') or linetext.startswith('def '):
                blockname = (((linetext.split('('))[0]).strip().split(' '))[-1]  # get only class/fnc name
                if not (scene.CodeNavIgnoreBuiltIn and (blockname in built_in_functions)):
                    row = col.row()
                    labelicon = 'RADIOBUT_OFF'
                    if line.body.strip().startswith('def'):
                        labelicon = 'LAYER_USED'
                    if not line.body.startswith('    '):
                        row.label(text=blockname, icon=labelicon)
                    else:
                        row.label(text="    " + blockname, icon=labelicon)
                    r = row.operator('codenav.scroll', text='', icon='TRIA_RIGHT', emboss=False)
                    r.line = linenum

        col = layout.column(align=True)
        row = col.row(align=True)
        col = col.box()
        row.prop(scene, 'CodeNavLineNum')
        if len(list(text.lines)) >= scene.CodeNavLineNum:
            line_text = text.lines[scene.CodeNavLineNum-1].body
            line_text = line_text.strip()
            if line_text:
                row.operator('codenav.scroll', text='', icon='TRIA_RIGHT').line = scene.CodeNavLineNum
                col.label(text=line_text)
            else:
                row.operator('codenav.scroll', text='', icon='RIGHTARROW_THIN').do_nothing = True
                col.label(text='        < Blank Line >')
        else:
            row.operator('codenav.scroll', text='', icon='TRIA_LEFT').last_line = len(list(text.lines))
            col.label(text='        < No More Lines >')

        col = layout.column()
        row = col.row(align=True)
#        row.operator('codenav.edit_ext')
        row.prop(scene, 'CodeNavIgnoreBuiltIn', toggle=True)
        row.operator('codenav.reload_run')


def menu_func(self, context):
    if context.area.spaces[0].text:
        if context.area.spaces[0].text.filepath != '':
            col = self.layout.column()
            row = col.row()
            row.operator('codenav.reload_run', text='', icon='FILE_REFRESH')


classes = (
    CodeNavigation,
    TEXT_OT_code_nav_edit_externally,
    TEXT_OT_code_nav_reload_run,
    TEXT_OT_code_nav_scroll,
    OBJECT_PT_code_nav,
    )

addon_keymaps = []


def register():
    bpy.types.Scene.CodeNavIgnoreBuiltIn = bpy.props.BoolProperty(
        name="Hide Built-in",
        default=True,
        description="Do not show built-in functions (execute, poll, draw, register...)")
    bpy.types.Scene.CodeNavLineNum = bpy.props.IntProperty(
        name="Line",
        default=1,
        min=1,
        description="The line to jump to")

    bpy.types.TEXT_HT_header.append(menu_func)

    # Sets up hotkey
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(
            name='Text', space_type='TEXT_EDITOR')
        kmi = km.keymap_items.new(
            "codenav.reload_run",
            type='P',
            value='PRESS',
            ctrl=True,
            alt=True)
        addon_keymaps.append((km, kmi))

    for i in classes:
        bpy.utils.register_class(i)


def unregister():
    del bpy.types.Scene.CodeNavIgnoreBuiltIn
    del bpy.types.Scene.CodeNavLineNum

    bpy.types.TEXT_HT_header.remove(menu_func)

    # Removes up hotkey
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    for i in classes:
        bpy.utils.unregister_class(i)

if __name__ == "__main__":
    register()
