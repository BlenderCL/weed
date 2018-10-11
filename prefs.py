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



import bpy
#from weed.text_editor_tools import (
#    find_replace
#)

#def register_find_replace(self, context):
#    if self.find_replace_pref:
#        find_replace.register()
#    else:
#        find_replace.unregister()

class SubmoduleGroup(bpy.types.PropertyGroup):

    level = bpy.props.IntProperty()
    name = bpy.props.StringProperty()
    icon = bpy.props.StringProperty()


class WeedPreferences(bpy.types.AddonPreferences):
    bl_idname = "weed"

    # api_nav_props
    anp_path = bpy.props.StringProperty(name='path',
                          description='Enter bpy.ops.api_navigator to see the documentation',
                          default='bpy')
    anp_old_path = bpy.props.StringProperty(name='old_path', default='')
    anp_filter = bpy.props.StringProperty(name='filter',
                            description='Filter the resulting modules', default='')
    anp_reduce_to = bpy.props.IntProperty(name='Reduce to ',
                            description='Display a maximum number of x entries by pages',
                            default=10, min=1)
    anp_pages = bpy.props.IntProperty(name='Pages',
                        description='Display a Page', default=0, min=0)

    submodules = bpy.props.CollectionProperty(type=SubmoduleGroup)

    # Features show in Menu
    show_bge_console = bpy.props.BoolProperty(
        name = "Show Bge Console Menu",
        description = "Show Bge Console Menu on Main Weed Menu",
        default = True)
    show_code_editor = bpy.props.BoolProperty(
        name = "Show Code Editor Menu",
        description = "Show Code Editor Menu on Main Weed Menu",
        default = True)
    show_icons_get = bpy.props.BoolProperty(
        name = "Show icons get Menu",
        description = "Show icons get Menu on Main Weed Menu",
        default = True)

    # Code Editor Preferences
    opacity = bpy.props.FloatProperty(
        name = "Panel Background transparency",
        description = "0 - fully opaque, 1 - fully transparent",
        min = 0.0, max = 1.0, default = 0.2)
    
    show_tabs = bpy.props.BoolProperty(
        name = "Show Tabs in Panel when multiple text blocks",
        description = "Show opened textblock in tabs next to minimap",
        default = True)
    
    minimap_width = bpy.props.IntProperty(
        name = "Minimap panel width",
        description = "Minimap base width in px",
        min = 25, max = 400, default = 100)
    
    window_min_width = bpy.props.IntProperty(
        name = "Hide Panel when area width less than",
        description = "Set 0 to deactivate side panel hiding, set huge to disable panel",
        min = 0, max = 4096, default = 600)
    
    symbol_width = bpy.props.FloatProperty(
        name = "Minimap character width",
        description = "Minimap character width in px",
        min = 1.0, max = 10.0, default = 1.5)
    
    line_height = bpy.props.IntProperty(
        name = "Minimap line spacing",
        description = "Minimap line spacign in px",
        min = 2, max = 10, default = 4)
    
    block_trans = bpy.props.FloatProperty(
        name = "Code block markings transparency",
        description = "0 - fully opaque, 1 - fully transparent",
        min = 0.0, max = 1.0, default = 0.6)
    
    indent_trans = bpy.props.FloatProperty(
        name = "Indentation markings transparency",
        description = "0 - fully opaque, 1 - fully transparent",
        min = 0.0, max = 1.0, default = 0.9)
    
    show_margin = bpy.props.BoolProperty(
        name = "Activate global Text Margin marker",
        default = True)
    
    margin_column = bpy.props.IntProperty(
        name = "Margin Column",
        description = "Column number to show marker at",
        min = 0, max = 1024, default = 80)

    #Register Unregister module Find Replace
    find_replace_pref = bpy.props.BoolProperty(#update=register_find_replace,
        name = "Find Replace fix",
        description = "popup version of find replace",
        default = True
    )

#### incorporar preferences del code autocomplete
# class AddonPreferences(bpy.types.AddonPreferences):
#     bl_idname = __name__

    line_amount = bpy.props.IntProperty(name = "Lines", default = 8,  
                    min = 1, max = 20,
                    description = "Amount of lines shown in the context box")
    show_dot_files = bpy.props.BoolProperty(name = ' Show hidden files',
                    default = False,
                    description = 'Show hidden files on addon files panel')
    show_dot_addons = bpy.props.BoolProperty(name = 'Show dot Addons',
                    default = False,
                    description = 'Show hidden addons on addon files panel')
    user_site_packages = bpy.props.BoolProperty(name = 'Browse User Site Packages',
                    default = False,
                    description = 'Browse User Site Packages on addon files panel')


    def draw(self, context):
        layout = self.layout

        # layout.label(text = "Here you can enable or disable " 
        #                     "specific tools, in case they interfere "
        #                     "with others or are just plain annoying")

        split = layout.split(percentage=0.3)

        col = split.column()
        sub = col.column(align=True)

        sub.prop(self, "show_bge_console", toggle=True)
        sub.prop(self, "show_code_editor", toggle=True)
        sub.prop(self, "show_icons_get", toggle=True)

        sub.separator()
        
        sub.label(text="3D View", icon='VIEW3D')
        sub.label(text="3D View", icon='VIEW3D')
        #sub.label(text="3D View", icon='VIEW3D')
        sub.prop(self, "find_replace_pref", toggle=True)

        # Code Editor Settings
        col = split.column()
        
        box = col.box()
        
        box.label(text="Code Editor Settings", icon='WORDWRAP_ON')
        row = box.row()
        sub = row.column(align=True)
        sub.prop(self, "opacity")
        sub.prop(self, "show_tabs", toggle=True)
        sub.prop(self, "window_min_width")
        sub = row.column(align=True)
        sub.prop(self, "minimap_width")
        sub.prop(self, "symbol_width")
        sub.prop(self, "line_height")
        
        box.separator()
        
        row = box.row(align=True)
        row.prop(self, "show_margin", toggle=True)
        row.prop(self, "margin_column")

        box.separator()

        row = box.row(align=True)
        row.prop(self, "block_trans")
        row.prop(self, "indent_trans")
#     def draw(self, context):
#         layout = self.layout
#         row = layout.row(align = False)
#         row.prop(self, 'show_dot_files')
#         row.prop(self, 'show_dot_addons')
#         row.prop(self, 'line_amount')



# registro automatico con register_module
# register y unregister comentados

# def register():
#     bpy.utils.register_class(SubmoduleGroup)
#     bpy.utils.register_class(WeedPreferences)


# def unregister():
#     bpy.utils.unregister_class(WeedPreferences)
#     bpy.utils.unregister_class(SubmoduleGroup)
