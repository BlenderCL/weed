import bpy

def add_items_from_collection_callback(self, context):
    items = []
    scene = context.scene
    for item in scene.my_items.values():
        items.append((item.some_str, item.some_str, ""))
    return items

class MyEnumItems(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Scene.my_enum_items = bpy.props.PointerProperty(type=MyEnumItems)

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.my_enum_items

    asdf : bpy.props.EnumProperty(
        name="bookmark",
        description="bookmark path",
        # items argument required to initialize, just filled with empty values
        items = add_items_from_collection_callback,
    )


class MyItem(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Scene.my_items = bpy.props.CollectionProperty(type=MyItem)
        bpy.types.Scene.bookmark = bpy.props.StringProperty(
                                        name = "bookmark",
                                        default = "",
                                        subtype = 'DIR_PATH'
                                    )

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.my_items

    some_str : bpy.props.StringProperty(
        name = "bookmark",
        default = "",
        subtype = 'DIR_PATH'
    )

class MY_OT_add_item(bpy.types.Operator):
    ''' add item to bpy.context.scene.my_items '''
    bl_label = "add item"
    bl_idname = "my.add_item"

    def execute(self, context):
        # create a new item, assign its properties
        item = bpy.context.scene.my_items.add()
        item.some_str = "asdf" + str(len(bpy.context.scene.my_items))
        return {'FINISHED'}

class MY_PT_simple_panel(bpy.types.Panel):
    bl_label = "Simple Panel"
    bl_idname = "MY_PT_simple_panel"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "simple panel"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        layout.operator("my.add_item")
        layout.prop(context.scene.my_enum_items, "asdf")
        layout.prop(context.scene, "bookmark")

classes = (MyEnumItems, MyItem, MY_OT_add_item, MY_PT_simple_panel)
register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()