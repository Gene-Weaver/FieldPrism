import os, cv2, pybboxes, torch, inspect, sys, imutils
import numpy as np
from dataclasses import dataclass, field
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
try:
    from utils_processing import get_color
    from utils_overlay import generate_overlay_QR_add
    from utils_processing import bcolors
except:
    from fieldprism.utils_processing import get_color
    from fieldprism.utils_overlay import generate_overlay_QR_add
    from fieldprism.utils_processing import bcolors
'''
Main Function
'''
def process_barcodes(cfg, image_name_jpg, all_barcodes, image, image_bboxes, img_w, img_h, Dirs):
    color_fail = (200,80,80)
    use_unstable_QR_code_decoder = cfg['fieldprism']['QR_codes']['use_unstable_QR_code_decoder']
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
        QR_Candidate = QRcode(i_candidate, image_name_jpg, image, image_bboxes, row, bbox, Dirs.path_QRcodes_raw, Dirs.path_QRcodes_summary, use_unstable_QR_code_decoder)
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

    return image, image_bboxes, QR_List_Pass, QR_List_Fail

'''
Classes
'''
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

    use_unstable_QR_code_decoder: bool = False
    

    def __init__(self, number, image_name_jpg, image, image_bboxes, row, bbox, path_QRcodes_raw, path_QRcodes_summary, use_unstable_QR_code_decoder) -> None:
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
        self.use_unstable_QR_code_decoder = use_unstable_QR_code_decoder
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
        # self.qr_code_bi = imutils.rotate_bound(self.qr_code_bi, -5)
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
        if not self.use_unstable_QR_code_decoder:
            try:
                content, pts, self.straight_qrcode = cv2.QRCodeDetector().detectAndDecode(self.croppped_QRcode)
            except:
                content = ''
                self.straight_qrcode = None
        else: ### **** Using detectAndDecodeCurved can cause a memory exception. This will kill the program without any explanation.
            try:
                content, pts, self.straight_qrcode = cv2.QRCodeDetector().detectAndDecode(self.croppped_QRcode)
                if content == '':
                    content, pts, self.straight_qrcode = cv2.QRCodeDetector().detectAndDecodeCurved(self.croppped_QRcode)
            except:
                content = ''
                self.straight_qrcode = None

        if content != '':
            self.text_raw = content
            bad_code = False
        else:
            bad_code = True
        return bad_code

    def decode_QRcode(self) -> None:
        if not self.use_unstable_QR_code_decoder:
            try:
                content, pts, self.straight_qrcode = cv2.QRCodeDetector().detectAndDecode(self.qr_code_bi)
            except:
                content = ''
                self.straight_qrcode = None
        else: ### **** Using detectAndDecodeCurved can cause a memory exception. This will kill the program without any explanation.
            try:
                content, pts, self.straight_qrcode = cv2.QRCodeDetector().detectAndDecode(self.qr_code_bi)
                if content == '':
                    content, pts, self.straight_qrcode = cv2.QRCodeDetector().detectAndDecodeCurved(self.qr_code_bi)
            except:
                content = ''
                self.straight_qrcode = None

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


