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

    # add_DataFS()
    FS_image_row: list[str] = field(default_factory=list)

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
    n_barcode_after: int = ''
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
    Marker_Info: list[str] = field(default_factory=list)

    # add_process_barcodes()
    QR_List_Pass: list[str] = field(default_factory=list)
    QR_List_Fail: list[str] = field(default_factory=list)
    new_full_name: str = ''
    rename_success: bool = False
    QR_raw_text: list[str] = field(default_factory=list)

    # rename 
    rename: str = ''
    rename_backup: str = ''
    rename_backup_dirs: list[str] = field(default_factory=list)



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
        self.rename_backup_dirs = []

    def add_DataFS(self, image_row) -> None:
        self.FS_image_row = image_row

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

    def add_bboxes(self, do_remove_overlap, n_barcode_before, n_ruler_before, n_barcode_after, n_ruler_after, all_text, all_rulers, all_barcodes) -> None:
        self.do_remove_overlap = do_remove_overlap
        self.n_barcode_before = n_barcode_before
        self.n_ruler_before = n_ruler_before
        self.n_barcode_after = n_barcode_after
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
        self.Marker_Info = []
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
            self.Marker_Info.append(info)
            # print(info)
            
    def add_process_barcodes(self, QR_List_Pass, QR_List_Fail) -> None:
        if self.cfg['fieldprism']['QR_codes']['do_rename_images']:
            n_QR_codes = self.cfg['fieldprism']['QR_codes']['n_QR_codes']
            sep_value = self.cfg['fieldprism']['QR_codes']['sep_value']

            QR_Naming = QR_Deconstructor(QR_List_Pass, n_QR_codes, sep_value)

            self.new_full_name = QR_Naming.new_full_name
            self.rename_success = QR_Naming.rename_success
            self.QR_raw_text = QR_Naming.QR_raw_text

            # for key in QR_List_Pass.values():
            #     # print(f'pass:\n{key.text_raw}')
            #     qr_label = ''.join(['L: ',key.rank, ' C: ',key.rank_value])
            # for key in QR_List_Fail.values():
            #     qr_label = 'FAIL'
            return True
    
    def get_new_full_name(self) -> None:
        return self.new_full_name

def build_empty_csv(has_FS, path_data,cfg):
    if has_FS:
        CSV_out = pd.DataFrame(columns=[
        "img_name_new",
        "img_name_original",
        "option",
        "average_one_cm_distance",

        "GPS_lat",
        "GPS_long",
        "GPS_altitude",
        "GPS_climb",
        "GPS_speed",
        "GPS_lat_error_est",
        "GPS_lon_error_est",
        "GPS_alt_error_est",
        "GPS_session_time",
        "GPS_time_of_collection",

        "index_img",
        "n_total_img",
        "project",
        "run",
        "image_out_location",
        "QR_raw_text",
        "has_ML_prediction",
        "rename_success",
        "do_remove_overlap",
        "use_pixel_conversion",
        "use_distortion_correction",
        "img_h_og",
        "img_w_og",
        "img_h_corrected",
        "img_w_corrected",
        "n_QR_pre",
        "n_QR_post",
        "n_ruler_pre",
        "n_ruler_post",
        "n_markers",
        "Marker_Info",
        "marker_ratio",
        "dir_images_to_process",
        "image_label_file",
        ])
    else:
        CSV_out = pd.DataFrame(columns=[
        "img_name_new",
        "img_name_original",
        "option",
        "average_one_cm_distance",

        "index_img",
        "n_total_img",
        "project",
        "run",
        "image_out_location",
        "QR_raw_text",
        "has_ML_prediction",
        "rename_success",
        "do_remove_overlap",
        "use_pixel_conversion",
        "use_distortion_correction",
        "img_h_og",
        "img_w_og",
        "img_h_corrected",
        "img_w_corrected",
        "n_QR_pre",
        "n_QR_post",
        "n_ruler_pre",
        "n_ruler_post",
        "n_markers",
        "Marker_Info",
        "marker_ratio",
        "dir_images_to_process",
        "image_label_file",
        ])

    path_CSV_out = os.path.join(path_data, ''.join([cfg['fieldprism']['dirname_current_project'], '_', cfg['fieldprism']['dirname_current_run'], '.csv']))
    CSV_out.to_csv(path_CSV_out, mode='a', header=True, index=False)
    return path_CSV_out

