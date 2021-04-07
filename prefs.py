import bpy

class WeedPreferences(bpy.types.AddonPreferences):
    bl_idname = 'weed'
    for active, module, path in _modules:
        if active:
            exec(f"print('{module}'")

    # # API navigator Prefs
    api_navigator: PointerProperty(type=api_navigator.Preferences)
    # # icon viewer Prefs
    # props_icons_get: PointerProperty(type=PropsIconsGet)
    # # find-replace Prefs
    find_replace: PointerProperty(type=find_replace.Preferences)
    # # code editor props 'coed'
    # coed_last_text: StringProperty(name='last_text', default='')
