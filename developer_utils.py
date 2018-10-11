import os
import sys
import pkgutil
import importlib

def setup_addon_modules(path, package_name, reload):
    """
    Imports and reloads all modules in this addon. 
    
    path -- __path__ from __init__.py
    package_name -- __name__ from __init__.py
    """
    # Import from a static curated list
    #    than the function get_submodule_names
    
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
        #'bge_console.bgeCon',                      # disabled
        #'developer_utils',                         # disabled
        #'graphics',                                # disabled
        #'modal_handler',                           # disabled
        #'name_utils',                              # disabled
        #'operators.api_context_operators',         # disabled
        #'operators.assign_or_compare_operators',   # disabled
        #'operators.bpy_ops_operators',             # disabled
        #'operators.dynamic_snippets_operators',    # disabled
        #'operators.extend_word_operators',         # disabled
        #'operators.operator_hub',                  # disabled
        #'operators.parameter_operators',           # disabled
        #'operators.suggestions_from_before',       # disabled
        #'text_block',                              # disabled
        #'text_editor_utils',                       # disabled
        #'text_operators',                          # disabled
        'addon_development_manager',                # ok
        'bge_console.console',                      # ok
        'debugger_tools.pudb_wrapper',              # ok
        'documentation',                            # ok
        'expression_utils',                         # ok
        'insert_templates_via_ui',                  # ok
        'prefs',                                    # ok
        'quick_operators',                          # ok
        'text_editor_tools.api_navigator',          # ok
        'text_editor_tools.code_editor',            # ok
        'text_editor_tools.code_tree',              # ok
        'text_editor_tools.find_replace',           # ok
        'text_editor_tools.icons_get',              # ok
        'ui'                                        # ok
    ]
    modules = import_submodules(names)        
    if reload: 
        reload_modules(modules) 
    return modules
