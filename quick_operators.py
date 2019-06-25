import bpy
import os
import re
from bpy.props import *
from . text_block import TextBlock

class SolveWhitespaceInconsistency(bpy.types.Operator):
    bl_idname = "weed.correct_whitespaces"
    bl_label = "Correct Whitespaces"
    bl_description = "Convert whitespaces to spaces or tabs"
    
    def execute(self, context):
        if context.edit_text.use_tabs_as_spaces:
            bpy.ops.text.convert_whitespace(type = "SPACES")
        else:
            bpy.ops.text.convert_whitespace(type = "TABS")
        return { "FINISHED" } 

class SelectWholeString(bpy.types.Operator):
    bl_idname = "weed.select_whole_string"
    bl_label = "Select Whole String"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    def execute(self, context):
        text_block = TextBlock.get_active()
        if not text_block: return {"CANCELLED"}
        
        line_text = text_block.current_line
        character_index = text_block.current_character_index
        
        string_letter = text_block.get_string_definition_type(line_text, character_index)
        if string_letter is None: return {"CANCELLED"}
        start, end = text_block.get_range_surrounded_by_letter(line_text, string_letter, character_index)
        if start != end:
            text_block.set_selection_in_line(start, end)
            
        return {"FINISHED"}
        
class SwitchLines(bpy.types.Operator):
    bl_idname = "weed.switch_lines"
    bl_label = "Switch Lines"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    def execute(self, context):
        text_block = TextBlock.get_active()
        if not text_block: return {"CANCELLED"}
        
        line_index = text_block.current_line_index
        if line_index < 1: return {"CANCELLED"}
        line_text = text_block.lines[line_index]
        line_text_before = text_block.lines[line_index - 1]
        
        text_block.set_line_text(line_index, line_text_before)
        text_block.set_line_text(line_index - 1, line_text)
        
        return {"FINISHED"}
         
        
class ConvertFileIndentation(bpy.types.Operator):
    bl_idname = "weed.convert_file_indentation"
    bl_label = "Convert File Indentation"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    path = StringProperty()
    old_indentation = StringProperty(default = "\t")
    new_indentation = StringProperty(default = "    ")
    
    @classmethod
    def poll(cls, context):
        return True
        
    def execute(self, context):
        if not os.path.exists(self.path): return {"CANCELLED"}
        
        old = self.old_indentation
        new = self.new_indentation
        
        file = open(self.path, "r")
        lines = file.readlines()
        file.close()
        
        new_lines = []
        for line in lines:
            new_line = ""
            while line.startswith(old):
                new_line += new
                line = line[len(old):]
            new_line += line.rstrip()
            new_lines.append(new_line)
            
        file = open(self.path, "w")
        file.write("\n".join(new_lines))
        file.close()
        return {"FINISHED"}


class SelectTextBlockMenu(bpy.types.Menu):
    bl_idname = "weed.select_text_block"
    bl_label = "Select Text Block"
    
    def draw(self, context):
        layout = self.layout
        
        if len(bpy.data.texts) == 0:
            layout.label("There are no texts in this file", icon = "INFO")
        else:
            for text in bpy.data.texts:
                operator = layout.operator("weed.open_text_block", text = text.name)
                operator.name = text.name
            
class OpenTextBlock(bpy.types.Operator):
    bl_idname = "weed.open_text_block"
    bl_label = "Open Text Block"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    name = StringProperty()
    
    @classmethod
    def poll(cls, context):
        return hasattr(context.space_data, "text")
    
    def execute(self, context):
        context.space_data.text = bpy.data.texts[self.name]
        return {"FINISHED"}        
               
               
def right_click_menu_extension(self, context):
    layout = self.layout
    layout.separator()
    layout.operator("text.comment")
    layout.operator("text.uncomment")
    
    text_block = TextBlock.get_active()
    if text_block:
        line = text_block.current_line
        match = re.match("def (\w+)\(\):", line)
        if match:
            function_name = match.group(1)
            operator = layout.operator("weed.execute_function")
            operator.filepath = text_block.filepath
            operator.function_name = function_name
    
    
def format_menu_extension(self, context):
    text_block = TextBlock.get_active()
    if text_block:
        layout = self.layout
        operator = layout.operator("weed.convert_addon_indentation")
        if text_block.use_tabs_as_spaces:
            operator.old_indentation = "\t"
            operator.new_indentation = "    "
        else:
            operator.old_indentation = "    "
            operator.new_indentation = "\t"
      
def autocomplete_menu(self, context):
    layout = self.layout
    layout.menu('autocomplete_MT_main_menu',
                text='Code Autocomplete',
                icon='SAVE_COPY')
        
def weed_menu(self, context):
    layout = self.layout
    layout.menu('WEED_MT_main_menu', text=' Weed', icon='FORCE_SMOKEFLOW')

def rmb_weed_context(self, context):
    layout = self.layout
    layout.operator_context = 'INVOKE_DEFAULT'
    #layout.menu('WEED_MT_main_menu', text='Weed Blender IDE', icon='FORCE_SMOKEFLOW')
    #layout.separator()
    layout.separator()
    layout.operator('weed.icons_dialog',
                    text='Insert Icon ID',
                    icon='PASTEDOWN')
    layout.operator('weed.popup_api_navigator',
                    text='Popup Api Navigator',
                    icon='OOPS')
    code_editors = context.window_manager.code_editors
    if str(context.area) in code_editors.keys():
        layout.operator("weed.view_code_tree", text='View Code Tree', icon='OOPS')
    else:
        layout.label(text='View Code Tree', icon='OOPS')


def register_menus():
    bpy.types.TEXT_MT_toolbox.append(right_click_menu_extension)  
    bpy.types.TEXT_MT_format.append(format_menu_extension) 
    bpy.types.TEXT_MT_view.prepend(autocomplete_menu)
    bpy.types.TEXT_MT_toolbox.prepend(autocomplete_menu)
    bpy.types.TEXT_MT_toolbox.append(rmb_weed_context)
    bpy.types.TEXT_MT_toolbox.prepend(weed_menu)
    bpy.types.TEXT_MT_view.prepend(weed_menu)
    
def unregister_menus():
    bpy.types.TEXT_MT_toolbox.remove(right_click_menu_extension)  
    bpy.types.TEXT_MT_format.remove(format_menu_extension)
    bpy.types.TEXT_MT_view.remove(autocomplete_menu)
    bpy.types.TEXT_MT_toolbox.remove(autocomplete_menu)
    bpy.types.TEXT_MT_view.remove(weed_menu)
    bpy.types.TEXT_MT_toolbox.remove(weed_menu)
    bpy.types.TEXT_MT_toolbox.remove(rmb_weed_context)

# def register():
#     bpy.utils.register_class(WEED_MT_MainMenu)
#     bpy.types.TEXT_MT_toolbox.append(rmb_weed_context)
#     bpy.types.TEXT_MT_toolbox.prepend(weed_menu)
#     bpy.types.TEXT_MT_view.prepend(weed_menu)

# def unregister():
#     bpy.types.TEXT_MT_view.remove(weed_menu)
#     bpy.types.TEXT_MT_toolbox.remove(weed_menu)
#     bpy.types.TEXT_MT_toolbox.remove(rmb_weed_context)
#     bpy.utils.unregister_class(WEED_MT_MainMenu)
