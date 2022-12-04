# Run yolov5 on dir
import os, yaml, cv2, torch, math, time, re, pybboxes
import numpy as np
from torchvision.utils import draw_bounding_boxes, draw_keypoints
from torchvision.transforms import ToPILImage
from dataclasses import dataclass, field
from scipy.spatial import KDTree
from pathlib import Path
from tqdm import tqdm
from typing import List, Optional, Tuple, Union
from PIL import Image, ImageColor, ImageDraw, ImageFont
import pandas as pd
import platform
import tkinter
import matplotlib.pyplot as plt
from skimage.transform import resize 
from skimage.metrics import structural_similarity as ssim
from skimage.filters import threshold_otsu 
from skimage.morphology import closing, square 
from skimage.measure import find_contours 
from skimage import filters, transform
from skimage.measure import label
from skimage.morphology import dilation, erosion
# from qrcode.image.styledpil import StyledPilImage

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'



@dataclass
class ImageCorrected:
    path: str = ''
    location: str = ''
    image: list = field(default_factory=None)

    def __init__(self, path, image, location) -> None:
        self.path = path
        self.location = location
        self.image = image

@dataclass
class ImageOverlay:
    path: str = ''
    location: str = ''
    image: list = field(default_factory=None)

    def __init__(self, path, image, location) -> None:
        self.path = path
        self.location = location
        self.image = image

@dataclass
class File_Structure():
    path_distortion_corrected: str = ''
    path_distortion_not_corrected: str = ''
    path_markers_missing: str = ''
    path_overlay: str = ''
    path_overlay_not: str = ''
    path_QRcodes_raw : str = ''
    path_QRcodes_summary: str = ''
    path_Detections_for_Distortion_Correction: str = ''
    path_Detections_for_Processsing: str = '' 
    path_Data: str = '' 
    path_Config: str = '' 
    actual_save_dir: str = '' 

    def __init__(self, actual_save_dir) -> None:
        self.actual_save_dir = actual_save_dir
        self.path_distortion_corrected = os.path.join(actual_save_dir,'Images_Corrected')
        self.path_distortion_not_corrected = os.path.join(actual_save_dir,'Images_Not_Corrected')
        self.path_markers_missing = os.path.join(actual_save_dir,'Images_Markers_Missing')
        self.path_overlay = os.path.join(actual_save_dir,'Overlay_Corrected')
        self.path_overlay_not = os.path.join(actual_save_dir,'Overlay_Not_Corrected')
        self.path_QRcodes_raw = os.path.join(actual_save_dir,'QR_Code_Bin')
        # self.path_QRcodes_summary = os.path.join(actual_save_dir,'QR_Codes_Summary')
        self.path_Detections_for_Distortion_Correction = os.path.join(actual_save_dir,'Detections_Not_Corrected')
        self.path_Detections_for_Processsing = os.path.join(actual_save_dir,'Detections_Corrected')
        self.path_Data = os.path.join(actual_save_dir,'Data')
        self.path_Config = os.path.join(actual_save_dir,'Config')

        validate_dir(self.path_distortion_corrected)
        validate_dir(self.path_distortion_not_corrected)
        validate_dir(self.path_markers_missing)
        validate_dir(self.path_overlay)
        validate_dir(self.path_overlay_not)
        validate_dir(self.path_QRcodes_raw)
        # validate_dir(self.path_QRcodes_summary)
        validate_dir(self.path_Detections_for_Distortion_Correction)
        validate_dir(self.path_Detections_for_Processsing)
        validate_dir(self.path_Data)
        validate_dir(self.path_Config)

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

            candidate_square = self.remove_border_blobs(candidate_square)

            result, min_score = self.compare_mask(candidate_square, self.directory_masks, 0.4)

            result_area = self.compare_binary_blob_areas(candidate_square, self.directory_masks, 0.3)
            cv2.imwrite(''.join(["./fieldprism/marker2/",self.image_name.split('.')[0],"__",str(bi),"__","SC-",str(min_score),".jpg"]),candidate_square)
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
            self.cropped_marker_bi = cv2.cvtColor(image_0, cv2.COLOR_RGB2GRAY)

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
        if len(self.centroid_list) in [3, 4]: # used to be == 4:
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
            self.one_cm_pixels = np.floor(np.multiply(np.divide(mean_hypot_distance,2),np.sqrt(2))) # removed np.floor
            self.success_conv = True
            self.success_dist = True
            print(f"{bcolors.BOLD}      Side of 1 CM square = {self.one_cm_pixels} pixels{bcolors.ENDC}")

            center_location_ind = total_distances.index(min(total_distances))
            self.center_point = self.centroid_list[center_location_ind]
            # cv2.circle(self.cropped_marker_plot, (self.center_point[0], self.center_point[1]), 10, (255, 0, 0), -1)
            print(f"{bcolors.BOLD}      Center point is: {self.center_point}{bcolors.ENDC}")

            self.translate_center_point = [self.bbox[0] + self.center_point[0], self.bbox[1] + self.center_point[1]]

            ### if the binarization is a failure, then the center point might have drifted. If it did, then treat it as failure
            x_wiggle = np.multiply((self.bbox[2] - self.bbox[0]), 0.25)
            y_wiggle = np.multiply((self.bbox[3] - self.bbox[1]), 0.25)
            new_point_x_low = int(self.rough_center[0] -  x_wiggle)
            new_point_x_high = int(self.rough_center[0] + x_wiggle)
            new_point_y_low = int(self.rough_center[1] - y_wiggle)
            new_point_y_high = int(self.rough_center[1] + y_wiggle)

            if ((new_point_x_low < self.translate_center_point[0]) and (new_point_x_high > self.translate_center_point[0]) and 
                (new_point_y_low < self.translate_center_point[1]) and (new_point_y_high > self.translate_center_point[1])):
                self.translate_center_point = self.translate_center_point
            else:
                self.translate_center_point = self.rough_center
                self.one_cm_pixels = np.nan
            print('')
            
        else:
            self.one_cm_pixels = np.nan
            self.success_conv = True
            self.success_dist = False
            self.translate_center_point = self.rough_center
            print(f"{bcolors.WARNING}      Could not locate all four markers in {self.location} of image {self.image_name}{bcolors.ENDC}")
        # cv2.imshow("Image", self.cropped_marker_plot)
        # cv2.waitKey(0)

