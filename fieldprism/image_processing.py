import os, cv2, time
import shutil
from pathlib import Path
import pandas as pd
from torchvision.transforms import ToPILImage
from torchvision.io import read_image
from utils_processing import (get_cfg_from_full_path, make_images_in_dir_vertical, get_scale_ratio, write_yaml, 
                                make_file_names_valid, remove_overlapping_predictions, increment_path)
from utils_processing import bcolors, File_Structure
from component_detector import detect_components_in_image
from utils_rulers import process_rulers
from utils_barcodes import process_barcodes
from utils_data import Data_Vault

def identify_and_process_markers(cfg, option, ratio, dir_images_to_process, Dirs):
    # Get marker templates for maker matching
    dir_FP = os.path.dirname(os.path.dirname(__file__))
    path_directory_masks = os.path.join(dir_FP,'fieldprism','marker_template')
    directory_masks = [cv2.threshold(cv2.imread(os.path.join(path_directory_masks, filename), cv2.IMREAD_GRAYSCALE), 128, 255, cv2.THRESH_BINARY)[1] for filename in os.listdir(path_directory_masks)]
    
    # Loop through image dir and process each image
    n_total = len(os.listdir(dir_images_to_process))

    writing_dirs = ['Detections_Corrected', 'Detections_Not_Corrected', 'Images_Corrected', 'Images_Markers_Missing', 'Images_Not_Corrected', 'Labels_Not_Corrected', 'Overlay_Corrected', 'Overlay_Not_Corrected']

    for index, image_name_jpg in enumerate(os.listdir(dir_images_to_process)):
        chosen_path = ''
        print(f"{bcolors.OKCYAN}\nWorking on image {index+1} / {n_total} | Image: {image_name_jpg}{bcolors.ENDC}")


        # Initialize empty data vault
        DataVault = Data_Vault(cfg, Dirs, option, ratio, image_name_jpg, dir_images_to_process, index, n_total)


        # Only process jpgs
        has_ML_prediction = True
        if image_name_jpg.endswith((".jpg",".JPG",".jpeg",".JPEG")):
            image_name = os.path.splitext(image_name_jpg)[0]
            image_name_txt = '.'.join([image_name,'txt'])

            # Add to vault
            DataVault.add_image_name(image_name, image_name_txt)


            # Get matching labels from .txt file
            if option == 'distortion':
                try:
                    # Read image
                    chosen_path = os.path.join(dir_images_to_process, image_name_jpg)
                    image = cv2.imread(chosen_path)
                    img_h, img_w, img_c = image.shape
                    path_image_label_file = os.path.join(Dirs.actual_save_dir,'Labels_Not_Corrected', image_name_txt)
                    image_label_file = pd.read_csv(path_image_label_file, sep=' ', header=None)
                    
                    # Add to vault
                    DataVault.add_image_label_size(has_ML_prediction, chosen_path, image, img_h, img_w, image_label_file, path_image_label_file)
                except:
                    # Read image
                    chosen_path = os.path.join(dir_images_to_process, image_name_jpg)
                    image = cv2.imread(chosen_path)
                    img_h, img_w, img_c = image.shape
                    has_ML_prediction = False
                    # Add to vault
                    DataVault.add_image_label_size(has_ML_prediction, chosen_path, image, img_h, img_w, [], 'No_ML_Bounding_Boxes')



            elif option == 'corrected':
                try:
                    # Read image
                    chosen_path = os.path.join(Dirs.path_distortion_corrected, image_name_jpg)
                    image = cv2.imread(chosen_path)
                    img_h, img_w, img_c = image.shape
                    path_image_label_file = os.path.join(Dirs.actual_save_dir,'Labels_Corrected',image_name_txt)
                    image_label_file = pd.read_csv(os.path.join(Dirs.actual_save_dir,'Labels_Corrected',image_name_txt),sep=' ',header=None)
                    # Add to vault
                    DataVault.add_image_label_size(has_ML_prediction, chosen_path, image, img_h, img_w, image_label_file, path_image_label_file)
                except: # if the image could not have distortion corrected, read the old txt
                    try:
                        # Read image
                        chosen_path = os.path.join(dir_images_to_process, image_name_jpg)
                        image = cv2.imread(chosen_path)
                        img_h, img_w, img_c = image.shape
                        path_image_label_file = os.path.join(Dirs.actual_save_dir,'Labels_Not_Corrected',image_name_txt)
                        image_label_file = pd.read_csv(path_image_label_file,sep=' ',header=None)
                        # Add to vault
                        DataVault.add_image_label_size(has_ML_prediction, chosen_path, image, img_h, img_w, image_label_file, path_image_label_file)

                    except:
                        chosen_path = os.path.join(dir_images_to_process, image_name_jpg)
                        image = cv2.imread(chosen_path)
                        img_h, img_w, img_c = image.shape
                        has_ML_prediction = False
                        # Add to vault
                        DataVault.add_image_label_size(has_ML_prediction, chosen_path, image, img_h, img_w, [], 'No_ML_Bounding_Boxes')


            # Skip images that have no predictions
            if has_ML_prediction:
                all_text = image_label_file.loc[image_label_file[0] == 3]
                all_rulers = image_label_file.loc[image_label_file[0] == 0]
                all_barcodes = image_label_file.loc[image_label_file[0] == 1]

                n_barcode_before = all_barcodes.shape[0]
                n_ruler_before = all_rulers.shape[0]
                # Remove overlapping bboxes - optional
                if cfg['fieldprism']['do_remove_overlap']:    
                    print(f"{bcolors.OKCYAN}      Removing intersecting predictions. Prioritizing class: {cfg['fieldprism']['overlap_priority']}{bcolors.ENDC}")
                    print(f"{bcolors.BOLD}            Before - number of barcodes: {n_barcode_before}{bcolors.ENDC}")
                    print(f"{bcolors.BOLD}            Before - number of rulers: {n_ruler_before}{bcolors.ENDC}")
                    if cfg['fieldprism']['overlap_priority'] == 'ruler':
                        all_rulers, all_barcodes = remove_overlapping_predictions(all_rulers, all_barcodes, img_w, img_h)
                    else:
                        all_barcodes, all_rulers = remove_overlapping_predictions(all_barcodes, all_rulers, img_w, img_h)
                    n_barcode_afer = all_barcodes.shape[0]
                    n_ruler_after = all_rulers.shape[0]
                    print(f"{bcolors.BOLD}            After - number of barcodes: {n_barcode_afer}{bcolors.ENDC}")
                    print(f"{bcolors.BOLD}            After - number of rulers: {n_ruler_after}{bcolors.ENDC}")
                else:
                    n_barcode_afer = all_barcodes.shape[0]
                    n_ruler_after = all_rulers.shape[0]

                # Add to vault
                DataVault.add_bboxes(cfg['fieldprism']['do_remove_overlap'], n_barcode_before, n_ruler_before, n_barcode_afer, n_ruler_after, all_text, all_rulers, all_barcodes)

                # Read image to use pytorch overlays, is tensor image NOT numpy
                try:
                    image_bboxes = read_image(os.path.join(Dirs.path_overlay,image_name_jpg))
                except:
                    image_bboxes = read_image(chosen_path)
                

                '''Rulers and Distortion Correction'''
                average_one_cm_distance, image, image_bboxes, use_conversion, use_distortion_correction, Image_Out, Overlay_Out, Markers_All = process_rulers(cfg, directory_masks, image_name_jpg, all_rulers, option, ratio, image, image_bboxes, img_w, img_h, dir_images_to_process, Dirs)

                # Add to vault
                DataVault.add_process_rulers(average_one_cm_distance, image, use_conversion, use_distortion_correction, Image_Out, Overlay_Out, Markers_All)

                '''Save Distortion Corrected Images'''
                # Save corrected image
                if Image_Out:
                    cv2.imwrite(Image_Out.path, Image_Out.image)
                if option == 'corrected':
                    if Overlay_Out:
                        Overlay_Out.image.save(Overlay_Out.path)


                '''Barcodes'''
                # Process barcodes on first pass if the image is not distortion corrected
                # Process barcodes on second pass (corrected) if the image was corrected
                barcodes_added = False
                if ((option == 'corrected') or (Image_Out.location in ['path_markers_missing','path_distortion_not_corrected'])):
                    image, image_bboxes, QR_List_Pass, QR_List_Fail = process_barcodes(cfg, image_name_jpg, all_barcodes, image, image_bboxes, img_w, img_h, Dirs)
                    # Overwrite previous corrected image *if* user wants clean QR codes inserted
                    if cfg['fieldprism']['insert_clean_QR_codes']:
                        cv2.imwrite(Image_Out.path, image)


                    # Add to vault
                    barcodes_added = DataVault.add_process_barcodes(QR_List_Pass, QR_List_Fail)


                # image, image_bboxes = process_barcodes(cfg, image_name_jpg, all_barcodes, image, image_bboxes, img_w, img_h, Dirs)
                if option == 'distortion':
                    if not use_distortion_correction:
                        image_bboxes_show = ToPILImage()(image_bboxes)
                        # image_bboxes_show.show()
                        image_bboxes_show.save(os.path.join(Dirs.path_overlay_not, image_name_jpg))
                    
                if option == 'corrected':
                    image_bboxes_show = ToPILImage()(image_bboxes)
                    # image_bboxes_show.show()
                    image_bboxes_show.save(os.path.join(Dirs.path_overlay, image_name_jpg))



            else:
                # Images with no ML predictions will go into 'Distortion_Not_Corrected'
                print(f"{bcolors.FAIL}      Image: {image_name_jpg} had no ruler predictions{bcolors.ENDC}")
                chosen_path = os.path.join(dir_images_to_process, image_name_jpg)
                image = cv2.imread(chosen_path)
                cv2.imwrite(os.path.join(Dirs.path_markers_missing,image_name_jpg),image)
                average_one_cm_distance = None

        if average_one_cm_distance is None:
            print(f"{bcolors.FAIL}            Could not convert pixel distance to metric{bcolors.ENDC}")
        elif average_one_cm_distance > 0:
            print(f"{bcolors.OKGREEN}      Pixel to Metric Conversion: {average_one_cm_distance} pixels = 1 cm.{bcolors.ENDC}")
        else:
            print(f"{bcolors.FAIL}      Could not determine pixel to metric conversion: {average_one_cm_distance} pixels = 1 cm.{bcolors.ENDC}")


        # Change file names
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

                                        success_rename = rename_loop(file_to_rename, new_file_name)
                                        # os.rename(file_to_rename, new_file_name)
                                        print(f"{bcolors.OKCYAN}      File Renamed: Original --> {''.join([os.path.basename(os.path.normpath(path_search)), '/', DataVault.image_name, ext])} New --> {''.join([os.path.basename(os.path.normpath(path_search)), '/', new_file_name, ext])}{bcolors.ENDC}")
                                else: # Rename with as much as we can get from the QR code
                                    if not os.path.exists(os.path.join(path_search, ''.join([DataVault.new_full_name, ext]))):
                                        success_rename = rename_loop(file_to_rename, os.path.join(path_search, ''.join([DataVault.new_full_name, ext])))
                                        
                                        # os.rename(file_to_rename, os.path.join(path_search, ''.join([DataVault.new_full_name, ext])))
                                        print(f"{bcolors.OKCYAN}      File Renamed: Original --> {''.join([os.path.basename(os.path.normpath(path_search)), '/', DataVault.image_name, ext])} New --> {''.join([os.path.basename(os.path.normpath(path_search)), '/', DataVault.new_full_name, ext])}{bcolors.ENDC}")
                                    else:
                                        new_file_name = increment_filename_duplicate_barcodes(path_search, DataVault.new_full_name, ext)
                                        new_file_name = ''.join([new_file_name, ext])
                                        _head, tail = os.path.split(new_file_name)
                                        success_rename = rename_loop(file_to_rename, os.path.join(path_search, new_file_name))
                                        
                                        # os.rename(file_to_rename, os.path.join(path_search, new_file_name))
                                        print(f"{bcolors.OKCYAN}      File Renamed: Original --> {''.join([os.path.basename(os.path.normpath(path_search)), '/', DataVault.image_name, ext])} New --> {''.join([os.path.basename(os.path.normpath(path_search)), '/', tail])}{bcolors.ENDC}")
                
        # Write data to csv


