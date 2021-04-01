import bpy
import re

def timer(func, *args, delay=0, init=False):
    if init:
        func(*args)
        return
    bpy.app.timers.register(lambda: timer(func, *args, init=True),
                            first_interval=delay)

# class CodeTree:
    # code_tree = { "context.space_data.text.as_pointer" :
    #                   { line_n : ('name', 'type', 'indnt', 'open', 'low_limit', 'upper_limit') } }
class CodeTreeManager(dict):
    __slots__ = ('__dict__',)


    class CodeTreeNode(object):
        __slots__ = ('code', 'code_type', 'indnt', 'expanded', 'low_limit', 'upper_limit')

        def __init__(self, code, code_type, indnt = 0, expanded = None):
            self.code = code
            self.code_type = code_type
            self.indnt = indnt
            self.expanded = expanded
            self.low_limit = 0
            self.upper_limit = 0

        def __repr__(self):
            return (f"(code:{self.code}, "
                    f"code_type:{self.code_type}, "
                    f"indnt:{self.indnt}, "
                    f"expanded:{self.expanded}, "
                    f"low_limit:{self.low_limit}, "
                    f"upper_limit:{self.upper_limit})")


    def __init__(self):
        super(__class__, self).__init__()
        self.__dict__ = self
        self.indent_with = 4 # bpy.context.space_data.tab_width

    def gcollect(self):
        act_txts = {f"code_tree_{txt.as_pointer()}" for txt in bpy.data.texts}
        for code_tree in (*self.keys(),):
            if code_tree not in act_txts:
                del self[code_tree]

    def nuke(self):
        self.clear()

    def update_code_tree(self, context):
        if not hasattr(context, 'edit_text'):
            return None
        handle_id = f"code_tree_{context.edit_text.as_pointer()}"
        handle = self.get(handle_id)

        if (not handle
                or handle[-1] != len(context.edit_text.lines)):
            self.gcollect()  # remove closed code_trees
            self[handle_id] = handle = self.build_code_tree(context)
            context.area.tag_redraw()
        return handle

    def build_code_tree(self, context):
        ptrn = re.compile('(class|def|import|from)\s([^\s\(:]+)([^:]+)?')

        # code_tree = { "context.space_data.text.as_pointer" :
        #                   { line_n : ('name', 'type', 'indnt', 'open', 'low_limit', 'upper_limit') } }
        code_tree = { -1 : len(context.edit_text.lines),
                       0 : self.CodeTreeNode('imports', 'imports', 0, False) }
        prev_code_tree = self.get(f"code_tree_{context.edit_text.as_pointer()}")
        self.indent_with = bpy.context.space_data.tab_width

        first_match = True
        for ln, line in enumerate(context.edit_text.lines):
            code = line.body.lstrip()
            indnt = int((len(line.body) - len(code)) / self.indent_with)
            match = re.match(ptrn, code)
            last_match = sorted(code_tree.keys())[-1]
            ln += 1
            if match:
                if (match.group(1) == 'import'
                     or match.group(1) == 'from'):
                    code_tree[ln] = self.CodeTreeNode(code, 'import', 1, None)
                else:    
                    if (not first_match
                         and  indnt > code_tree[last_match].indnt):
                        if (prev_code_tree
                            and prev_code_tree.get(ln)
                            and code == prev_code_tree.get(ln).code):
                            code_tree[last_match].expanded = prev_code_tree.get(ln).expanded
                        else:
                            code_tree[last_match].expanded = False

                    code_tree[ln] = self.CodeTreeNode(match.group(2), match.group(1), indnt, None)
                    code_tree[last_match].low_limit = ln
                    first_match = False


            code_tree[last_match].upper_limit = ln + 1

        return code_tree            


# handle keyboard events in text editor to update
class WEED_OT_code_tree_textinput_event(bpy.types.Operator):
    bl_idname = "weed.code_tree_textinput_event"
    bl_label = "Text Input"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if getattr(context, 'edit_text', False):
            event = WEED_OT_code_tree_event_catcher(context.window)
            if event:
                #breakpoint.here
                bpy.types.Text.code_tree_manager.update_code_tree(context)


# catch the event so it can be accessed outside of operators
class WEED_OT_code_tree_event_catcher(bpy.types.Operator):
    bl_idname = "weed.code_tree_event_catcher"
    bl_label = "Event Catcher"
    bl_options = {'INTERNAL'}

    import _bpy  # use call instead of bpy.ops to reduce overhead
    call = _bpy.ops.call
    del _bpy

    def __new__(cls, window):
        timer(cls.call, cls.__name__, {'window': window}, {}, 'INVOKE_DEFAULT')
        return getattr(cls, 'event', None)

    def invoke(self, context, event):
        __class__.event = event
        return {'CANCELLED'}


class WEED_OT_code_tree_jump(bpy.types.Operator):

    'Go to line and select in text editor'
    bl_idname = 'weed.code_tree_jump'
    bl_label = 'Jump Here'
    line: bpy.props.IntProperty()
    last_line: bpy.props.IntProperty()
    do_nothing: bpy.props.BoolProperty(default = False)

    def execute(self, context):
        if self.do_nothing:
            return {'CANCELLED'}

        if self.last_line:
            self.line = self.last_line
        if context.area.spaces[0].text.lines[self.line - 1].body:
            oldfind = context.area.spaces[0].find_text
            oldwrap = bpy.context.space_data.use_find_wrap
            oldcase = bpy.context.space_data.use_match_case
            context.space_data.use_find_wrap = True
            context.space_data.use_match_case = True
            while context.area.spaces[0].text.current_line_index+1 != self.line:
                context.area.spaces[0].find_text = context.area.spaces[0].text.lines[self.line - 1].body
                bpy.ops.text.find()

            context.area.spaces[0].find_text = oldfind
            context.space_data.use_find_wrap = oldwrap
            context.space_data.use_match_case = oldcase

        self.last_line = 0
        context.scene.CodeNavLineNum = self.line
        return {'FINISHED'}