@dataclass
class QRcode:
    text_raw: str = ''

    rank: str = ''
    rank_value: str = ''

    number: int = 0
    success: bool = False
    expanded: bool = False
    expanded_n: int = 50

    image_name_jpg: str = ''
    image_name: str = ''
    image: list = field(default_factory=None)
    image_bboxes: list = field(default_factory=None)
    image_centroids: list = field(default_factory=None)

    row: list = field(default_factory=None)
    bbox: list = field(default_factory=None)
    rough_center: list = field(default_factory=None)
    centroid_list: list = field(default_factory=None)
    croppped_QRcode: list = field(default_factory=None)
    qr_code_bi: list = field(default_factory=None)

    path_QRcodes_raw: str = ''
    path_QRcodes_summary: str = ''

    name_QR_raw_png: str = ''

    straight_qrcode: list = field(default_factory=None)
    

    def __init__(self, number, image_name_jpg, image, image_bboxes, row, bbox, path_QRcodes_raw, path_QRcodes_summary) -> None:
        self.image_name_jpg = image_name_jpg
        self.path_QRcodes_raw = path_QRcodes_raw
        self.path_QRcodes_summary = path_QRcodes_summary
        self.number = str(number)
        self.image = image
        self.image_bboxes = image_bboxes
        self.row = row
        self.bbox = bbox
        self.image_name = self.image_name_jpg.split('.')[0]
        self.name_QR_raw_png = ''.join([self.image_name,'__QR_',self.number,'.png'])
        self.crop_QRcode()
        self.process_QRcode()
        self.parse_text()

    def parse_text(self) -> None:
        if self.text_raw != '':
            self.rank = self.text_raw.split(':')[0]
            self.rank_value = self.text_raw.split(':')[1]


    def crop_QRcode(self) -> None:
        self.croppped_QRcode = self.image[self.bbox[1]:self.bbox[3], self.bbox[0]:self.bbox[2]]
        # cv2.imwrite(os.path.join(self.path_QRcodes_raw,self.name_QR_raw_png),self.croppped_QRcode)
        # cv2.imshow('QR_Code', self.croppped_QRcode)
        # cv2.waitKey(0)
    
    def expand_QRcode(self, n_pixels) -> None:
        h,w,ch = self.image.shape
        # n_pixels = 100

        new_A = max(self.bbox[1] - n_pixels, 0)
        new_B = min(self.bbox[3] + n_pixels, h)
        new_C = max(self.bbox[0] - n_pixels, 0)
        new_D = min(self.bbox[2] + n_pixels, w)
        self.croppped_QRcode = self.image[new_A:new_B, new_C:new_D]
        self.expanded = True
        self.expanded_n = 50
        # cv2.imwrite(os.path.join(self.path_QRcodes_raw,self.name_QR_raw_png),self.croppped_QRcode)

    def prepare_QRcode(self,bi) -> None:
        ret, self.qr_code_bi = cv2.threshold(self.croppped_QRcode,bi,255,cv2.THRESH_BINARY)
        # cv2.imshow('QR_Code', self.qr_code_bi)
        # cv2.waitKey(0)

    def get_QR_level(self) -> None:
        use_default = False
        if '|' in self.text_raw:
            use_default = True
        level = self.text_raw.split(':')[0]
        level = level.split('_')[1]
        sep = ""
        name = sep.join(['L',str(level),'.jpg'])
        image_QR_level = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'QR_code_builder', 'QR_levels',name)
        return use_default, image_QR_level

    def insert_straight_QR_code(self) -> None:
        max_y, max_x, chan = self.image.shape
        min_dim = min([self.qr_code_bi.shape[0],self.qr_code_bi.shape[1]])
        
        if self.expanded:
            min_dim = min_dim - np.multiply(self.expanded_n, 2)

        new_dim = int(np.multiply(min_dim, 0.9))
        new_dim_offset = int(np.multiply(min_dim, 0.05))

        start_x = self.bbox[0] + new_dim_offset
        start_y = self.bbox[1] + new_dim_offset

        # Build new QR code
        # use_default, image_QR_level = self.get_QR_level()
        use_default = False
        if use_default:
            new_QR_code = cv2.resize(self.straight_qrcode, (new_dim, new_dim), interpolation = cv2.INTER_AREA)
            new_QR_code = cv2.cvtColor(new_QR_code,cv2.COLOR_GRAY2RGB)  
            
            new_bg = np.zeros((min_dim, min_dim,3))
            new_bg[new_bg == 0] = 255

            stop_x = start_x + min_dim
            stop_y = start_y + min_dim

            if stop_y >= max_y:
                start_y = start_y - (stop_y - max_y)
                stop_y = max_y
            if stop_x >= max_x:
                start_x = start_x - (stop_x - max_x)
                stop_x = max_x

            self.image[start_y : stop_y , start_x : stop_x] = new_bg.astype(np.uint8)
            self.image[start_y + new_dim_offset : start_y + new_QR_code.shape[0] + new_dim_offset , start_x + new_dim_offset : start_x + new_QR_code.shape[0] + new_dim_offset ] = new_QR_code

            
        else: # Build new including level image
            new_QR_code = cv2.QRCodeEncoder().create()
            new_QR_code.Params.correction_level = 3
            new_QR_code = new_QR_code.encode(self.text_raw)
            new_QR_code = cv2.resize(new_QR_code, (new_dim, new_dim), interpolation = cv2.INTER_AREA)
            new_QR_code = cv2.cvtColor(new_QR_code,cv2.COLOR_GRAY2RGB)  
            
            # qr = qrcode.QRCode(version=4, # version might need to be higher?
            #     error_correction=qrcode.constants.ERROR_CORRECT_H,
            #     box_size=10,border=4)
            # qr.add_data(self.text_raw)
            
            # new_QR_code = qr.make_image(fill_color="black", back_color="white",
            #     image_factory=StyledPilImage, embeded_image_path=image_QR_level)
            # new_QR_code.save(os.path.join(self.path_QRcodes_raw,'temp.png'))
            # new_QR_code = cv2.imread(os.path.join(self.path_QRcodes_raw,'temp.png'))
            # dim_scale = new_QR_code.shape[0]
            # try:
            #     os.remove(os.path.join(self.path_QRcodes_raw,'temp.png'))
            # except:
            #     time.sleep(1)
            #     os.remove(os.path.join(self.path_QRcodes_raw,'temp.png'))
            # if dim_scale >= min_dim: # shrink
            #     new_QR_code = cv2.resize(new_QR_code, (min_dim, min_dim), interpolation = cv2.INTER_AREA)
            # else: # upscale
            #     new_QR_code = cv2.resize(new_QR_code, (min_dim, min_dim), interpolation = cv2.INTER_CUBIC)
            # ret, new_QR_code = cv2.threshold(new_QR_code,60,255,cv2.THRESH_BINARY)

            stop_x = start_x + new_dim - new_dim_offset
            stop_y = start_y + new_dim - new_dim_offset

            if stop_y >= max_y:
                start_y = start_y - (stop_y - max_y)
                stop_y = max_y
            if stop_x >= max_x:
                start_x = start_x - (stop_x - max_x)
                stop_x = max_x

            self.image[start_y : start_y + new_QR_code.shape[0], start_x : start_x + new_QR_code.shape[0]] = new_QR_code

    def decode_QRcode_RGB(self) -> None:
        # cv2.imshow('QR_Code success', self.croppped_QRcode)
        # cv2.waitKey(0)
        # cv2.imshow('QR_Code success', self.qr_code_bi)
        # cv2.waitKey(0)
        try:
            content, pts, self.straight_qrcode = cv2.QRCodeDetector().detectAndDecode(self.croppped_QRcode)
        except:
            content = ''
            self.straight_qrcode = None

        # try:
        #     content, pts, self.straight_qrcode = cv2.QRCodeDetector().detectAndDecode(self.croppped_QRcode)
        #     if content == '':
        #         content, pts, self.straight_qrcode = cv2.QRCodeDetector().detectAndDecodeCurved(self.croppped_QRcode)
        # except:
        #     content = ''
        #     self.straight_qrcode = None

        if content != '':
            self.text_raw = content
            bad_code = False
        else:
            bad_code = True
        return bad_code

    def decode_QRcode(self) -> None:
        try:
            content, pts, self.straight_qrcode = cv2.QRCodeDetector().detectAndDecode(self.qr_code_bi)
        except:
            content = ''
            self.straight_qrcode = None
        # try:
        #     content, pts, self.straight_qrcode = cv2.QRCodeDetector().detectAndDecode(self.qr_code_bi)
        #     if content == '':
        #         content, pts, self.straight_qrcode = cv2.QRCodeDetector().detectAndDecodeCurved(self.qr_code_bi)
        # except:
        #     content = ''
        #     self.straight_qrcode = None

        if content != '':
            self.text_raw = content
            bad_code = False
        else:
            bad_code = True
        return bad_code

    def process_QRcode(self) -> None:
        ''' First pass of QR code reader'''
        bad_code = True

        self.prepare_QRcode(80)
        bad_code = self.decode_QRcode_RGB()
        if not bad_code:
            print(f"{bcolors.OKGREEN}            Success! Quick read RGB. QR Code Content: {self.text_raw}{bcolors.ENDC}")

        if bad_code:
            bad_code = self.decode_QRcode()
            if not bad_code:
                print(f"{bcolors.OKGREEN}            Success! Quick read binary. QR Code Content: {self.text_raw}{bcolors.ENDC}")

        ''' If not successful, adjust binarization '''
        bi_options = range(10, 200, 10)
        if bad_code:
            while bad_code:
                print('            Trying binarization level:',end="")
                for bi in bi_options:
                    print(f' {bi},',end="")
                    self.prepare_QRcode(bi)
                    bad_code = self.decode_QRcode()
                    if not bad_code:
                        print('')
                        print(f"{bcolors.OKGREEN}            Success! Changed binarization to {bi}. QR Code Content: {self.text_raw}{bcolors.ENDC}")
                        
                        # cv2.imshow('QR_Code success', self.qr_code_bi)
                        # cv2.waitKey(0)
                        
                        break
                    elif bi >= 190:
                        print('')
                        print(f"{bcolors.BOLD}            Expanding QR code bounding box{bcolors.ENDC}")
                        ''' If binarization fails, expand the QR Code bbox by n pixels'''
                        n_pixels = 50
                        self.expand_QRcode(n_pixels)
                        bad_code = True
                        self.prepare_QRcode(80)
                        bad_code = self.decode_QRcode()

                        # cv2.imshow('QR_Code failed bi', self.qr_code_bi)
                        # cv2.waitKey(0)

                        ''' If not successful, adjust binarization '''
                        bi_options = range(10, 200, 10)
                        if not bad_code:
                            print(f"{bcolors.OKGREEN}            Success! Expanded QR Code bbox by {n_pixels} pixels. QR Code Content: {self.text_raw}{bcolors.ENDC}")
                        else:
                            while bad_code:
                                print('            Trying binarization level:',end="")
                                for bi2 in bi_options:
                                    print(f' {bi2},',end="")
                                    self.prepare_QRcode(bi2)
                                    bad_code = self.decode_QRcode()
                                    if not bad_code:
                                        print('')
                                        print(f"{bcolors.OKGREEN}            Success! Expanded QR Code bbox by {n_pixels} pixels. QR Code Content: {self.text_raw}{bcolors.ENDC}")
                                        # cv2.imshow('QR_Code after expand', self.qr_code_bi)
                                        # cv2.waitKey(0)
                                        break
                                    elif bi2 >= 190:
                                        print('')
                                        print(f"{bcolors.FAIL}            FAILED TO READ QR CODE{bcolors.ENDC}")
                                        bad_code = False
                                        break
        # else:
            # print("")
            # print(f"{bcolors.OKGREEN}            Success! QR Code Content: {self.text_raw}{bcolors.ENDC}")
            # cv2.imshow('QR_Code End', self.qr_code_bi)
            # cv2.waitKey(0)

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

