import bpy
import os
import sys
import zipfile
import importlib
import subprocess
import addon_utils
from bpy.props import *
from os import listdir, sep
from os.path import isfile, isdir, join, split, dirname, basename, exists
from shutil import rmtree
from collections import defaultdict
from bpy.app.handlers import persistent
from . text_block import TextBlock
from . developer_utils import is_binary_file

is_setting = False

# directory name handlers
def set_directory_name_handler(self, value):
    global is_setting
    if not is_setting:
        is_setting = True
        self["directory_name_internal"] = correct_file_name(value, is_directory = True)
        is_setting = False
def get_directory_name_handler(self):
    try: return self["directory_name_internal"]
    except: return ""

# file name handlers
def set_file_name_handler(self, value):
    global is_setting
    if not is_setting:
        is_setting = True
        self["file_name_internal"] = correct_file_name(value, is_directory = False)
        is_setting = False
def get_file_name_handler(self):
    try: return self["file_name_internal"]
    except: return ""

#class AddonDevelopmentSceneProperties(bpy.types.PropertyGroup):
#    addon_name = StringProperty(name = "Addon Name", default = "my_addon", description = "Name of the currently selected addon")

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



addons_path = bpy.utils.user_resource("SCRIPTS", "addons")
directory_visibility = defaultdict(bool)
#code_visibility = defaultdict(bool)


