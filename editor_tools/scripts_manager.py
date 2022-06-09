import bpy
import os
import sys
import zipfile
import importlib
import subprocess
import addon_utils
# from bpy.props import *
from bpy.props import (BoolProperty, StringProperty, IntProperty,
                       EnumProperty, CollectionProperty)
from os import listdir, sep
from os.path import isfile, isdir, join, split, dirname, basename, exists, abspath
from shutil import rmtree
from collections import defaultdict
from bpy.app.handlers import persistent
from . text_block import TextBlock
from weed import _icon_types
from site import getsitepackages, getusersitepackages

ignore_names = ["__pycache__", ".git", ".gitignore"]

textchars = bytearray({7, 8, 9, 10, 12, 13, 27} 
                      | set(range(0x20, 0x100)) - {0x7f})

is_setting = False

addons_path = bpy.utils.user_resource('SCRIPTS', path='addons')

directory_visibility = defaultdict(bool)
# code_visibility = defaultdict(bool)

new_addon_type_items = [
    ("BASIC", "Basic", ""),
    ("MULTIFILE", "Multi-File (recommended)", "") ]


# file functions
def get_file_names(directory):
    try:
        dirs = sorted([file_name for file_name in listdir(directory)
                       if isfile(join(directory, file_name))
                       and file_name not in ignore_names])
        if not get_prefs().show_dot_files:
            dirs = [file_name for file_name in dirs
                    if file_name[0] != '.']
        return dirs
    except:
        return []

def is_binary_file(filepath):
    try:
        bytes = open(filepath, 'rb').read(512)
        return bool(bytes.translate(None, textchars))
    except:
        return False

def correct_file_name(name, is_directory = False):
    new_name = ""
    for char in name:
        if char.isupper():
            new_name += char.lower()
        elif char.islower() or char == "_":
            new_name += char
        elif char == " ":
            new_name += "_"
        elif char.isdigit() and len(new_name) > 0:
            new_name += char
        elif not is_directory and char == "." and new_name.count(".") == 0:
            new_name += char
    return new_name


# file name handlers
def get_file_name_handler(self):
    try: return self["file_name_internal"]
    except: return ""

def set_file_name_handler(self, value):
    global is_setting
    if not is_setting:
        is_setting = True
        self["file_name_internal"] = correct_file_name(value, is_directory = False)
        is_setting = False


# directory functions
def get_directory_names(directory):
    try:
        dirs = sorted([file_name for file_name in listdir(directory)
                       if not isfile(join(directory, file_name))
                       and file_name not in ignore_names])
        if not get_prefs().show_dot_files:
            dirs = [file_name for file_name in dirs
                    if file_name[0] != '.']
        return dirs
    except:
        return []

def get_addons_names(directory):
    addons = sorted([file_name for file_name in listdir(directory)
                    if file_name not in ignore_names
                    and (not isfile(join(directory, file_name))
                    or isfile(join(directory, file_name))
                    and file_name[-3:] == '.py')])
    if not get_prefs().show_dot_addons:
        addons = [file_name for file_name in addons
                if file_name[0] != '.']
    return addons


# directory name handlers
def get_directory_name_handler(self):
    try: return self["directory_name_internal"]
    except: return ""

def set_directory_name_handler(self, value):
    global is_setting
    if not is_setting:
        is_setting = True
        self["directory_name_internal"] = correct_file_name(value, is_directory = True)
        is_setting = False


def get_folders_list(self, context):
    
    #list.append(('folder/path','ui_label','tooltip'))
    folder_list = []
    for addon in get_addons_names(addons_path):
        try:
            folder_list.append((join(addons_path, addon),
                        addon,
                        __import__(addon).bl_info['description']))
        except:
            folder_list.append((addon,
                        addon, 
                        'hidden or one file Addon'))
    return folder_list

def get_libs_folders_list(self, context):
    folder_list = []
    for folder in bpy.utils.script_paths(user_pref=False, use_user=False):
        folder_list.append((folder,
                     split(folder)[-1],
                     'Blender Internal Script Folder'))
    folder = getusersitepackages()                    # + sep
    folder_list.append((folder,
                'user ' + split(folder)[-1],
                "User 'site packages' Python libs"))
    for folder in getsitepackages():
        folder_list.append((folder,
                    'global ' + split(folder)[-1],
                    "Global 'site packages' Python libs"))
    return folder_list

def get_bookmarks_list(self, context):
    #breakpoint.here
    bookmarks = [(bkmrk.path, split(bkmrk.path)[-1], '')
                    for bkmrk in bpy.context.scene.bookmarks_paths.values()]
    if bookmarks:
        return bookmarks
    else:
        return [('None', 'Add bookmarks to select', '')]



# get preferences caller function
def get_prefs():
    return bpy.context.preferences.addons['weed'].preferences.scripts_manager


def update_prefs(self, context):
    #breakpoint.here
    if self.own_tab:
        bpy.types.WEED_PT_scripts_manager.bl_category = 'Scripts Manager'
    else:
        bpy.types.WEED_PT_scripts_manager.bl_category = 'Weed IDE'
    try:
        bpy.utils.unregister_class(WEED_PT_scripts_manager)
    except:
        pass
    try:
        bpy.utils.register_class(WEED_PT_scripts_manager)
    except:
        pass


def update_bkmrk_abspath(self, context):
#    if isdir(bpy.path.abspath(self.bkmrk_select)):
#        # self.bkmrk_select = bpy.path.abspath(self.bkmrk_select)
#        # self.bkmrk_select = abspath(self.bkmrk_select)
    #breakpoint.here
    if (self.bkmrk_select and
            self.bkmrk_select != 
            abspath(bpy.path.abspath(self.bkmrk_select))):
            
        self.bkmrk_select = abspath(bpy.path.abspath(self.bkmrk_select))


#def clean_bkmrk_select(self, context):
#    breakpoint.here
#    if self.bkmrk_add_tggl:
#        self.bkmrk_select = ''
##    if isdir(bpy.path.abspath(self.bkmrk_select)):
##        # self.bkmrk_select = bpy.path.abspath(self.bkmrk_select)
##        # self.bkmrk_select = abspath(self.bkmrk_select)
#    if self.bkmrk_select != abspath(bpy.path.abspath(self.bkmrk_select)):
#        self.bkmrk_select = abspath(bpy.path.abspath(self.bkmrk_select))


