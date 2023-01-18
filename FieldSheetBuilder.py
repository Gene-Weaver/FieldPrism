import os, inspect, sys
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from QR_code_builder.build_PDF import build_pdf

'''
For tabloid, add this to fpdf.py

in class FPDF(object):
in the list of # Page format

elif(format=='tabloid'): # added by Will Weaver 2023
    format=(790.87,1224.57)
    
'''

if __name__ == '__main__':
    build_pdf(None)