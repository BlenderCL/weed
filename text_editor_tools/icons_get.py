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

# <pep8 compliant>

"""
bl_info = {
    "name": "Icons",
    "author": "Crouch, N.tox, PKHG, Campbell Barton, Dany Lebel",
    "version": (1, 5, 2),
    "blender": (2, 57, 0),
    "location": "Text Editor > Properties or " "Console > Console Menu",
    "warning": "",
    "description": "Click an icon to display its name and "
                   "copy it to the clipboard",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/"
                "Py/Scripts/System/Display_All_Icons",
    "category": "Development",
}
"""

import bpy


def create_icon_list():
    rna_prop = bpy.types.UILayout.bl_rna.functions['prop']
    icons = rna_prop.parameters['icon'].enum_items.keys()
    #icons.remove('NONE')
    return icons


class WM_OT_icon_info(bpy.types.Operator):
    bl_idname = 'wm.icon_info'
    bl_label = 'Icon Info'
    bl_description = 'Click to copy this icon name to the clipboard'
    bl_options = {'REGISTER', 'INTERNAL'}
    icon = bpy.props.StringProperty()

    def invoke(self, context, event):
        bpy.data.window_managers['WinMan'].clipboard = "%s" % self.icon
        self.report({'INFO'}, "%s copied" % self.icon)
        return {'FINISHED'}
    
    
class WEED_OT_IconsDialog(bpy.types.Operator):
    bl_idname = 'weed.icons_dialog'
    bl_label = 'Icons Info'
    bl_description = 'show icons'
    bl_options = {'REGISTER', 'INTERNAL'}

    def __init__(self):
        self.amount = 42
        self.icon_list = create_icon_list()

    def draw(self, context):
        layout = self.layout
        # render the icons
        col = layout.column(align = True)
        for i, icon in enumerate(self.icon_list):
            if i % self.amount == 0:
                row = col.row(align = True)
            row.operator('wm.icon_info',
                         text = ' ',
                         icon = icon,
                         emboss = False).icon = icon
        for i in range(self.amount - len(self.icon_list) \
        % self.amount):
            row.label('')
    
    def execute(self, context):
        #print('testing...')
        bpy.ops.text.paste()
        return {'FINISHED'} 

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=840)



def register():
    bpy.utils.register_class(WM_OT_icon_info)
    bpy.utils.register_class(WEED_OT_IconsDialog)
    #bpy.types.TEXT_HT_header_weed_menu.append(icons_menu_entry)

def unregister():
    bpy.utils.unregister_class(WM_OT_icon_info)
    bpy.utils.unregister_class(WEED_OT_IconsDialog)
    #bpy.types.TEXT_HT_header_weed_menu.remove(icons_menu_entry)


###############
# Corregir luego con una version que no tenga boton ok
################
