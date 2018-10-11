import bpy
from . modal_handler import ModalHandler
from . text_editor_utils import *
from . documentation import get_documentation

running = False
def start():
    global running
    running = True
def stop():
    global running
    running = False


class IsRunningAutoCompletion(bpy.types.Operator):
    bl_idname = "weed.is_running"
    bl_label = "is running"

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        global running
        if running:
            return { "FINISHED" }
        else:
            return { "CANCELLED" }


class StartAutoCompletion(bpy.types.Operator):
    bl_idname = "weed.start_auto_completion"
    bl_label = "Start"
    
    @classmethod
    def poll(cls, context):
        return not running
    
    def modal(self, context, event):
        if not running or event.type == "F8":
            self.modal_handler.free()
            return { "FINISHED" }
    
        block_event = False
        if active_text_block_exists():
            context.area.tag_redraw()
            block_event = self.modal_handler.update(event)
            
        if not block_event:
            return { "PASS_THROUGH" }
        return { "RUNNING_MODAL" }

    def invoke(self, context, event):
        get_documentation().build_if_necessary()
        self.modal_handler = ModalHandler()
        context.window_manager.modal_handler_add(self)
        start()
        return { "RUNNING_MODAL" }


class RebuildDocumentation(bpy.types.Operator):
    bl_idname = "weed.rebuild_documentation"
    bl_label = "Reload API"
    
    @classmethod
    def poll(cls, context):
        return get_documentation().is_build
    
    def execute(self, context):
        get_documentation().build()
        return { "FINISHED" }


class StopAutoCompletion(bpy.types.Operator):
    bl_idname = "weed.stop_auto_completion"
    bl_label = "Stop"
    
    @classmethod
    def poll(cls, context):
        return running
    
    def execute(self, context):
        stop()
        return { "FINISHED" }   


class CodeAutocompleteMenu(bpy.types.Menu):
    bl_label = 'Code Autocomplete Menu'
    bl_idname = 'autocomplete_MT_main_menu'
    bl_options = {'REGISTER'}

    def draw(self, context):
        #global running
        #prefs = bpy.context.user_preferences.addons['weed'].preferences
        #layout = self.layout

        #if prefs.show_code_editor:
        #    layout.label(text='Text Editor Tools', icon='SYNTAX_ON')

        layout = self.layout
        if running: 
            layout.operator("weed.stop_auto_completion", icon = "PANEL_CLOSE")
        else: layout.operator("weed.start_auto_completion", icon = "LIBRARY_DATA_DIRECT")
        if get_documentation().is_build:
            layout.operator("weed.rebuild_documentation", icon='FILE_REFRESH')
        layout.operator("weed.correct_whitespaces", icon='ALIGN')


class WEED_MT_MainMenu(bpy.types.Menu):
    bl_label = 'Weed Menu'
    # bl_idname = 'OBJECT_MT_custom_menu'
    bl_idname = 'WEED_MT_main_menu'
    bl_options = {'REGISTER'}

    def draw(self, context):
        #if 'weed' not in bpy.context.user_preferences.addons.keys():
        #    return
        #scene = bpy.context.scene
        global running
        prefs = bpy.context.user_preferences.addons['weed'].preferences
        layout = self.layout

        if prefs.show_code_editor:
            #layout.label(text='Text Editor Tools', icon='SYNTAX_ON')
            if str(context.area) in context.window_manager.code_editors:
                layout.operator('weed.code_editor_end',
                                text = 'Exit Code Editor',
                                icon = 'PANEL_CLOSE')
            else:
                layout.operator('weed.code_editor_start',
                                text = 'Start Code Editor',
                                icon = 'SYNTAX_ON')

        # RuntimeError: Calling operator
        # "bpy.ops.weed.is_running" error,
        # can't modify blend data in this state (drawing/rendering)

        # if bpy.ops.weed.is_running() == { 'FINISHED' }:
        #     layout.operator("weed.stop_auto_completion",
        #                     text = 'Stop Auto Complete',
        #                     icon = "PANEL_CLOSE")
        # else:
        #     layout.operator("weed.start_auto_completion",
        #                     text = 'Start Auto Complete',
        #                     icon = "LIBRARY_DATA_DIRECT")
        if prefs.show_bge_console:
            objects = bpy.data.objects
            scene = bpy.context.scene
            layout.separator()
            #layout.label(text='BGE Console', icon='CONSOLE')
            if '!BgeCon' in objects:
                if '!BgeCon' in scene.objects:
                    #layout.label(text='Attach Bge Console',
                    #             icon='NONE')
                    layout.operator('weed.dettach_bge_console',
                                    text='Dettach Bge Console',
                                    icon='ZOOMOUT')
                    layout.operator('weed.remove_bge_console',
                                    text='Remove Bge Console',
                                    icon='PANEL_CLOSE')
                else:
                    layout.operator('weed.attach_bge_console',
                                    text='Attach Bge Console',
                                    icon='CONSOLE')
                    #layout.label(text='Dettach Bge Console',
                    #             icon='NONE')
                    layout.operator('weed.remove_bge_console',
                                    text='Remove Bge Console',
                                    icon='PANEL_CLOSE')
            else:
                    layout.operator('weed.attach_bge_console',
                                    text='Attach Bge Console',
                                    icon='CONSOLE')
                    #layout.label(text='Dettach Bge Console',
                    #             icon='NONE')
                    #layout.label(text='Remove Bge Console',
                    #             icon='NONE')

        layout.separator()
        layout.operator('weed.insert_breakpoint',
                        text = 'Insert pudb Breakpoint here',
                        icon = 'RECOVER_AUTO')
        layout.operator('weed.search_breakpoint',
                        text = 'Search pudb Breakpoint',
                        icon = 'VIEWZOOM')

        ## use an operator enum property to populate a sub-menu
        #layout.operator_menu_enum('object.select_by_type',
        #                          property='type',
        #                          text='Select All by Type...',
        #                          )

        ## call another menu
        #layout.operator('wm.call_menu', text='Unwrap').name = 'VIEW3D_MT_uv_map'
