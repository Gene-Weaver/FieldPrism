import os, time, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
try:
    from utils_processing import bcolors
except:
    from fieldprism.utils_processing import bcolors


''' Get DataVault.new_full_name '''

################################################################
# Search and rename
################################################################
def dv_rename_fail(DataVault, file_to_rename, path_search, ext):
    if DataVault.new_full_name == '':
        DataVault.add_process_barcodes([],[])
    
    add_orig_name = DataVault.image_name.split('.')[0]
    new_file_name = ''.join([DataVault.new_full_name, '___',add_orig_name]) #increment_filename_duplicate_barcodes(path_search, DataVault.new_full_name, ext)
    # new_file_name = ''.join([new_full_name, ext])

    success_rename = rename_loop(file_to_rename, new_file_name)
    DataVault.rename = new_file_name
    print(f"{bcolors.OKCYAN}      File Renamed: Original --> {''.join([os.path.basename(os.path.normpath(path_search)), '/', DataVault.image_name, ext])} New --> {''.join([os.path.basename(os.path.normpath(path_search)), '/', new_file_name, ext])}{bcolors.ENDC}")
    return DataVault, success_rename 

def dv_rename_success(DataVault, file_to_rename, path_search, ext):
    # Rename with as much as we can get from the QR code
    if not os.path.exists(os.path.join(path_search, ''.join([DataVault.new_full_name, ext]))):
        success_rename = rename_loop(file_to_rename, os.path.join(path_search, ''.join([DataVault.new_full_name, ext])))
        DataVault.rename = DataVault.new_full_name
        print(f"{bcolors.OKCYAN}      File Renamed: Original --> {''.join([os.path.basename(os.path.normpath(path_search)), '/', DataVault.image_name, ext])} New --> {''.join([os.path.basename(os.path.normpath(path_search)), '/', DataVault.new_full_name, ext])}{bcolors.ENDC}")
    # If the name already exists...
    else:
        add_orig_name = DataVault.image_name.split('.')[0]
        new_file_name = ''.join([DataVault.new_full_name, '___',add_orig_name]) #increment_filename_duplicate_barcodes(path_search, DataVault.new_full_name, ext)
        # new_file_name = ''.join([new_full_name, ext])
        # _head, tail = os.path.split(new_file_name)
        success_rename = rename_loop(file_to_rename, os.path.join(path_search, new_file_name))
        print(f"{bcolors.OKCYAN}      File Renamed: Original --> {''.join([os.path.basename(os.path.normpath(path_search)), '/', DataVault.image_name, ext])} New --> {''.join([os.path.basename(os.path.normpath(path_search)), '/', new_file_name])}{bcolors.ENDC}")
        # DataVault.rename = os.path.basename(tail).split('.')[0]
        DataVault.rename = new_file_name
    return DataVault, success_rename
################################################################
# Rename using DataVaule.rename
################################################################
def dv_rename_fail_short(DataVault, file_to_rename, path_search, ext):
    if DataVault.new_full_name == '':
        DataVault.add_process_barcodes([],[])
    
    new_file_name = ''.join([DataVault.rename, ext])

    success_rename = rename_loop(file_to_rename, new_file_name)
    print(f"{bcolors.OKCYAN}      File Renamed: Original --> {''.join([os.path.basename(os.path.normpath(path_search)), '/', DataVault.image_name, ext])} New --> {''.join([os.path.basename(os.path.normpath(path_search)), '/', new_file_name, ext])}{bcolors.ENDC}")
    return DataVault, success_rename 

def dv_rename_success_short(DataVault, file_to_rename, path_search, ext):
    # Rename with as much as we can get from the QR code
    if not os.path.exists(os.path.join(path_search, ''.join([DataVault.rename, ext]))):
        success_rename = rename_loop(file_to_rename, os.path.join(path_search, ''.join([DataVault.rename, ext])))
        print(f"{bcolors.OKCYAN}      File Renamed: Original --> {''.join([os.path.basename(os.path.normpath(path_search)), '/', DataVault.image_name, ext])} New --> {''.join([os.path.basename(os.path.normpath(path_search)), '/', DataVault.rename, ext])}{bcolors.ENDC}")
    # If the name already exists...
    else:
        add_orig_name = DataVault.image_name.split('.')[0]
        new_file_name = ''.join([DataVault.new_full_name, '___',add_orig_name]) #increment_filename_duplicate_barcodes(path_search, DataVault.new_full_name, ext)
        # new_file_name = ''.join([new_full_name, ext])
        # _head, tail = os.path.split(new_file_name)
        # DataVault.rename_backup = tail.split('.')[0]
        # DataVault.rename_backup_dirs = DataVault.rename_backup_dirs.append(os.path.basename(os.path.normpath(path_search)))
        success_rename = rename_loop(file_to_rename, os.path.join(path_search, new_file_name))
        print(f"{bcolors.OKCYAN}      File Renamed: Original --> {''.join([os.path.basename(os.path.normpath(path_search)), '/', DataVault.image_name, ext])} New --> {''.join([os.path.basename(os.path.normpath(path_search)), '/', new_file_name])}{bcolors.ENDC}")
    return DataVault, success_rename

