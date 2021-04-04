import sys
from os import path
from os import path, listdir, access, W_OK
from shutil import copytree, rmtree
from . checksumdir import dirhash
from site import getsitepackages, getusersitepackages
import builtins
import bpy

# Ultimate all proof breakpoint with validation
# exec('try:breakpoint.here\nexcept:print("# weed breakpoint lefted here")')
# get lost in the scope
breakpoint_text = 'breakpoint.here\n'
find_breakpoint = 'breakpoint.here'
#breakpoint_text = "exec('try:breakpoint.here\\nexcept:pass')\n"
#find_breakpoint = "exec('try:breakpoint.here"


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
    # try with global site package
    # a folder inside blender (but maybe without permission)
    for site_package in getsitepackages():
        if path.basename(site_package) == 'site-packages':
            break
    print('global site package folder, {}'.format(site_package))
    # test for write access. if fails it gets user site package
    if not access(site_package, W_OK):
        site_package = getusersitepackages()
        print('user site package folder override, {}'.format(site_package))

    # before register module...
    # of pudb_wrapper, install python low level libraries
    #############################################################
    # register with the proper site_package folder (*md5sum tal vez?)
    # definir mecanismo, no reinstalar estas librerias cada vez...
    md5_hashes = {
            'bpython'  : 'a8071668c3e8f4932d35ca43476336a3',
            'colorama' : '3743e16974a48b497ed64312987f8949',
            'pudb'     : '574c7d70267988255fde242d0ed30ef3',
            'pygments' : '21f797c1d16df6fa412644f319278145',
            'urwid'    : 'ad93d4f9533c4a77f512feb6492bd598'
            }
    src_libs_path = path.join(path.dirname(__file__),
                        'sitepackages_libs')
    trgt_libs_list = listdir(site_package)
    for lib in sorted(md5_hashes.keys()):
        if not lib in trgt_libs_list:
            print(lib, 'module is not present, will be installed')
            copytree(path.join(src_libs_path, lib),
                     path.join(site_package, lib))
        elif md5_hashes[lib] != dirhash(path.join(site_package, lib), 'md5',
                                excluded_extensions=['pyc', 'gitignore'],
                                excluded_files=['pudb.cfg',
                                                'saved_breakpoints'
                                ]):
            print(lib, 'module maybe is outdated, will be replaced')
            md5_hash = dirhash(path.join(site_package, lib), 'md5',
                                excluded_extensions=['pyc', 'gitignore'],
                                excluded_files=['pudb.cfg',
                                                'saved_breakpoints'
                                ])
            print('md5 hash was', md5_hash)
            rmtree(path.join(site_package, lib), ignore_errors=True)
            copytree(path.join(src_libs_path, lib),
                     path.join(site_package, lib))
        else:
            print(lib, "module it's already installed")


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
            bpy.ops.text.insert(text = indent + breakpoint_text)
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
        sd.find_text = find_breakpoint
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


def pudb_menu(self, context):
    layout = self.layout
    layout.operator_context = 'INVOKE_DEFAULT'
    layout.label(text="PuDB debugger", icon='VIEW_PAN')
    layout.operator(InsertBreakpoint.bl_idname,
                    text='Insert PuDB breakpoint',
                    icon='NONE')
    layout.operator(SearchBreakpoint.bl_idname,
                    text='Search PuDB breakpoint',
                    icon='NONE')
    # layout.separator()


def register():
    _install_low_level_libs()
    builtins.__dict__["breakpoint"] = BreakpointShortcut()
    bpy.utils.register_class(InsertBreakpoint)
    bpy.utils.register_class(SearchBreakpoint)
    bpy.types.WEED_MT_main_menu.append(pudb_menu)

def unregister():
    bpy.types.WEED_MT_main_menu.remove(pudb_menu)
    bpy.utils.unregister_class(SearchBreakpoint)
    bpy.utils.unregister_class(InsertBreakpoint)
    try:
        builtins.__dict__.pop("breakpoint")
    except KeyError:
        self.report({'INFO'}, 'breakpoint caller, already removed from builtins')


