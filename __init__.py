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
"""
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
"""

#import bpy
import sys

# import weed's modules

# NOTE: avoid local imports whenever possible!
# Thanks to Christopher Crouzet for let me know about this.
# http://stackoverflow.com/questions/13392038/python-making-a-class-variable-static-even-when-a-module-is-imported-in-differe

from weed.text_editor_tools import (
    code_editor,
    icons_get,
    api_navigator,
    find_replace,
    )

from weed.bge_console import (
    console,
    )

from weed.debugger_tools import (
    pudb_wrapper,
    )

from weed import prefs

from weed import ui





#~ from amaranth.modeling import symmetry_tools
#~ 
#~ from amaranth.scene import (
    #~ refresh,
    #~ save_reload,
    #~ current_blend,
    #~ stats,
    #~ goto_library,
    #~ debug,
    #~ material_remove_unassigned,
    #~ )

# register the addon + modules found in globals()
bl_info = {
    "name": "Weed Blender IDE",
    "author": "Cristian Hasbun",
    "version": (0, 3, 1),
    "blender": (2, 74),
    "location": "Text Editor | Interactive Console | Terminal Console",
    "description": "WEED Enhances Empowered Developers !, Debug Blender inside Blender",
    "warning": "",
    "wiki_url": "http://www.blender.cl/weed_IDE",
    "tracker_url": "",
    "category": "Development",
}


def _call_globals(attr_name):
    for m in globals().values():
        if hasattr(m, attr_name):
            getattr(m, attr_name)()


def _flush_modules(pkg_name):
    pkg_name = pkg_name.lower()
    for k in tuple(sys.modules.keys()):
        if k.lower().startswith(pkg_name):
            del sys.modules[k]


def register():
    # replaced for explicit calls
    #_call_globals("register")
    code_editor.register()
    icons_get.register()
    api_navigator.register()
    find_replace.register()
    console.register()
    pudb_wrapper.register()
    prefs.register()
    ui.register()


def unregister():
    # DON'T WORK, Order dependant
    #_call_globals("unregister")
    code_editor.unregister()
    icons_get.unregister()
    api_navigator.unregister()
    find_replace.unregister()
    console.unregister()
    pudb_wrapper.unregister()
    prefs.unregister()
    ui.unregister()
    
    _flush_modules("weed")  # reload weed


