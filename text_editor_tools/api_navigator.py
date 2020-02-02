# development_api_navigator.py
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

#bl_info = {
#     "name": "API Navigator",
#     "author": "Dany Lebel (Axon_D)",
#     "version": (1, 0, 2),
#     "blender": (2, 80, 0),
#     "location": "Text Editor > Properties > API Navigator Panel",
#     "description": "Allows exploration of the python api via the user interface",
#     "warning": "",
#     "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/"
#                 "Scripts/Text_Editor/API_Navigator",
#     "category": "Development",
# }

"""
    You can browse through the tree structure of the api. Each child object appears in a list
that tries to be representative of its type. These lists are :

    * Items (for an iterable object)
    * Item Values (for an iterable object which only supports index)
    * Modules
    * Types
    * Properties
    * Structs and Functions
    * Methods and Functions
    * Attributes
    * Inaccessible (some objects may be listed but inaccessible)

    The lists can be filtered to help searching in the tree. Just enter the text in the
filter section. It is also possible to explore other modules. Go the the root and select
it in the list of available modules. It will be imported dynamically.

    In the text section, some informations are displayed. The type of the object,
what it returns, and its docstring. We could hope that these docstrings will be as
descriptive as possible. This text data block named api_doc_ can be toggled on and off
with the Escape key. (but a bug prevent the keymap to register correctly at start)

"""

import bpy
from console.complete_import import get_root_modules


############ Global Variables ############

last_text = None  # last text data block

root_module = None  # root module of the tree

root_m_path = ''  # root_module + path as a string

current_module = None  # the object itself in the tree structure

tree_level = None  # the list of objects from the current_module


def init_tree_level():
    global tree_level
    tree_level = [[], [], [], [], [], [], [], [], []]


init_tree_level()

api_doc_ = ''  # the documentation formated for the API Navigator

module_type = None  # the type of current_module

return_report = ''  # what current_module returns

filter_mem = {}  # remember last filters entered for each path

too_long = False  # is tree_level list too long to display in a panel?


############   Functions   ############

def get_root_module(path):
    # print('get_root_module')
    global root_module
    if '.' in path:
        root = path[:path.find('.')]
    else:
        root = path
    try:
        root_module = __import__(root)
    except:
        root_module = None


def evaluate(module):
    # print('evaluate')
    global root_module, tree_level, root_m_path

    # path = prefs.anp_path
    try:
        len_name = root_module.__name__.__len__()
        root_m_path = 'root_module' + module[len_name:]
        current_module = eval(root_m_path)
        return current_module
    except:
        init_tree_level()
        return None


def get_tree_level():
    # print('get_tree_level')
    prefs = bpy.context.preferences.addons['weed'].preferences
    path = prefs.anp_path

    def object_list():
        # print('object_list')
        global current_module, root_m_path

        itm, val, mod, typ, props, struct, met, att, bug = [], [], [], [], [], [], [], [], []
        iterable = isiterable(current_module)
        if iterable:
            iter(current_module)
            current_type = str(module_type)
            if current_type != "<class 'str'>":
                if iterable == 'a':
                    # if iterable == 'a':
                    # current_type.__iter__()
                    itm = list(current_module.keys())
                    if not itm:
                        val = list(current_module)
                else:
                    val = list(current_module)

        for i in dir(current_module):
            try:
                t = str(type(eval(root_m_path + '.' + i)))
            except (AttributeError, SyntaxError):
                bug += [i]
                continue

            if t == "<class 'module'>":
                mod += [i]
            elif t[0:16] == "<class 'bpy_prop":
                props += [i]
            elif t[8:11] == 'bpy':
                struct += [i]
            elif t == "<class 'builtin_function_or_method'>":
                met += [i]
            elif t == "<class 'type'>":
                typ += [i]
            else:
                att += [i]

        return [itm, val, mod, typ, props, struct, met, att, bug]

    if not path:
        return [[], [], [i for i in get_root_modules()], [], [], [], [], [], []]
    return object_list()


def parent(path):
    """Returns the parent path"""
    # print('parent')

    parent = path
    if parent[-1] == ']' and '[' in parent:
        while parent[-1] != '[':
            parent = parent[:-1]
    elif '.' in parent:
        while parent[-1] != '.':
            parent = parent[:-1]
    else:
        return ''
    parent = parent[:-1]
    return parent


def update_filter():
    """Update the filter according to the current path"""
    global filter_mem
    prefs = bpy.context.preferences.addons['weed'].preferences

    try:
        prefs.anp_filter = filter_mem[prefs.anp_path]
    except:
        prefs.anp_filter = ''


def isiterable(mod):
    try:
        iter(mod)
    except:
        return False
    try:
        mod['']
        return 'a'
    except KeyError:
        return 'a'
    except (AttributeError, TypeError):
        return 'b'


