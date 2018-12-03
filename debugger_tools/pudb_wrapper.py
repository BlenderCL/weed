import bpy

# Ultimate all proof breakpoint with validation
# exec('try:breakpoint.here\nexcept:print("# weed breakpoint lefted here")')
# get lost in the scope
# breakpoint_text = "{0}exec('try:breakpoint.here\\nexcept:pass')\n"
breakpoint_text = "{0}breakpoint.here\n"


class InsertBreakpoint(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "weed.insert_breakpoint"
    bl_label = "Insert pudb Breakpoint"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        try:
            line = context.space_data.text.current_line.body
            indent = line[:len(line) - len(line.lstrip())]
            bpy.ops.text.move(type = 'LINE_BEGIN')
            bpy.ops.text.insert(text = breakpoint_text.format(indent))
        except AttributeError:
            self.report({'INFO'}, 'It seems that there is no any open text')
        return {'FINISHED'}


class SearchBreakpoint(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "weed.search_breakpoint"
    bl_label = "Search for Breakpoint"

    @classmethod
    def poll(cls, context):
        return context.space_data.type == 'TEXT_EDITOR'

    def execute(self, context):
        sd = context.space_data
        sd.find_text = 'breakpoint.here'
        sd.use_find_all = True
        try:
            bpy.ops.text.find()
            if sd.text.current_line_index:
                bpy.ops.text.move(type='LINE_BEGIN')
                bpy.ops.text.move_select(type = 'NEXT_LINE')
        except RuntimeError:
            self.report({'INFO'}, 'It seems that there is no any open text')
        except IndexError:
            self.report({'INFO'}, 'It seems that is an empty text')
        finally:
            return {'FINISHED'}

