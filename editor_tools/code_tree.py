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
    #                   indnt   code_type                                    name
    _ptrn = re.compile('(^\s*)(class|def|import|from\s*\S*\simport)\s+([^\n:\(#]+)')
    #
    #_ptrn = re.compile('(class|def|import|from\s*\S*\simport)\s([^\s\(:]+)([^:]+)?')

    class CodeTreeNode(object):
        __slots__ = ('code_type', 'name', 'indnt', 'expanded', 'upper_limit')

        def __init__(self, code_type, name, indnt = 0, expanded = None):
            self.code_type = code_type
            self.name = name
            self.indnt = indnt
            self.expanded = expanded
            self.upper_limit = 0

        def __repr__(self):
            return (f"(code_type:{self.code_type}, "
                    f"name:{self.name}, "
                    f"indnt:{self.indnt}, "
                    f"expanded:{self.expanded}, "
                    f"upper_limit:{self.upper_limit})")


    def __init__(self):
        super(__class__, self).__init__()
        self.__dict__ = self

    def gcollect(self):
        act_txts = {f"code_tree_{txt.as_pointer()}" for txt in bpy.data.texts}
        for code_tree in (*self.keys(),):
            if code_tree not in act_txts:
                print(f'4.- gcollect eliminando {code_tree}')
                del self[code_tree]

    def nuke(self):
        self.clear()

    def update_code_tree(self, context):
        if not hasattr(context, 'edit_text'):
            return None
        handle_id = f"code_tree_{context.edit_text.as_pointer()}"
        handle = self.get(handle_id)
        print('2.-update code tree')
        if (not handle
                or handle['total_lines'] != len(context.edit_text.lines)):
            print('3.-detectada diferencia')
            self.gcollect()  # remove closed code_trees
            self[handle_id] = handle = self.build_code_tree(context)
            context.area.tag_redraw()
        return handle

    def build_code_tree(self, context):
        print('5.-build code tree')
        return_obj = { 'total_lines' : len(context.edit_text.lines),
                       'tree' : { -1 : self.CodeTreeNode('imports', 'imports', 0, False) }
        }
        code_tree = return_obj['tree']
        prev_code_tree = self.get(f"code_tree_{context.edit_text.as_pointer()}")
        indent_width = bpy.context.space_data.tab_width
        class_def_finded = False

        for ln, line in enumerate(context.edit_text.lines):
            #breakpoint.here
            match = re.match(self._ptrn, line.body)
            # { match.group(1)=indnt, match.group(2)=code_type, match.group(3)=name
            if match:
                last_match = list(code_tree)[-1]
                code_tree[ln] = self.CodeTreeNode(match.group(2),
                                                  match.group(3),
                                                  int(len(match.group(1)) / indent_width),
                                                  None)

                if (match.group(2) == 'import'
                     or match.group(2)[:4] == 'from'):
                    code_tree[ln].code_type = 'import'
                    if not class_def_finded:
                        code_tree[ln].indnt += 1
                    elif code_tree[last_match].code_type != 'import':
                        code_tree[last_match].expanded = False

                else:    
                    class_def_finded = True
                    if code_tree[ln].indnt > code_tree[last_match].indnt:
                        if (prev_code_tree
                            and prev_code_tree.get(ln)
                            and code_tree[ln].name == prev_code_tree[ln].name):
                            code_tree[last_match].expanded = prev_code_tree[ln].expanded
                        else:
                            code_tree[last_match].expanded = False

        lines_matched = list(code_tree.keys())
        # breakpoint.here
        for i, ln in enumerate(lines_matched):
            code_tree[ln].upper_limit = return_obj['total_lines']
            for ln_nxt in lines_matched[i+1:]:
                if code_tree[ln].indnt >= code_tree[ln_nxt].indnt:
                    code_tree[ln].upper_limit = ln_nxt - 1
                    break
        return return_obj            


# handle events in text editor to update code tree
class WEED_OT_code_tree_event(bpy.types.Operator):
    bl_idname = "weed.code_tree_event"
    bl_label = "Text Input"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if getattr(context, 'edit_text', False):
            print('0.-en el contexto adecuado')
            event = WEED_OT_code_tree_event_catcher(context.window)
            if event:
                print('1.-evento capturado')
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

        if self.line == 0:
            bpy.ops.text.move(type='FILE_TOP')
            return {'FINISHED'}
        if self.last_line:
            self.line = self.last_line
        if context.area.spaces[0].text.lines[self.line - 1].body:
            oldfind = context.area.spaces[0].find_text
            oldcase = context.space_data.use_match_case
            oldwrap = context.space_data.use_find_wrap
            oldall  = context.space_data.use_find_all
            context.space_data.use_match_case = True
            context.space_data.use_find_wrap = True
            context.space_data.use_find_all = False
            
            while context.area.spaces[0].text.current_line_index+1 != self.line:
                context.area.spaces[0].find_text = context.area.spaces[0].text.lines[self.line - 1].body
                bpy.ops.text.find()

            context.area.spaces[0].find_text = oldfind
            context.space_data.use_match_case = oldcase
            context.space_data.use_find_wrap = oldwrap
            context.space_data.use_find_all = oldall

        self.last_line = 0
        #context.scene.CodeNavLineNum = self.line
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
        code_tree = bpy.types.Text.code_tree_manager[handle_id]['tree']
        code_tree[self.line].expanded = not code_tree[self.line].expanded
        return {"FINISHED"}