def increment_filename_duplicate_barcodes(dir_path, new_filename, ext):
    # create a path object for the new filename
    path_new_filename = os.path.join(dir_path, ''.join([new_filename, ext]))

    # check if the new filename already exists in the directory
    if os.path.exists(path_new_filename):
        f_stem = new_filename.split('___DUP')[0]
        try:
            inc = new_filename.split('___DUP')[1]
            inc = int(inc) + 1
            new_filename = os.path.join(dir_path, ''.join([f_stem, '___DUP1', str(inc)]))
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
                                
def increment_filename(dir_path, new_filename, ext):
    # create a path object for the new filename
    path_new_filename = os.path.join(dir_path, ''.join([new_filename, ext]))

    # check if the new filename already exists in the directory
    if os.path.exists(path_new_filename):
        f_stem = new_filename.split('___')[0]
        inc = new_filename.split('___')[1]
        inc = int(inc) + 1
        new_filename = os.path.join(dir_path, ''.join([f_stem, '___', str(inc)]))
        return increment_filename(dir_path, new_filename, ext)
    else:
        if '___' in new_filename:
            inc = new_filename.split('___')[1]
        else:
            f_stem = new_filename.split('___')[0]
            new_filename = os.path.join(dir_path, ''.join([f_stem, '___1']))
        
        if os.path.exists(os.path.join(dir_path, ''.join([new_filename, ext]))):
            f_stem = new_filename.split('___')[0]
            inc = new_filename.split('___')[1]
            inc = int(inc) + 1
            new_filename = os.path.join(dir_path, ''.join([f_stem, '___', str(inc)]))
            return increment_filename(dir_path, new_filename, ext)

        return new_filename

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


