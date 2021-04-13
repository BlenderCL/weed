import bpy
from bpy.props import IntProperty
import re
from weed import _icon_types


class CodeTreeManager(dict):
    __slots__ = ('__dict__',)
    #                   indnt   code_type                                    name
    _ptrn = re.compile('(^\s*)(class|def|import|from\s*\S*\simport)\s+([^\n:\(#]+)')


    class CodeTreeNode(object):
        __slots__ = ('code_type', 'name', 'indnt', 'expanded', 'upper_limit', 'upper_limit_expanded')

        def __init__(self, code_type, name, indnt = 0, expanded = None):
            self.code_type = code_type
            self.name = name
            self.indnt = indnt
            self.expanded = expanded
            self.upper_limit = 0
            self.upper_limit_expanded = 0

        def __repr__(self):
            return (f"(code_type:{self.code_type}, "
                    f"name:{self.name}, "
                    f"indnt:{self.indnt}, "
                    f"expanded:{self.expanded}, "
                    f"upper_limit:{self.upper_limit}, "
                    f"upper_limit_expanded:{self.upper_limit_expanded})")

    def __init__(self):
        super(__class__, self).__init__()
        self.__dict__ = self

    def gcollect(self):
        print('gcollect')
        act_txts = {txt.as_pointer() for txt in bpy.data.texts}
        for code_tree in (*self.keys(),):
            if code_tree not in act_txts:
                print(f'code tree {code_tree} eliminado')
                del self[code_tree]

    def nuke(self):
        self.clear()

    def verify_code_tree(self, context):
        #ctm = bpy.types.Text.code_tree_manager
        handle_id = context.edit_text.as_pointer()
        if not self.get(handle_id):
            print('new code tree')
            #ctm.gcollect()  # remove closed code_trees
            self[handle_id] = self.build_code_tree(context)
        elif len(context.edit_text.lines) != self[handle_id]['total_lines']:
            print('remake code tree')
            self.gcollect()  # remove closed code_trees
            self[handle_id] = self.build_code_tree(context)
            # context.area.tag_redraw() # maybe to an tab UI
        return self[handle_id]['tree']

    def build_code_tree(self, context):
        return_obj = { 'total_lines' : len(context.edit_text.lines),
                       'tree' : { -1 : self.CodeTreeNode('imports', 'imports', 0, False) }
        }
        code_tree = return_obj['tree']
        prev_code_tree = self.get(context.edit_text.as_pointer())
        indent_width = bpy.context.space_data.tab_width
        class_def_finded = False
        lines_matched = [-1]

        for ln, line in enumerate(context.edit_text.lines):
            match = re.match(self._ptrn, line.body)
            # { match.group(1)=indnt, match.group(2)=code_type, match.group(3)=name }
            if match:
                last_match = list(code_tree)[-1]
                lines_matched.append(ln)
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
                        code_tree[last_match].expanded = False

        if prev_code_tree:
            prev = list(prev_code_tree['tree'].values())
        for i, ln in enumerate(lines_matched):
            code_tree[ln].upper_limit = return_obj['total_lines']
            code_tree[ln].upper_limit_expanded = return_obj['total_lines']
            # set upper_limit
            for ln_nxt in lines_matched[i+1:]:
                if code_tree[ln].indnt >= code_tree[ln_nxt].indnt:
                    code_tree[ln].upper_limit = ln_nxt - 1
                    break
            # set upper_limit_expanded
            if i+1 < len(lines_matched):
                code_tree[ln].upper_limit_expanded = lines_matched[i+1] - 1
            # get last expanded state
            try:
                if prev[i].expanded:
                    code_tree[ln].expanded = True
            except:
                pass

        return return_obj            


class WEED_OT_code_tree_jump(bpy.types.Operator):
    'Go to line and select in text editor'
    bl_idname = 'weed.code_tree_jump'
    bl_label = 'Jump Here'
    line: IntProperty()
    last_line: IntProperty()

    def execute(self, context):
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
        return {'FINISHED'}


class WEED_OT_code_tree_expand(bpy.types.Operator):
    bl_idname = "weed.code_tree_expand"
    bl_label = "Expand Code Tree Node"
    bl_description = ""
    bl_options = {"REGISTER", "INTERNAL"}

    line : IntProperty(name = "line", default = 0)

    def execute(self, context):
        handle_id = context.edit_text.as_pointer()
        code_tree = bpy.types.Text.code_tree_manager[handle_id]['tree']
        code_tree[self.line].expanded = not code_tree[self.line].expanded
        return {"FINISHED"}


def draw_code_tree_panel(self, context):
    wm = context.window_manager
    st = context.space_data
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
    col.label(icon = _icon_types.get(
                        st.text.name.split('.')[-1].lower(), 'FILE'),
              text = st.text.name)
    col.separator()

    subnode_closed = False
    node_indnt = 0
    active = getattr(st, "text", None)

    code_tree = bpy.types.Text.code_tree_manager.verify_code_tree(context)

    for ln, code_tree_node in code_tree.items():
        if subnode_closed and code_tree_node.indnt > node_indnt:
            continue
        if (code_tree_node.expanded and
            ln <= active.current_line_index <= code_tree_node.upper_limit_expanded):
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
        icon = code_tree_node.code_type + ('_open'
                                            if code_tree_node.expanded
                                            else '')
        prop = row.operator('weed.code_tree_jump',
                            text = code_tree_node.name,
                            icon = icons[icon],
                            emboss = False)
        prop.line = ln + 1
    layout.separator()


class WEED_OT_code_tree_popup(bpy.types.Operator):
    bl_idname = "weed.code_tree_popup"
    bl_label = "Code Tree popup"
    bl_description = "Code Tree"
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(cls, context):
        return hasattr(context.space_data.text,'name')

    draw = draw_code_tree_panel

    def close(self):
        bpy.context.window.screen = bpy.context.window.screen

    def check(self, context):
        return True

    def cancel(self, context):
        return None

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(
            self, width=250)


class WEED_PT_code_tree(bpy.types.Panel):
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_label = "Code Tree"
    bl_category = "Code Tree"
    bl_options = {'HEADER_LAYOUT_EXPAND'}#, 'DRAW_BOX'}
    # bl_options = {'DRAW_BOX'}

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
    WEED_OT_code_tree_jump,
    WEED_OT_code_tree_expand,
    WEED_OT_code_tree_popup,
    WEED_PT_code_tree
)

def register():
    bpy.types.Text.code_tree_manager = CodeTreeManager()

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TEXT_MT_view.append(code_tree_menu)
    bpy.types.TEXT_MT_context_menu.append(code_tree_menu)
    bpy.types.TEXT_HT_footer.append(code_tree_menu)

def unregister():
    bpy.types.TEXT_MT_context_menu.remove(code_tree_menu)
    bpy.types.TEXT_MT_view.remove(code_tree_menu)
    bpy.types.TEXT_HT_footer.remove(code_tree_menu)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    bpy.types.Text.code_tree_manager.nuke()
    del bpy.types.Text.code_tree_manager