# TODO completely inside/outside
def remove_overlapping_predictions(priority_item, remove_item, img_w, img_h):
    keep_remove = []
    for i_r, remove in remove_item.iterrows(): 
        do_keep_ru = True
        bbox_remove = (remove[1], remove[2], remove[3], remove[4])
        bbox_remove = pybboxes.convert_bbox(bbox_remove, from_type="yolo", to_type="voc", image_size=(img_w, img_h))
        for i_bc, priority in priority_item.iterrows(): 
            bbox_priority = (priority[1], priority[2], priority[3], priority[4])
            bbox_priority = pybboxes.convert_bbox(bbox_priority, from_type="yolo", to_type="voc", image_size=(img_w, img_h))
            # Intersection
            if (bbox_remove[0] >= bbox_priority[2]) or (bbox_remove[2]<=bbox_priority[0]) or (bbox_remove[3]<=bbox_priority[1]) or (bbox_remove[1]>=bbox_priority[3]):
                continue
            # Completely inside of the remove bbox
            elif ((bbox_remove[0] <= bbox_priority[0]) and (bbox_remove[1] <= bbox_priority[1]) and (bbox_remove[2] >= bbox_priority[2])  and (bbox_remove[3] >= bbox_priority[3])):
                continue
            # Completely surrounding the remove bbox
            elif ((bbox_remove[0] >= bbox_priority[0]) and (bbox_remove[1] >= bbox_priority[1]) and (bbox_remove[2] <= bbox_priority[2])  and (bbox_remove[3] <= bbox_priority[3])):
                continue
            else:
                do_keep_ru = False
        if do_keep_ru:
            keep_remove.append(remove.values)
    remove_item = pd.DataFrame(keep_remove)
    return priority_item, remove_item

