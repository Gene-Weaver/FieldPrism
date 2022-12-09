import os, cv2, math
from dataclasses import dataclass, field
import numpy as np
import pandas as pd
from utils_processing import bcolors


@dataclass
class Data_Vault:
    # Initialize with these
    cfg: list[str] = field(default_factory=list)
    Dirs: list[str] = field(default_factory=list)
    option: str = ''
    ratio: str = ''
    image_name_jpg: str = ''
    dir_images_to_process: str = ''
    index: str = ''
    n_total: str = ''

    # add_image_name()
    image_name: str = ''
    image_name_txt: str = ''

    # add_image_label_size()
    has_ML_prediction: bool = False
    chosen_path: str = ''
    image: list[str] = field(default_factory=list)
    img_h_og: int = ''
    img_w_og: int = ''
    image_label_file: list[str] = field(default_factory=list)
    path_image_label_file: str = ''

    # add_bboxes()
    do_remove_overlap: bool = False
    n_barcode_before: int = ''
    n_ruler_before: int = ''
    n_barcode_afer: int = ''
    n_ruler_after: int = ''
    all_text: list[str] = field(default_factory=list)
    all_rulers: list[str] = field(default_factory=list)
    all_barcodes: list[str] = field(default_factory=list)

    # add_process_rulers()
    average_one_cm_distance: float = 0
    img_h_corrected: int = ''
    img_w_corrected: int = ''
    use_conversion: bool = False
    use_distortion_correction: bool = False
    image_out_corrected_path: str = ''
    image_out_corrected_location: str = ''
    overlay_out_corrected_path: str = ''
    overlay_out_corrected_location: str = ''
    n_markers: int = ''

    # add_process_barcodes()
    QR_List_Pass: list[str] = field(default_factory=list)
    QR_List_Fail: list[str] = field(default_factory=list)
    new_full_name: str = ''
    rename_success: bool = False


    def __init__(self, cfg, Dirs, option, ratio, image_name_jpg, dir_images_to_process, index, n_total) -> None:
        # Initialize with these
        self.cfg = cfg
        self.Dirs = Dirs
        self.option = option
        self.ratio = ratio
        self.image_name_jpg = image_name_jpg
        self.dir_images_to_process = dir_images_to_process
        self.index = index
        self.n_total = n_total

    def add_image_name(self, image_name, image_name_txt) -> None:
        self.image_name = image_name
        self.image_name_txt = image_name_txt

    def add_image_label_size(self, has_ML_prediction, chosen_path, image, img_h, img_w, image_label_file, path_image_label_file) -> None:
        self.has_ML_prediction = has_ML_prediction
        self.chosen_path = chosen_path
        self.image = image
        self.img_h_og = img_h
        self.img_w_og = img_w
        self.image_label_file = image_label_file
        self.path_image_label_file = path_image_label_file

    def add_bboxes(self, do_remove_overlap, n_barcode_before, n_ruler_before, n_barcode_afer, n_ruler_after, all_text, all_rulers, all_barcodes) -> None:
        self.do_remove_overlap = do_remove_overlap
        self.n_barcode_before = n_barcode_before
        self.n_ruler_before = n_ruler_before
        self.n_barcode_afer = n_barcode_afer
        self.n_ruler_after = n_ruler_after
        self.all_text = all_text
        self.all_rulers = all_rulers
        self.all_barcodes = all_barcodes
    
    def add_process_rulers(self, average_one_cm_distance, image, use_conversion, use_distortion_correction, Image_Out, Overlay_Out, Markers_All) -> None:
        self.average_one_cm_distance = average_one_cm_distance
        self.img_h_corrected, self.img_w_corrected, _ = image.shape
        self.use_conversion = use_conversion
        self.use_distortion_correction = use_distortion_correction

        self.image_out_corrected_path = Image_Out.path
        self.image_out_corrected_location = Image_Out.location
        if Overlay_Out is not None:
            self.overlay_out_corrected_path = Overlay_Out.path
            self.overlay_out_corrected_location = Overlay_Out.location
        else:
            self.overlay_out_corrected_path = ''
            self.overlay_out_corrected_location = 'no_overlay'

        if Markers_All is None:
            self.n_markers = 0
        else:
            self.n_markers = len(Markers_All)
        ### Can add more Marker info here
        Marker_Info = []
        for Marker in Markers_All:
            info = {'marker_location': Marker.location,
            'success_distortion_correction': Marker.success_dist,
            'success_pixel_to_metric': Marker.success_conv,
            'distortion_correction_was_approx': Marker.is_approx,
            'one_cm_pixels': Marker.one_cm_pixels,
            'center_point': Marker.translate_center_point,
            'center_point_approx': Marker.rough_center,
            'n_cm_boxes_found': Marker.count,
            'bbox_coordinates': Marker.bbox,
            }
            Marker_Info.append(info)
            # print(info)
            
    def add_process_barcodes(self, QR_List_Pass, QR_List_Fail) -> None:
        if self.cfg['fieldprism']['QR_codes']['do_rename_images']:
            n_QR_codes = self.cfg['fieldprism']['QR_codes']['n_QR_codes']
            sep_value = self.cfg['fieldprism']['QR_codes']['sep_value']

            QR_Naming = QR_Deconstructor(QR_List_Pass, n_QR_codes, sep_value)

            self.new_full_name = QR_Naming.new_full_name
            self.rename_success = QR_Naming.rename_success

            # for key in QR_List_Pass.values():
            #     # print(f'pass:\n{key.text_raw}')
            #     qr_label = ''.join(['L: ',key.rank, ' C: ',key.rank_value])
            # for key in QR_List_Fail.values():
            #     qr_label = 'FAIL'
            return True
    
    def get_new_full_name(self) -> None:
        return self.new_full_name