class WeedToolsPanel(bpy.types.Panel):
    bl_idname = "weed.tools_panel"
    bl_label = "Weed Tools"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        return current_addon_exists()


    def draw(self, context):
        wm = context.window_manager
        layout = self.layout
        row = layout.row(align=True)
        row.prop(wm, 'weed_active_toolbox', expand=False)
        #row.prop(get_addon_preferences(), 'show_code_tree',
        #         text = 'view tree', icon = 'OOPS')
        box = layout.box()
        draw_toolbox = getattr(self, wm.weed_active_toolbox)
        if (wm.weed_active_toolbox == 'draw_explorer_box' and
                get_addon_preferences().show_code_tree):
            self.draw_code_tree_box(context, box)
        else:
            draw_toolbox(context, box)


    def draw_debugger_box(self, context, layout):
        #layout.label('debugger box')
        label = layout.label(text = 'Debugger breakpoint', icon = 'REC')
        split_lyt = layout.split(percentage=0.05, align=True)
        split_lyt.label('breakpoint')
        split_lyt.operator('weed.insert_breakpoint',
                        text = 'add',
                        icon = 'PLUS')
        split_lyt.operator('weed.search_breakpoint',
                        text = 'find',
                        icon = 'VIEWZOOM')
        prefs = bpy.context.user_preferences.addons['weed'].preferences
        layout.separator()
        label = layout.label(text = 'Code Editor',
                     icon = 'WORDWRAP_ON')
        split_lyt = layout.split(percentage=0.05, align=True)
        split_lyt.label('')
        split_lyt.operator('weed.code_editor_start',
                        text = 'start',
                        icon = 'PLAY')
        split_lyt.operator('weed.code_editor_end',
                        text = 'exit',
                        icon = 'PANEL_CLOSE')
        label = layout.label(text = 'Autocomplete',
                     icon = 'LIBRARY_DATA_DIRECT')
        split_lyt = layout.split(percentage=0.05, align=True)
        split_lyt.label('')
        split_lyt.operator("weed.start_auto_completion",
                        text = 'start',
                        icon = "PLAY")
        split_lyt.operator("weed.stop_auto_completion",
                        text = 'exit',
                        icon = "PANEL_CLOSE")
        
        if prefs.show_bge_console:
            objects = bpy.data.objects
            scene = bpy.context.scene
            layout.separator()
            layout.label(text = 'Game Engine bge console', icon = 'LOGIC')
            split_lyt = layout.split(percentage=0.05, align=False)
            split_lyt.label('')
            if '!BgeCon' in objects:
                if '!BgeCon' in scene.objects:
                    #layout.label(text='Attach Bge Console',
                    #             icon='NONE')
                    split_lyt.operator('weed.dettach_bge_console',
                                    text='dettach',
                                    icon='ZOOMOUT')
                    split_lyt.operator('weed.remove_bge_console',
                                    text='remove',
                                    icon='PANEL_CLOSE')
                else:
                    split_lyt.operator('weed.attach_bge_console',
                                    text='attach',
                                    icon='CONSOLE')
                    #layout.label(text='Dettach Bge Console',
                    #             icon='NONE')
                    split_lyt.operator('weed.remove_bge_console',
                                    text='remove',
                                    icon='PANEL_CLOSE')
            else:
                    split_lyt.label('')
                    split_lyt.operator('weed.attach_bge_console',
                                    text='attach',
                                    icon='CONSOLE')
                    #layout.label(text='Dettach Bge Console',
                    #             icon='NONE')
                    #layout.label(text='Remove Bge Console',
                    #             icon='NONE')


    def draw_code_tree_box(self, context, layout):
        code_editors = context.window_manager.code_editors
        col = layout.column(align=False)
        row = col.row(align=False)
        row.prop(get_addon_preferences(), 'user_site_packages',
                 icon = 'RECOVER_AUTO', text = '')
        selector = row.row(align=True)
        selector.prop(context.scene, 'explorer_root_folder', text='')
        selector.operator('weed.open_addon_menu',
                     icon = 'COLLAPSEMENU', text = '')
        row.enabled = False
        col.prop(get_addon_preferences(), 'show_code_tree',
                 icon = 'OOPS', text = 'view code tree')
        if str(context.area) not in code_editors.keys():
            layout.label(text='to activate Code tree,', icon='INFO')
            #layout.label(text='Start code editor here')
            layout.operator('weed.code_editor_start', icon = 'SYNTAX_ON',
                            text = 'Start Code Editor here', emboss = True)
            return {'FINISHED'}

        icons = { 'imports' : 'OUTLINER_OB_GROUP_INSTANCE',
                  'imports_off' : 'GROUP',
                  'import' : 'OUTLINER_OB_GROUP_INSTANCE',
                  'toggle_open' : 'DISCLOSURE_TRI_RIGHT',
                  'toggle_close' : 'DISCLOSURE_TRI_DOWN',
                  'class' : 'OBJECT_DATA', 'class_off' : 'MATCUBE',
                  'def' : 'LAYER_ACTIVE', 'def_off' : 'FONT_DATA'}
        #layout.operator_context = 'EXEC_DEFAULT'
        col = layout.column(align=True)
        col.alignment = 'LEFT'
        col.label(icon = 'FILE_TEXT', text = context.space_data.text.name)
        #col.template_ID(context.space_data, "text")

        subnode_closed = False
        node_indnt = 0
        active = TextBlock.get_active()
        for i, codetree_node in enumerate(bpy.types.Text.code_tree):
            if subnode_closed and codetree_node.indnt > node_indnt:
                continue
            if codetree_node.low_limit <= active.get_line_index() < codetree_node.upper_limit:
                col2 = col.box()
            else:
                col2 = col
            if codetree_node.indnt > 0:
                indent = col2.split(percentage=(0.03 + codetree_node.indnt * 0.01) * codetree_node.indnt)
                indent.label('')
                row = indent.row(align=True)
            else:
                row = col2.row(align=True)
            row.alignment = 'LEFT'
            if codetree_node.open is not None:
                tggl = row.operator("weed.toogle_code_visibility",
                                 text = '',
                                 icon = 'DISCLOSURE_TRI_DOWN'
                                        if codetree_node.open
                                        else 'DISCLOSURE_TRI_RIGHT',
                                 emboss = False)
                tggl.index = i
                if codetree_node.open:
                    subnode_closed = False
                else:
                    subnode_closed = True
                node_indnt = codetree_node.indnt
            else:
                #row.label(text = '', icon = 'NONE')
                row.operator("weed.toogle_code_visibility",
                             text = '',
                             icon = 'SCULPT_DYNTOPO',
                             emboss = False)
            prop = row.operator('text.jump',
                                text = codetree_node.name,
                                icon = icons[codetree_node.type],
                                emboss = False)
            prop.line = codetree_node.line_n + 1

        