''' Rotate image, has 180 option, works with pytorch tensor images too '''
def make_image_vertical(image, h, w, do_rotate_180):
    did_rotate = False
    if do_rotate_180:
        # try:
        image = cv2.rotate(image, cv2.ROTATE_180)
        img_h, img_w, img_c = image.shape
        did_rotate = True
        # print("      Rotated 180")
    else:
        if h < w:
            # try:
            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
            img_h, img_w, img_c = image.shape
            did_rotate = True
            # print("      Rotated 90 CW")
        elif h >= w:
            image = image
            img_h = h
            img_w = w
            # print("      Not Rotated")
    return image, img_h, img_w, did_rotate

def make_images_in_dir_vertical(dir_images_unprocessed):
    n_rotate = 0
    n_total = len(os.listdir(dir_images_unprocessed))
    for image_name_jpg in tqdm(os.listdir(dir_images_unprocessed), desc=f'{bcolors.HEADER}Checking Image Dimensions{bcolors.ENDC}',colour="cyan",position=0,total = n_total):
        image = cv2.imread(os.path.join(dir_images_unprocessed, image_name_jpg))
        h, w, img_c = image.shape
        image, img_h, img_w, did_rotate = make_image_vertical(image, h, w, do_rotate_180=False)
        if did_rotate:
            n_rotate += 1
        cv2.imwrite(os.path.join(dir_images_unprocessed,image_name_jpg), image)
    print(f"{bcolors.BOLD}Number of Images Rotated: {n_rotate}{bcolors.ENDC}")

def rotate_image_90_ccw(image):
    image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    img_h, img_w, img_c = image.shape
    return image, img_h, img_w

def make_file_names_valid(dir):
    list_of_files = os.listdir(dir)
    n = len(list_of_files)
    d = f'{bcolors.HEADER}Checking File Names{bcolors.ENDC}'
    for file in tqdm(list_of_files, desc=d,colour="green",position=0,total = n):
        name = Path(file).stem
        ext = Path(file).suffix
        name_cleaned = re.sub(r"[^a-zA-Z0-9_-]","-",name)
        name_new = ''.join([name_cleaned,ext])
        os.rename(os.path.join(dir,file), os.path.join(dir,name_new))

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