# def dv_rename_backup(DataVault, file_to_rename, path_search, ext):
#     # Rename with as much as we can get from the QR code
#     if not os.path.exists(os.path.join(path_search, ''.join([DataVault.rename_backup, ext]))):
#         success_rename = rename_loop(file_to_rename, os.path.join(path_search, ''.join([DataVault.rename_backup, ext])))
#         print(f"{bcolors.OKCYAN}      File Renamed: Original --> {''.join([os.path.basename(os.path.normpath(path_search)), '/', DataVault.rename, ext])} New --> {''.join([os.path.basename(os.path.normpath(path_search)), '/', DataVault.rename_backup, ext])}{bcolors.ENDC}")
#     # If the name already exists...
#     else:
#         print(f"{bcolors.WARNING}      File Renamed: Original --> {''.join([os.path.basename(os.path.normpath(path_search)), '/', DataVault.rename, ext])} New --> {''.join([os.path.basename(os.path.normpath(path_search)), '/', DataVault.rename_backup, ext])}{bcolors.ENDC}")
#     return DataVault, success_rename

################################################################

def rename_loop(file_to_rename, new_name):
    success = False
    while not success:
        try:
            os.rename(file_to_rename, new_name)
            success = True
        except Exception as e:
            print("rename fail...")
            time.sleep(0.01)
    return success

def pick_search_dir(option, search_dirs):
    # Searh search_dirs for filename
    if option == 'distortion':
        search_dir = search_dirs[0]
    elif option == 'corrected':
        search_dir = search_dirs[1]
    return search_dir

def increment_filename_duplicate_barcodes(dir_path, new_filename, ext):
    # create a path object for the new filename
    path_new_filename = os.path.join(dir_path, ''.join([new_filename, ext]))

    # check if the new filename already exists in the directory
    if os.path.exists(path_new_filename):
        f_stem = new_filename.split('___DUP')[0]
        try:
            inc = new_filename.split('___DUP')[1]
            inc = int(inc) + 1
            new_filename = os.path.join(dir_path, ''.join([f_stem, '___DUP', str(inc)]))
        except:
            new_filename = os.path.join(dir_path, ''.join([f_stem, '___DUP1']))
        return increment_filename_duplicate_barcodes(dir_path, new_filename, ext)
    else:
        if '___' in new_filename:
            inc = new_filename.split('___DUP')[1]
        else:
            f_stem = new_filename.split('___DUP')[0]
            new_filename = os.path.join(dir_path, ''.join([f_stem, '___DUP1']))
        
        if os.path.exists(os.path.join(dir_path, ''.join([new_filename, ext]))):
            f_stem = new_filename.split('___DUP')[0]
            inc = new_filename.split('___DUP')[1]
            inc = int(inc) + 1
            new_filename = os.path.join(dir_path, ''.join([f_stem, '___DUP', str(inc)]))
            return increment_filename_duplicate_barcodes(dir_path, new_filename, ext)

        return new_filename

