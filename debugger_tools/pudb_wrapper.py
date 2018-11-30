import bpy
#from os import path, listdir
#from shutil import copytree, rmtree
#from site import getsitepackages, getusersitepackages
#import sys

# hacer un decorador para todo el proceso de lanzar
# el breakpoint. ## TODO ##
#breakpoint_text = '''
#{0}breakpoint.here ##### from here PuDB debugger start
#'''

# Ultimate all proof breakpoint with validation
#exec('try:breakpoint.here\nexcept:print("# weed breakpoint lefted here")')
breakpoint_text = "{0}exec('try:breakpoint.here\\nexcept:pass')\n"

# breakpoint = '''
# {0}###  W E E D  ########################################################
# {0}import pudb  #########################################################
# {0}global _MODULE_SOURCE_CODE  ##########################################
# {0}_MODULE_SOURCE_CODE = pudb.get_code(__file__)  #######################
# {0}pu.db  ################################################ Breakpoint ###
# 
# '''

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
        #sd.find_text = '###  W E E D'
        sd.find_text = 'breakpoint.here'
        sd.use_find_all = True
        #bpy.ops.text.jump(line=1)
        try:
            bpy.ops.text.find()
            bpy.ops.text.move(type='LINE_BEGIN')
            bpy.ops.text.move_select(type = 'NEXT_LINE')
            #brk_end = sd.text.lines[sd.text.current_line_index + 4].body.rstrip()
            # if (sd.text.current_character != sd.text.select_end_character and
            #             'Breakpoint' in brk_end):
            #     #bpy.ops.text.find_set_selected()
            #     bpy.ops.text.move(type='LINE_BEGIN')
            #     bpy.ops.text.move_select(type = 'NEXT_LINE')
            #     bpy.ops.text.move_select(type = 'NEXT_LINE')
            #     bpy.ops.text.move_select(type = 'NEXT_LINE')
            #     bpy.ops.text.move_select(type = 'NEXT_LINE')
            #     ##bpy.ops.text.move_select(type = 'LINE_END')
            #     bpy.ops.text.move_select(type = 'NEXT_LINE')
            #     #bpy.ops.text.cut()
            #     #bpy.context.window_manager.clipboard = ''
        except RuntimeError:
            self.report({'INFO'}, 'It seems that there is no any open text')
        except IndexError:
            self.report({'INFO'}, 'It seems that is an empty text')
        finally:
            return {'FINISHED'}

"""
# there are global site-packages lib folder for python, and
# there are user site-packages lib folder too...
# in some Blender installs global site-packages may not have
# permissions...
# right now using user site-packages folder
# (folder has permission, but it's a folder outside blender,
# in the user folder)

# user site package
site_package = getusersitepackages()

# global site package
#for site_package in getsitepackages():
#    if path.basename(site_package) == 'site-packages':
#        break


# registro automatico con register_module
# register y unregister comentados
    
def register():
    # register with the proper site_package folder 
    # revisar algun mecanismo para no reinstalar estas librerias
    # cada vez...
    libs = path.join(path.dirname(__file__), 'sitepackages_libs')
    for lib in listdir(libs):
        #print(lib)
        try:
            rmtree(path.join(site_package, lib), ignore_errors=True)
            copytree(path.join(libs, lib), path.join(site_package, lib))
        except:
            print('Unexpected error:', sys.exc_info()[0])
            print('weed Blender IDE: fail to install ', lib,
                ', debugger tools may not function properly')
    bpy.utils.register_class(InsertBreakpoint)
    bpy.utils.register_class(SearchBreakpoint)


def unregister():
    # continue with the proper site_package folder 
    libs = path.join(path.dirname(__file__), 'sitepackages_libs')
    for lib in listdir(libs):
        #print(lib)
        try:
            rmtree(path.join(site_package, lib))
            #copytree(path.join(libs, lib), path.join(site_package, lib))
        except:
            print('Unexpected error:', sys.exc_info()[0])
            print('weed Blender IDE:', lib, 'fail to uninstall',
                ', debugger tools could have left python modules')
    bpy.utils.unregister_class(SearchBreakpoint)
    bpy.utils.unregister_class(InsertBreakpoint)

# registro automatico con register_module
# register y unregister comentados
"""    


"""
INTEGRAR AHORA

## get from blender code
def get_code(filepath):
    import bpy, os.path
    try:
        import bge
        if hasattr(bge, 'is_fake'):
            print('# bge fake')
            in_game = False
        else:
            print('# bge real')
            in_game = True
    except ImportError:
        print('# bge not present')
        in_game = False
    if in_game:
        import bge
        script = bge.logic.getCurrentController().script
        if len(script.splitlines()) == 1:
            print('# bge module type controller call')
            script = script[:script.find('.')] + '.py'
            return bpy.data.texts[script].as_string()
        else:
            print('# bge script type controller call')
            return script
    else:
        try:
            print('# script open in collection bpy.data.texts')
            script = os.path.basename(filepath)
            return bpy.data.texts[script].as_string()
        except:
            print('# read script from disk')
            return open(filepath).read()

        # if hasattr(bpy, 'data') and hasattr(bpy.data, 'texts'):
        #     print('# commonly [alt]-[p] regular blender script')
        #     script = os.path.basename(filepath)
        #     return bpy.data.texts[script].as_string()
        # else:
        #     print('# inside restricted, like register addon')
        #     return open(filepath).read()


    ## show locals from caller stack
    @property
    def here(self):
        #"#""Print the local variables in the caller's frame."#""
        import inspect
        frame = inspect.currentframe()
        print('trying...')
        try:
            print(frame.f_back.f_locals['__file__'], 'being debbuged...')
            print()
        finally:
            del frame
"""

