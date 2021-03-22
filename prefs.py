import bpy
from bpy.props import *


class SubmoduleGroup(bpy.types.PropertyGroup):
    level: IntProperty()
    name: StringProperty()
    icon: StringProperty()


class PropsApiNav(bpy.types.PropertyGroup):

    path: StringProperty(
        name='path',
        description='Enter bpy.ops.api_navigator to see the documentation',
        default='bpy')
    
    old_path: StringProperty(
        name='old_path', 
        default='')
    
    api_filter: StringProperty(
        name='filter',
        description='Filter the resulting modules', 
        default='')
    
    reduce_to: IntProperty(
        name='Reduce to ',
        description='Display a maximum number of x entries by pages',
        default=10, 
        min=1)
    
    pages: IntProperty(
        name='Pages',
        description='Display a Page', 
        default=0, 
        min=0)

    submodules: CollectionProperty(type=SubmoduleGroup)


class PropsIconsGet(bpy.types.PropertyGroup):

    icg_filter: StringProperty(
        name='filter',
        description='Filter the resulting modules', 
        default='')
    icg_old_filter: StringProperty(
        name='filter',
        description='Filter the resulting modules', 
        default='n')    # 'n' value just for trigger at first time


class WeedPreferences(bpy.types.AddonPreferences):
    bl_idname = 'weed'

    # API navigator props 'anp'
    props_api_nav: PointerProperty(type=PropsApiNav)
    # icon get dialog props 'icg'
    props_icons_get: PointerProperty(type=PropsIconsGet)
    # code editor props 'coed'
    # coed_last_text: StringProperty(name='last_text', default='')



def register():
    bpy.utils.register_class(SubmoduleGroup)
    bpy.utils.register_class(PropsApiNav)
    bpy.utils.register_class(PropsIconsGet)
    bpy.utils.register_class(WeedPreferences)
 
 
def unregister():
    bpy.utils.unregister_class(WeedPreferences)
    bpy.utils.unregister_class(PropsIconsGet)
    bpy.utils.unregister_class(PropsApiNav)
    bpy.utils.unregister_class(SubmoduleGroup)
