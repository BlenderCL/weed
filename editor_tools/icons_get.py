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

# bl_info = {
#     "name": "Icons",
#     "author": "Crouch, N.tox, PKHG, Campbell Barton, Dany Lebel",
#     "version": (1, 5, 2),
#     "blender": (2, 57, 0),
#     "location": "Text Editor > Properties or " "Console > Console Menu",
#     "warning": "",
#     "description": "Click an icon to display its name and "
#                    "copy it to the clipboard",
#     "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/"
#                 "Py/Scripts/System/Display_All_Icons",
#     "category": "Development",
# }


import bpy
# from bpy.props import StringProperty

# class PropsIconsGet(bpy.types.PropertyGroup):

#     icg_filter: StringProperty(
#         name='filter',
#         description='Filter the resulting modules', 
#         default='')
#     icg_old_filter: StringProperty(
#         name='filter',
#         description='Filter the resulting modules', 
#         default='n')    # 'n' value just for trigger at first time

# bpy.utils.register_class(PropsIconsGet)

# bpy.types.WindowManager.props_weed_icons_get = bpy.props.PointerProperty(type=PropsIconsGet)

# icg_filter = ''
# icg_old_filter = ''

#icons_get = bpy.context.window_manager.props_weed_icons_get
# if bpy.context.preferences.addons.get('weed'):
#     check_prefs = True 
# else 
#     check_prefs = False

# icons_get = bpy.context.preferences.addons['weed'].preferences.props_icons_get

def create_icon_list(text_filter):
    rna_prop = bpy.types.UILayout.bl_rna.functions['prop']
    icons = [icon for icon in rna_prop.parameters['icon'].enum_items.keys()
             if text_filter.upper() in icon]
    #icons.remove('NONE')
    return icons


class WEED_OT_clear_filter(bpy.types.Operator):
    """Clear icon filter"""
    bl_idname = 'weed.icons_get_clear_filter'
    bl_label = 'Icons get clear filter'

    def execute(self, context):
        addons = bpy.context.preferences.addons
        if not addons.get('weed'):
            return {'CANCELLED'}
        addons['weed'].preferences.props_icons_get.icg_filter = ''
        return {'FINISHED'}


class WEED_OT_icon_info(bpy.types.Operator):
    bl_idname = 'weed.icon_info'
    bl_label = 'Icon Info'
    bl_description = 'Click to copy this icon name to the clipboard'
    bl_options = {'REGISTER', 'INTERNAL'}

    icon : bpy.props.StringProperty()

    def invoke(self, context, event):
        bpy.data.window_managers['WinMan'].clipboard = "%s" % self.icon
        self.report({'INFO'}, "%s copied" % self.icon)
        return {'FINISHED'}
    
    
class WEED_OT_IconsDialog(bpy.types.Operator):
    bl_idname = 'weed.icons_dialog'
    bl_label = 'Icons Info'
    bl_description = 'show icons'
    bl_options = {'REGISTER', 'UNDO'}
    
    def __init__(self):
        # self.icon_list = create_icon_list()
        self.icon_list = [] 
        # self.num_cols = int(1.6*sqrt(self.icon_list.__len__()))
        self.num_cols = 40

    @classmethod
    def poll(cls, context):
        return context.preferences.addons.get('weed')

    def check(self, context):
        addons = bpy.context.preferences.addons
        if not addons.get('weed'):
            return False
        icons_get = addons['weed'].preferences.props_icons_get
        if icons_get.icg_filter != icons_get.icg_old_filter:
            icons_get.icg_old_filter = icons_get.icg_filter 
            return True
        else:
            return False

    def draw(self, context):
        # text_filter = prefs.icg_filter       # prefs.icg_old_filter
        # render the icons
        # search

        addons = bpy.context.preferences.addons
        if not addons.get('weed'):
            return
        icons_get = addons['weed'].preferences.props_icons_get
        layout = self.layout
        row = layout.row(align=True)
        row.alignment = 'RIGHT'
        row.label(text='filter icon by name:')
        row.prop(
            icons_get,
            'icg_filter', 
            text=icons_get.icg_filter)
        #row.operator('weed.icons_get_clear_filter', text='', icon='FILTER')
        row.operator('weed.icons_get_clear_filter', text='', icon='PANEL_CLOSE')
        
        col = layout.column(align = True)
        self.icon_list = create_icon_list(icons_get.icg_filter)
        #self.num_cols = int(1.6*sqrt(self.icon_list.__len__()))

        if not len(self.icon_list):
            row = col.row(align = True)
            row.label(text='no matches...')
        else:
            for i, icon in enumerate(self.icon_list):
                    if i % self.num_cols == 0:
                        row = col.row(align = True)
                    row.operator('weed.icon_info',
                                text = ' ',
                                icon = icon,
                                emboss = False).icon = icon
            for i in range(self.num_cols - len(self.icon_list) % self.num_cols):
                row.label(text='')
        
    def execute(self, context):
        #print('testing...')
        try:
            bpy.ops.text.paste()
        except RuntimeError:
            self.report({'WARNING'}, 'no text open to paste into')
        return {'FINISHED'} 

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=770)


def icons_get_menu(self, context):
    layout = self.layout
    # layout.operator_context = 'INVOKE_DEFAULT'
    # layout.label(text="Icon get", icon='CONSOLE')
    layout.operator('weed.icons_dialog',
                text='get icon ID',
                icon='NONE')
    # layout.separator()



def register():
    bpy.utils.register_class(WEED_OT_clear_filter)
    bpy.utils.register_class(WEED_OT_icon_info)
    bpy.utils.register_class(WEED_OT_IconsDialog)
    bpy.types.WEED_MT_main_menu.append(icons_get_menu)
    #bpy.types.TEXT_HT_header_weed_menu.append(icons_menu_entry)

def unregister():
    bpy.types.WEED_MT_main_menu.remove(icons_get_menu)
    bpy.utils.unregister_class(WEED_OT_IconsDialog)
    bpy.utils.unregister_class(WEED_OT_icon_info)
    bpy.utils.unregister_class(WEED_OT_clear_filter)
    #bpy.types.TEXT_HT_header_weed_menu.remove(icons_menu_entry)
#     del(bpy.types.WindowManager.props_weed_icons_get)
# bpy.utils.register_class(PropsIconsGet)

# bpy.types.WindowManager.props_weed_icons_get = bpy.props.PointerProperty(type=PropsIconsGet)

###############
# Corregir luego con una version que no tenga boton ok
################
