import os
import sys
import pkgutil
import importlib

textchars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})

def is_binary_file(filepath):
    bytes = open(filepath, 'rb').read(512)
    return bool(bytes.translate(None, textchars))

def setup_addon_modules(path, package_name, reload):
    """
    Imports and reloads all modules in this addon.

    path -- __path__ from __init__.py
    package_name -- __name__ from __init__.py
    """
    # Import from a static curated list
    #    than the function get_submodule_names
    # used before

    #def get_submodule_names(path = path[0], root = ""):
    #    module_names = []
    #    for importer, module_name, is_package in pkgutil.iter_modules([path]):
    #        if is_package:
    #            sub_path = os.path.join(path, module_name)
    #            sub_root = root + module_name + "."
    #            module_names.extend(get_submodule_names(sub_path, sub_root))
    #        else:
    #            module_names.append(root + module_name)
    #    return module_names

    def import_submodules(names):
        modules = []
        for name in names:
            modules.append(importlib.import_module("." + name, package_name))
        return modules

    def reload_modules(modules):
        for module in modules:
            importlib.reload(module)

    # names = get_submodule_names()
    names = [
        #'bge_console.bgeCon',                      # no need to register
        #'checksumdir',                             # no need to register
        #'developer_utils',                         # no need to register
        #'graphics',                                # no need to register
        #'modal_handler',                           # no need to register
        #'name_utils',                              # no need to register
        #'operators.api_context_operators',         # no need to register
        #'operators.assign_or_compare_operators',   # no need to register
        #'operators.bpy_ops_operators',             # no need to register
        #'operators.dynamic_snippets_operators',    # no need to register
        #'operators.extend_word_operators',         # no need to register
        #'operators.operator_hub',                  # no need to register
        #'operators.parameter_operators',           # no need to register
        #'operators.suggestions_from_before',       # no need to register
        #'text_block',                              # no need to register
        #'text_editor_utils',                       # no need to register
        #'text_operators',                          # no need to register
        'bge_console.console',                      # register this module
        'debugger_tools.pudb_wrapper',              # register this module
        'documentation',                            # register this module
        'expression_utils',                         # register this module
        'insert_templates_via_ui',                  # register this module
        'prefs',                                    # register this module
        'quick_operators',                          # register this module
        'text_editor_tools.api_navigator',          # register this module
        'text_editor_tools.code_editor',            # register this module
        'text_editor_tools.code_tree',              # register this module
        'text_editor_tools.find_replace',           # register this module
        'text_editor_tools.icons_get',              # register this module
        'ui',                                       # register this module
        'weed_tools'                                # register this module
    ]
    modules = import_submodules(names)
    if reload:
        reload_modules(modules)
    return modules