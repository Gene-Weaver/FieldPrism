

def rename_files_from_QR_codes():
    if barcodes_added:
        if cfg['fieldprism']['QR_codes']['do_rename_images']:
            print(f"{bcolors.OKCYAN}      Renaming File...{bcolors.ENDC}")
            dirs_to_search = os.listdir(Dirs.actual_save_dir)
            # print(dirs_to_search)
            for folder in dirs_to_search:
                if folder in writing_dirs:
                    path_search = os.path.join(Dirs.actual_save_dir, folder)
                    files_to_search = os.listdir(path_search)
                    if len(files_to_search) > 0:
                        files = [os.path.splitext(filename)[0] for filename in files_to_search]
                        if DataVault.image_name in files:
                            ext = os.path.splitext(files_to_search[files == DataVault.image_name])[1]

                            file_to_rename = os.path.join(path_search, ''.join([DataVault.image_name, ext]))
                            # print(file_to_rename)
                            if not DataVault.rename_success:
                                if cfg['fieldprism']['QR_codes']['do_keep_original_name_if_fail']:
                                    pass
                                else: 
                                    # Rename the default string, check for increment
                                    if DataVault.new_full_name == '':
                                        DataVault.add_process_barcodes([],[])
                                    
                                    new_file_name = increment_filename(path_search, DataVault.new_full_name, ext)
                                    new_file_name = ''.join([new_file_name, ext])

                                    os.rename(file_to_rename, new_file_name)
                                    print(f"{bcolors.OKCYAN}      File Renamed: Original --> {''.join([os.path.basename(os.path.normpath(path_search)), '/', DataVault.image_name, ext])} New --> {''.join([os.path.basename(os.path.normpath(path_search)), '/', new_file_name, ext])}{bcolors.ENDC}")
                            else: # Rename with as much as we can get from the QR code
                                if not os.path.exists(os.path.join(path_search, ''.join([DataVault.new_full_name, ext]))):
                                    os.rename(file_to_rename, os.path.join(path_search, ''.join([DataVault.new_full_name, ext])))
                                    print(f"{bcolors.OKCYAN}      File Renamed: Original --> {''.join([os.path.basename(os.path.normpath(path_search)), '/', DataVault.image_name, ext])} New --> {''.join([os.path.basename(os.path.normpath(path_search)), '/', DataVault.new_full_name, ext])}{bcolors.ENDC}")
                                else:
                                    new_file_name = increment_filename_duplicate_barcodes(path_search, DataVault.new_full_name, ext)
                                    new_file_name = ''.join([new_file_name, ext])
                                    _head, tail = os.path.split(new_file_name)
                                    os.rename(file_to_rename, os.path.join(path_search, new_file_name))
                                    print(f"{bcolors.OKCYAN}      File Renamed: Original --> {''.join([os.path.basename(os.path.normpath(path_search)), '/', DataVault.image_name, ext])} New --> {''.join([os.path.basename(os.path.normpath(path_search)), '/', tail, ext])}{bcolors.ENDC}")
            