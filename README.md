![Field Prism](https://fieldprism.org/img/FieldPrism_Desktop_Large.jpg)

# FieldPrism

Table of Contents
=================

* [FieldPrism Software](#fieldprism-software)
* [Table of Contents](#table-of-contents)
   * [Installing FieldPrism](#installing-fieldprism)
      * [Prerequisites](#prerequisites)
      * [Installation - Cloning the FieldPrism Repository](#installation---cloning-the-fieldprism-repository)
      * [About Python Virtual Environments](#about-python-virtual-environments)
      * [Installation - Ubuntu 20.04](#installation---ubuntu-2004)
         * [Virtual Environment](#virtual-environment)
         * [Installing Packages](#installing-packages)
      * [Installation - Mac OS](#installation---mac-os)
         * [Virtual Environment](#virtual-environment-1)
         * [Installing Packages](#installing-packages-1)
      * [Installation - Windows 10+](#installation---windows-10)
         * [Virtual Environment](#virtual-environment-2)
         * [Installing Packages](#installing-packages-2)
      * [Troubleshooting CUDA](#troubleshooting-cuda)
   * [Using FieldPrism](#using-fieldprism)
      * [FieldSheetBuilder](#fieldsheetbuilder)
         * [Setup](#setup)
         * [Run](#run)
      * [QR Code Generator](#qr-code-generator)
         * [fieldsheetbuilder : setup](#fieldsheetbuilder--setup)
         * [fieldsheetbuilder : QR_code_builder](#fieldsheetbuilder--qr_code_builder)
         * [Run](#run-1)
      * [FieldPrism - Image Processing](#fieldprism---image-processing)
         * [FieldPrism Configurations](#fieldprism-configurations)
            * [FieldSheet Options](#fieldSheet-options)
            * [Make Images Vertical](#make-images-vertical)
            * [Processing Options](#processing-options)
            * [Justify the Distortion Corrected Images](#justify-the-distortion-corrected-images)
            * [Images to Process](#images-to-process)
            * [Output Directories](#output-directories)
            * [FieldStation Info](#fieldstation-info)
            * [ML Detection Options](#ml-detection-options)
            * [QR Code File Renaming Options](#qr-code-file-renaming-options)

## Installing FieldPrism

### Prerequisites
- Python 3.8.10
- PyTorch 1.11 
- CUDA version 11.3 (if utilizing a GPU)
- Git

- Note: we have also verified python 3.10.4  

### Installation - Cloning the FieldPrism Repository
1. First, install Python 3.8.10 on your machine of choice.
2. Open a terminal window and `cd` into the directory where you want to install FieldPrism.
3. Clone the FieldPrism repository from GitHub by running `git clone https://github.com/Gene-Weaver/FieldPrism.git` in the terminal.
4. Move into the FieldPrism directory by running `cd FieldPrism` in the terminal.
5. To run FieldPrism we need to install its dependencies inside of a python virtual environmnet. Follow the instructions below for your operating system. 

### About Python Virtual Environments
A virtual environment is a tool to keep the dependencies required by different projects in separate places, by creating isolated python virtual environments for them. This avoids any conflicts between the packages that you have installed for different projects. It makes it easier to maintain different versions of packages for different projects.

### Installation - Ubuntu 20.04

#### Virtual Environment

1. Still inside the FieldPrism directory, show that a venv is currently not active: 
    - `which python`
2. Then create the virtual environment (venv_fp is the name of our new virtual environment):  
    - `python3 -m venv venv_fp`
3. Activate the virtual environment:  
    - `source ./venv_fp/bin/activate`
4. Confirm that the venv is active (should be different from step 1):  
    - `which python`
5. If you want to exit the venv, deactivate the venv using:  
    - `deactivate`

#### Installing Packages

1. Install the required dependencies to use FieldPrism: 
    - `pip install opencv-python pandas pybboxes scipy scikit-image numpy tqdm pyyaml IPython matplotlib seaborn tensorboard fpdf`
2. Upgrade numpy: 
    - `pip install numpy -U`
3. Install qrcode[pil]:  
    - `pip install qrcode[pil]`
4. The FieldPrism machine learning algorithm requires PyTorch version 1.11 for CUDA version 11.3. If your computer does not have a GPU, then use the CPU version and the CUDA version is not applicable. PyTorch is large and will take a bit to install.
    - WITH GPU: `pip install torch==1.11.0+cu113 torchvision==0.12.0+cu113 torchaudio==0.11.0 --extra-index-url https://download.pytorch.org/whl/cu113`
    - WITH CPU ONLY: `pip install torch==1.11.0+cpu torchvision==0.12.0+cpu torchaudio==0.11.0 --extra-index-url https://download.pytorch.org/whl/cpu`
5. Test the installation:  
    - `python3 test.py`
    - If you see large red messages, then the installation was not successful. The rror message will be below the large red boxes, providing information on how to correct the installation error. If you need more help, please submit an inquiry in the form at [FieldPrism.org](https://fieldprism.org/)
6. You can view the test output in `FieldPrism/demo/demo_output/`

### Installation - Mac OS

#### Virtual Environment

1. Still inside the FieldPrism directory, show that a venv is currently not active:  
    - `which python`
2. Then create the virtual environment (venv_fp is the name of our new virtual environment):  
    - `python3 -m venv venv_fp`
3. Activate the virtual environment:  
    - `source venv_fp/bin/activate`
4. Confirm that the venv is active (should be different from step 1):  
    - `which python`
5. If you want to exit the venv, deactivate the venv using:  
    - `deactivate`

#### Installing Packages

1. Install the required dependencies to use FieldPrism:  
    - `pip install opencv-python pandas pybboxes scipy scikit-image numpy tqdm pyyaml IPython matplotlib seaborn tensorboard fpdf`
2. Upgrade numpy:  
    - `pip install numpy -U`
3. Install qrcode[pil]:  
    - `pip install qrcode[pil]`
4. The FieldPrism machine learning algorithm requires PyTorch version 1.11 
    - `pip install torch==1.11.0 torchvision==0.12.0 torchaudio==0.11.0`
5. Test the installation. test.py will test the QR code builder and image processing portions of FieldPrism:  
    - `python test.py`
    - If you see large red messages, then the installation was not successful. The rror message will be below the large red boxes, providing information on how to correct the installation error. If you need more help, please submit an inquiry in the form at [FieldPrism.org](https://fieldprism.org/)
6. Mac OS does not support the use of a GPU, so image processing will run more slowly.
7. You can view the test output in `FieldPrism/demo/demo_output/`

### Installation - Windows 10+

#### Virtual Environment

1. Still inside the FieldPrism directory, show that a venv is currently not active: 
    - `python --version`
2. Then create the virtual environment (venv_fp is the name of our new virtual environment):  
    - `python3 -m venv venv_fp`
3. Activate the virtual environment:  
    - `.\venv_fp\Scripts\activate`
4. Confirm that the venv is active (should be different from step 1):  
    - `python --version`
5. If you want to exit the venv, deactivate the venv using:  
    - `deactivate`

#### Installing Packages

1. Install the required dependencies to use FieldPrism:  
    - `pip install opencv-python pandas pybboxes scipy scikit-image numpy tqdm pyyaml IPython matplotlib seaborn tensorboard fpdf`
2. Upgrade numpy:  
    - `pip install numpy -U`
3. Install qrcode[pil]:  
    - `pip install qrcode[pil]`
4. The FieldPrism machine learning algorithm requires PyTorch version 1.11 for CUDA version 11.3. If your computer does not have a GPU, then use the CPU version and the CUDA version is not applicable. PyTorch is large and will take a bit to install.
    - WITH GPU: `pip install torch==1.11.0+cu113 torchvision==0.12.0+cu113 torchaudio==0.11.0 --extra-index-url https://download.pytorch.org/whl/cu113`
    - WITH CPU ONLY: `pip install torch==1.11.0+cpu torchvision==0.12.0+cpu torchaudio==0.11.0 --extra-index-url https://download.pytorch.org/whl/cpu`
5. Test the installation. test.py will test the QR code builder and image processing portions of FieldPrism:  
    - `python test.py`
    - If you see large red messages, then the installation was not successful. The rror message will be below the large red boxes, providing information on how to correct the installation error. If you need more help, please submit an inquiry in the form at [FieldPrism.org](https://fieldprism.org/)
6. You can view the test output in `FieldPrism/demo/demo_output/`

---

### Troubleshooting CUDA

- If your system already has another version of CUDA (e.g., CUDA 11.7) then it can be complicated to switch to CUDA 11.3. 
- The simplest solution is to install pytorch with CPU only, avoiding the CUDA problem entirely.
- Alternatively, you can install the [latest pytorch release]https://pytorch.org/get-started/locally/ for your specific system, either using the cpu only version `pip3 install torch`, `pip3 install torchvision`, `pip3 install torchaudio` or by matching the pythorch version to your CUDA version.
- We have not validated CUDA 11.6 or CUDA 11.7, but our code is likely to work with them too. If you have success with other versions of CUDA/pytorch, let us know and we will update our instructions. 

## Using FieldPrism
The FieldSheets, QR codes, and size check document can all be generated at the same time. Enable or disable each of the three option in the `FieldSheetBuilder.yaml`file. The `fieldsheetbuilder : field_sheet_builder : page_size` controls the size of the FieldSheet. The `fieldsheetbuilder : QR_code_builder : page_size` controls the size of paper that the QR codes will be printed on.

---

### FieldSheetBuilder

FieldSheetBuilder is a tool for creating field sheets and QR codes for use in FieldPrism projects. It allows you to specify which documents you want to create, as well as customize the size and appearance of the field sheet and QR codes. To change the settings of FieldSheetBuilder we need to edit the configuration file: `FieldSheetBuilder.yaml`. You can edit this file using a text editor (not Microsoft Word) or your favorite IDE, like VS Code, Sublime, or PyCharm. Premade FieldSheets are available at [https://fieldprism.org/]FieldPrism.org

#### Setup
- Enable building FieldSheets by setting `create_field_sheet: True`
   - If the other `create_` fields are set to `True` then you will also create QR codes and the size check
   - We recommend setting `create_size_check: True` to generate the size check document 
- Name your FieldSheets by setting `new_file_stem: 'my_project_name'`
   - For names, only use alphanumeric characters, underscores, or dashes.
- Set the FieldSheet size in the `field_sheet_builder` section with `page_size: 'letter'`
   - Options from small to large: 
      - `'A5'`
      - `'Letter'`
      - `'A4'`
      - `'Legal'`
      - `'Tabloid'`
      - `'A3'`
      - `'Custom'` --- Custom will print an A4 sheet that you can cut up and mount on larger surfaces
   - Note: Letter and A4 are interchangeable, Tabloid and A3 are interchangeable. Each have slightly different marker patterns to maximize the usable area, but as long as you print the sheets at 100% in your printer's settings, then either can be used. 
   - Note: To print with `Tabloid` you have to edit the fpdf script. If you are not comfortable doing that, then just use the A3 setting and print onto Tabloid sized paper. 
- Optional, assign an ouput directory by setting `dir_home: '/path/to/output/folder'`
   - by default, output will be saved to `FieldPrism/QR_code_builder/bin_PDF` 

#### Run 
1. To build FieldSheets we run FieldSheetBuilder.py
2. In a terminal window, make sure that you have `cd`'d into the FieldPrism directory and that the virtual environment is activated. 
3. To run: `python FieldSheetBuilder.py`
4. Then go to either your output directory or the default location to view your FieldSheets

---

### QR Code Generator
#### fieldsheetbuilder : setup
- Prepare your QR code naming file. This is a CSV file for naming and generating alias names, as mentioned in the paper. An example CSV file can be found in `FieldPrism/demo/names` or in the FieldPrism demo kit from [FieldPrism.org](https://fieldprism.org/).
   - Note: All headers must follow the pattern 'Level_1', 'Level_2', etc. or if using alias names 'Level_1', 'Alias_1'
   - Note: Specimen naming components cannot contain any characters other than letters, numbers, dashes, and underscores. All illegal characters will be replaced with a dash '-'.
   - Note: We validated up to 6 levels and do not recommend using more.
- Enable building QR codes by setting 
   - `create_QR_codes: True`
- Name your QR code project by setting
   - `new_file_stem: 'my_project_name'`
   - For names, only use alphanumeric characters, underscores, or dashes.
- Set the location of your CSV naming file:
   - `dir_containing_CSV_files: '/path/to/csv/folder'`   
- Set the name of your CSV naming file, with or without the extension:
   - `dir_containing_CSV_files: 'my_csv_file'`   
- Optional, assign an ouput directory by setting
   - `dir_home: '/path/to/output/folder'`
   - by default, output will be saved to `FieldPrism/QR_code_builder/bin_PDF` 

#### fieldsheetbuilder : QR_code_builder
This section of the config file has two parts. Part one allows you to use one of two premade QR code templates. To use these templates set 
- `ues_default_setup: True`
Pick from `'A4_Short_Names'` or `'A4_Long_Names'`
- A4_Short_Names
   - Fits 40 QR codes into an A4 or Letter sized page
   - Has enough room for 3-character names
   - Designed for indeterminate naming schemes
- A4_Long_Names
   - Fits 24 QR codes into an A4 or Letter sized page
   - Has enough room for 60-character names. We do NOT recommend long names. Long names shrink the pixel size of the QR codes and makes decoding less reliable.
   - Keep your names as short as possible
   - For long names, separate words with underscores. When long names are parsed, FieldPrism will attempt to put each word on a new line for better readability. See `A4_Max_Name_Length_QR_Codes.pdf` and its associated naming file `Demo_Long_Names_Max.csv` in the demo kit for more information. 
Then set the QR code density. We recommend leaving it at the default settings. It will automatically adjust based on the content.
   - `QR_density: 5`

Everything below this point is overwritten by using the premade settings `'A4_Short_Names'` or `'A4_Long_Names'`
Only change the remaining settings if you need to create custom QR codes. We have not validated larger, smaller, or different densities. Be sure to validate the performance of any custom settings.

#### Run 
1. To build FieldSheets we run FieldSheetBuilder.py
2. In a terminal window, make sure that you have `cd`'d into the FieldPrism directory and that the virtual environment is activated. 
3. To run: `python FieldSheetBuilder.py`
4. Then go to either your output directory or the default location to view your QR code sheets

---

### FieldPrism - Image Processing
Here are a few tips:
- The only characters allowed in file names are letters, numbers, underscores, and dashes.
- A script will run to remove any illegal characters - they will be replaced with dashes.
- Good images in = good images out!
- The biggest failure for FieldPRism is when a marker or QR code is in mixed lighting, i.e. half of the code is in shadow, half in bright light. Do your best to keep lighting consistent, but it does not have to be perfect.
- Covering a subject with plastic to keep it flat is normally okay, just mind the glare from the sun or reflections.
- The following descibes settings in the `FieldPrism.yaml` configuration file. Default settings are a good place to start. If a few images are being processed strangely or are problematic, copy those original files to a new directory and then start tuning processing settings. Some edge-case images will require different configurations to process successfully. Don't expect to process all images successfully using the same config, unless your dataset is quite homogeneous.

#### FieldPrism Configurations
##### FieldSheet Options
- **scale:**
    - **use_predefined** 
      - True: set contains images that used pre-defined scale-sheet
      - False: using a custom setup
    - **scale_size** 
      - 'A3': largest scale-sheet, tabloid, 11 x 17 inches
      - 'A4': default scale-sheet, A4, 8.5 x 11 inches
      - 'A5': smallest scale-sheet, A5, 5.8 x 8.3 inches
      - 'Legal': legal size, 8.5 x 14 inches
      - 'Tabloid': 11 x 17 inches
      - 'Letter': 8.5 x 11 inches
      - 'custom': placing markers on custom background (poster board etc.) larger or smaller
    - **custom_ratio**
      - null: Use null if using predefined scale-sheet
      - float: floating point number between 0 and 1 (0.65 OR 0.6111). To calculate, divide long side distance by short side
    - **custom_short_distance**
      - integer: distance in mm. between the two markers on the short side

##### Make Images Vertical
FP requires vertical images. If you are re-running a set you can set this to True to save time.
- **skip_make_images_vertical**
   - False: boolean, only set to True if you are re-running images that are already vertical!

##### Processing Options
- **strict_distortion_correction**
   - False: default. will use center of detected marker bbox if exact center cannot be determined.
   - True: requires all 4 boxes within all 4 markers to correct distortion, need good lighting for this option 
- **use_template_for_pixel_to_metric_conversion**
   - False: default.
   - True: If all four boxes inside at least one marker are not regularly found then this will find a very close approximation, usually +-3 % of true conversion 
- **do_remove_overlap**
   - False: default. start with False. set to True for images that may become heavily distorted OR if 
   - True: for images that may become extremely warped after processing OR if QR codes and rulers are predicted incorrectly. If a barcode in the middle of the image is predicted to be a ruler, then either the image will not go through distortion correction or it will be wildly warped. Setting to True can help correct this.
- **overlap_priority**
   - 'barcode': rulers that intersect with barcodes will be ignored
   - 'ruler': barcodes that intersect with rulers will be ignored
- **insert_clean_QR_codes**
   - True: insert a new QR code over the original one, which can be useful when the original QR code is difficult to read due to glare or other issues
   - False: default. use the original QR code for processing

##### Justify the Distortion Corrected Images
- **justify_corrected_images:**
    - **do_justify**
      - True: top left marker will be placed at the origin, padding will be added if needed, helps make images more uniform, especially if originals are heavily distorted
      - False: no image manipulation takes place after the image is corrected for distortion. overrides make_uniform
    - **justify_corrected_images_origin**
      - integer: x and y coordinate of where the center of the top left marker should be placed 500 works in most cases 
    - **make_uniform**
      - True: after distortion correction images are transformed into uniform dimensions images are scaled to the same size relative to the scale markers and will be resized to the same resolution
      - False: if do_justify = False, then make_uniform will be False
    - **make_uniform_buffer**
      - integer: distance in mm to leave around the edges outside of the scale markers, 40 is a good start
    - **uniform_h**
      - integer: pixel height of final image, eg. 4000
    - **uniform_w**
      - integer: pixel width of final image, eg. 3000

##### Images to Process
- **dir_images_unprocessed**
   - directory of the images that you want to process 
- **dir_images_unprocessed_labels**
   - directory of the labels for previously processed images. You can speed up processing by adding the folder that contains the machine learning predictions/labels from a previous run. The labels are in the "/Labels_Not_Corrected" folder. So set to `/path/to/Labels_Not_Corrected`

##### Output Directories
- **dir_home**
   - parent folder for all output files. Will go to `dir_home/dirname_images_processed/dirname_current_project/dirname_current_run`
- **dirname_images_processed**
   - image set
- **dirname_current_project**
   - project
- **dirname_current_run**
   - run

##### FieldStation Info
- If you collected data with FieldStation, add the data output file here
- **do_use_FieldStation_csv**
   - False: default. Did not use FieldStation
   - True: Did use FieldStation
- **path_to_FieldStation_csv**
   - full path to CSV data file: `path/to/file/FieldPrism_Data.csv`

##### ML Detection Options
- **model_size**
   - 'best': use the best model. Currently only one model is provided. More may come.
- **min_confidence_threshold**
   - float: default is 0.70, going lower may cause fals positives causing rulers to be confused with QR codes
- **show_predicted_text**
   - False: default. Skips placing bounding boxes around text labels
   - True: Places bounding boxes around text labels

##### QR Code File Renaming Options
- **use_unstable_QR_code_decoder**
   - False: default. Uses a stable method to detect and decode QR codes
   - True: uses an unstable method to decode QR codes. This method will detect QR codes in difficult situations, *BUT* this method relies on a dependency (a package in open-cv2) that can cause random memory faults. This may cause FieldPrism to crash without any explanation - the program will just die. We recommend moving images with undetected barcodes to a new folder and then setting this to True to process a subset of your images. If it doesn't crash, then great! You'll get even more successful QR code decodings. But if it crashes without explanation, this is why.
- **do_rename_images**
   - False: default. do not rename output images to match the QR codes in the image. 
   - True: rename output images to match the QR codes in the image. 
- **n_QR_codes**
   - integer: default 4. Tells how many levels to expect when reading QR codes. 
- **sep_value**
   - string: default '__'. The separator used to reconstruct the filenames
- **fail_value**
   - string: default null. What to put into a file name in place of a failed QR code. Default is recommended.
- **do_keep_original_name_if_fail**
   - True: default. If QR codes all fail, keep the original file name
   - False: If QR codes all fail the new file name will be "Level1__Level2.jpg" etc. Not recommended
