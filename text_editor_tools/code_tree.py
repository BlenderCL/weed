class AddonFilesPanel(bpy.types.Panel):
    bl_idname = "code_tree_panel"
    bl_label = "Code Tree"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"

    #@classmethod
    #def poll(cls, context):
    #    return current_addon_exists()

    def draw(self, context):
        layout = self.layout
        layout.alignment = "LEFT"
        #addon_path = get_current_addon_path()

        #row = layout.row(align=False)
        #row.prop(get_addon_preferences(), 'show_dot_files',
        #         text='', icon='FILE_HIDDEN')
        #row.operator("code_autocomplete.save_files",
        #             text='Save all {} files'.format(get_addon_name()[:15]),
        #             icon='SAVE_COPY')
        box = layout.box()
        self.draw_directory(box, addon_path)

    def draw_directory(self, layout, directory):
        if not self.is_directory_visible(directory):
            row = layout.row(align=True)
            row.alignment = "LEFT"
            op = row.operator("code_autocomplete.toogle_directory_visibility",
                              text=os.path.split(directory[:-1])[-1],
                              icon="FILESEL",
                              emboss=False)
            op.directory = directory
        else:
            split = layout.split(0.9)
            row = split.row(align=True)
            row.alignment = "LEFT"
            op = row.operator("code_autocomplete.toogle_directory_visibility",
                              text=os.path.split(directory[:-1])[-1],
                              icon="FILE_FOLDER",
                              emboss=False)
            op.directory = directory
            op = split.operator("code_autocomplete.open_dir_menu",
                                icon="COLLAPSEMENU",
                                text="",
                                emboss=False)
            op.directory = directory

            directory_names = get_directory_names(directory)
            split = layout.split(0.02)
            split.label('')
            col = split.column(align=True)
            col.alignment = "LEFT"
            # row = col.row(align=True)
            # row.alignment = "LEFT"

            for directory_name in directory_names:
                self.draw_directory(col, directory + directory_name + os.sep)

            file_names = get_file_names(directory)
            texts_paths = {text.filepath: text for text in bpy.data.texts}
            for file_name in file_names:
                full_path = directory + file_name
                split = col.split(0.8)
                row = split.row(align=True)
                row.alignment = "LEFT"
                props = row.operator("code_autocomplete.open_file_menu",
                                     icon="DISCLOSURE_TRI_RIGHT",
                                     text="",
                                     emboss=False)
                props.path = full_path
                op = row.operator("code_autocomplete.open_file",
                                  icon="FILE_TEXT",
                                  text=file_name,
                                  emboss=False)
                op.path = full_path
                if full_path == get_current_filepath():
                    split.label("", icon="GREASEPENCIL")
                else:
                    split.label("", icon="NONE")
                if full_path in texts_paths:
                    if texts_paths[full_path].is_dirty:
                        # call menu save/discard
                        props = split.operator(
                            'code_autocomplete.close_file_menu',
                            icon='HELP',
                            text='',
                            emboss=False)
                        props.path = full_path
                    else:
                        # close quietly
                        props = split.operator('code_autocomplete.close_file',
                                               text='',
                                               icon='PANEL_CLOSE',
                                               emboss=False)
                        props.path = full_path
                        props.save_it = False
                        props.close_it = True

    def is_directory_visible(self, directory):
        return directory_visibility[directory]


def code_tree_popup(self, context):
    icons = {'import': 'LAYER_ACTIVE',
             'class': 'OBJECT_DATA',
             'def': 'SCRIPTPLUGINS'}
    layout = self.layout
    layout.operator_context = 'EXEC_DEFAULT'
    col = layout.column(align=True)
    tot_imports = len(bpy.types.Text.code_tree['imports'])
    for i, (idx, indnt, (keyword, name, args)) in enumerate(
            bpy.types.Text.code_tree['imports']):
        # row = row if i%2 else layout.row(align=True)
        prop = col.operator('text.jump',
                            text=name,
                            icon=icons[keyword],
                            emboss=True)
        prop.line = idx + 1

    for idx, indnt, (keyword, name, args) in bpy.types.Text.code_tree[
        'class_def']:
        # if not indnt:
        #    col.separator()
        prop = col.operator('text.jump',
                            text='·   ' * indnt + name,
                            icon=icons[keyword] if not indnt else 'NONE',
                            emboss=True)
        prop.line = idx + 1
        prev_indnt = indnt