#         for i, (idx, indnt, (keyword, name, args)) in enumerate(
#                                         bpy.types.Text.code_tree['imports']):
#             #row = row if i%2 else layout.row(align=True)
#             row = col.row(align=True)
#             row.alignment = 'LEFT'
#             prop = row.operator('text.jump',
#                                 text = name,
#                                 icon = icons[keyword],
#                                 emboss = False)
#             prop.line = idx + 1
# 
#         for idx, indnt, (keyword, name, args) in bpy.types.Text.code_tree['class_def']:
#             #if not indnt:
#             #    col.separator()
#             row = col.row(align=True)
#             row.alignment = 'LEFT'
#             prop = row.operator('text.jump',
#                                 text = '·   '*indnt + name,
#                                 icon = icons[keyword] if not indnt else 'NONE',
#                                 emboss = False)
#             prop.line = idx + 1
#             prev_indnt = indnt


    def draw_explorer_box(self, context, layout):
        #layout = self.layout
        #row = layout.row(align = False)
        #row.prop(get_addon_preferences(), 'show_dot_addons',
                 #text='', icon='FILE_HIDDEN', emboss=True)
        col = layout.column(align=False)
        row = col.row(align=False)
        browse_libs = row.prop(get_addon_preferences(), 'user_site_packages',
                 icon = 'RECOVER_AUTO', text = '')
        selector = row.row(align=True)
        selector.prop(context.scene, 'explorer_root_folder', text='')
        selector.operator('weed.open_addon_menu',
                     icon = 'COLLAPSEMENU', text = '')
        col.prop(get_addon_preferences(), 'show_code_tree',
                 icon = 'OOPS', text = 'view code tree')
        if not current_addon_exists():
            if not is_addon_name_valid():
                col.operator('weed.make_addon_name_valid',
                                icon = 'ERROR', text = 'Correct Addon Name')
            else:
                #row.scale_y = 1.2
                col.operator_menu_enum('weed.new_addon', 'new_addon_type',
                                       icon = 'NEW', text = 'New Addon')
        else:
            #layout.alignment = "LEFT"
            addon_path = get_current_addon_path()

            #row = col.row(align=True)
            #row.prop(get_addon_preferences(), 'show_dot_files',
            #        text = '', icon = 'FILE_HIDDEN')
#            row.operator("weed.save_files",
#                       text = 'Save all {} files'.format(get_addon_name()[:15]),
#                        icon = 'SAVE_COPY')
            #box = layout.box()
            if not get_addon_preferences().user_site_packages:
                if isfile(addon_path):
                    directory, file_name = split(addon_path)
                    self.draw_element(layout, directory + sep, file_name)
                else:
                    self.draw_directory(layout, addon_path)
            else:
                import site, os
                selector.enabled = False
                layout.label('User:')
                self.draw_directory(layout, site.getusersitepackages() + sep)
                layout.label('Global:')
                for site in site.getsitepackages():
                    self.draw_directory(layout, site + sep)
                self.draw_directory(layout, split(site)[0] + sep)

    def draw_directory(self, layout, directory):
        if not self.is_directory_visible(directory):
            row = layout.row(align=True)
            row.alignment = "LEFT"
            op = row.operator("weed.toogle_directory_visibility",
                                 text = split(directory[:-1])[-1],
                                 icon = "FILESEL",
                                 emboss = False)
            op.directory = directory
        else:
            split_lyt = layout.split(0.9)
            row = split_lyt.row(align=True)
            row.alignment = "LEFT"
            op = row.operator("weed.toogle_directory_visibility",
                                text = split(directory[:-1])[-1],
                                icon = "FILE_FOLDER",
                                emboss = False)
            op.directory = directory
            op = split_lyt.operator("weed.open_dir_menu",
                              icon = "COLLAPSEMENU",
                              text = "",
                              emboss = False)
            op.directory = directory


            directory_names = get_directory_names(directory)
            split_lyt = layout.split(0.04)
            split_lyt.label('')
            col = split_lyt.column(align=True)
            col.alignment = "LEFT"
            #row = col.row(align=True)
            #row.alignment = "LEFT"

            for directory_name in directory_names:
                self.draw_directory(col, directory + directory_name + sep)

            file_names = get_file_names(directory)
            for file_name in file_names:
                self.draw_element(col, directory, file_name)


    def draw_element(self, layout, directory, file_name):
        texts_paths = {text.filepath: text for text in bpy.data.texts}
        full_path = directory + file_name
        if full_path != get_current_filepath():
            split_lyt = layout.split(0.8)
            row = split_lyt.row(align=True)
            row.alignment = "LEFT"
            op = row.operator("weed.open_file",
                      icon = "FILE_TEXT",
                      text = file_name,
                      emboss = False)
            op.path = full_path
            if is_binary_file(full_path):
                row.enabled = False
            split_lyt.label("", icon = "NONE")
        else:
            active = layout.box()
            split_lyt = active.split(0.8)
            row = split_lyt.row(align=True)
            row.alignment = "LEFT"
            op = row.operator("weed.open_file",
                      icon = "GREASEPENCIL",
                      text = file_name,
                      emboss = False)
            op.path = full_path
            split_lyt.label("", icon = "NONE")
        if full_path in texts_paths:
            if texts_paths[full_path].is_dirty:
                # call menu save/discard
                props = split_lyt.operator('weed.close_file_menu',
                                       icon = 'HELP',
                                       text = '',
                                       emboss = False)
                props.path = full_path
            else:
                # close quietly
                props = split_lyt.operator('weed.close_file',
                                       text = '',
                                       icon = 'X',
                                       emboss = False)
                props.path = full_path
                props.save_it = False
                props.close_it = True
        else:
            props = split_lyt.operator("weed.open_file_menu",
                              icon = "LAYER_USED",
                              text = "",
                              emboss = False)
            props.path = full_path

    def is_directory_visible(self, directory):
        return directory_visibility[directory]

