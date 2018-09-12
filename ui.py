"""
bl_info = {
    'name': 'Custom Menu',
    'author': 'Cristian Hasbun',
    'version': (0, 1),
    'blender': (2, 7, 1),
    'location': 'Text Editor > Header > Monkey',
    'description': 'Pack of tools for development...',
    'warning': 'It's very first beta! The addon is in progress!',
    'category': 'Development'}
"""
########## PUAJJJJJ
import bpy


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
        # "bpy.ops.code_autocomplete.is_running" error,
        # can't modify blend data in this state (drawing/rendering)

        # if bpy.ops.code_autocomplete.is_running() == { 'FINISHED' }:
        #     layout.operator("code_autocomplete.stop_auto_completion",
        #                     text = 'Stop Auto Complete',
        #                     icon = "PANEL_CLOSE")
        # else:
        #     layout.operator("code_autocomplete.start_auto_completion",
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
    if str(context.area) in context.window_manager.code_editors:
        layout.operator("weed.view_code_tree", text='View Code Tree', icon='OOPS')
    else:
        layout.label(text='View Code Tree', icon='OOPS')



def register():
    bpy.utils.register_class(WEED_MT_MainMenu)
    bpy.types.TEXT_MT_toolbox.append(rmb_weed_context)
    bpy.types.TEXT_MT_toolbox.prepend(weed_menu)
    bpy.types.TEXT_MT_view.prepend(weed_menu)

def unregister():
    bpy.types.TEXT_MT_view.remove(weed_menu)
    bpy.types.TEXT_MT_toolbox.remove(weed_menu)
    bpy.types.TEXT_MT_toolbox.remove(rmb_weed_context)
    bpy.utils.unregister_class(WEED_MT_MainMenu)

#bpy.ops.code_autocomplete.start_auto_completion()
#bpy.ops.code_autocomplete.correct_whitespaces()

#if __name__ == '__main__':
    #register()
    #unregister()
    # The menu can also be called from scripts
    #bpy.ops.wm.call_menu(name=CustomMenu.bl_idname)
    #bpy.ops.wm.call_menu(name='OBJECT_MT_custom_menu')
