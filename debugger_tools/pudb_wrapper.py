import bpy
import sys
from os import path, listdir, access, W_OK
from shutil import copytree, rmtree
from . checksumdir import dirhash
from site import getsitepackages, getusersitepackages

# Ultimate all proof breakpoint with validation
# >>> breakpoint.here if 'breakpoint' in __builtins__.__dict__ else None
# get lost in the scope
breakpoint_text = 'breakpoint.here\n'
find_breakpoint = 'breakpoint.here'


CURRENT_DEBUGGER = []

def _get_debugger(**kwargs):
    if not CURRENT_DEBUGGER:
        from pudb.debugger import Debugger
        dbg = Debugger(**kwargs)

        CURRENT_DEBUGGER.append(dbg)
        return dbg
    else:
        return CURRENT_DEBUGGER[0]


def _install_low_level_libs():
    _low_level_libs = {
        'rich'     : 'git+https://github.com/BlenderCL/rich.git', # .:'rich', 
        'textual'  : 'git+https://github.com/BlenderCL/textual.git', 
        'colorama' : 'git+https://github.com/BlenderCL/colorama.git', 
        'urwid'    : 'git+https://github.com/BlenderCL/urwid.git',
        'bpython'  : 'git+https://github.com/BlenderCL/bpython.git',
        'pudb'     : 'git+https://github.com/BlenderCL/pudb.git', # .:'pudb',
    }
    # check pip
    try:
        __import__('imp').find_module('pip')
        # from pip import _vendor
    except ImportError:
        # pip not intalled; install & upgrade
        import ensurepip
        ensurepip.bootstrap()
    else:
        # pip installed
        print('# pip installed')
        pass
    # import ensurepip
    # ensurepip.bootstrap()

    from pip._internal import main as pipmain
    pipmain(['install', '--upgrade', 'pip'])
    pipmain(['install', '--upgrade', 'wheel'])
    # old_argv = sys.argv
    # import runpy
    # sys.argv = [old_argv[0], 'install', '--upgrade', 'pip']
    # runpy.run_module('pip' , run_name='__main__')
    # sys.argv = [old_argv[0], 'install', '--upgrade', 'wheel']
    # runpy.run_module('pip' , run_name='__main__')
    # sys.argv = old_argv
    # install low level libs
    for lib in _low_level_libs:
        # sys.argv = [old_argv[0], 'install', _low_level_libs[lib]]
        # runpy.run_module('pip' , run_name='__main__')
        # sys.argv = old_argv
        try:
            __import__('imp').find_module(lib)
        except:
            pipmain(['install', '--upgrade', _low_level_libs[lib]])
            # print(lib, ' not installed !' )
        else:
            # lib already installed
            #print(lib, ' installed' )
            pass
    

class BreakpointShortcut(object):
    @property
    def here(self):
        #"#""Print the local variables in the caller's frame."#""
        import inspect
        frame = inspect.currentframe().f_back

        if ('__file__' in frame.f_locals
                and frame.f_locals['__file__']):
            caller_file = frame.f_locals['__file__']
        else:
            caller_file = frame.f_code.co_filename
        script = path.basename(caller_file)    
        # down here in code, can come up bugs in a near future ;) .
        # bpy.data.texts.keys() -->
        # ['__init__.py', '__init__.py.001', ...]
        if hasattr(bpy.data, 'texts') and script in bpy.data.texts:
            dbg_code = bpy.data.texts[script].as_string()
        elif path.isfile(caller_file):
            dbg_code = open(caller_file).read()
        elif caller_file == '<blender_console>':
            return '# put breakpoints on code, not on python console'
        elif caller_file == '<console>':
            return '# put breakpoints on code, not on python console (or bge)'
        else:
            dbg_code = '# cannot get source code...'
        #try:
        #    dbg_code = bpy.data.texts[script].as_string()
        #except:
        #    dbg_code = open(caller_file).read()
        frame.f_globals['_MODULE_SOURCE_CODE'] = dbg_code

        dbg = _get_debugger()
        
        # del inspect frame
        del frame
        from pudb import set_interrupt_handler
        import threading
        if isinstance(threading.current_thread(), threading._MainThread):
            set_interrupt_handler()
        dbg.set_trace(sys._getframe().f_back)


class WEED_OT_insert_breakpoint(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "weed.insert_breakpoint"
    bl_label = "Insert pudb Breakpoint"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        try:
            line = context.space_data.text.current_line.body
            indent = line[:len(line) - len(line.lstrip())]
            bpy.ops.text.move(type = 'LINE_BEGIN')
            bpy.ops.text.insert(text = indent + breakpoint_text)
        except AttributeError:
            #self.report({'INFO'}, 'It seems that there is no any open text')
            pass
        return {'FINISHED'}


class WEED_OT_search_breakpoint(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "weed.search_breakpoint"
    bl_label = "Search for Breakpoint"

    @classmethod
    def poll(cls, context):
        return context.space_data.type == 'TEXT_EDITOR'

    def execute(self, context):
        old_find = context.area.spaces[0].find_text
        old_case = context.space_data.use_match_case
        old_wrap = context.space_data.use_find_wrap
        old_all  = context.space_data.use_find_all

        context.space_data.find_text = find_breakpoint
        context.space_data.use_match_case = True
        context.space_data.use_find_wrap = True
        context.space_data.use_find_all = True
        
        try:
            bpy.ops.text.find()
            if context.space_data.text.current_line_index:
                bpy.ops.text.move(type='LINE_BEGIN')
                bpy.ops.text.move_select(type = 'NEXT_LINE')
        except RuntimeError:
            #self.report({'INFO'}, 'It seems that there is no any open text')
            pass
        except IndexError:
            #self.report({'INFO'}, 'It seems that is an empty text')
            pass
        finally:
            context.area.spaces[0].find_text = old_find
            context.space_data.use_match_case = old_case
            context.space_data.use_find_wrap = old_wrap
            context.space_data.use_find_all = old_all
            return {'FINISHED'}


def pudb_menu(self, context):
    if not hasattr(self,'modules_layout'):
        layout = self.layout 
    else:
        layout = self.modules_layout.box()
    layout.operator_context = 'INVOKE_DEFAULT'
    layout.label(text="PuDB breakpoints", icon='TOOL_SETTINGS')
    layout = layout.column(align=True)
    layout.operator("weed.insert_breakpoint",
                    text='Insert',
                    icon='NONE')
    layout.operator("weed.search_breakpoint",
                    text='Search',
                    icon='NONE')
    # layout.separator()


classes = (
    WEED_OT_insert_breakpoint,
    WEED_OT_search_breakpoint,
)


def register(prefs=True):
    _install_low_level_libs()
    __builtins__["breakpoint"] = BreakpointShortcut()

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.WEED_MT_main_menu.append(pudb_menu)
    bpy.types.WEED_PT_main_panel.append(pudb_menu)


def unregister(prefs=True):
    bpy.types.WEED_PT_main_panel.remove(pudb_menu)
    bpy.types.WEED_MT_main_menu.remove(pudb_menu)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    __builtins__.pop("breakpoint")

    