def draw_code_tree_panel(self, context):
    wm = context.window_manager
    layout = self.layout
    icons = {      'imports' : 'OUTLINER_OB_GROUP_INSTANCE',
              'imports_open' : 'GROUP',
                    'import' : 'ASSET_MANAGER',
                  'expanded' : 'DISCLOSURE_TRI_DOWN',
                    'closed' : 'DISCLOSURE_TRI_RIGHT',
                     'class' : 'PACKAGE',
                'class_open' : 'UGLYPACKAGE',
                       'def' : 'LAYER_ACTIVE', 
                  'def_open' : 'LAYER_USED'
            }

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
    for ln, code_tree_node in ctm[handle_id]['tree'].items():
        if subnode_closed and code_tree_node.indnt > node_indnt:
            continue
        if code_tree_node.expanded and ln == active.current_line_index:
            col2 = col.box()
        elif (not code_tree_node.expanded and
            ln <= active.current_line_index <= code_tree_node.upper_limit):
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
            row.label(text = '', icon = 'BLANK1')
            # row.operator("weed.code_tree_expand",
            #       text = '', icon = 'BLANK1' emboss = False).enabled = False
        icon = code_tree_node.code_type + ('_open'
                                            if code_tree_node.expanded
                                            else '')
        prop = row.operator('weed.code_tree_jump',
                            text = code_tree_node.name,
                            icon = icons[icon],
                            emboss = False)
        prop.line = ln + 1


class WEED_OT_code_tree_popup(bpy.types.Operator):
    bl_idname = "weed.code_tree_popup"
    bl_label = "Code Tree popup"
    bl_description = "Code Tree"
    # bl_property = "filter_auto_focus"

    # @classmethod
    # def poll(cls, context):
    #     return hasattr(context.space_data.text,'name')

    draw = draw_code_tree_panel

    def close(self):
        bpy.context.window.screen = bpy.context.window.screen

    def check(self, context):
        return True

    def cancel(self, context):
        print('canceled')

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(
            self, width=250)



class WEED_PT_code_tree(bpy.types.Panel):
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_label = "Code Tree"
    bl_category = "Weed"
    bl_options = {'DRAW_BOX'}

    @classmethod
    def poll(cls, context):
        return hasattr(bpy.context.space_data.text,'name')

    draw = draw_code_tree_panel

def code_tree_menu(self, context):
    layout = self.layout
    layout.operator_context = 'INVOKE_DEFAULT'
    layout.operator('weed.code_tree_popup',
                    text='Code Tree',
                    icon='OUTLINER')


classes = (
    WEED_OT_code_tree_event,
    WEED_OT_code_tree_event_catcher,
    WEED_OT_code_tree_jump,
    WEED_OT_code_tree_expand,
    WEED_OT_code_tree_popup,
    WEED_PT_code_tree
)

def register():
    # from bpy.types import Screen, TEXT_HT_header
    # from bpy.utils import register_class
    
    bpy.types.Text.code_tree_manager = CodeTreeManager()

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TEXT_MT_view.append(code_tree_menu)
    bpy.types.TEXT_MT_context_menu.append(code_tree_menu)
    bpy.types.TEXT_HT_footer.prepend(code_tree_menu)
    # TEXT_HT_header.append(CodeEditorPrefs.add_to_header)

    kc = bpy.context.window_manager.keyconfigs.addon.keymaps
    km = kc.get('Text', kc.new('Text', space_type='TEXT_EDITOR'))
    new = km.keymap_items.new
    kmi1 = new('weed.code_tree_event', 'ACTIONZONE_AREA', 'ANY', head=True) # TEXTINPUT

    register.keymaps = ((km, kmi1),)

def unregister():
    # bpy.types.TEXT_HT_header.remove(CodeEditorPrefs.add_to_header)
    for km, kmi in register.keymaps:
        km.keymap_items.remove(kmi)
    del register.keymaps

    bpy.types.TEXT_MT_context_menu.remove(code_tree_menu)
    bpy.types.TEXT_MT_view.remove(code_tree_menu)
    bpy.types.TEXT_HT_footer.remove(code_tree_menu)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    bpy.types.Text.code_tree_manager.nuke()
    del bpy.types.Text.code_tree_manager