#     def draw_code_branch(self, layout, code):
#         if not self.is_code_visible(code):
#             split_lyt = layout.split(0.9)
#             row = split_lyt.row(align=True)
#             row.alignment = "LEFT"
#             op = row.operator("weed.toogle_code_visibility",
#                                  text = code,
#                                  icon = "FILESEL",
#                                  emboss = False)
#             op.code = code
#         else:
#             split_lyt = layout.split(0.9)
#             row = split_lyt.row(align=True)
#             row.alignment = "LEFT"
#             op = row.operator("weed.toogle_directory_visibility",
#                                 text = split(directory[:-1])[-1],
#                                 icon = "FILE_FOLDER",
#                                 emboss = False)
#             op.directory = directory
#             op = split_lyt.operator("weed.open_dir_menu",
#                               icon = "COLLAPSEMENU",
#                               text = "",
#                               emboss = False)
#             op.directory = directory
# 
# 
#             directory_names = get_directory_names(directory)
#             split_lyt = layout.split(0.04)
#             split_lyt.label('')
#             col = split_lyt.column(align=True)
#             col.alignment = "LEFT"
#             #row = col.row(align=True)
#             #row.alignment = "LEFT"
# 
#             for directory_name in directory_names:
#                 self.draw_directory(col, directory + directory_name + sep)
# 
#             file_names = get_file_names(directory)
#             for file_name in file_names:
#                 self.draw_element(col, directory, file_name)
# 
# 
#     def draw_code_element(self, layout, code, file_name = None):
#         #texts_paths = {text.filepath: text for text in bpy.data.texts}
#         #full_path = directory + file_name
#         if full_path != get_current_filepath():
#             split_lyt = layout.split(0.8)
#             row = split_lyt.row(align=True)
#             row.alignment = "LEFT"
#             op = row.operator("weed.open_file",
#                       icon = "FILE_TEXT",
#                       text = file_name,
#                       emboss = False)
#             op.path = full_path
#             if is_binary_file(full_path):
#                 row.enabled = False
#             split_lyt.label("", icon = "NONE")
#         else:
#             active = layout.box()
#             split_lyt = active.split(0.8)
#             row = split_lyt.row(align=True)
#             row.alignment = "LEFT"
#             op = row.operator("weed.open_file",
#                       icon = "GREASEPENCIL",
#                       text = file_name,
#                       emboss = False)
#             op.path = full_path
#             split_lyt.label("", icon = "NONE")
#         if full_path in texts_paths:
#             if texts_paths[full_path].is_dirty:
#                 # call menu save/discard
#                 props = split_lyt.operator('weed.close_file_menu',
#                                        icon = 'HELP',
#                                        text = '',
#                                        emboss = False)
#                 props.path = full_path
#             else:
#                 # close quietly
#                 props = split_lyt.operator('weed.close_file',
#                                        text = '',
#                                        icon = 'X',
#                                        emboss = False)
#                 props.path = full_path
#                 props.save_it = False
#                 props.close_it = True
#         else:
#             props = split_lyt.operator("weed.open_file_menu",
#                               icon = "LAYER_USED",
#                               text = "",
#                               emboss = False)
#             props.path = full_path

    def is_code_visible(self, code):
        return code_visibility[code]


