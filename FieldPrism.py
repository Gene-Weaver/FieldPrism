import os, inspect, sys
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from fieldprism.image_processing import process_images

if __name__ == '__main__':
    ### Each time you process images the config file is saved. You can change the path
    ### here to reuse a previous config. Use full path.
    ###      set: cfg_to_use = '/full/path/to/yaml_file.yaml'
    ###
    ### To use the FieldPrism.yaml file
    ###      set: cfg_to_use = None
    ###
    ### To test the FieldPrism installation 
    ###      set: cfg_to_use = 'test_installation'
    
    cfg_to_use = None
    process_images(None)