@dataclass
class QRcodeFS:
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

    bbox: list = field(default_factory=None)
    rough_center: list = field(default_factory=None)
    centroid_list: list = field(default_factory=None)
    croppped_QRcode: list = field(default_factory=None)
    qr_code_bi: list = field(default_factory=None)

    path_QRcodes_raw: str = ''
    path_QRcodes_summary: str = ''

    name_QR_raw_png: str = ''

    straight_qrcode: list = field(default_factory=None)

    use_unstable_QR_code_decoder: bool = False
    

    def __init__(self, number, image, qr, use_unstable_QR_code_decoder) -> None:
        # self.image_name_jpg = image_name_jpg
        # self.path_QRcodes_raw = path_QRcodes_raw
        # self.path_QRcodes_summary = path_QRcodes_summary
        self.number = str(number)
        self.image = image
        self.row = qr
        # self.image_bboxes = image_bboxes
        self.image_name = self.image_name_jpg.split('.')[0]
        self.name_QR_raw_png = ''.join([self.image_name,'__QR_',self.number,'.png'])
        self.use_unstable_QR_code_decoder = use_unstable_QR_code_decoder
        self.process_QRcode()
        self.parse_text()

    def parse_text(self) -> None:
        if self.text_raw != '':
            self.rank = self.text_raw.split(':')[0]
            self.rank_value = self.text_raw.split(':')[1]


    def prepare_QRcode(self,bi) -> None:
        ret, self.qr_code_bi = cv2.threshold(self.croppped_QRcode,bi,255,cv2.THRESH_BINARY)

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

        if not self.use_unstable_QR_code_decoder:
            try:
                content, pts, self.straight_qrcode = cv2.QRCodeDetector().detectAndDecode(self.croppped_QRcode)
            except:
                content = ''
                self.straight_qrcode = None
        else: ### **** Using detectAndDecodeCurved can cause a memory exception. This will kill the program without any explanation.
            try:
                content, pts, self.straight_qrcode = cv2.QRCodeDetector().detectAndDecode(self.croppped_QRcode)
                if content == '':
                    content, pts, self.straight_qrcode = cv2.QRCodeDetector().detectAndDecodeCurved(self.croppped_QRcode)
            except:
                content = ''
                self.straight_qrcode = None

        if content != '':
            self.text_raw = content
            bad_code = False
        else:
            bad_code = True
        return bad_code

    def decode_QRcode(self) -> None:
        if not self.use_unstable_QR_code_decoder:
            try:
                content, pts, self.straight_qrcode = cv2.QRCodeDetector().detectAndDecode(self.qr_code_bi)
            except:
                content = ''
                self.straight_qrcode = None
        else: ### **** Using detectAndDecodeCurved can cause a memory exception. This will kill the program without any explanation.
            try:
                content, pts, self.straight_qrcode = cv2.QRCodeDetector().detectAndDecode(self.qr_code_bi)
                if content == '':
                    content, pts, self.straight_qrcode = cv2.QRCodeDetector().detectAndDecodeCurved(self.qr_code_bi)
            except:
                content = ''
                self.straight_qrcode = None

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
                        break
                    elif bi >= 190:
                        print('')
                        print(f"{bcolors.FAIL}            FAILED TO READ QR CODE{bcolors.ENDC}")
                        bad_code = False
                        break

'''
Helper Functions FS
'''
def read_QR_codes(n_qr, cropped_QRs):
    RESULTS = {
    "Level_1": "none",
    "Level_2": "none",
    "Level_3": "none",
    "Level_4": "none",
    "Level_5": "none",
    "Level_6": "none"
    }

    use_unstable_QR_code_decoder = False

    i_candidate = 0
    i_pass = 0
    i_fail = 0 
    QR_List_Pass = {}
    QR_List_Fail = {}
    color = []
    for qr in cropped_QRs:
        i_candidate += 1
        print(f"{bcolors.BOLD}            Processing QR Code {i_candidate}{bcolors.ENDC}")
        QR_Candidate = QRcodeFS(i_candidate, image, qr, use_unstable_QR_code_decoder)
        if QR_Candidate.text_raw != '':
            i_pass += 1
            QR_List_Pass[i_pass-1] = QR_Candidate

            image = QR_Candidate.image
        else:
            i_fail += 1
            QR_List_Fail[i_fail-1] = QR_Candidate

    for key in QR_List_Pass.values():
        # print(f'pass:\n{key.text_raw}')
        if key.rank in RESULTS:
            RESULTS[key.rank] = key.rank_value
        # qr_label = ''.join(['L: ',key.rank, ' C: ',key.rank_value])


    print("RESULTS:")
    print(RESULTS)
    return RESULTS