def get_addon_preferences():
    addon_path_name = basename(dirname(__file__))
    addon = bpy.context.user_preferences.addons.get(addon_path_name)
    if addon is None:
        return None
    else:
        return addon.preferences

ignore_names = ["__pycache__", ".git", ".gitignore"]

def get_directory_names(directory):
    try:
        dirs = sorted([file_name for file_name in listdir(directory)
                       if not isfile(join(directory, file_name))
                       and file_name not in ignore_names])
        if not get_addon_preferences().show_dot_files:
            dirs = [file_name for file_name in dirs
                    if file_name[0] is not '.']
        return dirs
    except:
        return []

def get_addons_names(directory):
    addons = sorted([file_name for file_name in listdir(directory)
                    if file_name not in ignore_names
                    and (not isfile(join(directory, file_name))
                    or isfile(join(directory, file_name))
                    and file_name[-3:] == '.py')])
    if not get_addon_preferences().show_dot_addons:
        addons = [file_name for file_name in addons
                if file_name[0] is not '.']
    return addons

def get_file_names(directory):
    try:
        dirs = sorted([file_name for file_name in listdir(directory)
                       if isfile(join(directory, file_name))
                       and file_name not in ignore_names])
        if not get_addon_preferences().show_dot_files:
            dirs = [file_name for file_name in dirs
                    if file_name[0] is not '.']
        return dirs
    except:
        return []

def get_folders_list(self, context):
    #list.append(('folder/path','ui_label','tooltip'))
    list = []
    for addon in get_addons_names(addons_path):
        try:
            list.append((join(addons_path, addon),
                         'addon: ' + addon,
                         __import__(addon).bl_info['description']))
        except:
            list.append((addon, addon, 'one file or hidden Addon'))
    blend_path = bpy.path.abspath('//').rstrip(sep)
    if blend_path:
        list.append((blend_path,
                    'folder for ' + bpy.path.basename(bpy.data.filepath),
                    'folder from current blend file'))
        
    return list


class MakeAddonNameValid(bpy.types.Operator):
    bl_idname = "weed.make_addon_name_valid"
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


new_addon_type_items = [
    ("BASIC", "Basic", ""),
    ("MULTIFILE", "Multi-File (recommended)", "") ]

class CreateNewAddon(bpy.types.Operator):
    bl_idname = "weed.new_addon"
    bl_label = "New Addon"
    bl_description = "Create an addon in addons folder and setup a basic code base"
    bl_options = {"REGISTER"}

    new_addon_type = EnumProperty(default = "BASIC", items = new_addon_type_items)
    name = StringProperty(name = "New Addon Name", default = "")#, set = set_file_name_handler, get = get_file_name_handler)

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
            bpy.ops.weed.open_file(path = addon_path + "__init__.py")
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



class RenameAddon(bpy.types.Operator):
    bl_idname = "weed.rename_addon"
    bl_label = "Rename Addon"
    bl_description = "Rename the current Addon"
    bl_options = {"REGISTER"}

    name = StringProperty(name = "New Addon Name", default = "")#, set = set_file_name_handler, get = get_file_name_handler)

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
                self.report({'INFO'}, 'destination already exist')
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


class DeleteAddon(bpy.types.Operator):
    bl_idname = "weed.delete_addon"
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


class NewFile(bpy.types.Operator):
    bl_idname = "weed.new_file"
    bl_label = "New File"
    bl_description = "Create a new file in this directory"
    bl_options = {"REGISTER"}

    directory = StringProperty(name = "Directory", default = "")
    name = StringProperty(name = "File Name", default = "", set = set_file_name_handler, get = get_file_name_handler)

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
            bpy.ops.weed.open_file(path = path)
            context.area.tag_redraw()
        return {"FINISHED"}


