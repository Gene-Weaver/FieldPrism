from QR_code_builder.build_PDF import build_pdf

'''
For tabloid, add this to fpdf.py

in class FPDF(object):
in the list of # Page format

elif(format=='tabloid'): # added by Will Weaver 2023
    format=(790.87,1224.57)
    
'''

if __name__ == '__main__':
    build_pdf()