def write_datarow_to_file(has_FS, path_CSV_out, DataVault, image_out_location, cfg):
    if not DataVault.rename_success:
        new_full_name = 'no_QR_info'
    else:
        new_full_name = DataVault.rename

    if image_out_location == '':
        image_out_location = 'path_markers_missing'
    else:
        image_out_location = image_out_location.location

    try:
        QR_raw_text = DataVault.QR_raw_text
    except:
        QR_raw_text = []
        
    try:
        Marker_Info = DataVault.Marker_Info
    except:
        Marker_Info = []
    
    if has_FS:
        CSV_out = pd.DataFrame({
            "img_name_new" : [new_full_name],
            "img_name_original" : [DataVault.image_name],
            "option" : [DataVault.option],
            "average_one_cm_distance" : [DataVault.average_one_cm_distance],

            "GPS_lat" : [DataVault.FS_image_row['latitude'].values[0]],
            "GPS_long" : [DataVault.FS_image_row['longitude'].values[0]],
            "GPS_altitude" : [DataVault.FS_image_row['altitude'].values[0]],
            "GPS_climb" : [DataVault.FS_image_row['climb'].values[0]],
            "GPS_speed" : [DataVault.FS_image_row['speed'].values[0]],
            "GPS_lat_error_est" : [DataVault.FS_image_row['lat_error_est'].values[0]],
            "GPS_lon_error_est" : [DataVault.FS_image_row['lon_error_est'].values[0]],
            "GPS_alt_error_est" : [DataVault.FS_image_row['alt_error_est'].values[0]],
            "GPS_session_time" : [DataVault.FS_image_row['session_time'].values[0]],
            "GPS_time_of_collection" : [DataVault.FS_image_row['time_of_collection'].values[0]],

            "index_img" : [DataVault.index],
            "n_total_img" : [DataVault.n_total],
            "project" : [cfg['fieldprism']['dirname_current_project']],
            "run" : [cfg['fieldprism']['dirname_current_run']],
            "image_out_location" : [image_out_location],
            "QR_raw_text" : [QR_raw_text],
            "has_ML_prediction" : [DataVault.has_ML_prediction],
            "rename_success" : [DataVault.rename_success],
            "do_remove_overlap" : [DataVault.do_remove_overlap],
            "use_pixel_conversion" : [DataVault.use_conversion],
            "use_distortion_correction" : [DataVault.use_distortion_correction],
            "img_h_og" : [DataVault.img_h_og],
            "img_w_og" : [DataVault.img_w_og],
            "img_h_corrected" : [DataVault.img_h_corrected],
            "img_w_corrected" : [DataVault.img_w_corrected],
            "n_QR_pre" : [DataVault.n_barcode_before],
            "n_QR_post" : [DataVault.n_barcode_after],
            "n_ruler_pre" : [DataVault.n_ruler_before],
            "n_ruler_post" : [DataVault.n_ruler_after],
            "n_markers" : [DataVault.n_markers],
            "Marker_Info" : [Marker_Info],
            "marker_ratio" : [DataVault.ratio],
            "dir_images_to_process" : [cfg['fieldprism']['dir_images_unprocessed']],
            "image_label_file" : [cfg['fieldprism']['dir_images_unprocessed_labels']],
            })
    else:
        CSV_out = pd.DataFrame({
            "img_name_new" : [new_full_name],
            "img_name_original" : [DataVault.image_name],
            "option" : [DataVault.option],
            "average_one_cm_distance" : [DataVault.average_one_cm_distance],

            "index_img" : [DataVault.index],
            "n_total_img" : [DataVault.n_total],
            "project" : [cfg['fieldprism']['dirname_current_project']],
            "run" : [cfg['fieldprism']['dirname_current_run']],
            "image_out_location" : [image_out_location],
            "QR_raw_text" : [QR_raw_text],
            "has_ML_prediction" : [DataVault.has_ML_prediction],
            "rename_success" : [DataVault.rename_success],
            "do_remove_overlap" : [DataVault.do_remove_overlap],
            "use_pixel_conversion" : [DataVault.use_conversion],
            "use_distortion_correction" : [DataVault.use_distortion_correction],
            "img_h_og" : [DataVault.img_h_og],
            "img_w_og" : [DataVault.img_w_og],
            "img_h_corrected" : [DataVault.img_h_corrected],
            "img_w_corrected" : [DataVault.img_w_corrected],
            "n_QR_pre" : [DataVault.n_barcode_before],
            "n_QR_post" : [DataVault.n_barcode_after],
            "n_ruler_pre" : [DataVault.n_ruler_before],
            "n_ruler_post" : [DataVault.n_ruler_after],
            "n_markers" : [DataVault.n_markers],
            "Marker_Info" : [Marker_Info],
            "marker_ratio" : [DataVault.ratio],
            "dir_images_to_process" : [cfg['fieldprism']['dir_images_unprocessed']],
            "image_label_file" : [cfg['fieldprism']['dir_images_unprocessed_labels']],
            })
    CSV_out.to_csv(path_CSV_out, mode='a', index=False, header=False)

@dataclass
class QR_Deconstructor:
    L1: str = 'LEVEL1'
    L2: str = 'LEVEL2'
    L3: str = 'LEVEL3'
    L4: str = 'LEVEL4'
    L5: str = 'LEVEL5'
    L6: str = 'LEVEL6'

    QR_raw_text: str = ''

    new_full_name: str = ''
    rename_success: bool = False

    def __init__(self, QR_List_Pass, n_QR_codes, sep_value) -> None:
        self.QR_raw_text = []
        if len(QR_List_Pass) > 0:
            for key in QR_List_Pass.values():
                self.QR_raw_text.append(key.text_raw)
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

        # self.new_full_name = sep_value.join([self.L1, self.L2, self.L3, self.L4, self.L5, self.L6])

@dataclass
class Data_FS:
    csv_FS: list[str] = field(default_factory=list)
    has_FS: bool = False

    def __init__(self, cfg) -> None:
        # Open FieldStation csv file if applicable
        if cfg['fieldprism']['do_use_FieldStation_csv']:
            if (cfg['fieldprism']['do_use_FieldStation_csv'] is not None) and (cfg['fieldprism']['do_use_FieldStation_csv'] != ''):
                path_FS = cfg['fieldprism']['path_to_FieldStation_csv']
                # Add row once the file exists
                self.csv_FS = pd.read_csv(path_FS, dtype=str)
                self.has_FS = True
        else:
            self.csv_FS = []
            self.has_FS = False

    def get_image_row(self, image_name) -> None:
        image_row = self.csv_FS[self.csv_FS['filename_short'] == image_name]
        # image_row = self.csv_FS[self.csv_FS == image_name]
        return image_row