import os, cv2, pybboxes, torch
from dataclasses import dataclass, field
import math
import numpy as np
import pandas as pd
from scipy.spatial import KDTree
from torchvision.transforms import ToPILImage
from torchvision.io import read_image
from utils_processing import get_color, get_approx_conv_factor, get_scale_ratio
from utils_processing import bcolors, ImageCorrected
from utils_overlay import ImageOverlay, generate_overlay, generate_overlay_add
from skimage.morphology import closing, square 
from skimage.measure import find_contours 
from skimage import filters, transform
from skimage.measure import label
from skimage.morphology import dilation, erosion
from skimage.transform import resize 

'''
Main Function
'''
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
        image_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

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
            
            # # Find darkest region instead
            # # Find the coordinates of the darkest pixels
            # cropped_image = image_gray[bbox[1]:bbox[3], bbox[0]:bbox[2]]
            # darkest = np.where(cropped_image == np.min(cropped_image))
            # # Find the highest density of dark pixels by taking the mean of the coordinates
            # cp_x, cp_y = np.mean(darkest[0]), np.mean(darkest[1])
            # cp_x = int(cp_x + bbox[0])
            # cp_y = int(cp_y + bbox[1])

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

                elif option == 'corrected':
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
                elif option == 'corrected':
                    # Below only used for referencing dir location
                    Image_Out = ImageCorrected(os.path.join(Dirs.path_distortion_not_corrected,image_name_jpg), [], location='path_images_not_corrected')
                    print(f"{bcolors.WARNING}      Marker lost after distortion correction{bcolors.ENDC}")
            Markers_All = [Marker_Top_Left, Marker_Top_Right, Marker_Bottom_Left, Marker_Bottom_Right]
            
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
            Markers_All = []

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
                Markers_All.append(Marker_Unknown)
            ### More than 4, fewer than 4 markers
            if len(distances_list) > 0:
                if option == 'corrected':    
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
        Markers_All = None
        print(f"{bcolors.FAIL}      Only non-square rulers located{bcolors.ENDC}")
    return average_one_cm_distance, image, image_bboxes, use_conversion, use_distortion_correction, Image_Out, Overlay_Out, Markers_All

