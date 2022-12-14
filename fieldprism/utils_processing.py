# Run yolov5 on dir
import os, yaml, cv2, re, pybboxes
import numpy as np
from dataclasses import dataclass, field
from pathlib import Path
from tqdm import tqdm
import pandas as pd
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



def remove_overlapping_predictions(cfg, n_barcode_before, n_ruler_before, all_rulers, all_barcodes, img_w, img_h):
    if cfg['fieldprism']['do_remove_overlap']:    
        print(f"{bcolors.OKCYAN}      Removing intersecting predictions. Prioritizing class: {cfg['fieldprism']['overlap_priority']}{bcolors.ENDC}")
        print(f"{bcolors.BOLD}            Before - number of barcodes: {n_barcode_before}{bcolors.ENDC}")
        print(f"{bcolors.BOLD}            Before - number of rulers: {n_ruler_before}{bcolors.ENDC}")
        if cfg['fieldprism']['overlap_priority'] == 'ruler':
            all_rulers, all_barcodes = check_overlap(all_rulers, all_barcodes, img_w, img_h)
        else:
            all_barcodes, all_rulers = check_overlap(all_barcodes, all_rulers, img_w, img_h)
        n_barcode_afer = all_barcodes.shape[0]
        n_ruler_after = all_rulers.shape[0]
        print(f"{bcolors.BOLD}            After - number of barcodes: {n_barcode_afer}{bcolors.ENDC}")
        print(f"{bcolors.BOLD}            After - number of rulers: {n_ruler_after}{bcolors.ENDC}")
    else:
        n_barcode_afer = all_barcodes.shape[0]
        n_ruler_after = all_rulers.shape[0]
    return all_barcodes, all_rulers, n_barcode_afer, n_ruler_after

def check_overlap(priority_item, remove_item, img_w, img_h):
    keep_remove = []
    for i_r, remove in remove_item.iterrows(): 
        do_keep_ru = True
        bbox_remove = (remove[1], remove[2], remove[3], remove[4])
        bbox_remove = pybboxes.convert_bbox(bbox_remove, from_type="yolo", to_type="voc", image_size=(img_w, img_h))
        intersect_count = 0
        for i_bc, priority in priority_item.iterrows(): 
            bbox_priority = (priority[1], priority[2], priority[3], priority[4])
            bbox_priority = pybboxes.convert_bbox(bbox_priority, from_type="yolo", to_type="voc", image_size=(img_w, img_h))
            # Intersection

            do_keep_ru = check_overlap_conditions(bbox_priority, bbox_remove)
            if not do_keep_ru:
                intersect_count += 1


            # if (bbox_remove[0] >= bbox_priority[2]) or (bbox_remove[2]<=bbox_priority[0]) or (bbox_remove[3]<=bbox_priority[1]) or (bbox_remove[1]>=bbox_priority[3]):
            #     continue
            # # Completely inside of the remove bbox
            # elif ((bbox_remove[0] <= bbox_priority[0]) and (bbox_remove[1] <= bbox_priority[1]) and (bbox_remove[2] >= bbox_priority[2])  and (bbox_remove[3] >= bbox_priority[3])):
            #     continue
            # # Completely surrounding the remove bbox
            # elif ((bbox_remove[0] >= bbox_priority[0]) and (bbox_remove[1] >= bbox_priority[1]) and (bbox_remove[2] <= bbox_priority[2])  and (bbox_remove[3] <= bbox_priority[3])):
            #     continue
            # else:
            #     do_keep_ru = False

        if intersect_count == 0:
            keep_remove.append(remove.values)
    remove_item = pd.DataFrame(keep_remove)
    return priority_item, remove_item

