import os, cv2, pybboxes, torch
import shutil
from pathlib import Path
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial import KDTree
# import qrcode # pip install qrcode[pil]
from torchvision.transforms import ToPILImage
from torchvision.io import read_image
from utils_processing import (get_cfg_from_full_path, get_label_from_index, get_color, make_images_in_dir_vertical, get_approx_conv_factor, get_scale_ratio,
                            determine_success_unknown, determine_success, generate_overlay_add, generate_overlay, correct_distortion, write_yaml,
                            generate_overlay_QR_add, make_file_names_valid, remove_overlapping_predictions, increment_path)
from utils_processing import bcolors, Marker, QRcode, Located_BBOXES, File_Structure, ImageCorrected, ImageOverlay
from component_detector import detect_components_in_image

# @dataclass
# class DataVault:
#     image_name_jpg: str = ''
#     option: str = ''
#     dir_images_to_process

#     # image: list = field(default_factory=None)
#     img_w
#     img_h

#     def __init__(self, path, image, location) -> None:
#         self.path = path
#         self.location = location
#         self.image = image

def process_rulers(cfg, directory_masks, image_name_jpg, all_rulers, option, ratio, image, image_bboxes, img_w, img_h, dir_images_to_process, Dirs):
    Overlay_Out = None
    Image_Out = None
    use_conversion = False
    use_distortion_correction = False

    print(f"{bcolors.OKCYAN}      Processing Ruler Markers in {image_name_jpg}{bcolors.ENDC}")

    # If there are not exactly 4 markers, do stuff
    if all_rulers.shape[0] != 4:
        print(f"{bcolors.WARNING}      Failed to find exactly 4 corner markers. Found {all_rulers.shape[0]} markers.{bcolors.ENDC}")
    keep = []
    i_keep = 0

    # Iterate through possible rulers, only keep those that are mostly square
    for index_keep, row in all_rulers.iterrows():
        i_keep += 1
        print(f"{bcolors.BOLD}            Processing marker {i_keep}{bcolors.ENDC}")
        box_dec = (row[1], row[2], row[3], row[4])
        bbox = pybboxes.convert_bbox(box_dec, from_type="yolo", to_type="voc", image_size=(img_w, img_h))
        x_diff = bbox[2] - bbox[0]
        y_diff = bbox[3] - bbox[1]

        tol = np.multiply(min([x_diff,y_diff]),1) #0.2

        if (max([x_diff,y_diff]) <= (min([x_diff,y_diff]) + tol)):# or (max([x_diff,y_diff]) <= (min([x_diff,y_diff]) - tol)):
            keep.append(row.values)
            print(f"{bcolors.BOLD}            KEEP, ruler is square: x-side {x_diff} vs. y-side {y_diff}{bcolors.ENDC}")
        else:
            print(f"{bcolors.BOLD}            IGNORE, ruler not square: x-side {x_diff} vs. y-side {y_diff}{bcolors.ENDC}")
    # update all_rulers 
    all_rulers = pd.DataFrame(keep)

    # try again, are there 4 markers now?
    if all_rulers.shape[0] != 4:
        print(f"{bcolors.WARNING}      Failed to find exactly 4 corner markers. Will use available {all_rulers.shape[0]} markers.{bcolors.ENDC}")
        print(f"{bcolors.WARNING}      -- This image will not undergo distortion correction.{bcolors.ENDC}")
        print(f"{bcolors.WARNING}      -- Verify that its pixel-metric conversion is accurate.{bcolors.ENDC}")

    # If there is at least one marker we will try to get a pixel conversion
    if (all_rulers.shape[0] > 0):# and (all_rulers.shape[0] <= 4):
        bbox_list = []
        labels_list = []
        colors_list = []

        centers_list = []
        centers_loc_list = []
        label_row = []

        # iterate through the markers, find the rough centers to start organizing the markers
        for index_label, row in all_rulers.iterrows():
            label_row.append(index_label)
            colors_list.append(get_color(row[0]))

            object_name = get_label_from_index(row[0])
            labels_list.append(object_name)

            box_dec = (row[1], row[2], row[3], row[4])
            bbox = pybboxes.convert_bbox(box_dec, from_type="yolo", to_type="voc", image_size=(img_w, img_h))
            bbox_list.append(bbox)
            # print(f"bbox {index_label}:\n{bbox}")

            # Find center and add to dict
            cp_x = int(np.average([bbox[0],bbox[2]]))
            cp_y = int(np.average([bbox[1],bbox[3]]))
            centers_loc_list.append([cp_x, cp_y])
            center_point = cp_x + cp_y
            centers_list.append(center_point)
        ###########################################################################
        ###########################################################################
        ###########################################################################
        # if there are exactly 4 markers, then we can try to correct for distortion
        if len(centers_list) == 4:
            # print(f"dict:\n{centers_list}")
            centers_list2 = centers_list.copy()
            label_row2 = label_row.copy()
            bbox_list2 = bbox_list.copy()
            centers_loc_list2 = centers_loc_list.copy()
            Bboxes_4 = Located_BBOXES(centers_list2,label_row2,bbox_list2,centers_loc_list2)
            Bboxes_4.confirm_orientation()

            # if the image is vertical, but the markers are hor, then rotate the image again ccw
            TL_to_TR = math.dist([Bboxes_4.top_left_center[0], Bboxes_4.top_left_center[1]], [Bboxes_4.top_right_center[0], Bboxes_4.top_right_center[1]])
            TL_to_BL = math.dist([Bboxes_4.top_left_center[0], Bboxes_4.top_left_center[1]], [Bboxes_4.bottom_left_center[0], Bboxes_4.bottom_left_center[1]])
            if TL_to_TR < TL_to_BL:
                pass
            else:
                print(f"{bcolors.WARNING}      Image was vertical, markers were not. Rotating the image 90ccw{bcolors.ENDC}")
                Bboxes_4.rotate_locations_90_ccw()

            bbox = torch.tensor(bbox_list, dtype=torch.int)

            print(f"{bcolors.OKGREEN}      Found All 4 Markers!{bcolors.ENDC}")
            print(f"{bcolors.OKCYAN}      Processing Top Left Marker...{bcolors.ENDC}")
            Marker_Top_Left = Marker(cfg, directory_masks, 'top_left', image_name_jpg, image, Bboxes_4.top_left_ind_label, Bboxes_4.top_left_bbox, Bboxes_4.top_left_center)

            print(f"{bcolors.OKCYAN}      Processing Top Right Marker...{bcolors.ENDC}")
            Marker_Top_Right = Marker(cfg, directory_masks, 'top_right', image_name_jpg, image, Bboxes_4.top_right_ind_label, Bboxes_4.top_right_bbox, Bboxes_4.top_right_center)

            print(f"{bcolors.OKCYAN}      Processing Bottom Left Marker...{bcolors.ENDC}")
            Marker_Bottom_Left = Marker(cfg, directory_masks, 'bottom_left', image_name_jpg, image, Bboxes_4.bottom_left_ind_label, Bboxes_4.bottom_left_bbox, Bboxes_4.bottom_left_center)

            print(f"{bcolors.OKCYAN}      Processing Bottom Right Marker...{bcolors.ENDC}")
            Marker_Bottom_Right = Marker(cfg, directory_masks, 'bottom_right', image_name_jpg, image, Bboxes_4.bottom_right_ind_label, Bboxes_4.bottom_right_bbox, Bboxes_4.bottom_right_center)

            if Marker_Top_Left.is_approx or Marker_Top_Right.is_approx or Marker_Bottom_Left.is_approx or Marker_Bottom_Right.is_approx:
                Marker_Top_Left.translate_center_point = Marker_Top_Left.rough_center
                Marker_Top_Right.translate_center_point = Marker_Top_Right.rough_center
                Marker_Bottom_Left.translate_center_point = Marker_Bottom_Left.rough_center
                Marker_Bottom_Right.translate_center_point = Marker_Bottom_Right.rough_center
                Marker_Top_Left.is_approx = True
                Marker_Top_Right.is_approx = True
                Marker_Bottom_Left.is_approx = True
                Marker_Bottom_Right.is_approx = True

            use_distortion_correction, use_conversion = determine_success(Marker_Top_Left,Marker_Top_Right,Marker_Bottom_Left,Marker_Bottom_Right)

            # if option == 'processing' and not use_distortion_correction:
                

            if use_conversion:
                if cfg['fieldprism']['use_template_for_pixel_to_metric_conversion']:
                    conv_success, marker_dist = get_approx_conv_factor(cfg)
                    if conv_success:
                        average_one_cm_distance = np.multiply(np.divide(TL_to_TR,marker_dist), 10)
                        Marker_Top_Left.one_cm_pixels = average_one_cm_distance
                        Marker_Top_Right.one_cm_pixels = average_one_cm_distance
                        Marker_Bottom_Left.one_cm_pixels = average_one_cm_distance
                        Marker_Bottom_Right.one_cm_pixels = average_one_cm_distance
                else: # This is the goal, it's the exact conversion factor
                    if ((Marker_Top_Left.one_cm_pixels is np.nan) and (Marker_Top_Right.one_cm_pixels is np.nan) and (Marker_Bottom_Left.one_cm_pixels is np.nan) and (Marker_Bottom_Right.one_cm_pixels is np.nan)):
                        average_one_cm_distance = np.nan
                    else:
                        average_one_cm_distance = np.nanmean([Marker_Top_Left.one_cm_pixels,Marker_Top_Right.one_cm_pixels,Marker_Bottom_Left.one_cm_pixels,Marker_Bottom_Right.one_cm_pixels])
            else:
                if not cfg['fieldprism']['strict_distortion_correction']:
                    conv_success, marker_dist = get_approx_conv_factor(cfg)
                    if conv_success:
                        average_one_cm_distance = np.multiply(np.divide(TL_to_TR,marker_dist), 10)
                        Marker_Top_Left.one_cm_pixels = average_one_cm_distance
                        Marker_Top_Right.one_cm_pixels = average_one_cm_distance
                        Marker_Bottom_Left.one_cm_pixels = average_one_cm_distance
                        Marker_Bottom_Right.one_cm_pixels = average_one_cm_distance

                else:
                    average_one_cm_distance = np.nan
            if average_one_cm_distance is np.nan:
                conv_success, marker_dist = get_approx_conv_factor(cfg)
                if conv_success:
                    average_one_cm_distance = np.multiply(np.divide(TL_to_TR,marker_dist), 10)
                    Marker_Top_Left.one_cm_pixels = average_one_cm_distance
                    Marker_Top_Right.one_cm_pixels = average_one_cm_distance
                    Marker_Bottom_Left.one_cm_pixels = average_one_cm_distance
                    Marker_Bottom_Right.one_cm_pixels = average_one_cm_distance


            ### Distortion correction success, can get a conversion 
            if use_distortion_correction:
                centers = [Marker_Top_Left.translate_center_point,
                            Marker_Top_Right.translate_center_point,
                            Marker_Bottom_Right.translate_center_point,
                            Marker_Bottom_Left.translate_center_point]
                if option == 'distortion':
                    image, centers_corrected = correct_distortion(cfg, image, centers, ratio)                    
                    # Write the distortion corrected image 
                    # cv2.imwrite(os.path.join(Dirs.path_distortion_corrected,image_name_jpg), image)
                    Image_Out = ImageCorrected(os.path.join(Dirs.path_distortion_corrected,image_name_jpg), image, location='path_images_corrected')

                elif option == 'processing':
                    centers_corrected = centers
                    image_bboxes = generate_overlay(Dirs.path_overlay, image_name_jpg, average_one_cm_distance, image_bboxes, bbox, labels_list, colors_list, centers_corrected, Marker_Top_Left, Marker_Top_Right, Marker_Bottom_Right, Marker_Bottom_Left)
                    # Below only used for referencing dir location
                    Image_Out = ImageCorrected(os.path.join(Dirs.path_distortion_corrected,image_name_jpg), [], location='path_images_corrected')

            ### Distortion failed, but can still get a conversion 
            else: #  use_conversion and not use_distortion_correction: 
                # Write the NOT distortion corrected image 
                if option == 'distortion':
                    # cv2.imwrite(os.path.join(Dirs.path_distortion_not_corrected,image_name_jpg), image)
                    Image_Out = ImageCorrected(os.path.join(Dirs.path_distortion_not_corrected,image_name_jpg), image, location='path_images_not_corrected')
                elif option == 'processing':
                    # Below only used for referencing dir location
                    Image_Out = ImageCorrected(os.path.join(Dirs.path_distortion_not_corrected,image_name_jpg), [], location='path_images_not_corrected')
                    print(f"{bcolors.WARNING}      Marker lost after distortion correction{bcolors.ENDC}")

            
            # ### No markers found
            # else: # no markers found
            #     # Write the FAILED
            #     cv2.imwrite(os.path.join(Dirs.path_markers_missing,image_name_jpg), image)
        
        ### There were too many or too few markers
        else:
            # Write path_distortion_not_corrected image 
            # cv2.imwrite(os.path.join(Dirs.path_distortion_not_corrected,image_name_jpg), image)
            Image_Out = ImageCorrected(os.path.join(Dirs.path_distortion_not_corrected,image_name_jpg), image, location='path_distortion_not_corrected')

            distances_list = []

            # image_bboxes = read_image(os.path.join(dir_images_to_process, image_name_jpg))
            for i, val in enumerate(centers_list):
                ind = centers_list[i]
                ind_label = label_row[i]
                bbox_m = bbox_list[i]
                center = centers_loc_list[i]

                print(f"{bcolors.OKCYAN}      Processing Unknown Marker {i+1} / {len(centers_list)}{bcolors.ENDC}")
                Marker_Unknown = Marker(cfg, directory_masks, 'unknown', image_name_jpg, image, ind_label, bbox_m, center)

                use_conversion = determine_success_unknown(Marker_Unknown)
                if use_conversion:
                    distances_list.append(Marker_Unknown.one_cm_pixels)
                    try:
                        image_bboxes = generate_overlay_add(image_bboxes, torch.tensor([bbox_m], dtype=torch.int), labels_list[i], colors_list[i], Marker_Unknown.translate_center_point, Marker_Unknown,Marker_Unknown.one_cm_pixels)
                    except:
                        image_bboxes = read_image(os.path.join(dir_images_to_process, image_name_jpg))
                        image_bboxes = generate_overlay_add(image_bboxes, torch.tensor([bbox_m], dtype=torch.int), labels_list[i], colors_list[i], Marker_Unknown.translate_center_point, Marker_Unknown,Marker_Unknown.one_cm_pixels)

            ### More than 4, fewer than 4 markers
            if len(distances_list) > 0:
                if option == 'processing':    
                    try:
                        image_bboxes_show = ToPILImage()(image_bboxes)
                    except:
                        image_bboxes = read_image(os.path.join(dir_images_to_process, image_name_jpg))
                        image_bboxes_show = ToPILImage()(image_bboxes)

                    # image_bboxes_show.show()
                    # image_bboxes_show.save(os.path.join(Dirs.path_overlay, image_name_jpg))
                    Overlay_Out = ImageOverlay(os.path.join(Dirs.path_overlay, image_name_jpg), image_bboxes_show, location='path_overlay')


                average_one_cm_distance = np.nanmean(distances_list)


                print(f"{bcolors.OKGREEN}      Pixel to Metric Conversion: {average_one_cm_distance} pixels = 1 cm.{bcolors.ENDC}")
            
            ### No rulers
            else:
                average_one_cm_distance = np.nan
                print(f"{bcolors.FAIL}      Image: {image_name_jpg} had no ruler predictions - Marker_Unknown{bcolors.ENDC}")
    else:
        ### Write the FAILED. No rulers found
        # cv2.imwrite(os.path.join(Dirs.path_markers_missing,image_name_jpg), image)
        Image_Out = ImageCorrected(os.path.join(Dirs.path_markers_missing,image_name_jpg), image, location='path_markers_missing')
        average_one_cm_distance = 0
        print(f"{bcolors.FAIL}      Only non-square rulers located{bcolors.ENDC}")
    return average_one_cm_distance, image, image_bboxes, use_conversion, use_distortion_correction, Image_Out, Overlay_Out


