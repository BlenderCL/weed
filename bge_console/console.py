import bpy
from os import path

def createBgeCon():
    bpy.ops.object.empty_add(type = 'SPHERE',
                            view_align = False,
                            location = (0, 0, 0),
                            layers = (True, True, True, True, True,
                                    True, True, True, True, True,
                                    True, True, True, True, True,
                                    True, True, True, True, True))
    obj = bpy.context.object

    obj.name = "!BgeCon"
    sens = obj.game.sensors
    conts = obj.game.controllers
    props = obj.game.properties

    # Properties
    bpy.ops.object.game_property_new(name = 'blink',
                                    type = 'BOOL')
    props.get('blink').value = True
    bpy.ops.object.game_property_new(name = 'repeat_timer',
                                    type = 'TIMER')
    props.get('repeat_timer').value = 0.0
    bpy.ops.object.game_property_new(name = 'repeat_delay',
                                    type = 'FLOAT')
    props.get('repeat_delay').value = 0.4

    # Logic Brick
    bpy.ops.logic.sensor_add(type = 'DELAY',
                            name = 'init',
                            object = '!BgeCon')
    sens[-1].show_expanded = False
    sens[-1].delay = 10
    sens[-1].duration = 1
    bpy.ops.logic.controller_add(type = 'PYTHON',
                                name = 'init',
                                object = '!BgeCon')
    conts[-1].show_expanded = False
    conts[-1].mode = 'MODULE'
    conts[-1].module = 'bgeCon.register_draw'
    sens[-1].link(conts[-1])

    # Logic Brick
    bpy.ops.logic.sensor_add(type = 'ALWAYS',
                            name = 'blink',
                            object = '!BgeCon')
    sens[-1].show_expanded = False
    sens[-1].use_pulse_true_level = True
    sens[-1].tick_skip = 20
    bpy.ops.logic.controller_add(type = 'PYTHON',
                                name = 'doBlink',
                                object = '!BgeCon')
    conts[-1].show_expanded = False
    conts[-1].mode = 'MODULE'
    conts[-1].module = 'bgeCon.blink'
    sens[-1].link(conts[-1])

    # Logic Brick
    bpy.ops.logic.sensor_add(type = 'KEYBOARD',
                            name = 'any_key',
                            object = '!BgeCon')
    sens[-1].show_expanded = False
    sens[-1].use_all_keys = True
    sens[-1].use_pulse_true_level = True
    sens[-1].tick_skip = 3
    bpy.ops.logic.controller_add(type = 'PYTHON',
                                name = 'getText',
                                object = '!BgeCon')
    conts[-1].show_expanded = False
    conts[-1].mode = 'MODULE'
    conts[-1].module = 'bgeCon.main'
    sens[-1].link(conts[-1])


class AttachBgeConsole(bpy.types.Operator):
    """Attach Bge Console to actual scene"""
    bl_idname = "weed.attach_bge_console"
    bl_label = "Attach Bge Console to actual Scene."
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        objects = bpy.data.objects
        scene = bpy.context.scene
        # Avoid duplicates
        if '!BgeCon' in objects:
            if '!BgeCon' not in scene.objects:
                scene.objects.link(objects['!BgeCon'])
            else:
                pass
        else:
            if 'bgeCon.py' not in bpy.data.texts:
                bgeCon_file = path.normpath(path.dirname(__file__) + path.sep + 'bgeCon.py')
                bpy.data.texts.load(bgeCon_file)
            createBgeCon()        
        return {'FINISHED'}


class DettachBgeConsole(bpy.types.Operator):
    """Dettach Bge Console from actual scene"""
    bl_idname = "weed.dettach_bge_console"
    bl_label = "Dettach Bge Console from actual Scene."
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        objects = bpy.data.objects
        scene = bpy.context.scene
        if '!BgeCon' in objects:
            if '!BgeCon' in scene.objects:
                scene.objects.unlink(objects['!BgeCon'])
            else:
                pass
        else:
            pass        
        return {'FINISHED'}


class RemoveBgeConsole(bpy.types.Operator):
    """Remove Bge Console from actual blend file"""
    bl_idname = "weed.remove_bge_console"
    bl_label = "Remove Bge Console from actual blend file."
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        objects = bpy.data.objects
        scene = bpy.context.scene
        if 'bgeCon.py' in bpy.data.texts:
            bpy.data.texts.remove(bpy.data.texts['bgeCon.py'])
        if '!BgeCon' in objects:
            obj = objects['!BgeCon']
            for group in obj.users_group:
                group.objects.unlink(obj)
            for scene in obj.users_scene:
                scene.objects.unlink(obj)
            if obj.users == 0:
                bpy.data.objects.remove(obj)    
        else:
            pass        
        return {'FINISHED'}


"""
def bge_menu(self, context):
    layout = self.layout
    layout.operator_context = 'INVOKE_DEFAULT'
    layout.label(text="BGE Console", icon='CONSOLE')
    layout.operator(AttachBgeConsole.bl_idname,
                    text='Attach Bge Console',
                    icon='NONE')
    layout.operator(DettachBgeConsole.bl_idname,
                    text='Dettach Bge Console',
                    icon='NONE')
    layout.operator(RemoveBgeConsole.bl_idname,
                    text='Remove Bge Console',
                    icon='NONE')
    layout.separator()
"""

    
def register():
    bpy.utils.register_class(AttachBgeConsole)
    bpy.utils.register_class(DettachBgeConsole)
    bpy.utils.register_class(RemoveBgeConsole)
    #bpy.types.WEED_MT_main_menu.append(bge_menu)

def unregister():
    #bpy.types.WEED_MT_main_menu.remove(bge_menu)
    bpy.utils.unregister_class(RemoveBgeConsole)
    bpy.utils.unregister_class(DettachBgeConsole)
    bpy.utils.unregister_class(AttachBgeConsole)