def increment_path(path, exist_ok=False, sep='', mkdir=False):
    # Increment file or directory path, i.e. runs/exp --> runs/exp{sep}2, runs/exp{sep}3, ... etc.
    path = Path(path)  # os-agnostic
    if path.exists() and not exist_ok:
        path, suffix = (path.with_suffix(''), path.suffix) if path.is_file() else (path, '')

        # Method 1
        for n in range(2, 9999):
            p = f'{path}{sep}{n}{suffix}'  # increment path
            if not os.path.exists(p):  #
                break
        path = Path(p)

        # Method 2 (deprecated)
        # dirs = glob.glob(f"{path}{sep}*")  # similar paths
        # matches = [re.search(rf"{path.stem}{sep}(\d+)", d) for d in dirs]
        # i = [int(m.groups()[0]) for m in matches if m]  # indices
        # n = max(i) + 1 if i else 2  # increment number
        # path = Path(f"{path}{sep}{n}{suffix}")  # increment path

    if mkdir:
        path.mkdir(parents=True, exist_ok=True)  # make directory

    return path


def validate_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def get_cfg_from_full_path(path_cfg):
    with open(path_cfg, "r") as ymlfile:
        cfg = yaml.full_load(ymlfile)
    return cfg

def write_yaml(cfg,path_cfg):
    with open(path_cfg, 'w') as file:
        yaml.dump(cfg, file)

def get_color(index):
    hexs = ('00ff37', '69fffc', 'ffcb00', 'fcff00', '000000', 
                'ff34ff', '9a00ff', 'ff0009', 'ceffc4', 'ff8600',
                '901616', '00C2FF', '344593', '6473FF', '0018EC', '8438FF', '520085', 'CB38FF', 'FF95C8', 'FF37C7')
    h = hexs[int(index)]
    color = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    return color

def get_approx_conv_factor(cfg):
    conv_success = False
    predefined_names = ['A5', 'A4', 'A3', 'legal']
    custom_names = ['custom']
    if cfg['fieldprism']['scale']['use_predefined']:
        user_scale = cfg['fieldprism']['scale']['scale_size']
        if user_scale in predefined_names:
            if user_scale == 'A5':
                conv = 76  ### TODO check all ratios, good as of 11/11/2022
            elif user_scale == 'A4':
                conv = 137  ### TODO check all ratios, good as of 11/11/2022
            elif user_scale == 'A3':
                conv = 224  ### TODO check all ratios, good as of 11/11/2022
            elif user_scale == 'legal':
                conv = 140  ### TODO check all ratios, good as of 11/11/2022
            conv_success = True
            print(f"{bcolors.OKGREEN}Predefined Scale: {user_scale}{bcolors.ENDC}")
            print(f"{bcolors.OKGREEN}Scale Ratio: {conv} mm. between TL and TR markers{bcolors.ENDC}")
    elif not cfg['fieldprism']['scale']['use_predefined']:
        user_scale = cfg['fieldprism']['scale']['scale_size']
        if user_scale in custom_names:
            conv = int(cfg['fieldprism']['scale']['custom_short_distance'])
            if (0 < conv):
                conv_success = True
                print(f"{bcolors.OKCYAN}Custom Scale: {user_scale}{bcolors.ENDC}")
                print(f"{bcolors.OKCYAN}Scale Ratio: {conv}{bcolors.ENDC}")
            else:
                conv = 0
                print(f"{bcolors.FAIL}In FieldPrism.yaml - cfg['fieldprism']['scale']['custom_short_distance'] is not valid!{bcolors.ENDC}")
        else:
            print(f"{bcolors.FAIL}In FieldPrism.yaml - cfg['fieldprism']['scale']['scale_size'] must be 'custom' for a custom ratio{bcolors.ENDC}")
    else:
        print(f"{bcolors.FAIL}In FieldPrism.yaml - cfg['fieldprism']['scale']['use_predefined'] require boolean True or False{bcolors.ENDC}")
    return conv_success, int(conv)

def get_scale_ratio(cfg):
    scale_success = False
    predefined_names = ['A5', 'A4', 'A3', 'legal']
    custom_names = ['custom']
    if cfg['fieldprism']['scale']['use_predefined']:
        user_scale = cfg['fieldprism']['scale']['scale_size']
        if user_scale in predefined_names:
            if user_scale == 'A5':
                scale = np.divide(7.6,12.9)  ### TODO check all ratios, good as of 11/11/2022
            elif user_scale == 'A4':
                scale = np.divide(13.7,21.55)  ### TODO check all ratios, good as of 11/11/2022
            elif user_scale == 'A3':
                scale = np.divide(22.4,33.8)  ### TODO check all ratios, good as of 11/11/2022
            elif user_scale == 'legal':
                scale = np.divide(14.0,28.0)  ### TODO check all ratios, good as of 11/11/2022
            scale_success = True
            print(f"{bcolors.OKGREEN}Predefined Scale: {user_scale}{bcolors.ENDC}")
            print(f"{bcolors.OKGREEN}Scale Ratio: {scale}{bcolors.ENDC}")
    elif not cfg['fieldprism']['scale']['use_predefined']:
        user_scale = cfg['fieldprism']['scale']['scale_size']
        if user_scale in custom_names:
            scale = float(cfg['fieldprism']['scale']['custom_ratio'])
            if ((0 < scale) and (scale < 1)):
                scale_success = True
                print(f"{bcolors.OKCYAN}Custom Scale: {user_scale}{bcolors.ENDC}")
                print(f"{bcolors.OKCYAN}Scale Ratio: {scale}{bcolors.ENDC}")
            else:
                scale = 0
                print(f"{bcolors.FAIL}In FieldPrism.yaml - cfg['fieldprism']['scale']['custom_ratio'] is not a valid float between 0 and 1!{bcolors.ENDC}")
        else:
            print(f"{bcolors.FAIL}In FieldPrism.yaml - cfg['fieldprism']['scale']['scale_size'] must be 'custom' for a custom ratio{bcolors.ENDC}")
    else:
        print(f"{bcolors.FAIL}In FieldPrism.yaml - cfg['fieldprism']['scale']['use_predefined'] require boolean True or False{bcolors.ENDC}")
    return scale_success, scale

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

