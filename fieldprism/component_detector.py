import os, inspect, sys
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
# try:
#     from utils_processing import bcolors
#     from yolov5.detect import run
# except:
from fieldprism.utils_processing import bcolors
from fieldprism.yolov5.detect import run

def detect_components_in_image(option, cfg, run_name, dir_out,existing_folder):
    dir_FP = os.path.dirname(os.path.dirname(__file__))
    if cfg['fieldprism']['detector']['model_size'] == 'large':
        image_input_size = (1280, 1280)
        dir_weights =  os.path.join(dir_FP,'fieldprism','yolov5','weights','fp_large_v_1.pt')
    elif cfg['fieldprism']['detector']['model_size'] == 'small':
        image_input_size = (512, 512)
        dir_weights =  os.path.join(dir_FP,'fieldprism','yolov5','weights','fp_small_v_1.pt')
    elif cfg['fieldprism']['detector']['model_size'] == 'best':
        image_input_size = (1280, 1280)
        dir_weights =  os.path.join(dir_FP,'fieldprism','yolov5','weights_nano','best.pt')
    else:
        print(f"{bcolors.FAIL}In FieldPrism.yaml the parameter: is set incorrectly. cfg['fieldprism']['detector']['model_size'] MUST be either 'small' or 'large'{bcolors.ENDC}")
        print(f"{bcolors.WARNING}Defaulting to cfg['fieldprism']['detector']['model_size'] = 'small'{bcolors.ENDC}")
        image_input_size = (1280, 1280)
        dir_weights =  os.path.join(dir_FP,'fieldprism','yolov5','weights','fp_large_v_1.pt')
        
    try:
        actual_save_dir, img_out = run(weights=dir_weights,
        option = option,
        show_predicted_text = cfg['fieldprism']['detector']['show_predicted_text'],
        source = run_name,
        project = dir_out,
        name = cfg['fieldprism']['dirname_current_run'],
        imgsz = image_input_size,
        conf_thres = cfg['fieldprism']['detector']['min_confidence_threshold'],
        exist_ok = existing_folder)

        try:
            actual_save_dir = actual_save_dir._str
        except:
            actual_save_dir = actual_save_dir
        return actual_save_dir
    except Exception as e:
        print(f"{bcolors.WARNING}No images in {run_name}. \n      Error: {e}{bcolors.ENDC}")

def detect_barcodes_FS(path_img, dir_out, run_name):
    dir_FP = os.path.dirname(os.path.dirname(__file__))
    dir_weights =  os.path.join(dir_FP,'fieldprism','yolov5','weights','fp_large_v_1.pt')
    image_input_size = (1280, 1280)
    try:
        actual_save_dir, img_out = run(weights=dir_weights,
        option = 'fs',
        show_predicted_text = False,
        source = path_img,
        project = dir_out,
        name = run_name,
        imgsz = image_input_size,
        conf_thres = 0.70,
        exist_ok = True)

        try:
            actual_save_dir = actual_save_dir._str
        except:
            actual_save_dir = actual_save_dir
        return actual_save_dir, img_out
    except Exception as e:
        print(f"{bcolors.WARNING}No images in {run_name}. \n      Error: {e}{bcolors.ENDC}")
        

def check_QR_codes(path_img, dir_out, run_name, label_nqr_status):
    label_nqr_status = int(label_nqr_status)
    actual_save_dir, img_out = detect_barcodes_FS(path_img, dir_out, run_name)

    qr_found = True
    return qr_found, img_out