@dataclass
class QR_Deconstructor:
    L1: str = 'LEVEL1'
    L2: str = 'LEVEL2'
    L3: str = 'LEVEL3'
    L4: str = 'LEVEL4'
    L5: str = 'LEVEL5'
    L6: str = 'LEVEL6'

    new_full_name: str = ''
    rename_success: bool = False

    def __init__(self, QR_List_Pass, n_QR_codes, sep_value) -> None:

        # # Initialize new_full_name to defaul strings
        # if n_QR_codes == 1:
        #     self.new_full_name = sep_value.join([self.L1])
        # elif n_QR_codes == 2:
        #     self.new_full_name = sep_value.join([self.L1, self.L2])
        # elif n_QR_codes == 3:
        #     self.new_full_name = sep_value.join([self.L1, self.L2, self.L3])
        # elif n_QR_codes == 4:
        #     self.new_full_name = sep_value.join([self.L1, self.L2, self.L3, self.L4])
        # elif n_QR_codes == 5:
        #     self.new_full_name = sep_value.join([self.L1, self.L2, self.L3, self.L4, self.L5])
        # elif n_QR_codes == 6:
        #     self.new_full_name = sep_value.join([self.L1, self.L2, self.L3, self.L4, self.L5, self.L6])
        # else:
        #     print(f"{bcolors.FAIL}      Number of barcode in config file is not valid.{bcolors.ENDC}")
        #     print(f"{bcolors.FAIL}      Set cfg['fieldprism']['QR_codes']['n_QR_codes'] to an integer from 1 - 6{bcolors.ENDC}")
        #     self.new_full_name = sep_value.join([self.L1, self.L2, self.L3, self.L4, self.L5, self.L6])


        if len(QR_List_Pass) > 0:
            for key in QR_List_Pass.values():
                # print(f'pass:\n{key.text_raw}')
                rank =  key.rank
                QR_value = key.rank_value

                if rank == 'Level_1':
                    self.L1 = QR_value
                elif rank == 'Level_2':
                    self.L2 = QR_value
                elif rank == 'Level_3':
                    self.L3 = QR_value
                elif rank == 'Level_4':
                    self.L4 = QR_value
                elif rank == 'Level_5':
                    self.L5 = QR_value
                elif rank == 'Level_6':
                    self.L6 = QR_value

                self.rename_success = True
        else:
            self.rename_success = False


        if n_QR_codes == 1:
            self.new_full_name = sep_value.join([self.L1])
        elif n_QR_codes == 2:
            self.new_full_name = sep_value.join([self.L1, self.L2])
        elif n_QR_codes == 3:
            self.new_full_name = sep_value.join([self.L1, self.L2, self.L3])
        elif n_QR_codes == 4:
            self.new_full_name = sep_value.join([self.L1, self.L2, self.L3, self.L4])
        elif n_QR_codes == 5:
            self.new_full_name = sep_value.join([self.L1, self.L2, self.L3, self.L4, self.L5])
        elif n_QR_codes == 6:
            self.new_full_name = sep_value.join([self.L1, self.L2, self.L3, self.L4, self.L5, self.L6])
        else:
            print(f"{bcolors.FAIL}      Number of barcode in config file is not valid.{bcolors.ENDC}")
            print(f"{bcolors.FAIL}      Set cfg['fieldprism']['QR_codes']['n_QR_codes'] to an integer from 1 - 6{bcolors.ENDC}")
            self.new_full_name = sep_value.join([self.L1, self.L2, self.L3, self.L4, self.L5, self.L6])

        self.new_full_name = sep_value.join([self.L1, self.L2, self.L3, self.L4, self.L5, self.L6])