def generate_overlay_QR_add(image_bboxes, bbox, labels_list, colors_list):
    current_os = platform.system()
    # print("OS in my system : ",current_os)
    if current_os == 'Linux':
        font_pick = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
    elif current_os == 'Windows':
        font_pick = 'arial.ttf'
    elif current_os == 'Darwin':
        font_pick = '/Library/Fonts/Verdana/Verdana Regular.ttf' #TODO Check this path
    else:
        font_pick = ''
    # draw bounding boxes with fill color
    if font_pick == '':
        image_bboxes = draw_bounding_boxes_custom(image_bboxes, bbox, width=10, labels=[labels_list], 
                                            colors=[colors_list], fill=False, font_size=16, text_color = (255,0,255))
    else:
        image_bboxes = draw_bounding_boxes_custom(image_bboxes, bbox, width=10, labels=[labels_list], 
                                            colors=[colors_list], fill=False, font = font_pick, font_size=16, text_color = (255,0,255))   
    return image_bboxes

def generate_overlay_add(image_bboxes, bbox, labels_list, colors_list, centers_corrected, Marker_Unknown, distance):
    current_os = platform.system()
    # print("OS in my system : ",current_os)
    if current_os == 'Linux':
        font_pick = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
    elif current_os == 'Windows':
        font_pick = 'arial.ttf'
    elif current_os == 'Darwin':
        font_pick = '/Library/Fonts/Verdana/Verdana Regular.ttf' #TODO Check this path
    else:
        font_pick = ''
    # draw bounding boxes with fill color
    image_bboxes = draw_bounding_boxes_custom(image_bboxes, bbox, width=10, labels=[labels_list], colors=[colors_list], fill=True, font = font_pick, font_size=20, text_color = (255,0,255))  
    image_bboxes = draw_keypoints(image_bboxes, torch.tensor([[Marker_Unknown.translate_center_point]]), colors="white", radius=5)

    # Add one cm. box
    average_one_cm_distance = distance
    if average_one_cm_distance is not np.nan:
        label_1CM = [''.join(['1 CM = ',str(np.round(average_one_cm_distance,1)),' Pixels'])]
        label_10CM = [''.join(['10 CM = ',str(np.round(np.multiply(average_one_cm_distance, 10), 1)),' Pixels'])]
        image_bboxes = draw_bounding_boxes_custom(image_bboxes,torch.tensor([[
                                            centers_corrected[0]-(np.divide(average_one_cm_distance,2)),
                                            centers_corrected[1]-(np.divide(average_one_cm_distance,2)),
                                            centers_corrected[0]+(np.divide(average_one_cm_distance,2)),
                                            centers_corrected[1]+(np.divide(average_one_cm_distance,2))]]),
                                            width=1,labels=label_1CM,colors=(255, 0, 0),fill =True,font = font_pick, font_size=20, text_color = (255, 0, 0))  

        image_bboxes = draw_bounding_boxes_custom(image_bboxes,torch.tensor([[
                                            centers_corrected[0]-np.multiply((np.divide(average_one_cm_distance,2)),3),
                                            centers_corrected[1]+np.multiply((np.divide(average_one_cm_distance,2)),4),
                                            centers_corrected[0]+np.multiply((np.divide(average_one_cm_distance,2)),17),
                                            centers_corrected[1]+np.multiply((np.divide(average_one_cm_distance,2)),4.1)]]),
                                            width=1,labels=label_10CM,colors=(20, 120, 10),fill =True,font = font_pick, font_size=20, text_color = (20, 120, 10))  
    return image_bboxes

