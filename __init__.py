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
from os import path, listdir, access, W_OK
from shutil import copytree, rmtree
from site import getsitepackages, getusersitepackages
from . weed_tools import get_addons_list
from . quick_operators import register_menus, unregister_menus
from . checksumdir import dirhash
import builtins
from linecache import cache

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

# try with global site package
# a folder inside blender (but maybe without permission)
for site_package in getsitepackages():
   if path.basename(site_package) == 'site-packages':
       break
print('global site package folder, {}'.format(site_package))
# test for write access. if fails it gets user site package
if not access(site_package, W_OK):
    site_package = getusersitepackages()
    print('user site package folder override, {}'.format(site_package))


class CodeEditorsGroup(bpy.types.PropertyGroup):
    code_editor = bpy.props.StringProperty(name='code editor',
                                           default='')


class BreakpointShortcut(object):
    @property
    def here(self):
        #"#""Print the local variables in the caller's frame."#""
        import inspect
        frame = inspect.currentframe()
        try:
            caller_file = frame.f_back.f_locals['__file__']
        except:
            caller_file = '# no code'
            print('fail to get __file__')
        finally:
            del frame
        # def get_code(filepath):
        # import bpy, os.path
        try:
            import bge
            if hasattr(bge, 'is_fake'):
                #print('# bge fake')
                in_game = False
            else:
                #print('# bge real')
                in_game = True
        except ImportError:
            #print('# bge not present')
            in_game = False
        if in_game:
            import bge
            script = bge.logic.getCurrentController().script
            if len(script.splitlines()) == 1:
                #print('# bge module type controller call')
                script = script[:script.find('.')] + '.py'
                dbg_code = bpy.data.texts[script].as_string()
            else:
                #print('# bge script type controller call')
                dbg_code = script
        else:
            try:
                #print('# script open in collection bpy.data.texts')
                script = path.basename(caller_file)
                dbg_code = bpy.data.texts[script].as_string()
            except:
                #print('# read script from disk')
                try:
                    dbg_code = open(caller_file).read()
                except:
                    dbg_code = '# no code passed yet!..'
            # if hasattr(bpy, 'data') and hasattr(bpy.data, 'texts'):
            #     print('# commonly [alt]-[p] regular blender script')
            #     script = os.path.basename(caller_file)
            #     return bpy.data.texts[script].as_string()
            # else:
            #     print('# inside restricted, like register addon')
            #     return open(caller_file).read()
        cache[caller_file[:256]] = (len(dbg_code), 0,
                                    dbg_code,
                                    caller_file[:256])
        # import sys
        dbg = _get_debugger()
        from pudb import set_interrupt_handler
        import threading
        if isinstance(threading.current_thread(), threading._MainThread):
            set_interrupt_handler()
        dbg.set_trace(sys._getframe().f_back)


CURRENT_DEBUGGER = []

def _get_debugger(**kwargs):
    if not CURRENT_DEBUGGER:
        from pudb.debugger import Debugger
        dbg = Debugger(**kwargs)

        CURRENT_DEBUGGER.append(dbg)
        return dbg
    else:
        return CURRENT_DEBUGGER[0]


def register():
    # before register module...
    # of pudb_wrapper, install python low level libraries
    #############################################################
    # register with the proper site_package folder (*md5sum tal vez?)
    # definir mecanismo, no reinstalar estas librerias cada vez...
    md5_hashes = {
            'bpython'  : 'f71aa32d8a395e53c5629bcc1bde4763',
            'colorama' : 'af625c7cb8315d11e8c72027ea082295',
            'pudb'     : '2da49e650733873dc51b0e9aadfceb39',
            'pygments' : '86f122fc42f24ea825a03de8fe012d86',
            'urwid'    : '243d975bcaad214cef0ce6c11d1e601e'
            }
    src_libs_path = path.join(path.dirname(__file__),
                        'debugger_tools',
                        'sitepackages_libs')
    trgt_libs_list = listdir(site_package)
    for lib in sorted(md5_hashes.keys()):
        if not lib in trgt_libs_list:
            print(lib, 'module is not present, will be installed')
            copytree(path.join(src_libs_path, lib),
                     path.join(site_package, lib))
        elif md5_hashes[lib] != dirhash(path.join(site_package, lib), 'md5',
                                excluded_extensions=['pyc', 'gitignore'],
                                excluded_files=['pudb.cfg',
                                                'saved_breakpoints'
                                ]):
            print(lib, 'module maybe is outdated, will be replaced')
            md5_hash = dirhash(path.join(site_package, lib), 'md5',
                                excluded_extensions=['pyc', 'gitignore'],
                                excluded_files=['pudb.cfg',
                                                'saved_breakpoints'
                                ])
            print('md5 hash was', md5_hash)
            rmtree(path.join(site_package, lib), ignore_errors=True)
            copytree(path.join(src_libs_path, lib),
                     path.join(site_package, lib))
        else:
            print(lib, "module it's already installed")

    # register module...
    bpy.utils.register_class(CodeEditorsGroup)
    bpy.utils.register_module(__name__)
    
    # after register module...

    bpy.types.WindowManager.code_editors = bpy.props.CollectionProperty(
                                                        type=CodeEditorsGroup)
    bpy.types.WindowManager.weed_active_toolbox = bpy.props.EnumProperty(
            name = 'panel',
            default = 'draw_develop_box',
            items = [('draw_develop_box', 'Addon develop', '', 'SCRIPT', 0),
                     ('draw_code_tree_box', 'Code tree', '', 'OOPS', 1),
                     ('draw_debugger_box', 'Debugger tools', '', 'RECOVER_AUTO', 2)])
    register_keymaps()
    register_menus()
    bpy.types.Scene.addon_development = bpy.props.EnumProperty(
        items=get_addons_list,
        name="Addon Development")
    
    # Weed Blender IDE only use python3, it's default from blender 2.5x +
    # if PY3:
    #     import builtins
    #     builtins.__dict__["breakpoint"] = BreakpointShortcut()
    # else:
    #     import __builtin__
    #     __builtin__.__dict__["breakpoint"] = BreakpointShortcut()
    builtins.__dict__["breakpoint"] = BreakpointShortcut()

    for module in modules:
        print("{} submodule registered.".format(module.__name__))
    print("enable weed with {} modules registered.".format(len(modules)))
    # print(modules)



def unregister():
    # before module...
    # continue with the proper site_package folder 
    # libs = path.join(path.dirname(__file__),
    #                  'debugger_tools',
    #                  'sitepackages_libs')
    # for lib in listdir(libs):
    #     #print(lib)
    #     try:
    #         rmtree(path.join(site_package, lib))
    #         #copytree(path.join(libs, lib), path.join(site_package, lib))
    #     except:
    #         print('Unexpected error:', sys.exc_info()[0])
    #         print('weed Blender IDE:', lib, 'fail to uninstall,',
    #               'debugger tools could have left garbage python modules')

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
