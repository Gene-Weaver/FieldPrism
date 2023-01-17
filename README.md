# FieldPrism Software

### Prerequisites
- Python 3.8.10
- PyTorch 1.11 
- CUDA version 11.3 (if utilizing a GPU)
- Git

### Installation
1. First, install Python 3.8.10 on your machine of choice.
2. Create a python virtual environment.
3. Install the required packages.
4. Clone the FieldPrism repository from GitHub by running `git clone https://github.com/Gene-Weaver/FieldPrism.git` in the terminal.
5. Navigate to the location where you want to install FieldPrism. Example: `cd documents/home/mycomputer/programs/`
6. Verify that the FieldPrism directory is present by running `ls` in the terminal or by checking the directory in your file explorer.
7. Move into the FieldPrism directory by running `cd FieldPrism` in the terminal.
8. Create your virtual environment by following the instructions for your machine/OS.

### About Python Virtual Environments
A virtual environment is a tool to keep the dependencies required by different projects in separate places, by creating isolated python virtual environments for them. This avoids any conflicts between the packages that you have installed for different projects. It makes it easier to maintain different versions of packages for different projects.

### Installation - Ubuntu 20.04

#### Virtual Environment

1. Show that a venv is currently not active: `which python`
2. Install python virtual environment: `python3 -m pip install --user virtualenv`
3. Make sure you're inside of the FieldPrism directory, then create the virtual environment (venv_fp is the name of our new virtual environment): `python3 -m venv venv_fp`
4. Activate the virtual environment: `source ./venv_fp/bin/activate`
5. Confirm that the venv is active (should be different from step 1): `which python`
6. To deactivate the venv: `deactivate`

#### Installing packages

1. Install the required dependencies to use FieldPrism: `pip install opencv-python pandas pybboxes scipy scikit-image numpy tqdm pyyaml IPython matplotlib seaborn tensorboard fpdf`
2. Upgrade numpy: `pip install numpy -U`
3. Install qrcode[pil]: `pip install qrcode[pil]`
4. The FieldPrism machine learning algorithm requires PyTorch version 1.11 for CUDA version 11.3. If your computer does not have a GPU, then use the CPU version and the CUDA version is not applicable. PyTorch is large and will take a bit to install.
    - WITH GPU: `pip install torch==1.11.0+cu113 torchvision==0.12.0+cu113 torchaudio==0.11.0 --extra-index-url https://download.pytorch.org/whl/cu113`
    - WITH CPU ONLY: `pip install torch==1.11.0+cpu torchvision==0.12.0+cpu torchaudio==0.11.0 --extra-index-url https://download.pytorch.org/whl/cpu`
5. Test the installation: `python3 test.py`

### Installation - Mac OS

#### Virtual Environment

1. Show that a venv is currently not active: `which python`
2. Install python virtual environment: `python3 -m pip install virtualenv`
3. Make sure you're inside of the FieldPrism directory. use `cd` to change directories. Then create the virtual environment (venv_fp is the name of our new virtual environment): `python3 -m venv venv_fp`
4. Activate the virtual environment: `source venv_fp/bin/activate`
5. Confirm that the venv is active (should be different from step 1): `which python`
6. To deactivate the venv: `deactivate`

#### Installing packages

1. Install the required dependencies to use FieldPrism: `pip install opencv-python pandas pybboxes scipy scikit-image numpy tqdm pyyaml IPython matplotlib seaborn tensorboard fpdf`
2. Upgrade numpy: `pip install numpy -U`
3. Install qrcode[pil]: `pip install qrcode[pil]`
4. The FieldPrism machine learning algorithm requires PyTorch version 1.11 for CUDA version 11.3. If your computer does not have a GPU, then use the CPU version and the CUDA version is not applicable. PyTorch is large and will take a bit to install.
    - WITH GPU: `pip install torch==1.11.0+cu113 torchvision==0.12.0+cu113 torchaudio==0.11.0 --extra-index-url https://download.pytorch.org/whl/cu113`
    - WITH CPU ONLY: `pip install torch==1.11.0+cpu torchvision==0.12.0+cpu torchaudio==0.11.0 --extra-index-url https://download.pytorch.org/whl/cpu`
5. Test the installation: `python3 test.py`