class Preferences(bpy.types.PropertyGroup):
    """Scripts Manager Preferences Panel"""
    bl_idname = __name__

    show_dot_files  : BoolProperty(name = 'Show hidden files',
                         default = False,
                         description = 'Show hidden files on addon files panel')
    show_dot_addons : BoolProperty(
                        name = 'Show dot Addons',
                        default = False,
                        description = 'Show hidden addons on addon files panel')
    addons_folder   : EnumProperty(
                        name = "Addon Select",
                        items = get_folders_list)
    libs_folder     : EnumProperty(
                        name = "Library folder select",
                        items = get_libs_folders_list)
    bkmrks_folder   : EnumProperty(
                        name = "Bookmark folder select",
                        description = "description here bkmrks_folder",
                        items = get_bookmarks_list)
    bkmrk_select    : StringProperty(
                    name = "bookmark",
                    default = "",
                    update = update_bkmrk_abspath,
                    subtype = 'DIR_PATH')
    bkmrk_add_tggl  : BoolProperty(
                    name = 'Add new bookmark',
                    default = False,
#                    update = clean_bkmrk_select, 
                    description = 'Add new bookmark after browse it')
    compact_views   : BoolProperty(
                    name = 'compacts views selector',
                    default = True,
                    description = 'compacts views selector in scripts manager')
    c_views_btns    : BoolProperty(
                    name = 'compacts views buttons',
                    default = False,
                    description = 'compacts views buttons style')

    manager_view    : EnumProperty(
                    name = 'Explore',
                    items = [
            ('blend', '.blend file folder', 'Browse current .blend file folder',
             'FILE_BLEND', 0),
            ('addons', 'Addons folder', 'Browse addons folder',
             'PLUGIN', 1),
            ('libraries', 'Libraries folder', 'Browse bundled addons and libraries',
             'ASSET_MANAGER', 2),
            ('current', 'Currently open files', 'Browse currently opened files',
             'DOCUMENTS', 3),
            ('bookmarks', 'Bookmarked folders', 'Browse bookmarked folders',
             'BOOKMARKS', 4)

        ],
        default='blend')

    alt_layout: bpy.props.BoolProperty(
        name="alternative layout", default=False,
        description="Alternative layout on Code Tree view ",
    )

    own_tab: bpy.props.BoolProperty(
        name="Own Tab", default=False,
        description="Show Code Tree tab on Text Editor Sidebar ",
        update=update_prefs
    )

#    @classmethod
#    def default_prefs(self):
#        #breakpoint.here
#        obj = lambda : None
#        for attr, val in self.__annotations__.items():
#            setattr(obj, attr, val[1]['default'])
#        return obj

    def draw(self, layout):
        #layout.use_property_split = True

        flow = layout.grid_flow(columns=2, even_columns=1)
        flow.prop(self, "own_tab", toggle=1)
        flow.prop(self, "alt_layout", toggle=1)
        
        flow.prop(self, "compact_views")
        # flow.label()
        flow.prop(self, "c_views_btns")
        # flow.prop(self, "on_footer")



