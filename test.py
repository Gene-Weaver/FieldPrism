'''
Test FieldPrism installation
output files go to the FieldPrism/demo/demo_output dir
'''

from fieldprism.image_processing import process_images
from QR_code_builder.build_PDF import build_pdf

### Each time you process images the config file is saved. You can change the path
### here to reuse a previous config. Use full path.
###      set: cfg_to_use = '/full/path/to/yaml_file.yaml'
###
### To use the FieldPrism.yaml file
###      set: cfg_to_use = None
###
### To test the FieldPrism installation 
###      set: cfg_to_use = 'test_installation'

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
    CGREENBG2  = '\33[102m'
    CREDBG2    = '\33[101m'
    CWHITEBG2  = '\33[107m'

if __name__ == '__main__':
    cfg_to_use = 'test_installation'
    print(f"{bcolors.CWHITEBG2}                                                                            {bcolors.ENDC}")
    print(f"{bcolors.CWHITEBG2}  Testing FieldPrism -- QR Code Builder -- FieldSheetBuilder -- Size Check  {bcolors.ENDC}")
    print(f"{bcolors.CWHITEBG2}                                                                            {bcolors.ENDC}")

    try:
        build_pdf(cfg_to_use)
        print(f"{bcolors.CGREENBG2}                                                                            {bcolors.ENDC}")
        print(f"{bcolors.CGREENBG2}        PASSED >>> QR Code Builder -- FieldSheetBuilder -- Size Check       {bcolors.ENDC}")
        print(f"{bcolors.CGREENBG2}                                                                            {bcolors.ENDC}")
    except Exception as e:
        print(f"{bcolors.CREDBG2}                                                                            {bcolors.ENDC}")
        print(f"{bcolors.CREDBG2}           FAILED: QR Code Builder, FieldSheetBuilder, Size Check           {bcolors.ENDC}")
        print(f"{bcolors.CREDBG2}                                                                            {bcolors.ENDC}")
        print(e)

    print(f"{bcolors.CWHITEBG2}                                                                            {bcolors.ENDC}")
    print(f"{bcolors.CWHITEBG2}                   Testing FieldPrism -- Image Processing                   {bcolors.ENDC}")
    print(f"{bcolors.CWHITEBG2}                                                                            {bcolors.ENDC}")
    try:
        process_images(cfg_to_use)
        print(f"{bcolors.CGREENBG2}                                                                            {bcolors.ENDC}")
        print(f"{bcolors.CGREENBG2}                         PASSED >>> Image Processing                        {bcolors.ENDC}")
        print(f"{bcolors.CGREENBG2}                                                                            {bcolors.ENDC}")
    except Exception as e:
        print(f"{bcolors.CREDBG2}                                                                            {bcolors.ENDC}")
        print(f"{bcolors.CREDBG2}                         FAILED >>> Image Processing                        {bcolors.ENDC}")
        print(f"{bcolors.CREDBG2}                                                                            {bcolors.ENDC}")
        print(e)