# FieldPrism Software

Table of Contents
=================

* [Prerequisites](#prerequisites)
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

### Troubleshooting CUDA

- If your system already has another version of CUDA (e.g., CUDA 11.7) then it can be complicated to switch to CUDA 11.3. 
- The simplest solution is to install pytorch with CPU only, avoiding the CUDA problem entirely.
- Alternatively, you can install the [latest pytorch release]https://pytorch.org/get-started/locally/ for your specific system, either using the cpu only version `pip3 install torch`, `pip3 install torchvision`, `pip3 install torchaudio` or by matching the pythorch version to your CUDA version.
- We have not validated CUDA 11.6 or CUDA 11.7, but our code is likely to work with them too. If you have success with other versions of CUDA/pytorch, let us know and we will update our instructions. 

## Using FieldPrism
Generating the FieldSheets, QR codes, and size check document can all be run at the same time. Enable or disable each of the three option in the `FieldSheetBuilder.yaml`file.

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


### FieldPrism - Image Processing