class WEED_PT_scripts_manager(bpy.types.Panel):
    bl_idname = "WEED_PT_scripts_manager"
    bl_label = "Scripts Manager"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_category = "Weed IDE"
    #bl_options = {'HEADER_LAYOUT_EXPAND'}#, 'DRAW_BOX'}
    # bl_options = {'DRAW_BOX'}

    def __init__(self):
        #breakpoint.here
        self.manager_views = {
            'blend'     : self.draw_blend_folder_view,
            'addons'    : self.draw_addons_view,
            'libraries' : self.draw_libraries_view,
            'current'   : self.draw_current_files_view,
            'bookmarks' : self.draw_bookmarks_view
        }
        self.texts_paths = {}
        self.pref = get_prefs()

    @classmethod
    def poll(cls, context):
        return current_addon_exists()

    def draw(self, context):
        alt_layout = self.pref.alt_layout
        wm = context.window_manager

        self.texts_paths.clear()
        for text in bpy.data.texts:
            if text.is_in_memory:
                self.texts_paths['Text:Internal' + sep + text.name_full] = text 
            else:
                self.texts_paths[text.filepath] = text 
        
        header = self.layout if alt_layout else self.layout.box()
        split_sel = header.split(factor=0.4)
        split_sel.prop(self.pref, 'compact_views',
                            text = 'Browse:',
                            icon = 'DISCLOSURE_TRI_RIGHT' 
                                if self.pref.compact_views
                                else 'DISCLOSURE_TRI_DOWN',
                            emboss = False)
        if self.pref.compact_views:
            if self.pref.c_views_btns:
                row = split_sel.row()
                row.alignment = 'RIGHT'
                row.prop(self.pref, 'manager_view', text='', expand=True)
            else:
                col = split_sel.column()
                col.prop(self.pref, 'manager_view', text='')
        else:
            col = split_sel.column()
            col.prop(self.pref, 'manager_view', expand=True)
        self.layout.separator()
        self.manager_views.get(
            self.pref.manager_view)(self.layout.box() if
                alt_layout else self.layout
            )
        self.layout.separator()

    def draw_blend_folder_view(self, layout):
        blend_path = bpy.path.abspath('//').rstrip(sep)

        split_box = layout.split(factor=0.07)
        split_box.label()
        box = split_box.box()
        box.alignment = 'RIGHT'
        box.scale_y = 0.5
        box.active = False
        if not blend_path:
            box.label(text='current blend file', icon='ERROR')
            box.label(text='are not saved yet')
        else:
            box.label(text='files next to...', icon='DOCUMENTS')
            box.label(text=bpy.data.filepath.split(sep)[-1])
            layout.separator()
            self.draw_directory(layout, blend_path + sep)
        layout.separator()
        
    def draw_addons_view(self, layout):
        # pref = get_prefs()
        selector = layout.row(align=True)
        selector.prop(self.pref, 'addons_folder', text='addon')
        selector.operator('weed.py_mngr_open_addon_menu',
                          icon='COLLAPSEMENU', text='')
        layout.separator()
        addon_path = get_current_addon_path()
        if isfile(addon_path):
            directory, file_name = split(addon_path)
            self.draw_element(layout, directory + sep, file_name)
        else:
            self.draw_directory(layout, addon_path)

    def draw_libraries_view(self, layout):
        # pref = get_prefs()
        layout.prop(self.pref, 'libs_folder', text='lib folder')
        split_box = layout.split(factor=0.07)
        split_box.label()
        box = split_box.box()
        box.alignment = 'RIGHT'
        box.scale_y = 0.5
        box.active = False
        box.label(text='avoid modify files here,', icon='ERROR')
        box.label(text='use them as a reference')
        layout.separator()
        self.draw_directory(layout, self.pref.libs_folder + sep)
        layout.separator()

    def draw_current_files_view(self, layout):
        if not bpy.data.texts:
            split_box = layout.split(factor=0.05)
            split_box.label()
            box = split_box.box()
            box.alignment = 'RIGHT'
            box.scale_y = 0.5
            box.active = False
            box.label(text='no open files', icon='ERROR')
            box.label(text='in Text Editor')
            layout.separator()
            return None

        layout.label(text='current open files:')
        layout.separator()
        for curr_text in bpy.data.texts:
            if curr_text.is_in_memory:
                directory, file_name = 'Text:Internal', curr_text.name_full
            else:
                directory, file_name = split(curr_text.filepath)
            self.draw_element(layout, directory + sep, file_name, filepath_hint=True)
        layout.separator()
            
    def draw_bookmarks_view(self, layout):
        row_add = layout.row(align=True)
        row_add.alignment = 'RIGHT'
        if self.pref.bkmrk_add_tggl:
            row_add.alignment = 'EXPAND'
            row_ok = row_add.row(align=True)
            add_bkmrk = row_ok.operator('weed.py_mngr_add_bookmark',
                                      icon='CHECKMARK', text='')
            row_ok.enabled = isdir(self.pref.bkmrk_select)
            add_bkmrk.path = self.pref.bkmrk_select
            browse_path = row_add.prop(self.pref, 'bkmrk_select', text='')
        else:
            row_add.label(text='add bookmark:')
        row_add.prop(self.pref, 'bkmrk_add_tggl', text='', icon='ADD')

        # if there are no bookmarks
        if not bpy.context.scene.bookmarks_paths:
            split_box = layout.split(factor=0.05)
            split_box.label()
            box = split_box.box()
            box.label(text="there are no", icon='ERROR')
            box.label(text='bookmarks yet')
            #box.separator()
            box.scale_y = 0.5
            box.active = False
            return None

        # Draw bookmarks list
        for bkmrk in bpy.context.scene.bookmarks_paths.values():
            
            #bkmrk_element = layout
            # if current bookmark is active bookmark
            if bkmrk.path == self.pref.bkmrks_folder:
                bkmrk_element = layout.box().row(align=True)
                selector = bkmrk_element.column(align=True)
                self.draw_directory(selector, self.pref.bkmrks_folder + sep)
                split_hint = selector.column(align=True)
                #split_hint.label(text='')
                split_hint.label(text=bkmrk.path)
                split_hint.active = False
                split_hint.scale_y = 0.7
                split_hint.scale_x = 0.7
                rmv_bkmrk = bkmrk_element.operator('weed.py_mngr_remove_bookmark',
                                            icon='PANEL_CLOSE', text='',
                                            emboss = False)
                rmv_bkmrk.path = bkmrk.path
            
            # other bookmarks    
            else:
                bkmrk_element = layout.row(align=True)
                selector = bkmrk_element.column(align=True)
                selector.alignment = "LEFT"
                brws_bkmrk = selector.operator('weed.py_mngr_browse_bookmark',
                                          icon='BOOKMARKS',
                                          text=split(bkmrk.path)[-1],
                                          emboss = False)
                brws_bkmrk.path = bkmrk.path                          
                bkmrk_element.label(text='', icon='NONE')
                rmv_bkmrk = bkmrk_element.operator('weed.py_mngr_remove_bookmark',
                                            icon='PANEL_CLOSE', text='',
                                            emboss = False)
                rmv_bkmrk.path = bkmrk.path


        layout.separator()



    def draw_directory(self, layout, directory):
        element = layout.row(align=True)    # layout.split(factor=0.9)
        dir_op = element.row(align=True)
        dir_op.alignment = "LEFT"

        if not self.is_directory_visible(directory):
            op = dir_op.operator("weed.py_mngr_toogle_directory_visibility",
                                 text = split(directory[:-1])[-1],
                                 icon = "FILE_FOLDER",
                                 emboss = False)
            op.directory = directory
        else:
            op = dir_op.operator("weed.py_mngr_toogle_directory_visibility",
                                text = split(directory[:-1])[-1],
                                icon = "FOLDER_REDIRECT",
                                emboss = False)
            op.directory = directory
            element.label(text='', icon = 'NONE')
            op = element.operator("weed.py_mngr_open_dir_menu",
                              icon = "COLLAPSEMENU",
                              text = "",
                              emboss = False)
            op.directory = directory


            directory_names = get_directory_names(directory)
            split_lyt = layout.split(factor=0.04)
            split_lyt.label(text='')
            col = split_lyt.column(align=True)
            col.alignment = "LEFT"
            #row = col.row(align=True)
            #row.alignment = "LEFT"

            for directory_name in directory_names:
                self.draw_directory(col, directory + directory_name + sep)

            file_names = get_file_names(directory)
            for file_name in file_names:
                self.draw_element(col, directory, file_name)


    def draw_element(self, layout, directory, file_name, filepath_hint=False):
        full_path = directory + file_name
        internal = (directory == 'Text:Internal' + sep)
        if internal:
            icon_type = 'MEMORY'
            if file_name == bpy.context.space_data.text.name_full:
                layout = layout.box()
            else:
                filepath_hint = False
        elif full_path == get_current_filepath():
            icon_type = 'STYLUS_PRESSURE'
            layout = layout.box()
        else:
            icon_type = _icon_types.get(file_name.split('.')[-1].lower(), 'FILE')
            filepath_hint = False

        split_lyt = layout.row(align=True)
        row = split_lyt.row(align=True)
        row.alignment = "LEFT"
        op = row.operator("weed.py_mngr_open_file",
                          icon = icon_type,
                          text = file_name,
                          emboss = False)
        op.path = full_path
        row.enabled = not is_binary_file(full_path)
        split_lyt.label(text='', icon = 'NONE')
            
        if full_path in self.texts_paths:
            if not internal and self.texts_paths[full_path].is_dirty:
                operator = 'weed.py_mngr_close_file_menu'
                icon_type = 'GREASEPENCIL'
            else:
                operator = 'weed.py_mngr_close_file'
                icon_type = 'CANCEL'
            if self.texts_paths[full_path].is_modified:
                row = split_lyt.row(align=True)
                row.alert = True
                row.enabled = full_path == get_current_filepath()
                row.operator("text.resolve_conflict", text="", icon='HELP')
                
        else:
            operator = 'weed.py_mngr_open_file_menu'
            icon_type = 'LAYER_USED'

        props = split_lyt.operator(operator,
                                   text = '',
                                   icon = icon_type,
                                   emboss = False)
        props.path = full_path
        if operator == 'weed.py_mngr_close_file':
            props.save_it = False
            props.close_it = True
        
        if filepath_hint:
            hint_row = layout.column()
            # hint_row = layout.split(factor=0.9)
            hint_row.label(text=directory)
            hint_row.alignment = 'RIGHT'
            hint_row.use_property_split = False
            hint_row.active = False
            hint_row.scale_y = 0.7
            hint_row.scale_x = 0.7


    def is_directory_visible(self, directory):
        return directory_visibility[directory]

    # def is_code_visible(self, code):
    #     return code_visibility[code]


