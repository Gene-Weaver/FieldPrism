import os, cv2, sys, inspect
import shutil
from pathlib import Path
import pandas as pd
from torchvision.transforms import ToPILImage
from torchvision.io import read_image
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
try:
    from utils_processing import (get_cfg_from_full_path, make_images_in_dir_vertical, get_scale_ratio, write_yaml, 
                                    make_file_names_valid, remove_overlapping_predictions, increment_path)
    from utils_processing import bcolors, File_Structure
    from component_detector import detect_components_in_image
    from utils_rulers import process_rulers
    from utils_barcodes import process_barcodes
    from utils_rename import rename_files_from_QR_codes
    from utils_data import Data_Vault, Data_FS, build_empty_csv, write_datarow_to_file
except:
    from fieldprism.utils_processing import (get_cfg_from_full_path, make_images_in_dir_vertical, get_scale_ratio, write_yaml, 
                                make_file_names_valid, remove_overlapping_predictions, increment_path)
    from fieldprism.utils_processing import bcolors, File_Structure
    from fieldprism.component_detector import detect_components_in_image
    from fieldprism.utils_rulers import process_rulers
    from fieldprism.utils_barcodes import process_barcodes
    from fieldprism.utils_rename import rename_files_from_QR_codes
    from fieldprism.utils_data import Data_Vault, Data_FS, build_empty_csv, write_datarow_to_file

def identify_and_process_markers(cfg, option, ratio, dir_images_to_process, Dirs, path_CSV_out):
    # Get marker templates for maker matching
    dir_FP = os.path.dirname(os.path.dirname(__file__))
    path_directory_masks = os.path.join(dir_FP,'fieldprism','marker_template')
    directory_masks = [cv2.threshold(cv2.imread(os.path.join(path_directory_masks, filename), cv2.IMREAD_GRAYSCALE), 128, 255, cv2.THRESH_BINARY)[1] for filename in os.listdir(path_directory_masks)]
    
    # Loop through image dir and process each image
    n_total = len(os.listdir(dir_images_to_process))

    # Set dirs for renaming
    writing_dirs = ['Detections_Corrected',
                    'Detections_Not_Corrected',
                    'Images_Corrected',
                    'Images_Markers_Missing',
                    'Images_Not_Corrected',
                    'Labels_Not_Corrected',
                    'Overlay_Corrected',
                    'Overlay_Not_Corrected'] # Labels_Not_Corrected is included here for running during the second pass....

    search_dirs = ['Labels_Not_Corrected',
                    'Labels_Corrected']

    # Get FS data is applicable
    DataFS = Data_FS(cfg)

    for index, image_name_jpg in enumerate(os.listdir(dir_images_to_process)):
        if image_name_jpg.endswith((".jpg",".JPG",".jpeg",".JPEG")):
            # Only process jpgs
            has_ML_prediction = True
            Image_Out = ''
            barcodes_added = False
            chosen_path = ''

            print(f"{bcolors.OKCYAN}\nWorking on image {index+1} / {n_total} | Image: {image_name_jpg}{bcolors.ENDC}")

            # Names
            image_name = os.path.splitext(image_name_jpg)[0]
            image_name_txt = '.'.join([image_name,'txt'])

            # Initialize empty data vault
            DataVault = Data_Vault(cfg, Dirs, option, ratio, image_name_jpg, dir_images_to_process, index, n_total)

            # Find image row in csv_FS if applicable
            if DataFS.has_FS:
                image_row = DataFS.get_image_row(image_name)
                # print(image_row)
                DataVault.add_DataFS(image_row)

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
                all_barcodes, all_rulers, n_barcode_afer, n_ruler_after = remove_overlapping_predictions(cfg, n_barcode_before, n_ruler_before, all_rulers, all_barcodes, img_w, img_h)

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
        


        try:
            location_q = Image_Out.location
        except:
            location_q = Image_Out



        if ((option == 'distortion') and ((location_q == 'path_distortion_not_corrected') or (location_q == 'path_markers_missing') or (location_q == ''))):
            # Change file names
            DataVault = rename_files_from_QR_codes(cfg, option, barcodes_added, Dirs, search_dirs, writing_dirs, DataVault)

            # Write data to csv
            write_datarow_to_file(cfg['fieldprism']['do_use_FieldStation_csv'], path_CSV_out, DataVault, Image_Out, cfg)
        elif ((option == 'corrected')):# and (location_q == 'path_images_corrected')):
            # Change file names
            DataVault = rename_files_from_QR_codes(cfg, option, barcodes_added, Dirs, search_dirs, writing_dirs, DataVault)

            # Write data to csv
            write_datarow_to_file(cfg['fieldprism']['do_use_FieldStation_csv'], path_CSV_out, DataVault, Image_Out, cfg)



        if average_one_cm_distance is None:
            print(f"{bcolors.FAIL}            Could not convert pixel distance to metric{bcolors.ENDC}")
        elif average_one_cm_distance > 0:
            print(f"{bcolors.OKGREEN}      Pixel to Metric Conversion: {average_one_cm_distance} pixels = 1 cm.{bcolors.ENDC}")
        else:
            print(f"{bcolors.FAIL}      Could not determine pixel to metric conversion: {average_one_cm_distance} pixels = 1 cm.{bcolors.ENDC}")


        


