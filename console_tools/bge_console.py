import bpy
from os import path

def createBgeCon():
    if 'bgeCon.py' not in bpy.data.texts:
        bgeCon_file = path.normpath(path.dirname(__file__) + path.sep + 'bgeCon.py')
        bpy.data.texts.load(bgeCon_file)
    # guardar nombre coleccion activa
    # hacer lo mismo para objeto activo, tal vez
    active_collection = bpy.context.view_layer.active_layer_collection
    active_object = bpy.context.view_layer.objects.active
    selected_objects = bpy.context.view_layer.objects.selected.values()
    # crear coleccion !BgeCon
    bgecon = bpy.data.collections.new('!BgeCon') 
    # añadir coleccion !BgeCon a la escena activa
    bpy.context.scene.collection.children.link(bgecon)
    # poner coleccion !BgeCon como activa
    bgecon = bpy.context.view_layer.layer_collection.children.get('!BgeCon')
    bpy.context.view_layer.active_layer_collection = bgecon
    # crear objeto
    bpy.ops.object.empty_add(type = 'SPHERE',
                            align = 'WORLD',
                            location = (0, 0, 0)
                            )
    obj = bpy.context.object

    obj.name = "!BgeCon"
    # arreglar aca
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
    
    # volver a la coleccion activa anterior
    bpy.context.view_layer.active_layer_collection = active_collection
    bpy.context.view_layer.objects.active = active_object
    obj.select_set(False)
    for obj in selected_objects:
        obj.select_set(True)

class RemoveBgeConsole(bpy.types.Operator):
    """Remove Bge Console from actual blend file"""
    bl_idname = "weed.remove_bge_console"
    bl_label = "Remove Bge Console from actual blend file."
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        bgecon_txt = bpy.data.texts.get('bgeCon.py')
        bgecon_obj = bpy.data.objects.get('!BgeCon')
        bgecon_coll = bpy.data.collections.get('!BgeCon')
        if bgecon_txt:
            bpy.data.texts.remove(bgecon_txt)
        if bgecon_obj:
            bpy.data.objects.remove(bgecon_obj)
        if bgecon_coll:
            bpy.data.collections.remove(bgecon_coll)    
        return {'FINISHED'}


class DettachBgeConsole(bpy.types.Operator):
    """Dettach Bge Console from actual scene"""
    bl_idname = "weed.dettach_bge_console"
    bl_label = "Dettach Bge Console from actual Scene."
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        sce_collections = bpy.context.scene.collection.children
        if '!BgeCon' in sce_collections.keys():
                sce_collections.unlink(bpy.data.collections['!BgeCon'])
        return {'FINISHED'}


class AttachBgeConsole(bpy.types.Operator):
    """Attach Bge Console to actual scene"""
    bl_idname = "weed.attach_bge_console"
    bl_label = "Attach Bge Console to actual Scene."
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        bgecon = bpy.data.collections.get('!BgeCon')
        sce_collection = bpy.context.scene.collection.children
        # Avoid duplicates
        if bgecon and '!BgeCon' not in sce_collection.keys():
            sce_collection.link(bpy.data.collections['!BgeCon'])
        else:
            createBgeCon()        
        return {'FINISHED'}


def bge_menu(self, context):
    layout = self.layout
    layout.operator_context = 'INVOKE_DEFAULT'
    layout.label(text="BGE Console", icon='CONSOLE')
    sce_bgecon = bpy.context.scene.collection.children.get('!BgeCon')
    glb_bgecon = bpy.data.collections.get('!BgeCon')
    if sce_bgecon:
        layout.label(text='Attach Bge Console',
                    icon='NONE')
        layout.operator(DettachBgeConsole.bl_idname,
                    text='Dettach Bge Console',
                    icon='NONE')
        layout.operator(RemoveBgeConsole.bl_idname,
                    text='Remove Bge Console',
                    icon='NONE')
    elif glb_bgecon:
        layout.operator(AttachBgeConsole.bl_idname,
                    text='Attach Bge Console',
                    icon='NONE')
        layout.label(text='Dettach Bge Console',
                    icon='NONE')
        layout.operator(RemoveBgeConsole.bl_idname,
                    text='Remove Bge Console',
                    icon='NONE')
    else:
        layout.operator(AttachBgeConsole.bl_idname,
                    text='Attach Bge Console',
                    icon='NONE')
        layout.label(text='Dettach Bge Console',
                    icon='NONE')
        layout.label(text='Remove Bge Console',
                    icon='NONE')
        #layout.separator()

def register():
    bpy.utils.register_class(RemoveBgeConsole)
    bpy.utils.register_class(DettachBgeConsole)
    bpy.utils.register_class(AttachBgeConsole)
    bpy.types.WEED_MT_main_menu.append(bge_menu)

def unregister():
    bpy.types.WEED_MT_main_menu.remove(bge_menu)
    bpy.utils.unregister_class(AttachBgeConsole)
    bpy.utils.unregister_class(DettachBgeConsole)
    bpy.utils.unregister_class(RemoveBgeConsole)
    