def get_iou(a, b, epsilon=1e-7):
    # COORDINATES OF THE INTERSECTION BOX
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])

    # AREA OF OVERLAP - Area where the boxes intersect
    width = (x2 - x1)
    height = (y2 - y1)
    # handle case where there is NO overlap
    if (width<0) or (height <0):
        return True, 0.0
    area_overlap = width * height

    # COMBINED AREA
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    area_combined = area_a + area_b - area_overlap

    # RATIO OF AREA OF OVERLAP OVER COMBINED AREA
    iou = area_overlap / (area_combined+epsilon)
    # if iou > 1e-6:
    do_keep = False
    # else:
        # do_keep = True
    return do_keep, iou

def check_overlap_conditions(priority, ignore):
    px1, py1, px2, py2 = priority 
    ix1, iy1, ix2, iy2 = ignore 
    # check if ignore is completely inside of priority 
    if ((px1 <= ix1) and (py1 <= iy1)) and ((px2 >= ix2) and (py2 >= iy2)):
        print('            -> ignore is inside priority')
        return False 
    # check if ignore completely surrounds priority 
    elif ((px1 >= ix1) and (py1 >= iy1)) and ((px2 <= ix2) and (py2 <= iy2)):
        print('            -> ignore surrounds priority')
        return False 
    
    else: 
        do_keep_ru, iou = get_iou(priority, ignore, epsilon=1e-7)
        if do_keep_ru:
            return True
        else:
            print('            -> ignore intersects priority')
            return False


    # if (px1 >= ix1 and px2 <= ix2) and (py1 >= iy1 and py2 <= iy2): 
    #     return True 
    # # check if ignore completely surrounds priority 
    # elif (px1 < ix1 and px2 > ix2) and (py1 < iy1 and py2 > iy2): 
    #     return True 
    # # check if ignore intersects with priority on x-axis 
    # elif (px1 < ix1 and px2 > ix1) or (px1 < ix2 and px2 > ix2): 
    #     return True 
    # # check if ignore intersects with priority on y-axis 
    # elif (py1 < iy1 and py2 > iy1) or (py1 < iy2 and py2 > iy2): 
    #     return True 
    # else: 
    #     return False

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
        if image_name_jpg.endswith((".jpg",".JPG",".jpeg",".JPEG")):
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


if __name__ == '__main__':
    # test case 1: ignore surrounds priority
    print('ignore surrounds')
    ignore = (1,1,10,10)
    priority = (2,2,6,6)
    _ = check_overlap_conditions(priority, ignore)

    # test case 2: ignore is inside priority
    print('ignore is inside')
    priority = (1,1,10,10)
    ignore = (2,2,6,6)
    _ = check_overlap_conditions(priority, ignore)

    # test case 3: ignore intersects with priority on the x axis
    print('ignore intersects with priority on the x axis')
    ignore = (5,3,10,10)
    priority = (2,2,6,6)
    _ = check_overlap_conditions(priority, ignore)

    # test case 4: ignore intersects with priority on the y axis
    print('ignore intersects with priority on the y axis')
    ignore = (1,5,10,10)
    priority = (2,2,6,6)
    _ = check_overlap_conditions(priority, ignore)

    # test case 5: no overlap
    print('no overlap')
    ignore = (12,12,14,14)
    priority = (2,2,6,6)
    _ = check_overlap_conditions(priority, ignore)

#     dir_images_unprocessed= 'D:\Dropbox\LM2_Env\Image_Datasets\FieldPrism_Training_Images\FieldPrism_Training_Outside'
#     make_images_in_dir_vertical(dir_images_unprocessed)
#     dir_images_unprocessed= 'D:\Dropbox\LM2_Env\Image_Datasets\FieldPrism_Training_Images\FieldPrism_Training_Sheets'
#     make_images_in_dir_vertical(dir_images_unprocessed)
#     dir_images_unprocessed= 'D:\Dropbox\LM2_Env\Image_Datasets\FieldPrism_Training_Images\FieldPrism_Training_Sheets_QR'
#     make_images_in_dir_vertical(dir_images_unprocessed)
#     dir_images_unprocessed= 'D:\Dropbox\LM2_Env\Image_Datasets\FieldPrism_Training_Images\FieldPrism_Training_FS-Poor' 
#     make_images_in_dir_vertical(dir_images_unprocessed)