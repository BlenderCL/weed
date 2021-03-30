import bpy

def weed_menu(self, context):
    layout = self.layout
    layout.menu('WEED_MT_main_menu', text=' Weed', icon='FILE_SCRIPT')
    layout.separator()

def icon_get_menu(self, context):
    # iv.icons_show
    layout = self.layout
    layout.operator_context = 'INVOKE_DEFAULT'
    icon_show = layout.operator('iv.icons_show', text='get icon ID', icon='IMAGE_DATA')
    # icon_show.instance = icon_show

class WEED_MT_main_menu(bpy.types.Menu):
    bl_label = 'Weed Menu'
    # bl_idname = 'OBJECT_MT_custom_menu'
    bl_idname = 'WEED_MT_main_menu'
    # bl_idname = 'weed.main_menu'
    bl_options = {'REGISTER'}

    def draw(self, context):
        layout = self.layout


class WEED_PT_main_panel(bpy.types.Panel):
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_label = "Weed IDE"
    bl_category = "Weed"
    bl_options = {'DEFAULT_CLOSED'}

def register():
    bpy.utils.register_class(WEED_MT_main_menu)
    bpy.types.TEXT_MT_context_menu.append(weed_menu)
    bpy.types.TEXT_MT_view.append(weed_menu)
    if bpy.context.preferences.addons.get('development_icon_get'):
        bpy.types.TEXT_MT_context_menu.append(icon_get_menu)
        bpy.types.TEXT_MT_view.append(icon_get_menu)

def unregister():
    bpy.types.TEXT_MT_view.remove(weed_menu)
    bpy.types.TEXT_MT_context_menu.remove(weed_menu)
    bpy.utils.unregister_class(WEED_MT_MainMenu)
    if bpy.context.preferences.addons.get('development_icon_get'):
        bpy.types.TEXT_MT_context_menu.remove(icon_get_menu)
        bpy.types.TEXT_MT_view.remove(icon_get_menu)




# def register():
#     # bpy.types.TEXT_MT_toolbox.append(right_click_menu_extension)  
#     # bpy.types.TEXT_MT_format.append(format_menu_extension) 
#     # bpy.types.TEXT_MT_view.prepend(autocomplete_menu)
#     # bpy.types.TEXT_MT_toolbox.prepend(autocomplete_menu)
#     # bpy.types.TEXT_MT_toolbox.append(rmb_weed_context)
#     bpy.utils.register_class(WEED_MT_main_menu)
#     bpy.types.TEXT_MT_context_menu.append(weed_menu)
#     bpy.types.TEXT_MT_view.append(weed_menu)
    
# def unregister():
#     # bpy.types.TEXT_MT_toolbox.remove(right_click_menu_extension)  
#     # bpy.types.TEXT_MT_format.remove(format_menu_extension)
#     # bpy.types.TEXT_MT_view.remove(autocomplete_menu)
#     # bpy.types.TEXT_MT_toolbox.remove(autocomplete_menu)
#     bpy.types.TEXT_MT_view.remove(weed_menu)
#     bpy.types.TEXT_MT_context_menu.remove(weed_menu)
#     bpy.utils.unregister_class(WEED_MT_MainMenu)


# def rmb_weed_context(self, context):
#     layout = self.layout
#     layout.operator_context = 'INVOKE_DEFAULT'
#     #layout.menu('WEED_MT_main_menu', text='Weed Blender IDE', icon='FORCE_SMOKEFLOW')
#     #layout.separator()
#     layout.separator()
#     layout.operator('weed.icons_dialog',
#                     text='Insert Icon ID',
#                     icon='PASTEDOWN')
#     layout.operator('weed.popup_api_navigator',
#                     text='Popup Api Navigator',
#                     icon='OOPS')
#     code_editors = context.window_manager.code_editors
#     if str(context.area) in code_editors.keys():
#         layout.operator("weed.view_code_tree", text='View Code Tree', icon='OOPS')
#     else:
#         layout.label(text='View Code Tree', icon='OOPS')
#         layout.label(text='View Code Tree', icon='OOPS')

    # bpy.types.TEXT_MT_toolbox.remove(rmb_weed_context)

        # if prefs.show_code_editor:
        #     #layout.label(text='Text Editor Tools', icon='SYNTAX_ON')
        #     code_editors = context.window_manager.code_editors
        #     if str(context.area) in code_editors.keys():
        #         layout.operator('weed.code_editor_end',
        #                         text = 'Exit Code Editor',
        #                         icon = 'PANEL_CLOSE')
        #     else:
        #         layout.operator('weed.code_editor_start',
        #                         text = 'Start Code Editor',
        #                         icon = 'SYNTAX_ON')

        # # RuntimeError: Calling operator
        # # "bpy.ops.weed.is_running" error,
        # # can't modify blend data in this state (drawing/rendering)

        # # if bpy.ops.weed.is_running() == { 'FINISHED' }:
        # #     layout.operator("weed.stop_auto_completion",
        # #                     text = 'Stop Auto Complete',
        # #                     icon = "PANEL_CLOSE")
        # # else:
        # #     layout.operator("weed.start_auto_completion",
        # #                     text = 'Start Auto Complete',
        # #                     icon = "LIBRARY_DATA_DIRECT")
        # if prefs.show_bge_console:
        #     objects = bpy.data.objects
        #     scene = bpy.context.scene
        #     layout.separator()
        #     #layout.label(text='BGE Console', icon='CONSOLE')
        #     if '!BgeCon' in objects:
        #         if '!BgeCon' in scene.objects:
        #             #layout.label(text='Attach Bge Console',
        #             #             icon='NONE')
        #             layout.operator('weed.dettach_bge_console',
        #                             text='Dettach Bge Console',
        #                             icon='ZOOMOUT')
        #             layout.operator('weed.remove_bge_console',
        #                             text='Remove Bge Console',
        #                             icon='PANEL_CLOSE')
        #         else:
        #             layout.operator('weed.attach_bge_console',
        #                             text='Attach Bge Console',
        #                             icon='CONSOLE')
        #             #layout.label(text='Dettach Bge Console',
        #             #             icon='NONE')
        #             layout.operator('weed.remove_bge_console',
        #                             text='Remove Bge Console',
        #                             icon='PANEL_CLOSE')
        #     else:
        #             layout.operator('weed.attach_bge_console',
        #                             text='Attach Bge Console',
        #                             icon='CONSOLE')
        #             #layout.label(text='Dettach Bge Console',
        #             #             icon='NONE')
        #             #layout.label(text='Remove Bge Console',
        #             #             icon='NONE')

        # layout.separator()
        # layout.operator('weed.insert_breakpoint',
        #                 text = 'Insert pudb Breakpoint here',
        #                 icon = 'RECOVER_AUTO')
        # layout.operator('weed.search_breakpoint',
        #                 text = 'Search pudb Breakpoint',
        #                 icon = 'VIEWZOOM')