class WEED_OT_py_mngr_MakeAddonNameValid(bpy.types.Operator):
    bl_idname = "weed.py_mngr_make_addon_name_valid"
    bl_label = "Make Name Valid"
    bl_description = "Make the addon name a valid module name"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return not current_addon_exists() and not is_addon_name_valid()

    def execute(self, context):
        name = get_addon_name()
        addon_name = correct_file_name(name, is_directory = True)
        return {"FINISHED"}


class WEED_OT_py_mngr_CreateNewAddon(bpy.types.Operator):
    bl_idname = "weed.py_mngr_new_addon"
    bl_label = "New Addon"
    bl_description = "Create an addon in addons folder and setup a basic code base"
    bl_options = {"REGISTER"}

    new_addon_type : EnumProperty(default = "BASIC", items = new_addon_type_items)
    name : StringProperty(name = "New Addon Name", default = "")#, set = set_file_name_handler, get = get_file_name_handler)

    #@classmethod
    #def poll(cls, context):
    #    return not current_addon_exists() and is_addon_name_valid()

    def execute(self, context):
        #bpy.context.scene.addon_development = self.name
        #if not current_addon_exists() and is_addon_name_valid():
        if self.name not in bpy.context.scene.addon_development:
            print('create')
            self.create_addon_directory()
            bpy.context.scene.addon_development = self.name
            self.generate_from_template()
            addon_path = get_current_addon_path()
            bpy.ops.weed.py_mngr_open_file(path = addon_path + "__init__.py")
            make_directory_visible(addon_path)
            context.area.tag_redraw()
        else:
            print('ya existe')
        return {"FINISHED"}

    def create_addon_directory(self):
        os.makedirs(join(addons_path, self.name))

    def generate_from_template(self):
        t = self.new_addon_type
        if t == "BASIC":
            code = code = self.read_template_file("basic.txt")
            new_addon_file("__init__.py", code)

        if t == "MULTIFILE":
            code = self.read_template_file("multifile.txt")
            new_addon_file("__init__.py", code)
            code = self.read_template_file("developer_utils.txt")
            new_addon_file("developer_utils.py", code)

    def read_template_file(self, path):
        path = join(dirname(__file__), "addon_templates", path)
        file = open(path)
        text = file.read()
        file.close()
        return text

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 400)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'name')
        #layout.prop(self, 'new_addon_type')



class WEED_OT_py_mngr_RenameAddon(bpy.types.Operator):
    bl_idname = "weed.py_mngr_rename_addon"
    bl_label = "Rename Addon"
    bl_description = "Rename the current Addon"
    bl_options = {"REGISTER"}

    name : StringProperty(name = "New Addon Name", default = "")#, set = set_file_name_handler, get = get_file_name_handler)

    #@classmethod
    #def poll(cls, context):
    #    return not current_addon_exists() and is_addon_name_valid()

    def execute(self, context):
        if self.name not in os.listdir(addons_path):
            src_addon_path = get_current_addon_path()
            dst_addon_path = join(addons_path, self.name) + sep
            os.replace(src_addon_path, dst_addon_path)
            bpy.context.scene.addon_development = self.name
            for text in bpy.data.texts:
                if src_addon_path in text.filepath:
                    text.filepath = text.filepath.replace(
                                          src_addon_path, dst_addon_path)
            try:
                bpy.ops.text.resolve_conflict(resolution="IGNORE")
            except:
                #self.report({'INFO'}, 'destination already exist')
                pass
            context.area.tag_redraw()
        return {"FINISHED"}

    def create_addon_directory(self):
        os.makedirs(join(addons_path, self.name))

    def generate_from_template(self):
        t = self.new_addon_type
        if t == "BASIC":
            code = code = self.read_template_file("basic.txt")
            new_addon_file("__init__.py", code)

        if t == "MULTIFILE":
            code = self.read_template_file("multifile.txt")
            new_addon_file("__init__.py", code)
            code = self.read_template_file("developer_utils.txt")
            new_addon_file("developer_utils.py", code)

    def read_template_file(self, path):
        path = join(dirname(__file__), "addon_templates", path)
        file = open(path)
        text = file.read()
        file.close()
        return text

    def invoke(self, context, event):
        self.name = bpy.context.scene.addon_development
        return context.window_manager.invoke_props_dialog(self, width = 400)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'name')


class WEED_OT_py_mngr_DeleteAddon(bpy.types.Operator):
    bl_idname = "weed.py_mngr_delete_addon"
    bl_label = "Delete Addon"
    bl_description = "Delete the current Addon"
    bl_options = {"REGISTER"}

    #@classmethod
    #def poll(cls, context):
    #    return not current_addon_exists() and is_addon_name_valid()

    def execute(self, context):
        addon = get_current_addon_path()
        for text in bpy.data.texts:
            if addon in text.filepath:
                bpy.context.space_data.text = text
                bpy.ops.text.unlink()
        rmtree(addon, ignore_errors=True, onerror=None)
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    #def draw(self, context):
    #    layout = self.layout
    #    layout.prop(self, 'name')
        #layout.prop(self, 'new_addon_type')


class WEED_OT_py_mngr_NewFile(bpy.types.Operator):
    bl_idname = "weed.py_mngr_new_file"
    bl_label = "New File"
    bl_description = "Create a new file in this directory"
    bl_options = {"REGISTER"}

    directory : StringProperty(name = "Directory", default = "")
    name : StringProperty(name = "File Name", default = "", set = set_file_name_handler, get = get_file_name_handler)

    @classmethod
    def poll(cls, context):
        return current_addon_exists()

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 400)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "name")

    def execute(self, context):

        if self.name != "":
            path = self.directory + self.name
            new_file(path)
            bpy.ops.weed.py_mngr_open_file(path = path)
            context.area.tag_redraw()
        return {"FINISHED"}


class WEED_OT_py_mngr_NewDirectory(bpy.types.Operator):
    bl_idname = "weed.py_mngr_new_directory"
    bl_label = "New Directory"
    bl_description = "Create a new subdirectory"
    bl_options = {"REGISTER"}

    directory : StringProperty(name="Directory", default="")
    name : StringProperty(name="Directory Name", default="",
                          set=set_directory_name_handler,
                          get=get_directory_name_handler)

    @classmethod
    def poll(cls, context):
        return current_addon_exists()

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "name")

    def execute(self, context):
        if self.name != "":
            new_directory(self.directory + self.name)
            new_file(join(self.directory + self.name, "__init__.py"))
            context.area.tag_redraw()
        return {"FINISHED"}


