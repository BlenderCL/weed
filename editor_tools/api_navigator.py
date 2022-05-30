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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

# bl_info = {
#     "name": "API Navigator",
#     "author": "Dany Lebel (Axon_D)",
#     "version": (1, 0, 2),
#     "blender": (2, 57, 0),
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
from bpy.props import *

############ Global Variables ############

last_text = None  # last text data block

root_module = None  # root module of the tree

root_m_path = ''  # root_module + path as a string

current_module = None  # the object itself in the tree structure

tree_level = None  # the list of objects from the current_module

api_doc_ = ''  # the documentation formated for the API Navigator

module_type = None  # the type of current_module

return_report = ''  # what current_module returns

filter_mem = {}  # remember last filters entered for each path

too_long = False  # is tree_level list too long to display in a panel?

prev_filter = ''

prev_path = ''


def init_tree_level():
    global tree_level
    tree_level = [[], [], [], [], [], [], [], [], []]

init_tree_level()


# get preferences caller function
def get_prefs():
    return bpy.context.preferences.addons['weed'].preferences.api_navigator


class ApiNavModule(bpy.types.PropertyGroup):
    level: IntProperty()
    name: StringProperty()
    icon: StringProperty()


class Preferences(bpy.types.PropertyGroup):

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

    submodules: CollectionProperty(type=ApiNavModule)


############   Functions   ############

def get_root_module(path):
    # self.report({'DEBUG'}, 'get_root_module')
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
    # self.report({'DEBUG'}, 'evaluate')
    global root_module, tree_level, root_m_path

    try:
        len_name = root_module.__name__.__len__()
        root_m_path = 'root_module' + module[len_name:]
        current_module = eval(root_m_path)
        return current_module
    except:
        init_tree_level()
        return None



def get_tree_level():
    api_nav = get_prefs()
    def object_list():
        # self.report({'DEBUG'}, 'object_list')
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

    if not api_nav.path:
        return [[], [], [i for i in get_root_modules()], [], [], [], [], [], []]
    return object_list()


def parent(path):
    """Returns the parent path"""
    # self.report({'DEBUG'}, 'parent')

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
    api_nav = get_prefs()
    try:
        api_nav.api_filter = filter_mem[api_nav.path]
    except:
        api_nav.api_filter = ''


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
    api_nav = get_prefs()
    if api_nav.api_filter:
        filter_mem[api_nav.old_path] = api_nav.api_filter
    else:
        filter_mem.pop(api_nav.old_path, None)


######  API Navigator parent class  #######

class ApiNavigator():
    """Parent class for API Navigator"""

    @staticmethod
    def generate_global_values():
        """Populate the level attributes to display the panel buttons and the documentation"""
        global tree_level, current_module, module_type, return_report, last_text
        api_nav = get_prefs()

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
        api_nav.pages = 0
        get_root_module(api_nav.path)
        current_module = evaluate(api_nav.path)
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
        api_nav = get_prefs()

        api_doc_ = "Module: %s\nType: %s\nReturn: %s\n%s\n%s" % \
                   (api_nav.path, 
                   module_type, 
                   return_report, 
                   '_'*120, 
                   str(current_module.__doc__))
        return {'FINISHED'}


############   Operators   ############


def api_update(context):
    api_nav = get_prefs()
    if api_nav.path != api_nav.old_path:
        fill_filter_mem()
        api_nav.old_path = api_nav.path
        update_filter()
        ApiNavigator.generate_global_values()


class WEED_OT_api_nav_update(ApiNavigator, bpy.types.Operator):
    """Update the tree structure"""
    bl_idname = "weed.api_nav_update"
    bl_label = "API Navigator Update"

    def execute(self, context):
        api_update(context)
        return {'FINISHED'}


class WEED_OT_api_nav_back_to_bpy(ApiNavigator, bpy.types.Operator):
    """go back to module bpy"""
    bl_idname = "weed.api_nav_back_to_bpy"
    bl_label = "Back to bpy"

    def execute(self, context):
        fill_filter_mem()
        api_nav = get_prefs()

        api_nav.old_path = api_nav.path = 'bpy'
        # if not api_nav.path:
        #     api_nav.old_path = api_nav.path = 'bpy'
        # else:
        #     api_nav.old_path = api_nav.path = 'bpy'
        update_filter()
        self.generate_global_values()
        return {'FINISHED'}


class WEED_OT_api_nav_down(ApiNavigator, bpy.types.Operator):
    """go to this Module"""
    bl_idname = "weed.api_nav_down"
    bl_label = "API Navigator Down"
    pointed_module: StringProperty(name='Current Module', default='')

    def execute(self, context):
        fill_filter_mem()
        api_nav = get_prefs()

        if not api_nav.path:
            api_nav.old_path = api_nav.path = api_nav.path + self.pointed_module
        else:
            api_nav.old_path = api_nav.path = api_nav.path + '.' + self.pointed_module

        update_filter()
        self.generate_global_values()
        return {'FINISHED'}


class WEED_OT_api_nav_parent(ApiNavigator, bpy.types.Operator):
    """go to Parent Module"""
    bl_idname = "weed.api_nav_parent"
    bl_label = "API Navigator Parent"

    def execute(self, context):
        api_nav = get_prefs()

        if api_nav.path:
            fill_filter_mem()
            api_nav.old_path = api_nav.path = parent(api_nav.path)
            update_filter()
            self.generate_global_values()
        return {'FINISHED'}


