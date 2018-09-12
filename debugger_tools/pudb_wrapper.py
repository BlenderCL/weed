import bpy
from os import path, listdir
from shutil import copytree, rmtree
from site import getsitepackages, getusersitepackages
import sys

breakpoint = '''
{0}###  W E E D  ########################################################
{0}import pudb  #########################################################
{0}global _MODULE_SOURCE_CODE  ##########################################
{0}_MODULE_SOURCE_CODE = pudb.get_code(__file__)  #######################
{0}pu.db  ################################################ Breakpoint ###

'''

class InsertBreakpoint(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "weed.insert_breakpoint"
    bl_label = "Insert pudb Breakpoint"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        line = context.space_data.text.current_line.body
        indent = line[:len(line) - len(line.lstrip())]
        bpy.ops.text.move(type = 'LINE_BEGIN')
        bpy.ops.text.insert(text = breakpoint.format(indent))
        return {'FINISHED'}

class SearchBreakpoint(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "weed.search_breakpoint"
    bl_label = "Search for Breakpoint"

    @classmethod
    def poll(cls, context):
        return context.space_data.type == 'TEXT_EDITOR'

    def execute(self, context):
        sd = context.space_data
        sd.find_text = '###  W E E D'
        sd.use_find_all = True
        #bpy.ops.text.jump(line=1)
        bpy.ops.text.find()
        brk_end = sd.text.lines[sd.text.current_line_index + 4].body.rstrip()
        if (sd.text.current_character != sd.text.select_end_character and
            'Breakpoint' in brk_end):
            #bpy.ops.text.find_set_selected()
            bpy.ops.text.move(type='LINE_BEGIN')
            bpy.ops.text.move_select(type = 'NEXT_LINE')
            bpy.ops.text.move_select(type = 'NEXT_LINE')
            bpy.ops.text.move_select(type = 'NEXT_LINE')
            bpy.ops.text.move_select(type = 'NEXT_LINE')
            ##bpy.ops.text.move_select(type = 'LINE_END')
            bpy.ops.text.move_select(type = 'NEXT_LINE')
            #bpy.ops.text.cut()
            #bpy.context.window_manager.clipboard = ''
            return {'FINISHED'}
        else:
            return bpy.ops.weed.search_breakpoint()

# there are global site-packages lib for python or
# there are user site-packages too...
# in some Blender installs global site-packages may not have
# permissions...
# right now using user site-packages folder
# (folder has permission, but it's a folder outside blender,
# in the user folder)

# user site package
site_package = getusersitepackages()

# global site package
#for site_package in getsitepackages():
#    if path.basename(site_package) == 'site-packages':
#        break

def register():
    # register with the proper site_package folder 
    libs = path.join(path.dirname(__file__), 'sitepackages_libs')
    for lib in listdir(libs):
        #print(lib)
        try:
            rmtree(path.join(site_package, lib), ignore_errors=True)
            copytree(path.join(libs, lib), path.join(site_package, lib))
        except:
            print("Unexpected error:", sys.exc_info()[0])
            print('weed Blender IDE: fail to install ', lib,
                ', debugger tools may not function properly')
    bpy.utils.register_class(InsertBreakpoint)
    bpy.utils.register_class(SearchBreakpoint)


def unregister():
    # continue with the proper site_package folder 
    libs = path.join(path.dirname(__file__), 'sitepackages_libs')
    for lib in listdir(libs):
        #print(lib)
        try:
            rmtree(path.join(site_package, lib))
            #copytree(path.join(libs, lib), path.join(site_package, lib))
        except:
            print("Unexpected error:", sys.exc_info()[0])
            print('weed Blender IDE:', lib, 'fail to uninstall',
                ', debugger tools may leave python modules')
    bpy.utils.unregister_class(SearchBreakpoint)
    bpy.utils.unregister_class(InsertBreakpoint)