class WEED_OT_py_mngr_RenameDirectory(bpy.types.Operator):
    bl_idname = "weed.py_mngr_rename_directory"
    bl_label = "Rename Directory"
    bl_description = "Rename current directory"
    bl_options = {"REGISTER"}

    base_dir : StringProperty(name="Base directory", default="")
    actual_name : StringProperty(name="Actual name", default="")
    new_name : StringProperty(name="New name", default="",
                          set=set_directory_name_handler,
                          get=get_directory_name_handler)

    @classmethod
    def poll(cls, context):
        return current_addon_exists()

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.label(text='current name is ' + self.actual_name)
        layout.prop(self, "new_name")

    def execute(self, context):
        if self.new_name not in os.listdir(self.base_dir):
            try:
                actual_path = join(self.base_dir, self.actual_name)
                new_path = join(self.base_dir, self.new_name)
                os.rename(actual_path, new_path)
            except:
                #self.report({'INFO'},'rename failed')
                pass
            else:
                for text in bpy.data.texts:
                    if actual_path in text.filepath:
                        text.filepath = text.filepath.replace(
                            actual_path, new_path)
                try:
                    bpy.ops.text.resolve_conflict(resolution="IGNORE")
                except:
                    #self.report({'INFO'},'text editor conflict on open files')
                    pass
            finally:
                context.area.tag_redraw()
        return {"FINISHED"}


class WEED_OT_py_mngr_DeleteDirectory(bpy.types.Operator):
    bl_idname = "weed.py_mngr_delete_directory"
    bl_label = "Do you really want to delete directory?"
    bl_description = "Delete current directory"
    bl_options = {"REGISTER"}

    directory : StringProperty(name="Directory", default="")

    @classmethod
    def poll(cls, context):
        return current_addon_exists()

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        if exists(self.directory):
            rmtree(self.directory, ignore_errors=True, onerror=None)
        context.area.tag_redraw()
        return {"FINISHED"}



##################################################################
# bookmarks operators

# class MyEnumItems(bpy.types.PropertyGroup):
#     @classmethod
#     def register(cls):
#         bpy.types.Scene.my_enum_items = bpy.props.PointerProperty(type=MyEnumItems)

#     @classmethod
#     def unregister(cls):
#         del bpy.types.Scene.my_enum_items

#     asdf : bpy.props.EnumProperty(
#         name="asdf",
#         description="asdf",
#         # items argument required to initialize, just filled with empty values
#         items = add_items_from_collection_callback,
#     )