def generate_overlay(path_overlay, image_name_jpg, average_one_cm_distance, image_bboxes, bbox, labels_list, colors_list, centers_corrected, Marker_Top_Left, Marker_Top_Right, Marker_Bottom_Right, Marker_Bottom_Left):
    current_os = platform.system()
    # print("OS in my system : ",current_os)
    if current_os == 'Linux':
        font_pick = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
    elif current_os == 'Windows':
        font_pick = 'arial.ttf'
    elif current_os == 'Darwin':
        font_pick = '/Library/Fonts/Verdana/Verdana Regular.ttf' #TODO Check this path
    else:
        font_pick = ''
    # Unpack new center points
    Marker_Top_Left.translate_center_point, Marker_Top_Right.translate_center_point, Marker_Bottom_Right.translate_center_point, Marker_Bottom_Left.translate_center_point = centers_corrected[0], centers_corrected[1], centers_corrected[2], centers_corrected[3]

    # draw bounding boxes with fill color
    image_bboxes = draw_bounding_boxes_custom(image_bboxes, bbox, width=10, labels=labels_list, colors=colors_list, fill=True, font = font_pick, font_size=20, text_color = (20, 120, 10)) 

    # Add one cm. box
    if average_one_cm_distance is not np.nan:
        label_1CM = [''.join(['1 CM = ',str(np.round(average_one_cm_distance,1)),' Pixels'])]
        label_10CM = [''.join(['10 CM = ',str(np.round(np.multiply(average_one_cm_distance, 10), 1)),' Pixels'])]
        image_bboxes = draw_bounding_boxes_custom(image_bboxes,torch.tensor([[
                                            Marker_Top_Left.translate_center_point[0]-(np.divide(average_one_cm_distance,2)),
                                            Marker_Top_Left.translate_center_point[1]-(np.divide(average_one_cm_distance,2)),
                                            Marker_Top_Left.translate_center_point[0]+(np.divide(average_one_cm_distance,2)),
                                            Marker_Top_Left.translate_center_point[1]+(np.divide(average_one_cm_distance,2))]]),
                                            width=1,labels=label_1CM,colors=(255, 0, 0),fill =True,font = font_pick, font_size=20, text_color = (255, 0, 0)) 

        image_bboxes = draw_bounding_boxes_custom(image_bboxes,torch.tensor([[
                                            Marker_Top_Right.translate_center_point[0]-np.multiply((np.divide(average_one_cm_distance,2)),3),
                                            Marker_Top_Right.translate_center_point[1]+np.multiply((np.divide(average_one_cm_distance,2)),4),
                                            Marker_Top_Right.translate_center_point[0]+np.multiply((np.divide(average_one_cm_distance,2)),17),
                                            Marker_Top_Right.translate_center_point[1]+np.multiply((np.divide(average_one_cm_distance,2)),4.1)]]),
                                            width=1,labels=label_10CM,colors=(20, 120, 10),fill =True,font = font_pick, font_size=20, text_color = (20, 120, 10)) 
        image_bboxes = draw_bounding_boxes_custom(image_bboxes,torch.tensor([[
                                            Marker_Top_Left.translate_center_point[0]-np.multiply((np.divide(average_one_cm_distance,2)),3),
                                            Marker_Top_Left.translate_center_point[1]+np.multiply((np.divide(average_one_cm_distance,2)),4),
                                            Marker_Top_Left.translate_center_point[0]+np.multiply((np.divide(average_one_cm_distance,2)),17),
                                            Marker_Top_Left.translate_center_point[1]+np.multiply((np.divide(average_one_cm_distance,2)),4.1)]]),
                                            width=1,labels=label_10CM,colors=(20, 120, 10),fill =True,font = font_pick, font_size=20, text_color = (20, 120, 10)) 
        image_bboxes = draw_bounding_boxes_custom(image_bboxes,torch.tensor([[
                                            Marker_Bottom_Right.translate_center_point[0]-np.multiply((np.divide(average_one_cm_distance,2)),3),
                                            Marker_Bottom_Right.translate_center_point[1]+np.multiply((np.divide(average_one_cm_distance,2)),4),
                                            Marker_Bottom_Right.translate_center_point[0]+np.multiply((np.divide(average_one_cm_distance,2)),17),
                                            Marker_Bottom_Right.translate_center_point[1]+np.multiply((np.divide(average_one_cm_distance,2)),4.1)]]),
                                            width=1,labels=label_10CM,colors=(20, 120, 10),fill =True,font = font_pick, font_size=20, text_color = (20, 120, 10)) 
        image_bboxes = draw_bounding_boxes_custom(image_bboxes,torch.tensor([[
                                            Marker_Bottom_Left.translate_center_point[0]-np.multiply((np.divide(average_one_cm_distance,2)),3),
                                            Marker_Bottom_Left.translate_center_point[1]+np.multiply((np.divide(average_one_cm_distance,2)),4),
                                            Marker_Bottom_Left.translate_center_point[0]+np.multiply((np.divide(average_one_cm_distance,2)),17),
                                            Marker_Bottom_Left.translate_center_point[1]+np.multiply((np.divide(average_one_cm_distance,2)),4.1)]]),
                                            width=1,labels=label_10CM,colors=(20, 120, 10),fill =True,font = font_pick, font_size=20, text_color = (20, 120, 10)) 
    # image_bboxes = draw_keypoints(image_bboxes, torch.tensor([[bottom_right_center]]), colors="blue", radius=20)
    # image_bboxes = draw_keypoints(image_bboxes, torch.tensor([[top_left_center]]), colors="red", radius=20)
    # image_bboxes = draw_keypoints(image_bboxes, torch.tensor([[top_right_center]]), colors="green", radius=20)
    # image_bboxes = draw_keypoints(image_bboxes, torch.tensor([[bottom_left_center]]), colors="yellow", radius=20)
    image_bboxes = draw_keypoints(image_bboxes, torch.tensor([[Marker_Top_Left.translate_center_point]]), colors="blue", radius=5)
    image_bboxes = draw_keypoints(image_bboxes, torch.tensor([[Marker_Top_Right.translate_center_point]]), colors="red", radius=5)
    image_bboxes = draw_keypoints(image_bboxes, torch.tensor([[Marker_Bottom_Left.translate_center_point]]), colors="cyan", radius=5)
    image_bboxes = draw_keypoints(image_bboxes, torch.tensor([[Marker_Bottom_Right.translate_center_point]]), colors="yellow", radius=5)

    # image_bboxes = ToPILImage()(image_bboxes)
    # image_bboxes.show()
    # image_bboxes.save(os.path.join(path_overlay, image_name_jpg))
    return image_bboxes



# Calculate skew angle of an image
def find_skew_angle(cvImage) -> float:
    # Prep image, copy, convert to gray scale, blur, and threshold
    newImage = cvImage.copy()
    gray = cv2.cvtColor(newImage, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9, 9), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Apply dilate to merge text into meaningful lines/paragraphs.
    # Use larger kernel on X axis to merge characters into single line, cancelling out any spaces.
    # But use smaller kernel on Y axis to separate between different blocks of text
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    dilate = cv2.dilate(thresh, kernel, iterations=2)

    # cv2.imshow('QR_Code', thresh)
    # cv2.waitKey(0)

    # Find all contours
    contours, hierarchy = cv2.findContours(dilate, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key = cv2.contourArea, reverse = True)

    # Find largest contour and surround in min area box
    largestContour = contours[0]
    minAreaRect = cv2.minAreaRect(largestContour)

    # Determine the angle. Convert it to the value that was originally used to obtain skewed image
    angle = minAreaRect[-1]
    if angle < -45:
        angle = 90 + angle
    return -1.0 * angle