def fill_filter_mem():
    global filter_mem
    prefs = bpy.context.preferences.addons['weed'].preferences

    filter = prefs.anp_filter
    if filter:
        filter_mem[prefs.anp_old_path] = prefs.anp_filter
    else:
        filter_mem.pop(prefs.anp_old_path, None)


######  API Navigator parent class  #######

class ApiNavigator():
    """Parent class for API Navigator"""

    @staticmethod
    def generate_global_values():
        """Populate the level attributes to display the panel buttons and the documentation"""
        global tree_level, current_module, module_type, return_report, last_text
        prefs = bpy.context.preferences.addons['weed'].preferences

        try:
            text = bpy.context.space_data.text
            if text:
                if text.name != 'api_doc_':
                    last_text = bpy.context.space_data.text.name
                elif bpy.data.texts.__len__() < 2:
                    last_text = None
            else:
                last_text = None
        except:
            pass
        prefs.anp_pages = 0
        get_root_module(prefs.anp_path)
        current_module = evaluate(prefs.anp_path)
        module_type = str(type(current_module))
        return_report = str(current_module)
        tree_level = get_tree_level()

        if tree_level.__len__() > 30:
            global too_long
            too_long = True
        else:
            too_long = False

        ApiNavigator.generate_api_doc()
        return {'FINISHED'}

    @staticmethod
    def generate_api_doc():
        """Format the doc string for API Navigator"""
        global current_module, api_doc_, return_report, module_type
        prefs = bpy.context.preferences.addons['weed'].preferences
        path = prefs.anp_path
        doc = current_module.__doc__

        api_doc_ = "Module: %s\nType: %s\nReturn: %s\n%s\n%s" % \
                   (path, module_type, return_report, '_'*120, str(doc))
        return {'FINISHED'}


############   Operators   ############


def api_update(context):
    prefs = bpy.context.preferences.addons['weed'].preferences
    if prefs.anp_path != prefs.anp_old_path:
        fill_filter_mem()
        prefs.anp_old_path = prefs.anp_path
        update_filter()
        ApiNavigator.generate_global_values()


class Update(ApiNavigator, bpy.types.Operator):
    """Update the tree structure"""
    bl_idname = "weed.api_navigator_update"
    bl_label = "API Navigator Update"

    def execute(self, context):
        api_update(context)
        return {'FINISHED'}


class BackToBpy(ApiNavigator, bpy.types.Operator):
    """go back to module bpy"""
    bl_idname = "weed.api_navigator_back_to_bpy"
    bl_label = "Back to bpy"

    def execute(self, context):
        fill_filter_mem()
        prefs = bpy.context.preferences.addons['weed'].preferences

        if not prefs.anp_path:
            prefs.anp_old_path = prefs.anp_path = 'bpy'
        else:
            prefs.anp_old_path = prefs.anp_path = 'bpy'
        update_filter()
        self.generate_global_values()
        return {'FINISHED'}


class Down(ApiNavigator, bpy.types.Operator):
    """go to this Module"""
    bl_idname = "weed.api_navigator_down"
    bl_label = "API Navigator Down"
    pointed_module: bpy.props.StringProperty(name='Current Module', default='')

    def execute(self, context):
        fill_filter_mem()
        prefs = bpy.context.preferences.addons['weed'].preferences

        if not prefs.anp_path:
            prefs.anp_old_path = prefs.anp_path = prefs.anp_path + self.pointed_module
        else:
            prefs.anp_old_path = prefs.anp_path = prefs.anp_path + '.' + self.pointed_module

        update_filter()
        self.generate_global_values()
        return {'FINISHED'}


class Parent(ApiNavigator, bpy.types.Operator):
    """go to Parent Module"""
    bl_idname = "weed.api_navigator_parent"
    bl_label = "API Navigator Parent"

    def execute(self, context):
        prefs = bpy.context.preferences.addons['weed'].preferences
        path = prefs.anp_path

        if path:
            fill_filter_mem()
            prefs.anp_old_path = prefs.anp_path = parent(prefs.anp_path)
            update_filter()
            self.generate_global_values()
        return {'FINISHED'}


class Subscript(ApiNavigator, bpy.types.Operator):
    """Subscript to this Item"""
    bl_idname = "weed.api_navigator_subscript"
    bl_label = "API Navigator Subscript"
    subscription: bpy.props.StringProperty(name='', default='')

    def execute(self, context):
        fill_filter_mem()
        prefs = bpy.context.preferences.addons['weed'].preferences
        prefs.anp_old_path = prefs.anp_path = prefs.anp_path + '[' + self.subscription + ']'
        update_filter()
        self.generate_global_values()
        return {'FINISHED'}


class ClearFilter(ApiNavigator, bpy.types.Operator):
    """Clear the filter"""
    bl_idname = 'weed.api_navigator_clear_filter'
    bl_label = 'API Nav clear filter'

    def execute(self, context):
        prefs = bpy.context.preferences.addons['weed'].preferences
        prefs.anp_filter = ''
        return {'FINISHED'}