'''
Classes
'''
@dataclass
class Located_BBOXES:
    bottom_right_ind: int = field(init=False)
    bottom_right_ind_label: int = field(init=False)
    bottom_right_bbox: int = field(init=False)
    bottom_right_center: int = field(init=False)

    top_left_ind: int = field(init=False)
    top_left_ind_label: int = field(init=False)
    top_left_bbox: int = field(init=False)
    top_left_center: int = field(init=False)

    top_right_ind: int = field(init=False)
    top_right_ind_label: int = field(init=False)
    top_right_bbox: int = field(init=False)
    top_right_center: int = field(init=False)

    bottom_left_ind: int = field(init=False)
    bottom_left_ind_label: int = field(init=False)
    bottom_left_bbox: int = field(init=False)
    bottom_left_center: int = field(init=False)

    def __init__(self, centers_list, label_row, bbox_list, centers_loc_list) -> None:
        min_x = min([centers_loc_list[0][0],centers_loc_list[1][0],centers_loc_list[2][0],centers_loc_list[3][0]])
        min_y = min([centers_loc_list[0][1],centers_loc_list[1][1],centers_loc_list[2][1],centers_loc_list[3][1]])
        max_x = max([centers_loc_list[0][0],centers_loc_list[1][0],centers_loc_list[2][0],centers_loc_list[3][0]])
        max_y = max([centers_loc_list[0][1],centers_loc_list[1][1],centers_loc_list[2][1],centers_loc_list[3][1]])

        self.top_left_ind = centers_list.index(min(centers_list))
        self.top_left_ind_label = label_row[self.top_left_ind]
        self.top_left_bbox = bbox_list[self.top_left_ind]
        self.top_left_center = centers_loc_list[self.top_left_ind]

        # remaining_centers_list = list(np.delete(centers_list, [self.top_left_ind]))
        remaining_centers_list = centers_list.copy()
        remaining_label_row = label_row.copy()
        remaining_bbox_list = bbox_list.copy()
        remaining_centers_loc_list = centers_loc_list.copy()
        centers_list.pop(self.top_left_ind)
        label_row.pop(self.top_left_ind)
        bbox_list.pop(self.top_left_ind)
        centers_loc_list.pop(self.top_left_ind)

        D1 =  math.dist([self.top_left_center[0], self.top_left_center[1]], [centers_loc_list[0][0], centers_loc_list[0][1]])
        D2 =  math.dist([self.top_left_center[0], self.top_left_center[1]], [centers_loc_list[1][0], centers_loc_list[1][1]])
        D3 =  math.dist([self.top_left_center[0], self.top_left_center[1]], [centers_loc_list[2][0], centers_loc_list[2][1]])

        D_list = [D1,D2,D3]
        D_ind = [0,1,2]
        D_min = D_list.index(min([D1,D2,D3]))
        D_max = D_list.index(max([D1,D2,D3]))
        D_list2 = [D_min, D_max]
        D_mid = list(set(D_ind) - set(D_list2))[0]

        # check orientaiton. compare x and y diffs 
        TL_min_x = abs(self.top_left_center[0] - centers_loc_list[D_min][0]) # bigger
        TL_mid_x = abs(self.top_left_center[0] - centers_loc_list[D_mid][0])

        TL_min_y = abs(self.top_left_center[1] - centers_loc_list[D_min][1])
        TL_mid_y = abs(self.top_left_center[1] - centers_loc_list[D_mid][1]) # bigger

        # top left is correct, 
        if (((TL_min_x+TL_min_y) < (TL_mid_x+TL_mid_y)) and ((TL_min_x > TL_mid_x) or (TL_mid_y > TL_min_y))):
            # print('good orientation')

            # self.bottom_right_ind = remaining_centers_list.index(max(remaining_centers_list))
            # self.bottom_right_ind_label = remaining_label_row[self.bottom_right_ind]
            # self.bottom_right_bbox = remaining_bbox_list[self.bottom_right_ind]
            # self.bottom_right_center = remaining_centers_loc_list[self.bottom_right_ind]

            # self.top_left_ind = remaining_centers_list.index(min(remaining_centers_list))
            # self.top_left_ind_label = remaining_label_row[self.top_left_ind]
            # self.top_left_bbox = remaining_bbox_list[self.top_left_ind]
            # self.top_left_center = remaining_centers_loc_list[self.top_left_ind]

            # centers_loc_list_2 = list(np.delete(remaining_centers_list, [self.bottom_right_ind,self.top_left_ind]))

            # self.top_right_ind = remaining_centers_list.index(min(centers_loc_list_2))
            # self.top_right_ind_label = remaining_label_row[self.top_right_ind]
            # self.top_right_bbox = remaining_bbox_list[self.top_right_ind]
            # self.top_right_center = remaining_centers_loc_list[self.top_right_ind]

            # self.bottom_left_ind = remaining_centers_list.index(max(centers_loc_list_2))
            # self.bottom_left_ind_label = remaining_label_row[self.bottom_left_ind]
            # self.bottom_left_bbox = remaining_bbox_list[self.bottom_left_ind]
            # self.bottom_left_center = remaining_centers_loc_list[self.bottom_left_ind]
            
            # assign min to TR
            self.top_right_ind = D_min
            self.top_right_ind_label = label_row[self.top_right_ind]
            self.top_right_bbox = bbox_list[self.top_right_ind]
            self.top_right_center = centers_loc_list[self.top_right_ind]

            # assign max to BR
            self.bottom_right_ind = D_max
            self.bottom_right_ind_label = label_row[self.bottom_right_ind]
            self.bottom_right_bbox = bbox_list[self.bottom_right_ind]
            self.bottom_right_center = centers_loc_list[self.bottom_right_ind]

            # assign mid to BL
            self.bottom_left_ind = D_mid
            self.bottom_left_ind_label = label_row[self.bottom_left_ind]
            self.bottom_left_bbox = bbox_list[self.bottom_left_ind]
            self.bottom_left_center = centers_loc_list[self.bottom_left_ind]

            # when the hypotenuse is the mid, distortion messes with the TL anchor point
            L1 = self.make_line(self.top_left_center, self.bottom_left_center)
            L2 = self.make_line(self.top_right_center, self.bottom_right_center)

            x, y = self.line_intersection(L1, L2)
            # print(f'x{x} y{y}')

            if ((x < max_x) and (y < max_y)) and ((x > min_x) and (y > min_y)):#if ((abs(x) < max_x) and (abs(y) < max_y)) and ((abs(x) > min_x) and (abs(y) > min_y)):
                print('INVALID - swapping BL and BR')
                # hold
                hold_1 = self.bottom_right_ind
                hold_2 = self.bottom_right_ind_label
                hold_3 = self.bottom_right_bbox
                hold_4 = self.bottom_right_center

                self.bottom_right_ind = self.bottom_left_ind
                self.bottom_right_ind_label = self.bottom_left_ind_label
                self.bottom_right_bbox = self.bottom_left_bbox
                self.bottom_right_center = self.bottom_left_center

                self.bottom_left_ind = hold_1
                self.bottom_left_ind_label = hold_2
                self.bottom_left_bbox = hold_3
                self.bottom_left_center = hold_4

        else:
            # assign min to BR
            self.bottom_right_ind = D_min
            self.bottom_right_ind_label = label_row[self.bottom_right_ind]
            self.bottom_right_bbox = bbox_list[self.bottom_right_ind]
            self.bottom_right_center = centers_loc_list[self.bottom_right_ind]

            # assign max to TR
            self.top_right_ind = D_max
            self.top_right_ind_label = label_row[self.top_right_ind]
            self.top_right_bbox = bbox_list[self.top_right_ind]
            self.top_right_center = centers_loc_list[self.top_right_ind]

            # Reassign TL to BL
            self.bottom_left_ind = self.top_left_ind
            self.bottom_left_ind_label = self.top_left_ind_label
            self.bottom_left_bbox = self.top_left_bbox
            self.bottom_left_center = self.top_left_center

            # assign mid to TL
            self.top_left_ind = D_mid
            self.top_left_ind_label = label_row[self.top_left_ind]
            self.top_left_bbox = bbox_list[self.top_left_ind]
            self.top_left_center = centers_loc_list[self.top_left_ind]
            
            L1 = self.make_line(self.top_left_center, self.bottom_left_center)
            L2 = self.make_line(self.top_right_center, self.bottom_right_center)

            x, y = self.line_intersection(L1, L2)
            # print(f'x{x} y{y}')

            if ((x < max_x) and (y < max_y)) and ((x > min_x) and (y > min_y)):
                print('INVALID - swapping TR and TL')
                # hold
                hold_1 = self.top_right_ind
                hold_2 = self.top_right_ind_label
                hold_3 = self.top_right_bbox
                hold_4 = self.top_right_center

                self.top_right_ind = self.top_left_ind
                self.top_right_ind_label = self.top_left_ind_label
                self.top_right_bbox = self.top_left_bbox
                self.top_right_center = self.top_left_center

                self.top_left_ind = hold_1
                self.top_left_ind_label = hold_2
                self.top_left_bbox = hold_3
                self.top_left_center = hold_4

        # TL_to_TR = math.dist([Bboxes_4.top_left_center[0], Bboxes_4.top_left_center[1]], [Bboxes_4.top_right_center[0], Bboxes_4.top_right_center[1]])
        # TL_to_BL = math.dist([Bboxes_4.top_left_center[0], Bboxes_4.top_left_center[1]], [Bboxes_4.bottom_left_center[0], Bboxes_4.bottom_left_center[1]])
        # if TL_to_TR < TL_to_BL:
        #     pass
        # else:
        #     print(f"{bcolors.WARNING}      Image was vertical, markers were not. Rotating the image 90ccw{bcolors.ENDC}")



        # OLD 
        # self.bottom_right_ind = centers_list.index(max(centers_list))
        # self.bottom_right_ind_label = label_row[self.bottom_right_ind]
        # self.bottom_right_bbox = bbox_list[self.bottom_right_ind]
        # self.bottom_right_center = remaining_centers_loc_list[self.bottom_right_ind]

        # self.top_left_ind = centers_list.index(min(centers_list))
        # self.top_left_ind_label = label_row[self.top_left_ind]
        # self.top_left_bbox = bbox_list[self.top_left_ind]
        # self.top_left_center = remaining_centers_loc_list[self.top_left_ind]

        # centers_loc_list_2 = list(np.delete(centers_list, [self.bottom_right_ind,self.top_left_ind]))

        # self.top_right_ind = centers_list.index(min(centers_loc_list_2))
        # self.top_right_ind_label = label_row[self.top_right_ind]
        # self.top_right_bbox = bbox_list[self.top_right_ind]
        # self.top_right_center = remaining_centers_loc_list[self.top_right_ind]

        # self.bottom_left_ind = centers_list.index(max(centers_loc_list_2))
        # self.bottom_left_ind_label = label_row[self.bottom_left_ind]
        # self.bottom_left_bbox = bbox_list[self.bottom_left_ind]
        # self.bottom_left_center = remaining_centers_loc_list[self.bottom_left_ind]

    def make_line(self, p1, p2) -> None:
        A = (p1[1] - p2[1])
        B = (p2[0] - p1[0])
        C = (p1[0]*p2[1] - p2[0]*p1[1])
        return [A, B, -C]

    def line_intersection(self, L1, L2) -> None:
        D  = L1[0] * L2[1] - L1[1] * L2[0]
        Dx = L1[2] * L2[1] - L1[1] * L2[2]
        Dy = L1[0] * L2[2] - L1[2] * L2[0]
        if D != 0:
            x = Dx / D
            y = Dy / D
        else:
            x = 0
            y = 0
        return x, y

    def confirm_orientation(self) -> None:
        is_correct = False
        TL_to_TR = math.dist([self.top_left_center[0], self.top_left_center[1]], [self.top_right_center[0], self.top_right_center[1]])
        TL_to_BL = math.dist([self.top_left_center[0], self.top_left_center[1]], [self.bottom_left_center[0], self.bottom_left_center[1]])
        TL_to_BR = math.dist([self.top_left_center[0], self.top_left_center[1]], [self.bottom_right_center[0], self.bottom_right_center[1]])

        if ((TL_to_TR < TL_to_BL) & (TL_to_TR < TL_to_BR)):
            is_correct = True
        else:
            # swap top right, bottom left
            s_TL_to_TRbl = math.dist([self.top_left_center[0], self.top_left_center[1]], [self.bottom_left_center[0], self.bottom_left_center[1]])
            s_TL_to_BLtr = math.dist([self.top_left_center[0], self.top_left_center[1]], [self.top_right_center[0], self.top_right_center[1]])
            TL_to_BR = math.dist([self.top_left_center[0], self.top_left_center[1]], [self.bottom_right_center[0], self.bottom_right_center[1]])
            if ((s_TL_to_TRbl < s_TL_to_BLtr) & (TL_to_TR < TL_to_BR)):
                print('swap top right, bottom left')
        # return is_correct
    
    def rotate_locations_90_ccw(self) -> None:
        hold_a = self.bottom_right_ind
        hold_b = self.bottom_right_ind_label
        hold_c = self.bottom_right_bbox
        hold_d = self.bottom_right_center
        # bottom right --> bottom left
        self.bottom_right_ind = self.bottom_left_ind
        self.bottom_right_ind_label = self.bottom_left_ind_label
        self.bottom_right_bbox = self.bottom_left_bbox
        self.bottom_right_center = self.bottom_left_center
        # bottom left --> top left
        self.bottom_left_ind = self.top_left_ind
        self.bottom_left_ind_label = self.top_left_ind_label
        self.bottom_left_bbox = self.top_left_bbox
        self.bottom_left_center = self.top_left_center
        # top left --> top right
        self.top_left_ind = self.top_right_ind
        self.top_left_ind_label = self.top_right_ind_label
        self.top_left_bbox = self.top_right_bbox
        self.top_left_center = self.top_right_center
        # top right --> bottom right
        self.top_right_ind = hold_a
        self.top_right_ind_label = hold_b
        self.top_right_bbox = hold_c
        self.top_right_center = hold_d