class BookmarkPath(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Scene.bookmarks_paths = CollectionProperty(type=BookmarkPath)

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.bookmarks_paths

    path : bpy.props.StringProperty(
        name = "bookmark path",
        default = "",
        subtype = 'DIR_PATH'
    )


class WEED_OT_py_mngr_add_bookmark(bpy.types.Operator):
    ''' add bookmark to bpy.context.scene.bookmarks_paths '''
    bl_label = "add bookmark"
    bl_idname = "weed.py_mngr_add_bookmark"

    path : bpy.props.StringProperty(
        name = "bookmark path",
        default = "",
        subtype = 'DIR_PATH'
    )

    # @classmethod
    # def poll(cls, context):
    #     return isdir(cls.path)

    def execute(self, context):
        # if not self.path:
        #     return {'CANCELLED'}
        #breakpoint.here
        pref = get_prefs()
        
        paths = bpy.context.scene.bookmarks_paths
        if self.path not in [bkmk.path for bkmk in paths]:
            new_bkmrk = bpy.context.scene.bookmarks_paths.add()
            new_bkmrk.path = self.path  
            pref.bkmrk_add_tggl = False 
            pref.bkmrk_select = ''
            pref.bkmrks_folder = self.path             
        return {'FINISHED'}


class WEED_OT_py_mngr_browse_bookmark(bpy.types.Operator):
    ''' add bookmark to bpy.context.scene.bookmarks_paths '''
    bl_label = "add bookmark"
    bl_idname = "weed.py_mngr_browse_bookmark"

    path : bpy.props.StringProperty(
        name = "bookmark path",
        default = "",
        subtype = 'DIR_PATH'
    )

    # @classmethod
    # def poll(cls, context):
    #     return isdir(cls.path)

    def execute(self, context):
        # if not self.path:
        #     return {'CANCELLED'}
        #breakpoint.here
        get_prefs().bkmrks_folder = self.path             
        return {'FINISHED'}


class WEED_OT_py_mngr_remove_bookmark(bpy.types.Operator):
    ''' add item to bpy.context.scene.my_items '''
    bl_label = "remove bookmark"
    bl_idname = "weed.py_mngr_remove_bookmark"

    path : bpy.props.StringProperty(
        name = "bookmark path",
        default = "",
        subtype = 'DIR_PATH'
    )

    # @classmethod
    # def poll(cls, context):
    #     return (get_prefs().bkmrks_folder in bpy.context.scene.bookmarks_paths)

    def execute(self, context):
        #breakpoint.here
        pref = get_prefs()
        paths = bpy.context.scene.bookmarks_paths
        for idx, bkmrk in enumerate(paths):
            if bkmrk.path == self.path:
                pref.bkmrks_folder=paths[0].path 
                # breakpoint.here
                paths.remove(idx)
                break
        # new_bkmrk = bpy.context.scene.bookmarks_paths.add()
        # new_bkmrk.path = self.path    
        return {'FINISHED'}


# class MY_PT_simple_panel(bpy.types.Panel):
#     bl_label = "Simple Panel"
#     bl_idname = "MY_PT_simple_panel"
#     bl_space_type = "VIEW_3D"   
#     bl_region_type = "UI"
#     bl_category = "simple panel"
#     bl_context = "objectmode"

#     def draw(self, context):
#         layout = self.layout
#         layout.operator("my.add_item")
#         layout.prop(context.scene.my_enum_items, "asdf")

# classes = (MyEnumItems, MyItem, MY_OT_add_item, MY_PT_simple_panel)
# register, unregister = bpy.utils.register_classes_factory(classes)

# if __name__ == "__main__":
#     register()
##################################################################



def new_addon_file(path, default = ""):
    new_file(get_current_addon_path() + path, default)

def new_file(path, default = ""):
    dirname = dirname(path)
    new_directory(dirname)
    if not exists(path):
        file = open(path, "a")
        file.write(default)
        file.close()

def new_directory(path):
    if not exists(path):
        os.makedirs(path)


class WEED_OT_py_mngr_ToogleDirectoryVisibility(bpy.types.Operator):
    bl_idname = "weed.py_mngr_toogle_directory_visibility"
    bl_label = "Toogle Directory Visibility"
    bl_description = ""
    bl_options = {"REGISTER"}

    directory : StringProperty(name = "Directory", default = "")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        global directory_visibility
        directory_visibility[self.directory] = not directory_visibility[self.directory]
        return {"FINISHED"}


# class WEED_OT_py_mngr_ToogleCodeVisibility(bpy.types.Operator):
#     bl_idname = "weed.py_mngr_toogle_code_visibility"
#     bl_label = "Toogle Code Visibility"
#     bl_description = ""
#     bl_options = {"REGISTER"}

#     index : IntProperty(name = "index", default = 0)

#     @classmethod
#     def poll(cls, context):
#         return True

#     def execute(self, context):
#         bpy.types.Text.code_tree[self.index].open = not bpy.types.Text.code_tree[self.index].open
#         return {"FINISHED"}


class WEED_OT_py_mngr_FileMenuCloser(bpy.types.Operator):
    bl_idname = "weed.py_mngr_close_file_menu"
    bl_label = "Close File Menu"

    path : StringProperty(name = "Path", default = "")

    def invoke(self, context, event):
        for txt in bpy.data.texts:
            if self.path == txt.filepath:
                context.space_data.text = txt
                break
        context.window_manager.popup_menu(self.drawMenu,
                                          title = "{} - Close ?".format(basename(self.path)))
        return {"FINISHED"}

    def drawMenu(fileProps, self, context):
        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"
        props = layout.operator("weed.py_mngr_close_file",
                                text = "Save",
                                icon = 'IMPORT')
        props.path = fileProps.path
        props.save_it = True
        props.close_it = False
        props = layout.operator("weed.py_mngr_reload_file",
                                text = "Discard",
                                icon = 'RECOVER_LAST')
        props.path = fileProps.path
        #props.save_it = False
        #props.close_it = False
        layout.separator()
        props = layout.operator("weed.py_mngr_close_file",
                                text = "Save and Close",
                                icon = 'IMPORT')
        props.path = fileProps.path
        props.save_it = True
        props.close_it = True
        props = layout.operator("weed.py_mngr_close_file",
                                text = "Discard and Close",
                                icon = 'X')
        props.path = fileProps.path
        props.save_it = False
        props.close_it = True


class WEED_OT_py_mngr_CloseFile(bpy.types.Operator):
    bl_idname = "weed.py_mngr_close_file"
    bl_label = "Save and Close File"
    bl_description = "Save the file and unlink from the text editor"
    bl_options = {"REGISTER"}

    path : StringProperty(name = "Path", default = "")
    save_it : BoolProperty(name = "Save", default = False)
    close_it : BoolProperty(name = "Close", default = False)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        #breakpoint.here
        for text in bpy.data.texts:
            directory, file_name = split(self.path)
            if directory == 'Text:Internal' and file_name == text.name_full:
                context.space_data.text = text
                bpy.ops.text.unlink()
            elif text.filepath == self.path:
                if self.save_it:
                    save_text_block(text)
                context.space_data.text = text
                if self.close_it:
                    bpy.ops.text.unlink()
        try: bpy.ops.text.resolve_conflict(resolution = "IGNORE")
        except: pass
        return {"FINISHED"}


class WEED_OT_py_mngr_FileMenuOpener(bpy.types.Operator):
    bl_idname = "weed.py_mngr_open_file_menu"
    bl_label = "Open File Menu"

    path : StringProperty(name = "Path", default = "")

    def invoke(self, context, event):
        context.window_manager.popup_menu(self.drawMenu,
                                          title = basename(self.path))
        return {"FINISHED"}

    def drawMenu(fileProps, self, context):
        layout = self.layout
        layout.alignment = "RIGHT"
        layout.operator_context = "INVOKE_DEFAULT"
        props = layout.operator("weed.py_mngr_open_file",
                                icon = "ZOOM_ALL",
                                text="Open file")
        props.path = dirname(fileProps.path)
        props = layout.operator("weed.py_mngr_open_external_file_browser",
                                icon = "EXPORT",
                                text="Open on editor")
        props.path = dirname(fileProps.path)
        props = layout.operator("weed.py_mngr_rename_file",
                                icon = "DUPLICATE",
                                text = "Rename file")
        props.path = fileProps.path
        props = layout.operator("weed.py_mngr_delete_file",
                                icon = "CANCEL",
                                text = "Delete file")
        props.path = fileProps.path


class WEED_OT_py_mngr_AddonMenuOpener(bpy.types.Operator):
    bl_idname = "weed.py_mngr_open_addon_menu"
    bl_label = "Open Addon Menu"

    directory : StringProperty(name = "Path", default = "")

    def invoke(self, context, event):
        context.window_manager.popup_menu(self.drawMenu,
                                          title = 'Addon Menu')
        return {"FINISHED"}

    def drawMenu(dirProps, self, context):
        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"
        layout.prop(get_prefs(), 'show_dot_addons',
                 text='Show hidden addons')
        # RECUERDA, para enviar argumentos...
        # op = layout.operator("weed.py_mngr_renam...
        # op.directory = dirProps.directory
        layout.operator_menu_enum("weed.py_mngr_new_addon", "new_addon_type",
                                    icon = "NEWFOLDER",
                                    text = "Create New Addon")
        layout.operator("weed.py_mngr_rename_addon",
                            icon = "DUPLICATE", #"PLUS",
                            text = "Rename Addon")
        layout.operator("weed.py_mngr_delete_addon", # delete_addon
                            icon = "CANCEL",
                            text = "Delete Addon")
        layout.separator()
        layout.operator("weed.py_mngr_run_addon",
                            icon = "PLAY",
                            text = "Run")
        layout.operator("weed.py_mngr_unregister_addon",
                            icon = "LOOP_BACK",
                            text = "UnReg")
        layout.operator("weed.py_mngr_export_addon",
                            icon = "OUTLINER_OB_GROUP_INSTANCE",
                            text = "Zip")
        layout.operator("weed.py_mngr_restart_blender",
                            icon = "BLENDER")


class WEED_OT_py_mngr_DirMenuOpener(bpy.types.Operator):
    bl_idname = "weed.py_mngr_open_dir_menu"
    bl_label = "Open Folder Menu"

    directory : StringProperty(name = "Path", default = "")

    def invoke(self, context, event):
        context.window_manager.popup_menu(self.drawMenu,
                                          title = "in {} folder".format(
                                          split(dirname(self.directory))[-1]))
        return {"FINISHED"}

    def drawMenu(parent, self, context):
        layout = self.layout
    
        add_bkmrk = layout.operator('weed.py_mngr_add_bookmark',
                                  icon='BOOKMARKS', text='add this folder to bookmarks')
        add_bkmrk.path = parent.directory[:-1]
    
        layout.separator()
        layout.operator_context = "INVOKE_DEFAULT"
        layout.prop(get_prefs(), 'show_dot_files',
                 text='Show hidden addons')
        op = layout.operator("weed.py_mngr_new_file",
                            icon = "FILE_NEW",
                            text = "Create new file")
        op.directory = parent.directory
        op = layout.operator("weed.py_mngr_new_directory",
                            icon = "NEWFOLDER",
                            text = "Create new folder")
        op.directory = parent.directory
        layout.separator()
        if split(parent.directory.rstrip(sep))[0] != addons_path:
            op = layout.operator("weed.py_mngr_rename_directory",
                                icon = "DUPLICATE",
                                text = "Rename folder")
            op.base_dir, op.actual_name = split(
                                        parent.directory.rstrip(sep))
            op = layout.operator("weed.py_mngr_delete_directory",
                                 icon = "CANCEL",
                                 text = "Delete folder")
            op.directory = parent.directory
        else:
            op = layout.operator("weed.py_mngr_save_files",
                    text = 'Save all "{}" open files'.format(get_addon_name()[:15]),
                    icon = 'IMGDISPLAY')

        #op1.enabled = op2.enabled = True if (
                #split(parent.directory.rstrip(sep))[0] != addons_path
                #) else False

        #if split(parent.directory.rstrip(sep))[0] != addons_path:
        #    op1.enabled = op2.enabled = True
        #else:
        #    op1.enabled = op2.enabled = False


class WEED_OT_py_mngr_OpenFile(bpy.types.Operator):
    bl_idname = "weed.py_mngr_open_file"
    bl_label = "Open File"
    bl_description = "Load the file into the text editor"
    bl_options = {"REGISTER"}

    path : StringProperty(name = "Path", default = "")

    def execute(self, context):
        text_obj = None
        directory, file_name = split(self.path)
        for text in bpy.data.texts:
            if (self.path == text.filepath or
                directory == 'Text:Internal' and 
                file_name == text.name_full):
                text_obj = text
                break

        if not text_obj:
            text_obj = bpy.data.texts.load(self.path, internal = False)

        context.space_data.text = text_obj
        return {"FINISHED"}


class WEED_OT_py_mngr_ReloadFile(bpy.types.Operator):
    bl_idname = "weed.py_mngr_reload_file"
    bl_label = "Reload File"
    bl_description = "Reload current file"
    bl_options = {"REGISTER"}

    path : StringProperty(name = "Path", default = "")

    def execute(self, context):
#        text = None
#        for text_block in bpy.data.texts:
#            if text_block.filepath == self.path:
#                text = text_block
#                break
#        if not text:
        bpy.ops.text.unlink()
        text = bpy.data.texts.load(self.path, internal = False)

        context.space_data.text = text
        return {"FINISHED"}


class WEED_OT_py_mngr_OpenExternalFileBrowser(bpy.types.Operator):
    bl_idname = "weed.py_mngr_open_external_file_browser"
    bl_label = "Open External File Browser"
    bl_description = ""
    bl_options = {"REGISTER"}

    path : StringProperty(name = "Directory", default = "")

    def execute(self, context):
        bpy.ops.wm.path_open(filepath = self.path)
        return {"FINISHED"}


class WEED_OT_py_mngr_RenameFile(bpy.types.Operator):
    bl_idname = "weed.py_mngr_rename_file"
    bl_label = "Open External File Browser"
    bl_description = ""
    bl_options = {"REGISTER"}

    path : StringProperty(name = "Directory", default = "")
    new_name : StringProperty(name = "Directory", description = "New file name", default = "")

    def invoke(self, context, event):
        self.new_name = basename(self.path)
        return context.window_manager.invoke_props_dialog(self, width = 400)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "new_name")

    def execute(self, context):
        new_path = join(dirname(self.path), self.new_name)
        os.rename(self.path, new_path)
        self.correct_text_block_paths(self.path, new_path)
        context.area.tag_redraw()
        return {"FINISHED"}

    def correct_text_block_paths(self, old_path, new_path):
        for text in bpy.data.texts:
            if text.filepath == old_path:
                text.filepath = new_path