############ UI Classes ############

class SelectModule(ApiNavigator, bpy.types.Menu):
    """Pick a sub-module"""
    bl_idname = 'weed.api_navigator_select_module_menu'
    bl_label = 'Select Module for API'
    bl_options = {'REGISTER', 'UNDO'}

    menu_buttons = {
        0 : "col.operator('weed.api_navigator_subscript', text=str(obj)[:30],\
             emboss=True).subscription = '\"' + obj + '\"'",
        1 : "col.operator('weed.api_navigator_subscript', text=str(obj)[:30],\
             emboss=True).subscription = str(i)",
        8 : "col.label(text=obj[:30])"
    }

    def draw(self, context):
        global tree_level, current_module, module_type, return_report
        prefs = bpy.context.preferences.addons['weed'].preferences
        layout = self.layout
        text_filter = prefs.anp_filter
        split = layout.split()
        count = 0
        menu_cols = 0
        for i, obj in enumerate(tree_level[context.module.level]):
            if text_filter and text_filter.lower() not in str(obj).lower():
                continue
            if count % 20 == 0 and menu_cols < 4:
                col = split.column(align=True)
                menu_cols += 1
            exec(self.menu_buttons.get(context.module.level,
                 "col.operator('weed.api_navigator_down', text=obj[:30],\
                  emboss=True).pointed_module = obj"))
            count += 1


class PopupApiNavigator(ApiNavigator, bpy.types.Operator):
    """browse your API"""
    bl_idname = 'weed.popup_api_navigator'
    bl_label = 'Popup Api Navigator'
    bl_description = 'Show api navigator in a popup'
    bl_options = {'REGISTER', 'UNDO'}

    def __init__(self):
        prefs = bpy.context.preferences.addons['weed'].preferences
        modules_types = [
            (0, "Items", "DOTSDOWN"),
            (1, "Item Values", "DOTSDOWN"),
            (2, "Modules", "PACKAGE"),
            (3, "Types", "WORDWRAP_ON"),
            (4, "Properties", "BUTS"),
            (5, "Structs and Functions", "OOPS"),
            (6, "Methods and Functions", "SCRIPTWIN"),
            (7, "Attributes", "INFO"),
            (8, "Inaccessible", "ERROR")
        ]
        prefs.submodules.clear()
        for level, name, icon in modules_types:
            module = prefs.submodules.add()
            module.level = level
            module.name = name
            module.icon = icon


    def draw(self, context):
        global tree_level, current_module, module_type, return_report, api_doc_
        prefs = bpy.context.preferences.addons['weed'].preferences

        layout = self.layout
        box = layout.box()
        split = box.split(factor=0.7)
        split.prop(prefs, 'anp_path', text='', icon='OOPS')
        row = split.row(align=True)
        row.operator('weed.api_navigator_parent',
                       text='parent', icon='FILE_PARENT')
        row.operator('weed.api_navigator_back_to_bpy',
                       text='back to bpy', icon='BACK')

        split = box.split(factor=0.85)
        row = split.row(align=True)
        for module in prefs.submodules:
            if tree_level[module.level].__len__():
                row.context_pointer_set("module", module)
                row.menu('weed.api_navigator_select_module_menu',
                         text=module.name,
                         icon=module.icon)
        row = split.row(align=True)
        row.prop(prefs, 'anp_filter', text='')
        row.operator('weed.api_navigator_clear_filter', text='', icon='PANEL_CLOSE')

        col = layout.column(align=True)
        try:
            for line in api_doc_.splitlines():
                col.label(text=line)
        except:
            col.label(text='Empty:::')

    def check(self, context):
        return True

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        api_update(context)
        return context.window_manager.invoke_props_dialog(self, width=700)


## registro automatico de modulos.

#def register():
#    bpy.utils.register_class(Update)
#    bpy.utils.register_class(BackToBpy)
#    bpy.utils.register_class(Down)
#    bpy.utils.register_class(Parent)
#    bpy.utils.register_class(Subscript)
#    bpy.utils.register_class(ClearFilter)
#    bpy.utils.register_class(SelectModule)
#    bpy.utils.register_class(PopupApiNavigator)


#def unregister():
#    bpy.utils.unregister_class(PopupApiNavigator)
#    bpy.utils.unregister_class(SelectModule)
#    bpy.utils.unregister_class(ClearFilter)
#    bpy.utils.unregister_class(Subscript)
#    bpy.utils.unregister_class(Parent)
#    bpy.utils.unregister_class(Down)
#    bpy.utils.unregister_class(BackToBpy)
#    bpy.utils.unregister_class(Update)


#if __name__ == '__main__':
#    register()

##unregister()
