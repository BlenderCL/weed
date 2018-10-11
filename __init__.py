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
'''
Weed Blender IDE
       Weed Enhance Empowered Developers

Develop for Blender... from inside Blender.
Weed Blender IDE it's an integrated debugger for Blender and BGE. It
works inside terminal console (nobody thinks that terminal console
its so usefull).
Weed has a runtime console for BGE Game Engine, displayed on top of the
runtime with GL code.
Weed's mission its give a consistent environment for development. With
this objetive this addon packs a set of development
************ REESCRIBIR *************
'''

'''
Copyright (C) 2014 Jacques Lucke
mail@jlucke.com

Created by Jacques Lucke

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    "name": "Weed Blender IDE",
    "author": "Cristian Hasbun",
    "version": (2018, 10, 1),
    "blender": (2, 74),
    "location": "Text Editor | Interactive Console | Terminal Console",
    "description": "WEED Enhances Empowered Developers!  *recursive acronym",
    "warning": "",
    #"warning": "like in the butchery, not expect to be free of bugs...",
    "wiki_url": "http://www.blender.cl/weed_IDE",
    "tracker_url": "",
    "category": "Development",
}
   
import bpy
import sys
from os import path, listdir
import site
from . addon_development_manager import get_addons_list
from . quick_operators import register_menus, unregister_menus

# load and reload submodules
##################################    
from .developer_utils import setup_addon_modules
modules = setup_addon_modules(__path__, __name__, "bpy" in locals())

def _flush_modules(pkg_name):
    pkg_name = pkg_name.lower()
    for k in tuple(sys.modules.keys()):
        if k.lower().startswith(pkg_name):
            del sys.modules[k]

# register
##################################
addon_keymaps = []
def register_keymaps():
    global addon_keymaps
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Text',
                                         space_type='TEXT_EDITOR')
    kmi = km.keymap_items.new('weed.popup_find_replace',
                              'F', 'PRESS', ctrl=True, shift=True)
    kmi = km.keymap_items.new('weed.select_whole_string',
                              type='Y', value='PRESS', ctrl=True)
    kmi = km.keymap_items.new('weed.switch_lines',
                              type='R', value='PRESS', ctrl=True)
    kmi = km.keymap_items.new('wm.call_menu',
                              type='SPACE', value='PRESS', ctrl=True)
    kmi.properties.name = 'weed.insert_template_menu'
    kmi = km.keymap_items.new('wm.call_menu',
                              type='TAB', value='PRESS', ctrl=True)
    kmi.properties.name = 'weed.select_text_block'
    addon_keymaps.append(km)

    
def unregister_keymaps():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()
 
# there are global site-packages lib folder for python, and
# there are user site-packages lib folder too...
# in some Blender installs global site-packages may not have
# permissions...
# right now using user site-packages folder
# (folder has permission, but it's a folder outside blender,
# in the user folder)

# user site package
site_package = site.getusersitepackages()

# global site package
#for site_package in site.getsitepackages():
#    if path.basename(site_package) == 'site-packages':
#        break

def register():
    # before register module...

    # de pudb_wrapper, instalar librerias low level
    #############################################################
    # register with the proper site_package folder (*md5sum tal vez?)
    # definir mecanismo, no reinstalar estas librerias cada vez...
    libs = path.join(path.dirname(__file__),
                     'debugger_tools',
                     'sitepackages_libs')
    for lib in listdir(libs):
        #print(lib)
        try:
            rmtree(path.join(site_package, lib), ignore_errors=True)
            copytree(path.join(libs, lib), path.join(site_package, lib))
        except:
            print('Unexpected error:', sys.exc_info()[0])
            print('weed Blender IDE: fail to install ', lib,
                ', debugger tools may not function properly')

    # register module...
    bpy.utils.register_module(__name__)

    # after register module...
    bpy.types.WindowManager.code_editors = bpy.props.StringProperty(default="")
    register_keymaps()
    register_menus()
    bpy.types.Scene.addon_development = bpy.props.EnumProperty(
        items=get_addons_list,
        name="Addon Development")
    
    for module in modules:
        print("{} submodule registered.")
    print("enable weed with {} modules registered.".format(len(modules)))
    # print(modules)


def unregister():
    # before module...
    # continue with the proper site_package folder 
    libs = path.join(path.dirname(__file__),
                     'debugger_tools',
                     'sitepackages_libs')
    for lib in listdir(libs):
        #print(lib)
        try:
            rmtree(path.join(site_package, lib))
            #copytree(path.join(libs, lib), path.join(site_package, lib))
        except:
            print('Unexpected error:', sys.exc_info()[0])
            print('weed Blender IDE:', lib, 'fail to uninstall,',
                  'debugger tools could have left garbage python modules')

    # call module...
    bpy.utils.unregister_module(__name__)
    
    # after module
    unregister_keymaps()
    unregister_menus()
    # _flush_modules("weed")  # reload weed

    # remember try to clean this objects
    # del bpy.types.WindowManager.code_editors
    # del bpy.types.Scene.addon_development
    print("weed unregistered")