def process_barcodes(cfg, image_name_jpg, all_barcodes, image, image_bboxes, img_w, img_h, Dirs):
    color_fail = (200,80,80)
    print(f"{bcolors.OKCYAN}      Processing QR Codes in {image_name_jpg}{bcolors.ENDC}")
    need_n_QR_codes = int(cfg['fieldprism']['QR_codes']['n_QR_codes'])
    if need_n_QR_codes > 0:
        pass
    else:
        print(f"{bcolors.FAIL}      cfg['fieldprism']['QR_codes']['n_QR_codes'] needs to be an integer greater than zero{bcolors.ENDC}")
    
    if all_barcodes.shape[0] != need_n_QR_codes:
        print(f"{bcolors.WARNING}      Number of detected QR codes ({all_barcodes.shape[0]}) not equal to user-defined number ({need_n_QR_codes}){bcolors.ENDC}")
    
    i_candidate = 0
    i_pass = 0
    i_fail = 0 
    QR_List_Pass = {}
    QR_List_Fail = {}
    color = []
    for index_keep, row in all_barcodes.iterrows():
        color = get_color(row[0])
        i_candidate += 1
        print(f"{bcolors.BOLD}            Processing QR Code {i_candidate}{bcolors.ENDC}")
        box_dec = (row[1], row[2], row[3], row[4])
        bbox = pybboxes.convert_bbox(box_dec, from_type="yolo", to_type="voc", image_size=(img_w, img_h))
        QR_Candidate = QRcode(i_candidate, image_name_jpg, image, image_bboxes, row, bbox, Dirs.path_QRcodes_raw, Dirs.path_QRcodes_summary)
        if QR_Candidate.text_raw != '':
            i_pass += 1
            QR_List_Pass[i_pass-1] = QR_Candidate

            if cfg['fieldprism']['insert_clean_QR_codes']:
                QR_Candidate.insert_straight_QR_code()

            image = QR_Candidate.image
        else:
            i_fail += 1
            QR_List_Fail[i_fail-1] = QR_Candidate

    for key in QR_List_Pass.values():
        # print(f'pass:\n{key.text_raw}')
        qr_label = ''.join(['L: ',key.rank, ' C: ',key.rank_value])
        image_bboxes = generate_overlay_QR_add(image_bboxes, torch.tensor([key.bbox], dtype=torch.int), qr_label, color)
    for key in QR_List_Fail.values():
        # print(f'fail:\n{key.text_raw}')
        qr_label = 'FAIL'
        image_bboxes = generate_overlay_QR_add(image_bboxes, torch.tensor([key.bbox], dtype=torch.int), qr_label, color_fail)

    return image, image_bboxes
    