def rename_files_from_QR_codes(cfg, option, barcodes_added, Dirs, search_dirs, writing_dirs, DataVault):    
    if not barcodes_added:
        return DataVault
    if not cfg['fieldprism']['QR_codes']['do_rename_images']:
        return DataVault

    search_dir = pick_search_dir(option, search_dirs)
    path_search = os.path.join(Dirs.actual_save_dir, search_dir)

    print(f"{bcolors.OKCYAN}      Renaming File...{bcolors.ENDC}")

    # Search in the labels_txt files
    # If rename, then hold the new name to rename everything else
    files_to_search = os.listdir(path_search)
    if len(files_to_search) > 0:
        files = [os.path.splitext(filename)[0] for filename in files_to_search]
        if DataVault.image_name in files:
            ext = os.path.splitext(files_to_search[files == DataVault.image_name])[1]

            file_to_rename = os.path.join(path_search, ''.join([DataVault.image_name, ext]))
            if not DataVault.rename_success: #if not DataVault.rename_success:
                if cfg['fieldprism']['QR_codes']['do_keep_original_name_if_fail']:
                    pass
                else: 
                    # Rename the default string, check for increment
                    DataVault, success_rename = dv_rename_fail(DataVault, file_to_rename, path_search, ext)
            
            else: 
                DataVault, success_rename = dv_rename_success(DataVault, file_to_rename, path_search, ext)

    # rename everything else
    dirs_to_search = os.listdir(Dirs.actual_save_dir)
    for folder in dirs_to_search:
        if folder != search_dir:
            if folder in writing_dirs:
                path_search = os.path.join(Dirs.actual_save_dir, folder)
                files_to_search = os.listdir(path_search)
                if len(files_to_search) > 0:
                    files = [os.path.splitext(filename)[0] for filename in files_to_search]
                    if DataVault.image_name in files:
                        ext = os.path.splitext(files_to_search[files == DataVault.image_name])[1]

                        file_to_rename = os.path.join(path_search, ''.join([DataVault.image_name, ext]))
                        if not DataVault.rename_success: #if not DataVault.rename_success:
                            if cfg['fieldprism']['QR_codes']['do_keep_original_name_if_fail']:
                                pass
                            else: 
                                # Rename the default string, check for increment
                                DataVault, success_rename = dv_rename_fail_short(DataVault, file_to_rename, path_search, ext)
                        else: 
                            DataVault, success_rename, dv_rename_success_short(DataVault, file_to_rename, path_search, ext)

    # If DataVault.rename_backup == '' then everything went fine
    # If DataVault.rename_backup == 'something' then the image had strange ML predictions and was placed in the not-corrected folder, need to increment all uniformly 
    # if DataVault.rename_backup == '':
    #     return DataVault
    # else:
    #     files_to_search = os.listdir(path_search)
    #     if len(files_to_search) > 0:
    #         files = [os.path.splitext(filename)[0] for filename in files_to_search]
    #         if DataVault.rename in files:
    #             ext = os.path.splitext(files_to_search[files == DataVault.rename])[1]

    #             file_to_rename = os.path.join(path_search, ''.join([DataVault.rename, ext]))

    #             DataVault, success_rename = dv_rename_backup(DataVault, file_to_rename, path_search, ext)
    #             # if not DataVault.rename_success: #if not DataVault.rename_success:
    #             #     if cfg['fieldprism']['QR_codes']['do_keep_original_name_if_fail']:
    #             #         pass
    #             #     else: 
    #             #         # Rename the default string, check for increment
    #             #         DataVault, success_rename = dv_rename_fail(DataVault, file_to_rename, path_search, ext)
                
    #             # else: 
    #             #     DataVault, success_rename = dv_rename_success(DataVault, file_to_rename, path_search, ext)

    #     # rename everything else
    #     dirs_to_search = os.listdir(Dirs.actual_save_dir)
    #     for folder in dirs_to_search:
    #         if folder != DataVault.rename_backup_dirs: # these were already renamed
    #             if folder in writing_dirs:
    #                 path_search = os.path.join(Dirs.actual_save_dir, folder)
    #                 files_to_search = os.listdir(path_search)
    #                 if len(files_to_search) > 0:
    #                     files = [os.path.splitext(filename)[0] for filename in files_to_search]
    #                     if DataVault.rename in files:
    #                         ext = os.path.splitext(files_to_search[files == DataVault.rename])[1]

    #                         file_to_rename = os.path.join(path_search, ''.join([DataVault.rename, ext]))

    #                         DataVault, success_rename = dv_rename_backup(DataVault, file_to_rename, path_search, ext)
    #                         # if not DataVault.rename_success: #if not DataVault.rename_success:
    #                         #     if cfg['fieldprism']['QR_codes']['do_keep_original_name_if_fail']:
    #                         #         pass
    #                         #     else: 
    #                         #         # Rename the default string, check for increment
    #                         #         DataVault, success_rename = dv_rename_fail_short(DataVault, file_to_rename, path_search, ext)
    #                         # else: 
    #                         #     DataVault, success_rename, dv_rename_success_short(DataVault, file_to_rename, path_search, ext)
    return DataVault


                                
# def increment_filename(dir_path, new_filename, ext):
#     # create a path object for the new filename
#     path_new_filename = os.path.join(dir_path, ''.join([new_filename, ext]))

#     # check if the new filename already exists in the directory
#     if os.path.exists(path_new_filename):
#         f_stem = new_filename.split('___')[0]
#         inc = new_filename.split('___')[1]
#         inc = int(inc) + 1
#         new_filename = os.path.join(dir_path, ''.join([f_stem, '___', str(inc)]))
#         return increment_filename(dir_path, new_filename, ext)
#     else:
#         if '___' in new_filename:
#             inc = new_filename.split('___')[1]
#         else:
#             f_stem = new_filename.split('___')[0]
#             new_filename = os.path.join(dir_path, ''.join([f_stem, '___1']))
        
#         if os.path.exists(os.path.join(dir_path, ''.join([new_filename, ext]))):
#             f_stem = new_filename.split('___')[0]
#             inc = new_filename.split('___')[1]
#             inc = int(inc) + 1
#             new_filename = os.path.join(dir_path, ''.join([f_stem, '___', str(inc)]))
#             return increment_filename(dir_path, new_filename, ext)
#         return new_filename