class NewDirectory(bpy.types.Operator):
    bl_idname = "weed.new_directory"
    bl_label = "New Directory"
    bl_description = "Create a new subdirectory"
    bl_options = {"REGISTER"}

    directory = StringProperty(name="Directory", default="")
    name = StringProperty(name="Directory Name", default="",
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


class RenameDirectory(bpy.types.Operator):
    bl_idname = "weed.rename_directory"
    bl_label = "Rename Directory"
    bl_description = "Rename current directory"
    bl_options = {"REGISTER"}

    base_dir = StringProperty(name="Base directory", default="")
    actual_name = StringProperty(name="Actual name", default="")
    new_name = StringProperty(name="New name", default="",
                          set=set_directory_name_handler,
                          get=get_directory_name_handler)

    @classmethod
    def poll(cls, context):
        return current_addon_exists()

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.label('current name is ' + self.actual_name)
        layout.prop(self, "new_name")

    def execute(self, context):
        if self.new_name not in os.listdir(self.base_dir):
            try:
                actual_path = join(self.base_dir, self.actual_name)
                new_path = join(self.base_dir, self.new_name)
                os.rename(actual_path, new_path)
            except:
                self.report({'INFO'},
                            'rename failed')
            else:
                for text in bpy.data.texts:
                    if actual_path in text.filepath:
                        text.filepath = text.filepath.replace(
                            actual_path, new_path)
                try:
                    bpy.ops.text.resolve_conflict(resolution="IGNORE")
                except:
                    self.report({'INFO'},
                                'text editor conflict on open files')
            finally:
                context.area.tag_redraw()
        return {"FINISHED"}


class DeleteDirectory(bpy.types.Operator):
    bl_idname = "weed.delete_directory"
    bl_label = "Do you really want to delete directory?"
    bl_description = "Delete current directory"
    bl_options = {"REGISTER"}

    directory = StringProperty(name="Directory", default="")

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


class ToogleDirectoryVisibility(bpy.types.Operator):
    bl_idname = "weed.toogle_directory_visibility"
    bl_label = "Toogle Directory Visibility"
    bl_description = ""
    bl_options = {"REGISTER"}

    directory = StringProperty(name = "Directory", default = "")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        global directory_visibility
        directory_visibility[self.directory] = not directory_visibility[self.directory]
        return {"FINISHED"}


class ToogleCodeVisibility(bpy.types.Operator):
    bl_idname = "weed.toogle_code_visibility"
    bl_label = "Toogle Code Visibility"
    bl_description = ""
    bl_options = {"REGISTER"}

    index = IntProperty(name = "index", default = 0)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.types.Text.code_tree[self.index].open = not bpy.types.Text.code_tree[self.index].open
        return {"FINISHED"}


class FileMenuCloser(bpy.types.Operator):
    bl_idname = "weed.close_file_menu"
    bl_label = "Close File Menu"

    path = StringProperty(name = "Path", default = "")

    def invoke(self, context, event):
        context.window_manager.popup_menu(self.drawMenu,
                                          title = "{} - Close ?".format(basename(self.path)))
        return {"FINISHED"}

    def drawMenu(fileProps, self, context):
        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"
        props = layout.operator("weed.close_file",
                                text = "Save",
                                icon = 'SAVE_COPY')
        props.path = fileProps.path
        props.save_it = True
        props.close_it = False
        props = layout.operator("weed.reload_file",
                                text = "Discard",
                                icon = 'RECOVER_LAST')
        props.path = fileProps.path
        #props.save_it = False
        #props.close_it = False
        layout.separator()
        props = layout.operator("weed.close_file",
                                text = "Save and Close",
                                icon = 'SAVE_AS')
        props.path = fileProps.path
        props.save_it = True
        props.close_it = True
        props = layout.operator("weed.close_file",
                                text = "Discard and Close",
                                icon = 'X')
        props.path = fileProps.path
        props.save_it = False
        props.close_it = True


class CloseFile(bpy.types.Operator):
    bl_idname = "weed.close_file"
    bl_label = "Save and Close File"
    bl_description = "Save the file and unlink from the text editor"
    bl_options = {"REGISTER"}

    path = StringProperty(name = "Path", default = "")
    save_it = BoolProperty(name = "Save", default = False)
    close_it = BoolProperty(name = "Close", default = False)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        for text in bpy.data.texts:
            if text.filepath == self.path:
                if self.save_it:
                    save_text_block(text)
                context.space_data.text = text
                if self.close_it:
                    bpy.ops.text.unlink()
        try: bpy.ops.text.resolve_conflict(resolution = "IGNORE")
        except: pass
        return {"FINISHED"}


class FileMenuOpener(bpy.types.Operator):
    bl_idname = "weed.open_file_menu"
    bl_label = "Open File Menu"

    path = StringProperty(name = "Path", default = "")

    def invoke(self, context, event):
        context.window_manager.popup_menu(self.drawMenu,
                                          title = basename(self.path))
        return {"FINISHED"}

    def drawMenu(fileProps, self, context):
        layout = self.layout
        layout.alignment = "RIGHT"
        layout.operator_context = "INVOKE_DEFAULT"
        props = layout.operator("weed.open_file",
                                icon = "FILE_FOLDER",
                                text="Open file")
        props.path = dirname(fileProps.path)
        props = layout.operator("weed.open_external_file_browser",
                                icon = "EXPORT",
                                text="Open on editor")
        props.path = dirname(fileProps.path)
        props = layout.operator("weed.rename_file",
                                icon = "GHOST",
                                text = "Rename file")
        props.path = fileProps.path
        props = layout.operator("weed.delete_file",
                                icon = "CANCEL",
                                text = "Delete file")
        props.path = fileProps.path


class AddonMenuOpener(bpy.types.Operator):
    bl_idname = "weed.open_addon_menu"
    bl_label = "Open Addon Menu"

    directory = StringProperty(name = "Path", default = "")

    def invoke(self, context, event):
        context.window_manager.popup_menu(self.drawMenu,
                                          title = 'Addon Menu')
        return {"FINISHED"}

    def drawMenu(dirProps, self, context):
        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"
        layout.prop(get_addon_preferences(), 'show_dot_addons',
                 text='Show hidden addons')
        # RECUERDA, para enviar argumentos...
        # op = layout.operator("weed.renam...
        # op.directory = dirProps.directory
        layout.operator_menu_enum("weed.new_addon", "new_addon_type",
                                    icon = "NEWFOLDER",
                                    text = "Create New Addon")
        layout.operator("weed.rename_addon",
                            icon = "GHOST", #"PLUS",
                            text = "Rename Addon")
        layout.operator("weed.delete_addon", # delete_addon
                            icon = "CANCEL",
                            text = "Delete Addon")
        layout.separator()
        layout.operator("weed.run_addon",
                            icon = "PLAY",
                            text = "Run")
        layout.operator("weed.unregister_addon",
                            icon = "GO_LEFT",
                            text = "UnReg")
        layout.operator("weed.export_addon",
                            icon = "EXPORT",
                            text = "Zip")
        layout.operator("weed.restart_blender",
                            icon = "BLENDER")


class DirMenuOpener(bpy.types.Operator):
    bl_idname = "weed.open_dir_menu"
    bl_label = "Open Folder Menu"

    directory = StringProperty(name = "Path", default = "")

    def invoke(self, context, event):
        context.window_manager.popup_menu(self.drawMenu,
                                          title = "in {} folder".format(
                                          split(dirname(self.directory))[-1]))
        return {"FINISHED"}

    def drawMenu(parent, self, context):
        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"
        layout.prop(get_addon_preferences(), 'show_dot_files',
                 text='Show hidden addons')
        op = layout.operator("weed.new_file",
                            icon = "NEW",
                            text = "Create new file")
        op.directory = parent.directory
        op = layout.operator("weed.new_directory",
                            icon = "NEWFOLDER",
                            text = "Create new folder")
        op.directory = parent.directory
        layout.separator()
        if split(parent.directory.rstrip(sep))[0] != addons_path:
            op = layout.operator("weed.rename_directory",
                                icon = "GHOST",
                                text = "Rename folder")
            op.base_dir, op.actual_name = split(
                                        parent.directory.rstrip(sep))
            op = layout.operator("weed.delete_directory",
                                 icon = "CANCEL",
                                 text = "Delete folder")
            op.directory = parent.directory
        else:
            op = layout.operator("weed.save_files",
                    text = 'Save all "{}" open files'.format(get_addon_name()[:15]),
                    icon = 'IMGDISPLAY')

        #op1.enabled = op2.enabled = True if (
                #split(parent.directory.rstrip(sep))[0] != addons_path
                #) else False

        #if split(parent.directory.rstrip(sep))[0] != addons_path:
        #    op1.enabled = op2.enabled = True
        #else:
        #    op1.enabled = op2.enabled = False


class OpenFile(bpy.types.Operator):
    bl_idname = "weed.open_file"
    bl_label = "Open File"
    bl_description = "Load the file into the text editor"
    bl_options = {"REGISTER"}

    path = StringProperty(name = "Path", default = "")

    def execute(self, context):
        text = None
        for text_block in bpy.data.texts:
            if text_block.filepath == self.path:
                text = text_block
                break
        if not text:
            text = bpy.data.texts.load(self.path, internal = False)

        context.space_data.text = text
        return {"FINISHED"}


class ReloadFile(bpy.types.Operator):
    bl_idname = "weed.reload_file"
    bl_label = "Reload File"
    bl_description = "Reload current file"
    bl_options = {"REGISTER"}

    path = StringProperty(name = "Path", default = "")

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


class OpenExternalFileBrowser(bpy.types.Operator):
    bl_idname = "weed.open_external_file_browser"
    bl_label = "Open External File Browser"
    bl_description = ""
    bl_options = {"REGISTER"}

    path = StringProperty(name = "Directory", default = "")

    def execute(self, context):
        bpy.ops.wm.path_open(filepath = self.directory)
        return {"FINISHED"}


class RenameFile(bpy.types.Operator):
    bl_idname = "weed.rename_file"
    bl_label = "Open External File Browser"
    bl_description = ""
    bl_options = {"REGISTER"}

    path = StringProperty(name = "Directory", default = "")
    new_name = StringProperty(name = "Directory", description = "New file name", default = "")

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


class DeleteFile(bpy.types.Operator):
    bl_idname = "weed.delete_file"
    bl_label = "Delete File"
    bl_description = "Delete file on the hard drive"
    bl_options = {"REGISTER"}

    path = StringProperty(name = "Directory", default = "")

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        os.remove(self.path)
        context.area.tag_redraw()
        return {"FINISHED"}


class SaveFiles(bpy.types.Operator):
    bl_idname = "weed.save_files"
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


class ConvertAddonIndentation(bpy.types.Operator):
    bl_idname = "weed.convert_addon_indentation"
    bl_label = "Convert Addon Indentation"
    bl_description = ""
    bl_options = {"REGISTER"}

    old_indentation = StringProperty(default = "\t")
    new_indentation = StringProperty(default = "    ")

    @classmethod
    def poll(cls, context):
        return current_addon_exists()

    def execute(self, context):
        paths = self.get_addon_files()
        for path in paths:
            bpy.ops.weed.convert_file_indentation(
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


class ExportAddon(bpy.types.Operator):
    bl_idname = "weed.export_addon"
    bl_label = "Export Addon"
    bl_description = "Save a .zip file of the addon"
    bl_options = {"REGISTER"}

    filepath = StringProperty(subtype = "FILE_PATH")

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


class RunAddon(bpy.types.Operator):
    bl_idname = "weed.run_addon"
    bl_label = "Run Addon"
    bl_description = "Unregister, reload and register it again."
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return current_addon_exists()

    def execute(self, context):
        bpy.ops.weed.save_files()

        addon_name = get_addon_name()
        module = sys.modules.get(addon_name)
        if module:
            addon_utils.disable(addon_name)
            importlib.reload(module)
        addon_utils.enable(addon_name)
        return {"FINISHED"}


class UnregisterAddon(bpy.types.Operator):
    bl_idname = "weed.unregister_addon"
    bl_label = "Unregister Addon"
    bl_description = "Unregister only."
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return current_addon_exists()

    def execute(self, context):
        bpy.ops.weed.save_files()

        addon_utils.disable(get_addon_name())
        return {"FINISHED"}


class RestartBlender(bpy.types.Operator):
    bl_idname = "weed.restart_blender"
    bl_label = "Restart Blender"
    bl_description = "Close and open a new Blender instance to test the Addon on the startup file. (Currently only supported for windows)"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return sys.platform == "win32"

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        bpy.ops.weed.save_files()
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

# def get_addon_name():
#     return get_settings().addon_name

def get_addon_name():
    return bpy.context.scene.explorer_root_folder

#def save_text_block(text_block):
#    if not text_block: return
#    if not exists(text_block.filepath): return

#    file = open(text_block.filepath, mode = "w")
#    file.write(text_block.as_string())
#    file.close()

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