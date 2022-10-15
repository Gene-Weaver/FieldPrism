import os, yaml

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

def validate_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def load_cfg():
    with open("FieldPrism.yaml", "r") as ymlfile:
        cfg = yaml.full_load(ymlfile)
    return cfg