class WEED_OT_api_nav_subscript(ApiNavigator, bpy.types.Operator):
    """Subscript to this Item"""
    bl_idname = "weed.api_nav_subscript"
    bl_label = "API Navigator Subscript"
    subscription: StringProperty(name='', default='')

    def execute(self, context):
        fill_filter_mem()
        api_nav = get_prefs()

        api_nav.old_path = api_nav.path = api_nav.path + '[' + self.subscription + ']'
        update_filter()
        self.generate_global_values()
        return {'FINISHED'}

class WEED_OT_api_nav_clear_filter(ApiNavigator, bpy.types.Operator):
    """Clear the filter"""
    bl_idname = 'weed.api_nav_clear_filter'
    bl_label = 'API Nav clear filter'

    def execute(self, context):
        api_nav = get_prefs()
        api_nav.api_filter = ''
        return {'FINISHED'}


############ UI Classes ############

class WEED_MT_api_nav_select_module(ApiNavigator, bpy.types.Menu):
    """Pick a sub-module"""
    bl_idname = 'WEED_MT_api_nav_select_module'
    bl_label = 'Select Module for API'
    bl_options = {'REGISTER', 'UNDO'}

    menu_buttons = {
        0 : "col.operator('weed.api_nav_subscript', text=str(obj)[:30],\
             emboss=True).subscription = '\"' + obj + '\"'",
        1 : "col.operator('weed.api_nav_subscript', text=str(obj)[:30],\
             emboss=True).subscription = str(i)",
        8 : "col.label(text=obj[:30])"
    }

    @classmethod
    def poll(cls, context):
        return context.preferences.addons.get('weed')

    def draw(self, context):
        global tree_level, current_module, module_type, return_report
        api_nav = get_prefs()

        layout = self.layout
        text_filter = api_nav.api_filter
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
                 "col.operator('weed.api_nav_down', text=obj[:30],\
                  emboss=True).pointed_module = obj"))
            count += 1


class WEED_OT_api_nav_popup(ApiNavigator, bpy.types.Operator):
    """browse your API"""
    bl_idname = 'weed.api_nav_popup'
    bl_label = 'Popup Api Navigator'
    bl_description = 'Show api navigator in a popup'
    bl_options = {'REGISTER', 'UNDO'}

    def __init__(self):
        api_nav = get_prefs()
        if len(api_nav.submodules):
            return
        modules_types = [
            (0, "Items", "PRESET"),
            (1, "Item Values", "PRESET"),
            (2, "Modules", "PACKAGE"),
            (3, "Types", "WORDWRAP_ON"),
            (4, "Properties", "PROPERTIES"),
            (5, "Structs and Functions", "OUTLINER"),
            (6, "Methods and Functions", "PREFERENCES"),
            (7, "Attributes", "INFO"),
            (8, "Inaccessible", "ERROR")
        ]
        for level, name, icon in modules_types:
            module = api_nav.submodules.add()
            module.level = level
            module.name = name
            module.icon = icon

    # @classmethod
    # def poll(cls, context):
    #     return context.preferences.addons.get('weed')

    def draw(self, context):
        global tree_level, current_module, module_type, return_report, api_doc_
        api_nav = get_prefs()

        layout = self.layout
        box = layout.box()
        split = box.split(factor=0.7)
        split.prop(api_nav, 'path', text='', icon='OUTLINER')
        row = split.row(align=True)
        row.operator('weed.api_nav_parent',
                       text='parent', icon='FILE_PARENT')
        row.operator('weed.api_nav_back_to_bpy',
                       text='back to bpy', icon='BACK')

        split = box.split(factor=0.85)
        row = split.row(align=True)
        for module in api_nav.submodules:
            if tree_level[module.level].__len__():
                row.context_pointer_set("module", module)
                row.menu('WEED_MT_api_nav_select_module',
                         text=module.name,
                         icon=module.icon)
        row = split.row(align=True)
        row.prop(api_nav, 'api_filter', text='')
        row.operator('weed.api_nav_clear_filter', text='', icon='PANEL_CLOSE')

        col = layout.column(align=True)
        try:
            for line in api_doc_.splitlines():
                col.label(text=line)
        except:
            col.label(text='Empty:::')
        layout.separator()

    def check(self, context):
        return True

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        api_update(context)
        return context.window_manager.invoke_props_dialog(self, width=700)

def api_menu(self, context):
    layout = self.layout
    layout.operator_context = 'INVOKE_DEFAULT'
    layout.operator('weed.api_nav_popup',
                    text='API navigator',
                    icon='ASSET_MANAGER')
    # layout.separator()


prefs_classes = (
    ApiNavModule,
    Preferences
)

classes = (
    WEED_MT_api_nav_select_module,
    WEED_OT_api_nav_parent,
    WEED_OT_api_nav_update,
    WEED_OT_api_nav_back_to_bpy,
    WEED_OT_api_nav_down,
    WEED_OT_api_nav_subscript,
    WEED_OT_api_nav_clear_filter,
    WEED_OT_api_nav_popup
)

# registro explicito de modulos.
# con **kwargs para registrar o no las preferencias
def register(prefs=True):
    if prefs:
        for cls in prefs_classes:
            try:
                bpy.utils.unregister_class(cls)
            except:
                pass
                #self.report({'DEBUG'}, f'{cls} already unregistered')
            bpy.utils.register_class(cls)

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TEXT_MT_view.append(api_menu)
    bpy.types.TEXT_MT_context_menu.append(api_menu)
    bpy.types.TEXT_HT_footer.append(api_menu)

def unregister(prefs=True):
    bpy.types.TEXT_HT_footer.remove(api_menu)
    bpy.types.TEXT_MT_context_menu.remove(api_menu)
    bpy.types.TEXT_MT_view.remove(api_menu)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    if prefs:
        for cls in reversed(prefs_classes):
            bpy.utils.unregister_class(cls)


