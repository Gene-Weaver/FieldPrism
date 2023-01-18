# FieldPrism Software

### Prerequisites
- Python 3.8.10
- PyTorch 1.11 
- CUDA version 11.3 (if utilizing a GPU)
- Git

### Installation
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
2. Install python virtual environment:  
    - `python3 -m pip install --user virtualenv`
3. Then create the virtual environment (venv_fp is the name of our new virtual environment):  
    - `python3 -m venv venv_fp`
4. Activate the virtual environment:  
    - `source ./venv_fp/bin/activate`
5. Confirm that the venv is active (should be different from step 1):  
    - `which python`
6. If you want to exit the venv, deactivate the venv using:  
    - `deactivate`

#### Installing packages

1. Install the required dependencies to use FieldPrism: 
    - `pip install opencv-python pandas zipfile urllib pybboxes scipy scikit-image numpy tqdm pyyaml IPython matplotlib seaborn tensorboard fpdf`
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

### Installation - Mac OS

#### Virtual Environment

1. Still inside the FieldPrism directory, show that a venv is currently not active:  
    - `which python`
2. Install python virtual environment:  
    - `python3 -m pip install virtualenv`
3. Then create the virtual environment (venv_fp is the name of our new virtual environment):  
    - `python3 -m venv venv_fp`
4. Activate the virtual environment:  
    - `source venv_fp/bin/activate`
5. Confirm that the venv is active (should be different from step 1):  
    - `which python`
6. If you want to exit the venv, deactivate the venv using:  
    - `deactivate`

#### Installing packages

1. Install the required dependencies to use FieldPrism:  
    - `pip install opencv-python pandas zipfile urllib pybboxes scipy scikit-image numpy tqdm pyyaml IPython matplotlib seaborn tensorboard fpdf`
2. Upgrade numpy:  
    - `pip install numpy -U`
3. Install qrcode[pil]:  
    - `pip install qrcode[pil]`
4. The FieldPrism machine learning algorithm requires PyTorch version 1.11 
    - `pip install torch==1.11.0 torchvision==0.12.0 torchaudio==0.11.0`
5. Test the installation. test.py will test the QR code builder and image processing portions of FieldPrism:  
    - `python3 test.py`
    - If you see large red messages, then the installation was not successful. The rror message will be below the large red boxes, providing information on how to correct the installation error. If you need more help, please submit an inquiry in the form at [FieldPrism.org](https://fieldprism.org/)
6. Mac OS does not support the use of a GPU, so image processing will run more slowly.