# Rotate the image around its center
def rotate_image(cvImage, angle: float):
    newImage = cvImage.copy()
    (h, w) = newImage.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    newImage = cv2.warpAffine(newImage, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return newImage

# Deskew image
def deskew(cvImage):
    angle = find_skew_angle(cvImage)
    return rotate_image(cvImage, -1.0 * angle)


@torch.no_grad()
def draw_bounding_boxes_custom(
    image: torch.Tensor,
    boxes: torch.Tensor,
    labels: Optional[List[str]] = None,
    colors: Optional[Union[List[Union[str, Tuple[int, int, int]]], str, Tuple[int, int, int]]] = None,
    fill: Optional[bool] = False,
    width: int = 1,
    font: Optional[str] = None,
    font_size: int = 40,
    text_color: Optional[Union[List[Union[str, Tuple[int, int, int]]], str, Tuple[int, int, int]]] = None,
) -> torch.Tensor:

    """
    Draws bounding boxes on given image.
    The values of the input image should be uint8 between 0 and 255.
    If fill is True, Resulting Tensor should be saved as PNG image.

    Args:
        image (Tensor): Tensor of shape (C x H x W) and dtype uint8.
        boxes (Tensor): Tensor of size (N, 4) containing bounding boxes in (xmin, ymin, xmax, ymax) format. Note that
            the boxes are absolute coordinates with respect to the image. In other words: `0 <= xmin < xmax < W` and
            `0 <= ymin < ymax < H`.
        labels (List[str]): List containing the labels of bounding boxes.
        colors (color or list of colors, optional): List containing the colors
            of the boxes or single color for all boxes. The color can be represented as
            PIL strings e.g. "red" or "#FF00FF", or as RGB tuples e.g. ``(240, 10, 157)``.
            By default, random colors are generated for boxes.
        fill (bool): If `True` fills the bounding box with specified color.
        width (int): Width of bounding box.
        font (str): A filename containing a TrueType font. If the file is not found in this filename, the loader may
            also search in other directories, such as the `fonts/` directory on Windows or `/Library/Fonts/`,
            `/System/Library/Fonts/` and `~/Library/Fonts/` on macOS.
        font_size (int): The requested font size in points.

    Returns:
        img (Tensor[C, H, W]): Image Tensor of dtype uint8 with bounding boxes plotted.
    """

    # if not torch.jit.is_scripting() and not torch.jit.is_tracing():
    #     _log_api_usage_once(draw_bounding_boxes)
    if not isinstance(image, torch.Tensor):
        raise TypeError(f"Tensor expected, got {type(image)}")
    elif image.dtype != torch.uint8:
        raise ValueError(f"Tensor uint8 expected, got {image.dtype}")
    elif image.dim() != 3:
        raise ValueError("Pass individual images, not batches")
    elif image.size(0) not in {1, 3}:
        raise ValueError("Only grayscale and RGB images are supported")

    num_boxes = boxes.shape[0]

    if labels is None:
        labels: Union[List[str], List[None]] = [None] * num_boxes  # type: ignore[no-redef]
    elif len(labels) != num_boxes:
        raise ValueError(
            f"Number of boxes ({num_boxes}) and labels ({len(labels)}) mismatch. Please specify labels for each box."
        )

    # if colors is None:
    #     colors = _generate_color_palette(num_boxes)
    elif isinstance(colors, list):
        if len(colors) < num_boxes:
            raise ValueError(f"Number of colors ({len(colors)}) is less than number of boxes ({num_boxes}). ")
    else:  # colors specifies a single color for all boxes
        colors = [colors] * num_boxes

    colors = [(ImageColor.getrgb(color) if isinstance(color, str) else color) for color in colors]

    # Handle Grayscale images
    if image.size(0) == 1:
        image = torch.tile(image, (3, 1, 1))

    ndarr = image.permute(1, 2, 0).cpu().numpy()
    img_to_draw = Image.fromarray(ndarr)
    img_boxes = boxes.to(torch.int64).tolist()

    if fill:
        draw = ImageDraw.Draw(img_to_draw, "RGBA")
    else:
        draw = ImageDraw.Draw(img_to_draw)

    txt_font = ImageFont.load_default() if font is None else ImageFont.truetype(font=font, size=font_size)

    for bbox, color, label in zip(img_boxes, colors, labels):  # type: ignore[arg-type]
        if fill:
            fill_color = color + (100,)
            draw.rectangle(bbox, width=width, outline=color, fill=fill_color)
        else:
            draw.rectangle(bbox, width=width, outline=color)

        if label is not None:
            if width == 1:
                margin = 24
            else:
                margin = np.multiply(2,(width + 2))
            draw.text((bbox[0], bbox[1] - margin), label, fill=text_color, font=txt_font)

    return torch.from_numpy(np.array(img_to_draw)).permute(2, 0, 1).to(dtype=torch.uint8)

# if __name__ == '__main__':
#     dir_images_unprocessed= 'D:\Dropbox\LM2_Env\Image_Datasets\FieldPrism_Training_Images\FieldPrism_Training_Outside'
#     make_images_in_dir_vertical(dir_images_unprocessed)
#     dir_images_unprocessed= 'D:\Dropbox\LM2_Env\Image_Datasets\FieldPrism_Training_Images\FieldPrism_Training_Sheets'
#     make_images_in_dir_vertical(dir_images_unprocessed)
#     dir_images_unprocessed= 'D:\Dropbox\LM2_Env\Image_Datasets\FieldPrism_Training_Images\FieldPrism_Training_Sheets_QR'
#     make_images_in_dir_vertical(dir_images_unprocessed)
#     dir_images_unprocessed= 'D:\Dropbox\LM2_Env\Image_Datasets\FieldPrism_Training_Images\FieldPrism_Training_FS-Poor' 
#     make_images_in_dir_vertical(dir_images_unprocessed)