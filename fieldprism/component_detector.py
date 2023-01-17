import os, inspect, sys
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
try:
    from utils_processing import bcolors
    from yolov5.detect import run
except:
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
        dir_weights =  os.path.join(dir_FP,'fieldprism','yolov5','weights','best.pt')
    else:
        print(f"{bcolors.FAIL}In FieldPrism.yaml the parameter: is set incorrectly. cfg['fieldprism']['detector']['model_size'] MUST be either 'small' or 'large'{bcolors.ENDC}")
        print(f"{bcolors.WARNING}Defaulting to cfg['fieldprism']['detector']['model_size'] = 'small'{bcolors.ENDC}")
        image_input_size = (1280, 1280)
        dir_weights =  os.path.join(dir_FP,'fieldprism','yolov5','weights','fp_large_v_1.pt')
        
    try:
        actual_save_dir = run(weights=dir_weights,
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