class WEED_OT_py_mngr_DeleteFile(bpy.types.Operator):
    bl_idname = "weed.py_mngr_delete_file"
    bl_label = "Delete File"
    bl_description = "Delete file on the hard drive"
    bl_options = {"REGISTER"}

    path : StringProperty(name = "Directory", default = "")

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        os.remove(self.path)
        context.area.tag_redraw()
        return {"FINISHED"}


class WEED_OT_py_mngr_SaveFiles(bpy.types.Operator):
    bl_idname = "weed.py_mngr_save_files"
    bl_label = " Save All Files"
    bl_description = "Save all datablock files from an addon"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        addon_path = get_current_addon_path()
        for text in bpy.data.texts:
            if addon_path in text.filepath:
                save_text_block(text)
        try: bpy.ops.text.resolve_conflict(resolution = "IGNORE")
        except: pass
        return {"FINISHED"}


class WEED_OT_py_mngr_ConvertAddonIndentation(bpy.types.Operator):
    bl_idname = "weed.py_mngr_convert_addon_indentation"
    bl_label = "Convert Addon Indentation"
    bl_description = ""
    bl_options = {"REGISTER"}

    old_indentation : StringProperty(default = "\t")
    new_indentation : StringProperty(default = "    ")

    @classmethod
    def poll(cls, context):
        return current_addon_exists()

    def execute(self, context):
        paths = self.get_addon_files()
        for path in paths:
            bpy.ops.weed.py_mngr_convert_file_indentation(
                path = path,
                old_indentation = self.old_indentation,
                new_indentation = self.new_indentation)
        return {"FINISHED"}

    def get_addon_files(self):
        paths = []
        for root, dirs, files in os.walk(get_current_addon_path()):
            for file in files:
                if file.endswith(".py"):
                    paths.append(join(root, file))
        return paths


class WEED_OT_py_mngr_ExportAddon(bpy.types.Operator):
    bl_idname = "weed.py_mngr_export_addon"
    bl_label = "Export Addon"
    bl_description = "Save a .zip file of the addon"
    bl_options = {"REGISTER"}

    filepath : StringProperty(subtype = "FILE_PATH")

    @classmethod
    def poll(cls, context):
        return current_addon_exists()

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        subdirectory_name = get_addon_name() + sep
        source_path = get_current_addon_path()
        output_path = self.filepath
        if not output_path.lower().endswith(".zip"):
            output_path += ".zip"
        zip_directory(source_path, output_path, additional_path = subdirectory_name)
        return {"FINISHED"}