def process_images():
    print(f"{bcolors.HEADER}*****************************************{bcolors.ENDC}")
    print(f"{bcolors.HEADER}********** Starting FieldPrism **********{bcolors.ENDC}")
    print(f"{bcolors.HEADER}*****************************************{bcolors.ENDC}")

    dir_FP = os.path.dirname(os.path.dirname(__file__))
    path_cfg = os.path.join(dir_FP,'FieldPrism.yaml')
    cfg = get_cfg_from_full_path(path_cfg)

    dir_images_unprocessed = cfg['fieldprism']['dir_images_unprocessed']
    scale_success, ratio = get_scale_ratio(cfg)



    if scale_success:
        # Make sure all images are vertical
        print(f"{bcolors.HEADER}*****************************************{bcolors.ENDC}")
        print(f"{bcolors.HEADER}*** Step 1) Make all images vertical ****{bcolors.ENDC}")
        print(f"{bcolors.HEADER}*****************************************{bcolors.ENDC}")

        make_file_names_valid(cfg['fieldprism']['dir_images_unprocessed'])

        if cfg['fieldprism']['skip_make_images_vertical']:
            print(f"{bcolors.BOLD}User asserts that images are already vertial.{bcolors.ENDC}")
            print(f"{bcolors.BOLD}Skipping Step 1{bcolors.ENDC}")
            pass
        else:
            make_images_in_dir_vertical(cfg['fieldprism']['dir_images_unprocessed'])




        print(f"{bcolors.HEADER}*****************************************{bcolors.ENDC}")
        print(f"{bcolors.HEADER}*** Step 2) Detect Rulers - First Pass **{bcolors.ENDC}")
        print(f"{bcolors.HEADER}*****************************************{bcolors.ENDC}")

        if cfg['fieldprism']['dir_images_unprocessed_labels'] != None:
            run_name_1 = cfg['fieldprism']['dir_images_unprocessed']
            dir_out_1 = os.path.join(cfg['fieldprism']['dir_home'],
                                    cfg['fieldprism']['dirname_images_processed'],
                                    cfg['fieldprism']['dirname_current_project'])
            name = cfg['fieldprism']['dirname_current_run']
            exist_ok = False

            actual_save_dir = increment_path(Path(dir_out_1) / name, exist_ok=exist_ok)  # increment run
            dir_copied_labels  = os.path.join(actual_save_dir,'Labels_Not_Corrected')

            dir_exisiting_labels = cfg['fieldprism']['dir_images_unprocessed_labels']

            shutil.copytree(dir_exisiting_labels, dir_copied_labels)
        else:
            # Run ML object detector to locate labels, ruler markers, barcodes
            run_name_1 = cfg['fieldprism']['dir_images_unprocessed']

            dir_out_1 = os.path.join(cfg['fieldprism']['dir_home'],
                                    cfg['fieldprism']['dirname_images_processed'],
                                    cfg['fieldprism']['dirname_current_project'])

            actual_save_dir = detect_components_in_image('distortion',cfg, run_name_1, dir_out_1,False)

        Dirs = File_Structure(actual_save_dir)

        # Save config yaml that was used for this run
        name_yaml = ''.join(['FieldPrism_',os.path.basename(actual_save_dir),'.yaml'])
        write_yaml(cfg, os.path.join(Dirs.path_Config, name_yaml))



        print(f"{bcolors.HEADER}*****************************************{bcolors.ENDC}")
        print(f"{bcolors.HEADER}*** Step 3) Correct Distortion **********{bcolors.ENDC}")
        print(f"{bcolors.HEADER}*****************************************{bcolors.ENDC}")
        
        identify_and_process_markers(cfg, 'distortion', ratio, dir_images_unprocessed, Dirs)



        print(f"{bcolors.HEADER}*****************************************{bcolors.ENDC}")
        print(f"{bcolors.HEADER}*** Step 4) Detect Rulers - Second Pass *{bcolors.ENDC}")
        print(f"{bcolors.HEADER}*****************************************{bcolors.ENDC}")
        # Run ML object detector to locate labels, ruler markers, barcodes
        run_name_2 = Dirs.path_distortion_corrected

        dir_out_2 = actual_save_dir

        actual_save_dir = detect_components_in_image('corrected',cfg, run_name_2, dir_out_2,True)



        print(f"{bcolors.HEADER}*************************************************************{bcolors.ENDC}")
        print(f"{bcolors.HEADER}*** Step 5) Calculate Conversion Factor and re-read barcodes*{bcolors.ENDC}")
        print(f"{bcolors.HEADER}*************************************************************{bcolors.ENDC}")

        if actual_save_dir is None:
            print(f"{bcolors.WARNING}No images in 'Images_Corrected'{bcolors.ENDC}")
        else:
            dir_images_corrected = Dirs.path_distortion_corrected
            identify_and_process_markers(cfg, 'corrected', ratio, dir_images_corrected, Dirs)



# TODO
# make yaml for existing pdf builder etc...
# read image
# make vertical (use square patterns to always make it upright, align them between images so they stay in the same place?)
# run through LM2 PREP, only show label, barcode, ruler
# locate 4 ruler points
#       * within each, ohtsu imbinarize -> erode -> count 4 squares -> get pairwise distances -> smallest total will be the center -> get centroid = alignment point
#       * aspect ratio = fixed (possible to use cm2 to determine skew?)
#       * correct distortion
#       * calc distance between centroids = conversion factor
#       * save new image to Images_Processed 
# locate qr codes
#       * create a "don't use this" QR code
#       * user sets how many there should be
#       * locate them -> straighten them -> ohtsu??
#       * read them -> if fail, expand box, try again -> manipulate?
# determine heirachy 
#       * look for L1,L2....
#       * print summary in console
#       * rename the files, append to FieldPrism_Processed_Images.csv
#
# train more LM2 using FP images

if __name__ == '__main__':
    process_images()