class WEED_OT_code_tree_expand(bpy.types.Operator):
    bl_idname = "weed.code_tree_expand"
    bl_label = "Expand Code Tree Node"
    bl_description = ""
    bl_options = {"REGISTER"}

    line : bpy.props.IntProperty(name = "line", default = 0)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        handle_id = f"code_tree_{context.edit_text.as_pointer()}"
        code_tree = bpy.types.Text.code_tree_manager[handle_id]
        code_tree[self.line].expanded = not code_tree[self.line].expanded
        return {"FINISHED"}


class WEED_PT_code_tree(bpy.types.Panel):
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_label = "Code Tree"
    bl_category = "Weed"
    bl_options = {'DRAW_BOX'}

    # @classmethod
    # def poll(cls, context):
    #     return True

    def draw(self, context):
        wm = context.window_manager
        layout = self.layout

        icons = { 'imports' : 'OUTLINER_OB_GROUP_INSTANCE',
                  'imports_open' : 'GROUP',
                  'import' : 'OUTLINER_OB_GROUP_INSTANCE',
                  'expanded' : 'TRIA_DOWN',
                  'closed' : 'TRIA_RIGHT',
                  'class' : 'PACKAGE', 'class_open' : 'UGLYPACKAGE',
                  'def' : 'RADIOBUT_ON', 'def_open' : 'RADIOBUT_OFF'}
        #layout.operator_context = 'EXEC_DEFAULT'
        col = layout.column(align=True)
        col.alignment = 'LEFT'
        col.label(icon = 'FILE_TEXT', text = context.space_data.text.name)
        col.separator()
        #col.template_ID(context.space_data, "text")

        subnode_closed = False
        node_indnt = 0
        active = getattr(bpy.context.space_data, "text", None)

        handle_id = f"code_tree_{context.edit_text.as_pointer()}"
        ctm = bpy.types.Text.code_tree_manager
        if not ctm.get(handle_id):
            ctm.gcollect()  # remove closed code_trees
            ctm[handle_id] = ctm.build_code_tree(context)
            # context.area.tag_redraw() # maybe to an tab UI

        # >>> for i, (ln, o) in enumerate(sorted(c.items())[1:]):
        # ...     print(i, ln, o)
        for i, (ln, code_tree_node) in enumerate(sorted(ctm[handle_id].items())[1:]):
            if subnode_closed and code_tree_node.indnt > node_indnt:
                continue
            if code_tree_node.low_limit <= active.current_line_index < code_tree_node.upper_limit:
                col2 = col.box()
            else:
                col2 = col
            if code_tree_node.indnt > 0:
                indent = col2.split(factor=(0.03 + code_tree_node.indnt * 0.01) * code_tree_node.indnt)
                indent.label(text='')
                row = indent.row(align=True)
            else:
                row = col2.row(align=True)
            row.alignment = 'LEFT'
            if code_tree_node.expanded is not None:
                tggl = row.operator("weed.code_tree_expand",
                                 text = '',
                                 icon = icons['expanded']
                                        if code_tree_node.expanded
                                        else icons['closed'],
                                 emboss = False)
                tggl.line = ln
                if code_tree_node.expanded:
                    subnode_closed = False
                else:
                    subnode_closed = True
                node_indnt = code_tree_node.indnt
            else:
                #row.label(text = '', icon = 'NONE')
                row.operator("weed.code_tree_expand",
                             text = '',
                             icon = 'BLANK1',
                             emboss = False)
            icon = code_tree_node.code_type + ('_open'
                                             if code_tree_node.expanded
                                             else '')
            prop = row.operator('weed.code_tree_jump',
                                text = code_tree_node.code,
                                icon = icons[icon],
                                emboss = False)
            prop.line = ln




classes = (
    WEED_OT_code_tree_textinput_event,
    WEED_OT_code_tree_event_catcher,
    WEED_OT_code_tree_jump,
    WEED_OT_code_tree_expand,
    WEED_PT_code_tree
)

def register():
    # from bpy.types import Screen, TEXT_HT_header
    # from bpy.utils import register_class
    
    bpy.types.Text.code_tree_manager = CodeTreeManager()

    for cls in classes:
        bpy.utils.register_class(cls)

    # TEXT_HT_header.append(CodeEditorPrefs.add_to_header)

    kc = bpy.context.window_manager.keyconfigs.addon.keymaps
    km = kc.get('Text', kc.new('Text', space_type='TEXT_EDITOR'))
    new = km.keymap_items.new
    kmi1 = new('weed.code_tree_textinput_event', 'TEXTINPUT', 'ANY', head=True)

    register.keymaps = ((km, kmi1))

def unregister():
    # bpy.types.TEXT_HT_header.remove(CodeEditorPrefs.add_to_header)

    for km, kmi in register.keymaps:
        km.keymap_items.remove(kmi)
    del register.keymaps


    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    bpy.types.Text.code_tree_manager.nuke()
    del bpy.types.Text.code_tree_manager