class WEED_OT_py_mngr_RunAddon(bpy.types.Operator):
    bl_idname = "weed.py_mngr_run_addon"
    bl_label = "Run Addon"
    bl_description = "Unregister, reload and register it again."
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return current_addon_exists()

    def execute(self, context):
        bpy.ops.weed.py_mngr_save_files()

        addon_name = get_addon_name()
        module = sys.modules.get(addon_name)
        if module:
            addon_utils.disable(addon_name)
            importlib.reload(module)
        addon_utils.enable(addon_name)
        return {"FINISHED"}


class WEED_OT_py_mngr_UnregisterAddon(bpy.types.Operator):
    bl_idname = "weed.py_mngr_unregister_addon"
    bl_label = "Unregister Addon"
    bl_description = "Unregister only."
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return current_addon_exists()

    def execute(self, context):
        bpy.ops.weed.py_mngr_save_files()

        addon_utils.disable(get_addon_name())
        return {"FINISHED"}


class WEED_OT_py_mngr_RestartBlender(bpy.types.Operator):
    bl_idname = "weed.py_mngr_restart_blender"
    bl_label = "Restart Blender"
    bl_description = "Close and open a new Blender instance to test the Addon on the startup file. (Currently only supported for windows)"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return sys.platform == "win32"

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        bpy.ops.weed.py_mngr_save_files()
        save_status()
        start_another_blender_instance()
        bpy.ops.wm.quit_blender()
        return {"FINISHED"}


restart_data_path = join(dirname(__file__), "restart_data.txt")

id_addon_name = "ADDON_NAME: "
id_current_path = "CURRENT_PATH: "
id_visiblie_path = "VISIBLE_PATH: "
def save_status():
    file = open(restart_data_path, "w")
    file.write(id_addon_name + get_addon_name() + "\n")
    text_block = bpy.context.space_data.text
    if text_block:
        file.write(id_current_path + text_block.filepath + "\n")
    for path, is_open in directory_visibility.items():
        if is_open:
            file.write(id_visiblie_path + path + "\n")

    file.close()

@persistent
def open_status(scene):
    if exists(restart_data_path):
        file = open(restart_data_path)
        lines = file.readlines()
        file.close()
        os.remove(restart_data_path)
        parse_startup_file_lines(lines)

def parse_startup_file_lines(lines):
    for line in lines:
        if line.startswith(id_addon_name):
            addon_name = line[len(id_addon_name):].strip()
        if line.startswith(id_current_path):
            path = line[len(id_current_path):].strip()
            text_block = bpy.data.texts.load(path, internal = False)
            for screen in bpy.data.screens:
                for area in screen.areas:
                    for space in area.spaces:
                        if space.type == "TEXT_EDITOR":
                            space.text = text_block
        if line.startswith(id_visiblie_path):
            path = line[len(id_visiblie_path):].strip()
            make_directory_visible(path)

def make_directory_visible(path):
    global directory_visibility
    directory_visibility[path] = True

def get_current_filepath():
    try: return bpy.context.space_data.text.filepath
    except: return ""

def current_addon_exists():
    return exists(get_current_addon_path()) and get_addon_name() != ""

def get_current_addon_path():
    path_name = join(addons_path, get_addon_name())
    return path_name if isfile(path_name) else path_name + sep

def is_addon_name_valid():
    addon_name = get_addon_name()
    return addon_name == correct_file_name(
        addon_name, is_directory = True) and addon_name != ""

def get_addon_name():
    return get_prefs().addons_folder


def save_text_block(text_block):
    if not text_block: return
    if not exists(text_block.filepath): return

    bpy.context.space_data.text = text_block
    bpy.ops.text.save()

def zip_directory(source_path, output_path, additional_path = ""):
    try:
        parent_folder = dirname(source_path)
        content = os.walk(source_path)
        zip_file = zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED)
        for root, folders, files in content:
            for data in folders + files:
                absolute_path = join(root, data)
                relative_path = additional_path + absolute_path[len(parent_folder+sep):]
                zip_file.write(absolute_path, relative_path)
        zip_file.close()
    except: print("Could not zip the directory")

def start_another_blender_instance():
    open_file(bpy.app.binary_path)

# only works for windows currently
def open_file(path):
    if sys.platform == "win32":
        os.startfile(path)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, path])

bpy.app.handlers.load_post.append(open_status)




prefs_classes = (
    Preferences,
)

classes = (
    BookmarkPath,
    WEED_OT_py_mngr_add_bookmark,
    WEED_OT_py_mngr_browse_bookmark,
    WEED_OT_py_mngr_remove_bookmark,
    WEED_OT_py_mngr_MakeAddonNameValid,
    WEED_OT_py_mngr_CreateNewAddon,
    WEED_OT_py_mngr_RenameAddon,
    WEED_OT_py_mngr_DeleteAddon,
    WEED_OT_py_mngr_ConvertAddonIndentation,
    WEED_OT_py_mngr_ExportAddon,
    WEED_OT_py_mngr_RunAddon,
    WEED_OT_py_mngr_UnregisterAddon,
    WEED_OT_py_mngr_NewFile,
    WEED_OT_py_mngr_CloseFile,
    WEED_OT_py_mngr_OpenFile,
    WEED_OT_py_mngr_ReloadFile,
    WEED_OT_py_mngr_OpenExternalFileBrowser,
    WEED_OT_py_mngr_RenameFile,
    WEED_OT_py_mngr_DeleteFile,
    WEED_OT_py_mngr_SaveFiles,
    WEED_OT_py_mngr_NewDirectory,
    WEED_OT_py_mngr_RenameDirectory,
    WEED_OT_py_mngr_DeleteDirectory,
    WEED_OT_py_mngr_ToogleDirectoryVisibility,
    # WEED_OT_py_mngr_ToogleCodeVisibility,
    WEED_OT_py_mngr_RestartBlender,
    WEED_OT_py_mngr_FileMenuCloser,
    WEED_OT_py_mngr_FileMenuOpener,
    WEED_OT_py_mngr_AddonMenuOpener,
    WEED_OT_py_mngr_DirMenuOpener,
    WEED_PT_scripts_manager,
)


def register(prefs=True):
    if prefs:
        for cls in prefs_classes:
            try:
                bpy.utils.unregister_class(cls)
            except:
                print(f'{cls} already unregistered')
                #pass
            bpy.utils.register_class(cls)

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister(prefs=True):
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    if prefs:
        for cls in reversed(prefs_classes):
            bpy.utils.unregister_class(cls)