def process_images(cfg_file_path):
    print(f"{bcolors.HEADER}*****************************************{bcolors.ENDC}")
    print(f"{bcolors.HEADER}********** Starting FieldPrism **********{bcolors.ENDC}")
    print(f"{bcolors.HEADER}*****************************************{bcolors.ENDC}")

    dir_FP = os.path.dirname(os.path.dirname(__file__))

    if cfg_file_path == None:
        path_cfg = os.path.join(dir_FP,'FieldPrism.yaml')
        cfg = get_cfg_from_full_path(path_cfg)
    else:
        if cfg_file_path == 'test_installation':
            path_cfg = os.path.join(dir_FP,'demo','test_FP.yaml')
            cfg = get_cfg_from_full_path(path_cfg)
        else:
            path_cfg = cfg_file_path
            cfg = get_cfg_from_full_path(path_cfg)


    if cfg_file_path == 'test_installation':
        test_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),'demo')
        dir_home = os.path.join(test_path, 'demo_output')
        dir_images_unprocessed = os.path.join(test_path, 'images')
    else:
        dir_home = cfg['fieldprism']['dir_home']
        dir_images_unprocessed = cfg['fieldprism']['dir_images_unprocessed']
    scale_success, ratio = get_scale_ratio(cfg)



    if scale_success:
        # Make sure all images are vertical
        print(f"{bcolors.HEADER}*****************************************{bcolors.ENDC}")
        print(f"{bcolors.HEADER}*** Step 1) Make all images vertical ****{bcolors.ENDC}")
        print(f"{bcolors.HEADER}*****************************************{bcolors.ENDC}")

        make_file_names_valid(dir_images_unprocessed)

        if cfg['fieldprism']['skip_make_images_vertical']:
            print(f"{bcolors.BOLD}User asserts that images are already vertial.{bcolors.ENDC}")
            print(f"{bcolors.BOLD}Skipping Step 1{bcolors.ENDC}")
            pass
        else:
            make_images_in_dir_vertical(dir_images_unprocessed)




        print(f"{bcolors.HEADER}*****************************************{bcolors.ENDC}")
        print(f"{bcolors.HEADER}*** Step 2) Detect Rulers - First Pass **{bcolors.ENDC}")
        print(f"{bcolors.HEADER}*****************************************{bcolors.ENDC}")

        if cfg['fieldprism']['dir_images_unprocessed_labels'] != None:
            run_name_1 = dir_images_unprocessed
            dir_out_1 = os.path.join(dir_home,
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
            run_name_1 = dir_images_unprocessed

            dir_out_1 = os.path.join(dir_home,
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

        # Create CSV_out
        path_CSV_out = build_empty_csv(cfg['fieldprism']['do_use_FieldStation_csv'], Dirs.path_Data, cfg)

        
        identify_and_process_markers(cfg, 'distortion', ratio, dir_images_unprocessed, Dirs, path_CSV_out)



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
            identify_and_process_markers(cfg, 'corrected', ratio, dir_images_corrected, Dirs, path_CSV_out)



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