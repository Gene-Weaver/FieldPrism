# py -m ensurepip --upgrade
# .\venv\Scripts\activate
import os
from build_PDF_utils import bcolors, Input, get_cfg_from_full_path, createProjectPDF

def main() -> None:
    ### Import from config file
    dir_FP = os.path.dirname(os.path.dirname(__file__))
    path_cfg = os.path.join(dir_FP,'FieldSheetBuilder.yaml')
    cfg = get_cfg_from_full_path(path_cfg)

    
    ### Creating QR Codes and Field Sheet for use in FieldPrism Projects ###
    # Which documents do you want to create? 
    CREATE_FIELD_SHEET = cfg['fieldsheetbuilder']['setup']['create_field_sheet']
    CREATE_QR_CODES = cfg['fieldsheetbuilder']['setup']['create_QR_codes']
    CREATE_SIZE_CHECK = cfg['fieldsheetbuilder']['setup']['create_size_check']


    # Input / Output
    PDF_NAME = cfg['fieldsheetbuilder']['setup']['new_file_stem']
    DIR_CSV = cfg['fieldsheetbuilder']['setup']['dir_containing_CSV_files']
    CSV_NAME = cfg['fieldsheetbuilder']['setup']['name_CSV_file']
    QR_LOCATION = 'solo' # cfg['fieldsheetbuilder']['QR_code_builder']['QR_location']
    PAGESIZE_TEMPLATE = cfg['fieldsheetbuilder']['field_sheet_builder']['page_size']


    ### Default configs
    if cfg['fieldsheetbuilder']['QR_code_builder']['ues_default_setup']:
        if cfg['fieldsheetbuilder']['QR_code_builder']['default_config'] == 'A4_Long_Names':
            page = Input(PDF_NAME=PDF_NAME, DIR_CSV =DIR_CSV, CSV_NAME=CSV_NAME, QR_LOCATION=QR_LOCATION, CREATE_FIELD_SHEET = CREATE_FIELD_SHEET, CREATE_QR_CODES= CREATE_QR_CODES, CREATE_SIZE_CHECK = CREATE_SIZE_CHECK,
                        SIZE=12, SPACE=4,
                        LABELSHIFT=6,
                        PRINT_ORDER='row',
                        PAGESIZE_TEMPLATE = PAGESIZE_TEMPLATE,
                        PAGESIZE_QR = 'A4',
                        USE_LEVELS=True,
                        PAGE_MARGIN_LEFT=10,
                        PAGE_MARGIN_TOP=15,
                        QR_TEXT_X = 30,
                        QR_DIM_X = 30,
                        QR_DIM_Y = 30,
                        QR_TALL = 8, # with long labels = 10
                        QR_WIDE = 3,# with long labels = 3
                        QR_BUFFER_X = 30,
                        QR_BUFFER_Y = 4,
                        QR_DENSITY = cfg['fieldsheetbuilder']['QR_code_builder']['QR_density'])
        elif cfg['fieldsheetbuilder']['QR_code_builder']['default_config'] == 'A4_Short_Names':
            page = Input(PDF_NAME=PDF_NAME, DIR_CSV =DIR_CSV, CSV_NAME=CSV_NAME, QR_LOCATION=QR_LOCATION, CREATE_FIELD_SHEET = CREATE_FIELD_SHEET, CREATE_QR_CODES= CREATE_QR_CODES, CREATE_SIZE_CHECK = CREATE_SIZE_CHECK,
                        SIZE = 12, SPACE = 4, LABELSHIFT = 7, PRINT_ORDER= 'row', PAGESIZE_TEMPLATE = PAGESIZE_TEMPLATE, PAGESIZE_QR = 'A4',
                        USE_LEVELS = True,
                        PAGE_MARGIN_LEFT=15,
                        PAGE_MARGIN_TOP=15,
                        QR_TEXT_X = 30,
                        QR_DIM_X = 30,
                        QR_DIM_Y = 30,
                        QR_TALL = 8, # with long labels = 10
                        QR_WIDE = 5,# with long labels = 3
                        QR_BUFFER_X = 5,
                        QR_BUFFER_Y = 4,
                        QR_DENSITY = cfg['fieldsheetbuilder']['QR_code_builder']['QR_density'])
    ### Manual / Custom Config
    else:
        # Setup page
        page = Input(PDF_NAME=PDF_NAME, 
            DIR_CSV =DIR_CSV, 
            CSV_NAME=CSV_NAME,
            QR_LOCATION=QR_LOCATION,
            CREATE_FIELD_SHEET = CREATE_FIELD_SHEET,
            CREATE_QR_CODES= CREATE_QR_CODES,
            CREATE_SIZE_CHECK = CREATE_SIZE_CHECK,
            SIZE = cfg['fieldsheetbuilder']['QR_code_builder']['QR_label_font_size'],
            SPACE=4,
            PRINT_ORDER=cfg['fieldsheetbuilder']['QR_code_builder']['print_order'],
            PAGESIZE_TEMPLATE = PAGESIZE_TEMPLATE,
            PAGESIZE_QR = cfg['fieldsheetbuilder']['QR_code_builder']['page_size'],
            USE_LEVELS=True,
            PAGE_MARGIN_LEFT=cfg['fieldsheetbuilder']['QR_code_builder']['page_margin_left'],
            PAGE_MARGIN_TOP=cfg['fieldsheetbuilder']['QR_code_builder']['page_margin_top'],
            LABELSHIFT=cfg['fieldsheetbuilder']['QR_code_builder']['QR_text_y'],
            QR_TEXT_X = cfg['fieldsheetbuilder']['QR_code_builder']['QR_text_x'],
            QR_DIM_X = cfg['fieldsheetbuilder']['QR_code_builder']['QR_dim_x'],
            QR_DIM_Y = cfg['fieldsheetbuilder']['QR_code_builder']['QR_dim_y'],
            QR_TALL = cfg['fieldsheetbuilder']['QR_code_builder']['QR_tall'], # with long labels = 10
            QR_WIDE = cfg['fieldsheetbuilder']['QR_code_builder']['QR_wide'],# with long labels = 3
            QR_BUFFER_X = cfg['fieldsheetbuilder']['QR_code_builder']['QR_buffer_x'],# with long labels = 16
            QR_BUFFER_Y = cfg['fieldsheetbuilder']['QR_code_builder']['QR_buffer_y'],
            QR_DENSITY = cfg['fieldsheetbuilder']['QR_code_builder']['QR_density'])
    createProjectPDF(page)

if __name__ == '__main__':
    main()