def identify_and_process_markers(cfg, option, ratio, dir_images_to_process, Dirs):
    dir_FP = os.path.dirname(os.path.dirname(__file__))
    path_directory_masks = os.path.join(dir_FP,'fieldprism','marker_template')
    # directory_masks = [cv2.imread(f, 0) for f in os.listdir(path_directory_masks)]
    directory_masks = [cv2.threshold(cv2.imread(os.path.join(path_directory_masks, filename), cv2.IMREAD_GRAYSCALE), 128, 255, cv2.THRESH_BINARY)[1] for filename in os.listdir(path_directory_masks)]
    # Loop through image dir and process each image
    n_total = len(os.listdir(dir_images_to_process))
    for index, image_name_jpg in enumerate(os.listdir(dir_images_to_process)):
        chosen_path = ''
        print(f"{bcolors.OKCYAN}\nWorking on image {index+1} / {n_total} | Image: {image_name_jpg}{bcolors.ENDC}")

        # Only process jpgs
        has_ML_prediction = True
        if image_name_jpg.endswith((".jpg",".JPG",".jpeg",".JPEG")):
            image_name = os.path.splitext(image_name_jpg)[0]
            image_name_txt = '.'.join([image_name,'txt'])

            # Get matching labels from .txt file
            if option == 'distortion':
                try:
                    # Read image
                    chosen_path = os.path.join(dir_images_to_process, image_name_jpg)
                    image = cv2.imread(chosen_path)
                    img_h, img_w, img_c = image.shape
                    image_label_file = pd.read_csv(os.path.join(Dirs.actual_save_dir,'Labels_Not_Corrected',image_name_txt),sep=' ',header=None)
                except:
                    has_ML_prediction = False


            elif option == 'processing':
                try:
                    # Read image
                    chosen_path = os.path.join(Dirs.path_distortion_corrected, image_name_jpg)
                    image = cv2.imread(chosen_path)
                    img_h, img_w, img_c = image.shape
                    image_label_file = pd.read_csv(os.path.join(Dirs.actual_save_dir,'Labels_Corrected',image_name_txt),sep=' ',header=None)
                except: # if the image could not have distortion corrected, read the old txt
                    try:
                        # Read image
                        chosen_path = os.path.join(dir_images_to_process, image_name_jpg)
                        image = cv2.imread(chosen_path)
                        img_h, img_w, img_c = image.shape
                        image_label_file = pd.read_csv(os.path.join(Dirs.actual_save_dir,'Labels_Not_Corrected',image_name_txt),sep=' ',header=None)
                    except:
                        has_ML_prediction = False
            elif option == 'conversion_factor': ######################################################################################
                pass

            # print(image_label_file)
            # Skip images that have no predictions
            if has_ML_prediction:
                all_text = image_label_file.loc[image_label_file[0] == 3]
                all_rulers = image_label_file.loc[image_label_file[0] == 0]
                all_barcodes = image_label_file.loc[image_label_file[0] == 1]



                # keep_bc = []
                # for i_bc, bc in all_barcodes.iterrows(): 
                #     do_keep_bc = True
                #     bbox_b = (bc[1], bc[2], bc[3], bc[4])
                #     bbox_b = pybboxes.convert_bbox(bbox_b, from_type="yolo", to_type="voc", image_size=(img_w, img_h))
                #     for i_ru, ru in keep_ruler.iterrows(): 
                #         bbox_ruler = (bc[1], bc[2], bc[3], bc[4])
                #         bbox_ruler = pybboxes.convert_bbox(bbox_ruler, from_type="yolo", to_type="voc", image_size=(img_w, img_h))
                #         if (bbox_ruler[0] >= bbox_b[2]) or (bbox_ruler[2]<=bbox_b[0]) or (bbox_ruler[3]<=bbox_b[1]) or (bbox_ruler[1]>=bbox_b[3]):
                #             continue
                #         else:
                #             do_keep_bc = False
                #     if do_keep_bc:
                #         keep_bc.append(bc.values)
                # keep_bc = pd.DataFrame(keep_bc)
                if cfg['fieldprism']['do_remove_overlap']:
                    print(f"{bcolors.OKCYAN}      Removing intersecting predictions. Prioritizing class: {cfg['fieldprism']['overlap_priority']}{bcolors.ENDC}")
                    print(f"{bcolors.BOLD}            Before - number of barcodes: {all_barcodes.shape[0]}{bcolors.ENDC}")
                    print(f"{bcolors.BOLD}            Before - number of rulers: {all_rulers.shape[0]}{bcolors.ENDC}")
                    if cfg['fieldprism']['overlap_priority'] == 'ruler':
                        all_rulers, all_barcodes = remove_overlapping_predictions(all_rulers, all_barcodes, img_w, img_h)
                    else:
                        all_barcodes, all_rulers = remove_overlapping_predictions(all_barcodes, all_rulers, img_w, img_h)
                    print(f"{bcolors.BOLD}            Before - number of barcodes: {all_barcodes.shape[0]}{bcolors.ENDC}")
                    print(f"{bcolors.BOLD}            Before - number of rulers: {all_rulers.shape[0]}{bcolors.ENDC}")


                try:
                    image_bboxes = read_image(os.path.join(Dirs.path_overlay,image_name_jpg))
                except:
                    image_bboxes = read_image(chosen_path)
                

                '''Rulers and Distortion Correction'''
                average_one_cm_distance, image, image_bboxes, use_conversion, use_distortion_correction, Image_Out, Overlay_Out  = process_rulers(cfg, directory_masks, image_name_jpg, all_rulers, option, ratio, image, image_bboxes, img_w, img_h, dir_images_to_process, Dirs)


                '''Save Distortion Corrected Images'''
                if Image_Out:
                    cv2.imwrite(Image_Out.path, Image_Out.image)
                if option == 'processing':
                    if Overlay_Out:
                        Overlay_Out.image.save(Overlay_Out.path)

                
                '''Save Data'''


                '''Barcodes'''
                # Process barcodes on first pass if the image is not distortion corrected
                # Process barcodes on second pass (processing) if the image was corrected
                if ((option == 'processing') or (Image_Out.location in ['path_markers_missing','path_distortion_not_corrected'])):
                    image, image_bboxes = process_barcodes(cfg, image_name_jpg, all_barcodes, image, image_bboxes, img_w, img_h, Dirs)
                    # Overwrite previous corrected image *if* user wants clean QR codes inserted
                    if cfg['fieldprism']['insert_clean_QR_codes']:
                        cv2.imwrite(Image_Out.path, image)

                
                # image, image_bboxes = process_barcodes(cfg, image_name_jpg, all_barcodes, image, image_bboxes, img_w, img_h, Dirs)
                
                if option == 'distortion':
                    if not use_distortion_correction:
                        image_bboxes_show = ToPILImage()(image_bboxes)
                        # image_bboxes_show.show()
                        image_bboxes_show.save(os.path.join(Dirs.path_overlay_not, image_name_jpg))
                    
                if option == 'processing':
                    image_bboxes_show = ToPILImage()(image_bboxes)
                    # image_bboxes_show.show()
                    image_bboxes_show.save(os.path.join(Dirs.path_overlay, image_name_jpg))



            else:
                # Images with no ML predictions will go into 'Distortion_Not_Corrected'
                print(f"{bcolors.FAIL}      Image: {image_name_jpg} had no ruler predictions{bcolors.ENDC}")
                chosen_path = os.path.join(dir_images_to_process, image_name_jpg)
                image = cv2.imread(chosen_path)
                cv2.imwrite(os.path.join(Dirs.path_markers_missing,image_name_jpg),image)
                

        if average_one_cm_distance > 0:
            print(f"{bcolors.OKGREEN}      Pixel to Metric Conversion: {average_one_cm_distance} pixels = 1 cm.{bcolors.ENDC}")
        else:
            print(f"{bcolors.FAIL}      Could not determine pixel to metric conversion: {average_one_cm_distance} pixels = 1 cm.{bcolors.ENDC}")
        # return average_one_cm_distance


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

        actual_save_dir = detect_components_in_image('processing',cfg, run_name_2, dir_out_2,True)



        print(f"{bcolors.HEADER}*************************************************************{bcolors.ENDC}")
        print(f"{bcolors.HEADER}*** Step 5) Calculate Conversion Factor and re-read barcodes*{bcolors.ENDC}")
        print(f"{bcolors.HEADER}*************************************************************{bcolors.ENDC}")

        if actual_save_dir is None:
            print(f"{bcolors.WARNING}No images in 'Images_Corrected'{bcolors.ENDC}")
        else:
            dir_images_corrected = Dirs.path_distortion_corrected
            identify_and_process_markers(cfg, 'processing', ratio, dir_images_corrected, Dirs)



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