@dataclass
class Marker:
    location: str = ''
    success_conv: bool = False
    success_dist: bool = False
    is_approx: bool = False

    one_cm_pixels: int = np.nan
    center_point: list = field(default_factory=None)
    # Convert local cropped points to the whole image location
    translate_center_point: list = field(default_factory=None)

    count: int = 0

    image_name: str = ''
    image: list = field(default_factory=None)
    image_centroids: list = field(default_factory=None)

    label_row: list = field(default_factory=None)
    bbox: list = field(default_factory=None)
    rough_center: list = field(default_factory=None)
    centroid_list: list = field(default_factory=None)

    cropped_marker: list = field(default_factory=None)
    cropped_marker_gray: list = field(default_factory=None)
    cropped_marker_bi: list = field(default_factory=None)
    cropped_marker_plot: list = field(default_factory=None)
    directory_masks: list = field(default_factory=None)


    def __init__(self, cfg, directory_masks, location, image_name, image, label_row, bbox, rough_center) -> None:
        self.location = location
        self.image_name = image_name
        self.image = image
        self.label_row = label_row
        self.bbox = bbox
        self.rough_center = rough_center
        self.directory_masks = directory_masks
        self.sweep()

        if not self.success_conv:
            if not cfg['fieldprism']['strict_distortion_correction']:
                self.translate_center_point = self.rough_center
                self.success_conv = True
                print(f"{bcolors.WARNING}      Using approx. center point for distortion correction{bcolors.ENDC}")
        if cfg['fieldprism']['use_template_for_pixel_to_metric_conversion']:
            self.translate_center_point = self.rough_center
            self.success_conv = True
            print(f"{bcolors.WARNING}      Using approx. center point for distortion correction{bcolors.ENDC}")

    def remove_border_blobs(self, image: np.ndarray) -> np.ndarray:
        # Dilate the image by 3 pixels.
        dilated_image = dilation(image, footprint=np.ones((3, 3)))

        # Label the blobs in the dilated image.
        labeled_blobs, num_blobs = label(dilated_image, return_num=True)

        # If there are multiple blobs, find the blob with the largest area.
        if num_blobs > 1:
            # Find the size of each blob.
            blob_sizes = [np.sum(labeled_blobs == i) for i in range(1, num_blobs + 1)]

            # Find the index of the blob with the largest size.
            largest_blob_index = np.argmax(blob_sizes) + 1

            # Set all pixels in the labeled_blobs image to 0, except for the pixels in the largest blob.
            labeled_blobs[labeled_blobs != largest_blob_index] = 0

        # Erode the labeled_blobs image by 3 pixels.
        output_image = erosion(labeled_blobs, footprint=np.ones((3, 3)))

        # Convert the eroded_image into a 3 channel image, with white pixels representing the largest blob and black pixels representing everything else.
        output_image = np.where(output_image[:,:,None] >= 1, [255, 255, 255], [0, 0, 0])
        output_image = resize(output_image, (224, 224), preserve_range=True) 
        # output_image[output_image >=1] = 1
        # Return the output image.
        return output_image

    def compare_binary_blob_areas(self, binary_image1, binary_image2_list, thresh) -> None:
        _, binary_image1 = cv2.threshold(binary_image1, 128, 255, cv2.THRESH_BINARY)
        binary_image1 = cv2.convertScaleAbs(binary_image1, alpha=1.0, beta=0.0)
        binary_image1 = cv2.cvtColor(binary_image1, cv2.COLOR_BGR2GRAY)

        success = 0
        area1 = cv2.findNonZero(binary_image1)
        if area1 is None:
            return False
        else:
            for binary_image2 in binary_image2_list:
                # area1 = len(area1)
                try:
                    area1 = area1.shape[0]
                except: 
                    area1 = area1
                try:
                    area2 = cv2.findNonZero(binary_image2).shape[0]
                except:
                    area2 = area2
                # area2 = len(area2)

                # Check if the difference between the areas is no more than 30%
                if abs(area1 - area2) <= thresh*max(area1, area2):
                    success += 1
            if success > 0:
                return True
            else:
                return False

    def compare_mask(self, mask, accepted_masks, threshold) -> None:
        # Convert the mask to a binary image (with only 0s and 1s)
        _, mask = cv2.threshold(mask, 128, 255, cv2.THRESH_BINARY)

        # Convert each accepted mask to a binary image
        for i in range(len(accepted_masks)):
            _, accepted_masks[i] = cv2.threshold(accepted_masks[i], 128, 255, cv2.THRESH_BINARY)

        # Create a list to store the similarity scores between the mask and the accepted masks
        similarity_scores = []

        mask = cv2.convertScaleAbs(mask, alpha=1.0, beta=0.0)
        mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        # Find the contours of the binary mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        min_score = 999
        # Iterate over the contours of the mask
        for contour in contours:
            # Compare the mask to each accepted mask
            for accepted_mask in accepted_masks:
                # Find the contours of the accepted mask
                accepted_contours, _ = cv2.findContours(accepted_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # Iterate over the contours of the accepted mask
                for accepted_contour in accepted_contours:
                    # Use cv2.matchShapes() to compare the mask to the accepted mask
                    similarity_score = cv2.matchShapes(contour, accepted_contour, cv2.CONTOURS_MATCH_I1, 0)

                    # Add the similarity score to the list of scores
                    similarity_scores.append(similarity_score)

        # Check if any of the similarity scores are below the threshold
        if any(score < threshold for score in similarity_scores):
            # If any of the scores are below the threshold, return True
            min_score = int(round(min(similarity_scores)*100))
            return True, min_score
        else:
            try:
                min_score = int(round(min(similarity_scores)*100))
            except:
                pass
            # If all of the scores are above the threshold, return False
            return False, min_score

    def sweep(self) -> None:
        self.cropped_marker = self.image[self.bbox[1]:self.bbox[3], self.bbox[0]:self.bbox[2]]
        # self.cropped_marker = deskew(self.cropped_marker)  #############################################################################################
        self.cropped_marker_gray = cv2.cvtColor(self.cropped_marker, cv2.COLOR_RGB2GRAY)

        bi_options = [80, 120, 60, 100, 40, 20, 140, 160, 180]
        bi_sweep = []
        bi_sweep_score = []
        print(f"{bcolors.OKGREEN}            Checking marker patterns for {self.location}{bcolors.ENDC}")
        for bi in bi_options:
            ret, candidate_square = cv2.threshold(self.cropped_marker_gray,bi,255,cv2.THRESH_BINARY_INV) # was 127

            candidate_square2 = self.remove_border_blobs(candidate_square)

            result, min_score = self.compare_mask(candidate_square2, self.directory_masks, 0.4)

            result_area = self.compare_binary_blob_areas(candidate_square2, self.directory_masks, 0.3)
            # cv2.imwrite(''.join(["./fieldprism/marker2/",self.image_name.split('.')[0],"__",str(bi),"__","SC-",str(min_score),".jpg"]),candidate_square2)
            if result and result_area:
                # cv2.imwrite(''.join(["./fieldprism/marker/",self.image_name.split('.')[0],"__",str(bi),"__","SC-",min_score,".jpg"]),candidate_square)
                bi_sweep.append(candidate_square)
                bi_sweep_score.append(min_score)

        if bi_sweep != []:
            # Pick lowest score
            best_score = min(bi_sweep_score)
            best_index = bi_sweep_score.index(best_score)
            bi_sweep = bi_sweep[best_index] 
            print(f"{bcolors.OKGREEN}            Best marker score: {str(best_score)} - Picked from {len(bi_sweep_score)} binarized options{bcolors.ENDC}")
            
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
            image_0 = cv2.morphologyEx(bi_sweep, cv2.MORPH_CLOSE, kernel)

            # cv2.imshow('cropped_bi', image_0)
            # cv2.waitKey(0)

            image_0 = image_0.astype(np.uint8)
            self.cropped_marker_bi = image_0#cv2.cvtColor(image_0, cv2.COLOR_RGB2GRAY)

            self.erode_edges(self.cropped_marker_bi,6)
            self.erode_edges(self.cropped_marker_bi,6)

            try:
                self.find_centroid()
            except:
                self.success_conv = False
                self.success_dist = False
        else:
            self.success_conv = False
            self.success_dist = False

    def erode_edges(self, image, n) -> None:
        kernel = np.ones((n, n), np.uint8)
        self.cropped_marker_bi = cv2.erode(image, kernel)
        # cv2.imshow('cropped_bi_erode', self.cropped_marker_bi)
        # cv2.waitKey(0)

    def find_centroid(self) -> None:
        contours, hierarchy = cv2.findContours(self.cropped_marker_bi.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        self.count = len(contours)
        if self.count == 4:
            print(f"{bcolors.OKGREEN}      Number of squares: {self.count}{bcolors.ENDC}")
        else:
            print(f"{bcolors.BOLD}      Number of squares: {self.count}{bcolors.ENDC}")

        # keep only largest 4
        if self.count > 4:
            all_areas= []

            for cnt in contours:
                area = cv2.contourArea(cnt)
                all_areas.append(area)
            sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
            contours = sorted_contours[0:4]
            if len(contours) == 4:
                print(f"{bcolors.OKGREEN}      Number of sorted squares: {len(contours)}{bcolors.ENDC}")
            else:
                print(f"{bcolors.BOLD}      Number of sorted squares: {len(contours)}{bcolors.ENDC}")
            
        self.cropped_marker_plot = self.cropped_marker
        self.centroid_list = []

        for cnt in contours:
            centroid = cv2.moments(cnt)
            # calculate x,y coordinate of center
            try:
                c_x = int(centroid["m10"] / centroid["m00"])
                c_y = int(centroid["m01"] / centroid["m00"])
                self.centroid_list.append([c_x,c_y])
            except:
                pass
            
        hypot_distances = []
        total_distances = []
        kdtree = KDTree(self.centroid_list)
        if len(self.centroid_list)  == 4: #in [3, 4]: # used to be == 4:
            for c in self.centroid_list:
                # Get the conversion factor
                d, i = kdtree.query(c,k=2)
                d = d[1]
                i = i[1]
                hypot_distances.append(d)
                print(f"{bcolors.BOLD}            Closest point to {c} is {self.centroid_list[i]}: distange = {d}{bcolors.ENDC}")
                # Get the center point
                d_t, i_t = kdtree.query(c,k=4)
                total_distances.append(np.sum(d_t))
                
            mean_hypot_distance = np.mean(hypot_distances) # min vs mean ****************************************************************************************************************************************
            # self.one_cm_pixels = np.floor(np.multiply(np.divide(mean_hypot_distance,2),np.sqrt(2))) # removed np.floor
            self.one_cm_pixels = np.multiply(np.divide(mean_hypot_distance,2),np.sqrt(2)) # removed np.floor
            self.success_conv = True
            self.success_dist = True
            print(f"{bcolors.BOLD}      Side of 1 CM square = {self.one_cm_pixels} pixels{bcolors.ENDC}")

            center_location_ind = total_distances.index(min(total_distances))
            self.center_point = self.centroid_list[center_location_ind]
            # cv2.circle(self.cropped_marker_plot, (self.center_point[0], self.center_point[1]), 10, (255, 0, 0), -1)
            print(f"{bcolors.BOLD}      Center point is: {self.center_point}{bcolors.ENDC}")

            self.translate_center_point = [self.bbox[0] + self.center_point[0], self.bbox[1] + self.center_point[1]]

            ### if the binarization is a failure, then the center point might have drifted. If it did, then treat it as failure
            x_wiggle = np.multiply((self.bbox[2] - self.bbox[0]), 0.15)
            y_wiggle = np.multiply((self.bbox[3] - self.bbox[1]), 0.15)
            new_point_x_low = int(self.rough_center[0] -  x_wiggle)
            new_point_x_high = int(self.rough_center[0] + x_wiggle)
            new_point_y_low = int(self.rough_center[1] - y_wiggle)
            new_point_y_high = int(self.rough_center[1] + y_wiggle)

            if ((new_point_x_low < self.translate_center_point[0]) and (new_point_x_high > self.translate_center_point[0]) and 
                (new_point_y_low < self.translate_center_point[1]) and (new_point_y_high > self.translate_center_point[1])):
                self.translate_center_point = self.translate_center_point
                self.is_approx = False
            else:
                self.translate_center_point = self.rough_center
                self.one_cm_pixels = np.nan
                self.is_approx = True
            print('')
            
        else:
            self.one_cm_pixels = np.nan
            self.success_conv = True
            self.success_dist = False
            self.is_approx = True
            self.translate_center_point = self.rough_center
            print(f"{bcolors.WARNING}      Could not locate all four markers in {self.location} of image {self.image_name}{bcolors.ENDC}")
        # cv2.imshow("Image", self.cropped_marker_plot)
        # cv2.waitKey(0)



'''
Helper Functions
'''
def correct_distortion(cfg, image, centers, ratio):
    rows,cols,ch = image.shape

    new_h = math.sqrt((centers[2][0]-centers[1][0])*(centers[2][0]-centers[1][0])+(centers[2][1]-centers[1][1])*(centers[2][1]-centers[1][1]))
    new_w = np.multiply(ratio,new_h)
    centers_corrected = np.float32([[centers[0][0],centers[0][1]], [centers[0][0]+new_w, centers[0][1]], [centers[0][0]+new_w, centers[0][1]+new_h], [centers[0][0], centers[0][1]+new_h]])
    
    warped = cv2.getPerspectiveTransform(np.array(centers, np.float32), np.array(centers_corrected, np.float32))

    offset_w = 1000 + cols
    offset_h = 1000 + rows

    transformed = np.zeros((int(new_w + offset_w), int(new_h + offset_h)), dtype=np.uint8)
    dst = cv2.warpPerspective(image, warped, transformed.shape)
    
    points = np.float32([[[centers[0][0],centers[0][1]]], [[centers[1][0], centers[1][1]]], [[centers[2][0], centers[2][1]]], [[centers[3][0], centers[3][1]]]])

    # Transform the points
    shifted_points_0 = np.array(cv2.perspectiveTransform(points, warped))
    
    # implot = dst####
    shifted_points = []
    for row in shifted_points_0:
        px = int(row[0][0])
        py = int(row[0][1])
        shifted_points.append([px, py])
        # implot = cv2.circle(implot, [px, py], 50, color=(0, 0, 255), thickness=10)
    # cv2.imwrite("result.png",implot)

    if cfg['fieldprism']['justify_corrected_images']['do_justify']:
        if cfg['fieldprism']['justify_corrected_images']['make_uniform']:
            x_justify = int(cfg['fieldprism']['justify_corrected_images']['justify_corrected_images_origin'])
            y_justify = int(cfg['fieldprism']['justify_corrected_images']['justify_corrected_images_origin'])
            extra = int(cfg['fieldprism']['justify_corrected_images']['make_uniform_buffer'])

            TL_x = int(shifted_points[0][0])
            TL_y = int(shifted_points[0][1])

            TR_x = int(shifted_points[1][0]) #+ extra
            BR_y = int(shifted_points[2][1]) #+ extra


            # h = int(cfg['fieldprism']['justify_corrected_images']['uniform_h'])
            # w = int(cfg['fieldprism']['justify_corrected_images']['uniform_w'])
            origin = int(cfg['fieldprism']['justify_corrected_images']['justify_corrected_images_origin'])
            # extra = int(cfg['fieldprism']['justify_corrected_images']['make_uniform_buffer'])
            # _, conv_x = get_approx_conv_factor(cfg)
            # scale_success, ratio_x = get_scale_ratio(cfg)
            # ratio_y = 1/ratio_x
            # conv_y = int(conv_x*ratio_y)

            # real_width = TR_x - TL_x
            # real_height = BR_y - TL_y
            # fill_width = w - origin - extra
            # fill_height = h - origin - extra
            
            # strecth_x = real_width / fill_width
            # strecth_y = real_height / fill_height
            # fudge = int(((30 * 2) + conv_x) * strecth_x) # the marker is 30mm wide

            # new_origin = origin - int((strecth_x * origin))

            x_shift = origin - TL_x
            y_shift = origin - TL_y

            M = np.float32([
                [1, 0, x_shift],
                [0, 1, y_shift]
            ])

            # im = Image.fromarray(dst)
            # im.show()

            ### dst image is in TL corner, lots of black space south and east
            # shift to put TL center on (500,500)
            dst0 = cv2.warpAffine(dst, M, (dst.shape[1], dst.shape[0]))

            # im = Image.fromarray(dst0)
            # im.show()

            shifted_points2 = []
            for row in shifted_points:
                px = int(row[0]) + x_shift
                py = int(row[1]) + y_shift
                shifted_points2.append([px, py])
            
            # implot = dst0####
            # for row in shifted_points2:
            #     px = row[0]
            #     py = row[1]
            #     implot = cv2.circle(implot, [px, py], 50, color=(0, 0, 255), thickness=10)
            # cv2.imwrite("result.png",implot)
                
            TL_x = int(shifted_points2[0][0])
            TL_y = int(shifted_points2[0][1])

            TR_x = int(shifted_points2[1][0]) #+ extra
            BR_y = int(shifted_points2[2][1]) #+ extra

            # TR_x = int(shifted_points2[1][0]) + extra
            # BR_y = int(shifted_points2[2][1]) + extra
            dst0 = remove_black_space_justify(dst0)

            ##########################
            # x_shift = origin - TL_x
            # y_shift = origin - TL_y

            # M = np.float32([
            #     [1, 0, x_shift],
            #     [0, 1, y_shift]
            # ])

            # shift to put TL center on (500,500)
            # dst1 = cv2.warpAffine(dst0, M, (dst0.shape[1], dst0.shape[0]))
            # im = Image.fromarray(dst1)
            # im.show()

            # shifted_points3 = []
            # for row in shifted_points2:
            #     px = int(row[0]) + x_shift
            #     py = int(row[1]) + y_shift
            #     shifted_points3.append([px, py])
            
            # implot = dst0####
            # for row in shifted_points2:
            #     px = row[0]
            #     py = row[1]
            #     implot = cv2.circle(implot, [px, py], 50, color=(0, 0, 255), thickness=10)
            # cv2.imwrite("result.png",implot)
                
            # TL_x = int(shifted_points3[0][0])
            # TL_y = int(shifted_points3[0][1])

            # TR_x = int(shifted_points3[1][0]) #+ extra
            # BR_y = int(shifted_points3[2][1]) #+ extra

            # TR_x = int(shifted_points2[1][0]) + extra
            # BR_y = int(shifted_points2[2][1]) + extra
            # dst = remove_black_space_justify(dst)

            dst_fit = remove_black_space_justify_uniform(cfg, dst0, TL_x, TL_y, TR_x, BR_y)
            # im = Image.fromarray(dst_fit)
            # im.show()

        else:
            x_justify = int(cfg['fieldprism']['justify_corrected_images']['justify_corrected_images_origin'])
            y_justify = int(cfg['fieldprism']['justify_corrected_images']['justify_corrected_images_origin'])
            # extra = int(cfg['fieldprism']['make_uniform_buffer'])
            TL_x = int(centers_corrected[0][0])
            TL_y = int(centers_corrected[0][1])

            # TR_x = int(centers_corrected[1][0]) + extra
            # BR_y = int(centers_corrected[2][1]) + extra


            x_shift = x_justify - TL_x
            y_shift = y_justify - TL_y

            M = np.float32([
                [1, 0, x_shift],
                [0, 1, y_shift]
            ])

            dst = cv2.warpAffine(dst, M, (dst.shape[1], dst.shape[0]))
            dst_fit = remove_black_space_justify(dst)#), TR_x, BR_y)
    else:
        dst_fit = remove_black_space(dst)

    # cv2.imshow("Image", dst_fit)
    # cv2.waitKey(0)

    return dst_fit, centers_corrected

def resize_and_pad(img, size, padColor=0):

    h, w = img.shape[:2]
    sh, sw = size

    # interpolation method
    if h > sh or w > sw: # shrinking image
        interp = cv2.INTER_AREA
    else: # stretching image
        interp = cv2.INTER_CUBIC

    # aspect ratio of image
    aspect = w/h  # if on Python 2, you might need to cast as a float: float(w)/h

    # compute scaling and pad sizing
    if aspect > 1: # horizontal image
        new_w = sw
        new_h = np.round(new_w/aspect).astype(int)
        pad_vert = (sh-new_h)/2
        pad_top, pad_bot = np.floor(pad_vert).astype(int), np.ceil(pad_vert).astype(int)
        pad_left, pad_right = 0, 0
    elif aspect < 1: # vertical image
        new_h = sh
        new_w = np.round(new_h*aspect).astype(int)
        pad_horz = (sw-new_w)/2
        pad_left, pad_right = np.floor(pad_horz).astype(int), np.ceil(pad_horz).astype(int)
        pad_top, pad_bot = 0, 0
    else: # square image
        new_h, new_w = sh, sw
        pad_left, pad_right, pad_top, pad_bot = 0, 0, 0, 0

    # set pad color
    if len(img.shape) == 3 and not isinstance(padColor, (list, tuple, np.ndarray)): # color image but only one color provided
        padColor = [padColor]*3

    # scale and pad
    scaled_img = cv2.resize(img, (new_w, new_h), interpolation=interp)
    scaled_img = scaled_img[0:sh, 0:sw]
    try:
        scaled_img = cv2.copyMakeBorder(scaled_img, pad_top, pad_bot, pad_left, pad_right, borderType=cv2.BORDER_CONSTANT, value=padColor)
    except:
        pass
    return scaled_img

def remove_black_space(image):
    rows = np.any(image, axis=1)
    cols = np.any(image, axis=0)
    ymin, ymax = np.where(rows)[0][[0, -1]]
    xmin, xmax = np.where(cols)[0][[0, -1]]
    return image[ymin:ymax+1, xmin:xmax+1]

def remove_black_space_justify(image):#, TR_x, BR_y):
    rows = np.any(image, axis=1)
    cols = np.any(image, axis=0)
    ymin, ymax = np.where(rows)[0][[0, -1]]
    xmin, xmax = np.where(cols)[0][[0, -1]]
    return image[0:ymax+1, 0:xmax+1]

def remove_black_space_justify_uniform(cfg, image, TL_x, TL_y, TR_x, BR_y):
    # im = Image.fromarray(image)
    # im.show()
    h = int(cfg['fieldprism']['justify_corrected_images']['uniform_h'])
    w = int(cfg['fieldprism']['justify_corrected_images']['uniform_w'])
    origin = int(cfg['fieldprism']['justify_corrected_images']['justify_corrected_images_origin'])
    extra = int(cfg['fieldprism']['justify_corrected_images']['make_uniform_buffer'])
    _, conv_x = get_approx_conv_factor(cfg)
    scale_success, ratio_x = get_scale_ratio(cfg)
    ratio_y = 1/ratio_x
    conv_y = int(conv_x*ratio_y)

    real_width = TR_x - TL_x
    real_height = BR_y - TL_y
    fill_width = w - origin - origin
    fill_height = h - origin - origin
    
    mm_buffer = int(extra * (real_width / conv_x))

    strecth_x = real_width / fill_width
    strecth_y = real_height / fill_height
    fudge = int(((30 * 2) + conv_x) * strecth_x) # the marker is 30mm wide

    new_origin = origin - int((strecth_x * origin))
    new_extra_x = origin - int(strecth_x * origin)
    new_extra_y = origin - int(strecth_y * origin)

    start_y = int(TL_y - (strecth_y * real_height*0.1)) - mm_buffer
    end_y = int(BR_y + (strecth_y * real_height*0.1)) + mm_buffer
    start_x = int(TL_x - (strecth_y * real_height*0.1)) - mm_buffer
    end_x = int(TR_x + (strecth_y * real_height*0.1)) + mm_buffer
    if start_y < 0: start_y = 0
    if start_x < 0: start_x = 0
    if end_y > image.shape[0]: end_y = image.shape[0]
    if end_x > image.shape[1]: end_x = image.shape[1]

    # im = Image.fromarray(image)
    # im.show()

    image = image[start_y: end_y, start_x: end_x]

    # image = image[new_origin - fudge : BR_y + new_extra_y + fudge, new_origin - fudge: TR_x + new_extra_x + fudge]
    # image = image[0 : BR_y + new_extra_x, 0: TR_x + new_extra_x]

    # im = Image.fromarray(image)
    # im.show()

    image = resize_and_pad(image, (h,w), 0)

    # im = Image.fromarray(image)
    # im.show()

    return image

def determine_success(Marker_Top_Left,Marker_Top_Right,Marker_Bottom_Left,Marker_Bottom_Right):
    if (Marker_Top_Left.success_conv and Marker_Top_Right.success_conv and Marker_Bottom_Left.success_conv and Marker_Bottom_Right.success_conv):
        use_distortion_correction = True
        if (Marker_Top_Left.success_dist or Marker_Top_Right.success_dist or Marker_Bottom_Left.success_dist or Marker_Bottom_Right.success_dist):
            use_conversion = True
        else:
            use_conversion = False
    elif (Marker_Top_Left.success_dist or Marker_Top_Right.success_dist or Marker_Bottom_Left.success_dist or Marker_Bottom_Right.success_dist):
        use_distortion_correction = False
        use_conversion = True
    else:
        use_distortion_correction = False
        use_conversion = False

    list_index = [Marker_Top_Left.label_row, Marker_Top_Right.label_row, Marker_Bottom_Right.label_row, Marker_Bottom_Left.label_row]
    set_index = set(list_index)
    if len(list_index) != len(set_index):
        use_distortion_correction = False
    return use_distortion_correction, use_conversion

def determine_success_unknown(Marker_Unknown):
    if Marker_Unknown.success_conv:
        use_conversion = True
    else:
        use_conversion = False
    return use_conversion


def get_label_from_index(cls):#,annoType):
    # if annoType == 'PLANT':
    #     if cls == 0:
    #         annoInd = 'Leaf_WHOLE'
    #     elif cls == 1:
    #         annoInd = 'Leaf_PARTIAL'
    #     elif cls == 2:
    #         annoInd = 'Leaflet'
    #     elif cls == 3:
    #         annoInd = 'Seed_Fruit_ONE'
    #     elif cls == 4:
    #         annoInd = 'Seed_Fruit_MANY'
    #     elif cls == 5:
    #         annoInd = 'Flower_ONE'
    #     elif cls == 6:
    #         annoInd = 'Flower_MANY'
    #     elif cls == 7:
    #         annoInd = 'Bud'
    #     elif cls == 8:
    #         annoInd = 'Specimen'
    #     elif cls == 9:
    #         annoInd = 'Roots'
    #     elif cls == 10:
    #         annoInd = 'Wood'
    # if annoType == 'PREP':
    if cls == 0:
        annoInd = 'Ruler'
    elif cls == 1:
        annoInd = 'Barcode'
    elif cls == 2:
        annoInd = 'Colorcard'
    elif cls == 3:
        annoInd = 'Label'
    elif cls == 4:
        annoInd = 'Map'
    elif cls == 5:
        annoInd = 'Envelope'
    elif cls == 6:
        annoInd = 'Photo'
    elif cls == 7:
        annoInd = 'Attached Item'
    elif cls == 8:
        annoInd = 'Weights'
    return annoInd
