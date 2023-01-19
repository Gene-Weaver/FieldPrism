from __future__ import annotations
import os, yaml, time, re, inspect, sys
import qrcode # pip install qrcode[pil]
from dataclasses import dataclass, field
import pandas as pd
from fpdf import FPDF 
from cmath import isnan
from qrcode.image.styledpil import StyledPilImage
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
try:
    from QR_code_builder.build_PDF_PageSizes import PageInfo
except:
    from build_PDF_PageSizes import PageInfo

# from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
# from qrcode.image.styles.colormasks import RadialGradiantColorMask

def createProjectPDF(page):
    print(f"{bcolors.HEADER}Starting Project - {page.PDF_NAME}{bcolors.ENDC}")
    # nPages = labels.shape[0]

    # Initialize Page Dimension
    PageSizes = PageInfo()

    if page.CREATE_SIZE_CHECK:
        pdf = setupPDF(page,'field_sheet')
        newPage_size(page,pdf, PageSizes)
        savePDF_size(pdf,page)
        
    
    if page.QR_LOCATION =="imbed":
        pdf = setupPDF(page,'field_sheet')
        varNames = list(page.LABELS_DF.columns)
        for pageNumber in range(page.LABELS_DF.shape[0]):
            newPage(page, page.LABELS_DF, pdf, varNames, pageNumber, PageSizes)    
        savePDF(pdf, page)
            
    elif page.QR_LOCATION == "solo":
        if page.CREATE_FIELD_SHEET:
            # Print the template page
            pdf = setupPDF(page,'field_sheet')
            varNames = list(page.LABELS_DF.columns)
            newPage(page, page.LABELS_DF, pdf, varNames, 0, PageSizes)   
            savePDF(pdf,page)

        if page.CREATE_QR_CODES:
            # Print the QR code sheets
            pdf_QR = setupPDF(page, 'QR')
            varNames = list(page.LABELS_DF.columns)
            # for pageNumber in range(page.LABELS_DF.shape[0]):
            newPage_QR(page, page.LABELS_DF, pdf_QR, varNames, PageSizes)  
            savePDF_QR(pdf_QR,page)
    print(f"{bcolors.HEADER}Project Complete!{bcolors.ENDC}") 

@dataclass
class Input:
    CSV_NAME: str
    PDF_NAME: str = 'FieldPrism_Project'
    QR_LOCATION: str = 'solo' # 'solo' OR 'imbed'
    CREATE_FIELD_SHEET: bool = True,
    CREATE_QR_CODES: bool = True,
    CREATE_SIZE_CHECK: bool = True,
    POS: str = "top"
    FONT: str = "Helvetica"
    STYLE: str = "B"
    SIZE: int = 12
    SPACE: int = 4
    LABELSHIFT: int = 5
    SAVE_QR: bool = False
    USE_LEVELS: bool = False # When false = each row in CSV becomes 1 QR code # When true = each cell becomes a QR code
    PAGESIZE_TEMPLATE: str = "A4"
    PAGESIZE_QR: str = "A4"
    PRINT_ORDER: str = "row"
    DIR_CSV: str = ''
    DIR_QR_CODE_BUILDER: str = ''
    DIR_HOME: str = None
    DIR_QR: str = 'bin_QR'
    DIR_PDF: str = 'bin_PDF'
    COLOR: str = "gray"
    LABELS: str = field(init=False)
    LABELS_DF: list[str] = field(init=False,default_factory=list)
    QR_TEXT_X: int = 20
    QR_DIM_X: int = 20
    QR_DIM_Y: int = 20
    QR_TALL: int = 10
    QR_WIDE: int = 6
    QR_BUFFER_X: int = 20
    QR_BUFFER_Y: int = 5
    QR_DENSITY: int = 1
    PAGE_MARGIN_TOP: int = 15
    PAGE_MARGIN_LEFT: int = 15
    QR_TOTAL: int = field(init=False)
    IMG_LEVEL: str = field(init=False,default='QR_levels')

    def __post_init__(self) -> None:
        self.DIR_QR_CODE_BUILDER = os.path.join(os.path.dirname(__file__))
        if self.DIR_HOME == None:
            self.DIR_QR = os.path.join(self.DIR_QR_CODE_BUILDER, self.DIR_QR)
            self.DIR_PDF = os.path.join(self.DIR_QR_CODE_BUILDER, self.DIR_PDF)
        else:
            self.DIR_QR = os.path.join(self.DIR_HOME, self.DIR_QR)
            self.DIR_PDF = os.path.join(self.DIR_HOME, self.DIR_PDF)
        self.LABELS: str = buildCSVpath(self.CSV_NAME)
        self.LABELS_DF = pd.read_csv(os.path.join(self.DIR_CSV,self.LABELS),dtype=str) 
        self.LABELS_DF = self.filter_level_columns(self.LABELS_DF)
        self.QR_TALL = self.QR_TALL - 1
        self.QR_WIDE = self.QR_WIDE - 1
        self.QR_TOTAL = (self.QR_TALL + 1) * (self.QR_WIDE + 1)
        # if (self.PAGESIZE_TEMPLATE == 'L') or (self.PAGESIZE_TEMPLATE == 'legal'):
        #     self.PAGESIZE_TEMPLATE == 'Legal'
        # if (self.PAGESIZE_QR == 'L') or (self.PAGESIZE_QR == 'legal'):
        #     self.PAGESIZE_QR == 'Legal'

    def filter_level_columns(self, df):
        return df.filter(regex='Level')

class PDF(FPDF):
    pass # nothing happens when it is executed.

# A3.....297 x 420 mm
# A4.....210 x 297 mm
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

def get_cfg_from_full_path(path_cfg):
    with open(path_cfg, "r") as ymlfile:
        cfg = yaml.full_load(ymlfile)
    return cfg

def validateDir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def makeBin(bin):
    validateDir(bin)
    dirpath = os.path.abspath(bin)
    return dirpath

def setupPDF(page,QR_or_Template):
    if QR_or_Template == 'QR':
        PAGESIZE = page.PAGESIZE_QR
    else:
        PAGESIZE = page.PAGESIZE_TEMPLATE
    pdf = PDF(orientation='P',unit='mm',format=PAGESIZE) # 'L' landscape
    pdf.set_font(page.FONT, page.STYLE, page.SIZE)
    pdf.set_line_width(0.0)
    makeBin(page.DIR_QR)
    makeBin(page.DIR_PDF)   
    return pdf

def savePDF(pdf,page):
    pdfPath = os.path.join(page.DIR_PDF,page.PDF_NAME+'_Field_Sheet.pdf')
    pdf.output(pdfPath, 'F')

def savePDF_QR(pdf,page):
    pdfPath = os.path.join(page.DIR_PDF,page.PDF_NAME+'_QR_Codes.pdf')
    pdf.output(pdfPath, 'F')

def savePDF_size(pdf,page):
    pdfPath = os.path.join(page.DIR_PDF,page.PDF_NAME+'_Size_Check.pdf')
    pdf.output(pdfPath, 'F')

def color_red(pdf):
    pdf.set_fill_color(255,0,0)
    pdf.set_draw_color(255,0,0)

def color_green(pdf):
    pdf.set_fill_color(0,255,0)
    pdf.set_draw_color(0,255,0)

def color_blue(pdf):
    pdf.set_fill_color(0,0,255)
    pdf.set_draw_color(0,0,255)

def color_black(pdf):
    pdf.set_fill_color(0,0,0)
    pdf.set_draw_color(0,0,0)

def color_gray1(pdf):
    pdf.set_fill_color(100,100,100)
    pdf.set_draw_color(100,100,100)

def color_gray2(pdf):
    pdf.set_fill_color(150,150,150)
    pdf.set_draw_color(150,150,150)

def draw_1cm(pdf,x,y):
    pdf.rect(x,y,10,10, style = 'DF')

def drawMarker(pdf, color, POS, LR, PAGESIZE, PageSizes):
    x, y = PageSizes.xy_drawMarker(POS, LR, PAGESIZE)
        
    if color == 'color':
        color_red(pdf)
        draw_1cm(pdf,x,y)
        color_green(pdf)
        draw_1cm(pdf,x+20,y)
        color_blue(pdf)
        draw_1cm(pdf,x,y+20)
        color_black(pdf)
        draw_1cm(pdf,x+10,y+10)
    elif color == 'gray':
        # color_black(pdf)
        # draw_1cm(pdf,x,y)
        # color_gray1(pdf)
        # draw_1cm(pdf,x+20,y)
        # color_gray2(pdf)
        # draw_1cm(pdf,x,y+20)
        # color_black(pdf)
        # draw_1cm(pdf,x+10,y+10)
        # All black
        color_black(pdf)
        draw_1cm(pdf,x,y)
        color_black(pdf)
        draw_1cm(pdf,x+20,y)
        color_black(pdf)
        draw_1cm(pdf,x,y+20)
        color_black(pdf)
        draw_1cm(pdf,x+10,y+10)

def draw10cm(pdf,POS,SPACE,FONT,STYLE,SIZE,PAGESIZE, PageSizes):
    y = PageSizes.xy_draw10cm(POS, PAGESIZE)

    pdf.set_line_width(1)
    pdf.line(20.4,y,120,y)
    pdf.set_font('Helvetica', 'B', 16)
    pdf.text(35,y-(SPACE/3),''.join(['10cm - ',PAGESIZE]))
    pdf.set_font('Helvetica', 'B', 6)
    if PAGESIZE == 'A5':
        pdf.text(75,y-(SPACE/3),'www.FieldPrism.org')
    else:
        pdf.text(80,y-(SPACE/3),'www.FieldPrism.org')
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_line_width(0)

    #reset syles
    pdf.set_font(FONT, STYLE, SIZE)

   
def draw_credit_card(pdf,x,y,fill):
    if fill:
        pdf.rect(x,y,86,54, style = 'F')
    else:
        pdf.rect(x,y,86,54, style = 'D')

def insertText_credit_card(page,pdf,data,pos, PageSizes):
    x, y = PageSizes.xy_insertText_credit_card(page, pos)

    padding = y+(page.SPACE)
    pdf.text(x, padding, data)

def insertImage(page,pdf,image,x,y):
    pdf.image(image, x = x+7, y = y+3, w = 77, h = 50, type = '', link = '')

def drawMarker_credit_card(text_to_add, page, pdf, fill, POS, LR, PAGESIZE, PageSizes):
    dir_img = os.path.join(os.path.dirname(os.path.dirname(__file__)),'img')
    img_black = os.path.join(dir_img,'FieldPrism_Size_Ckeck_Black.jpg')
    img_white = os.path.join(dir_img,'FieldPrism_Size_Ckeck_White.jpg')
    
    if POS == 'top':
        image = img_white
    elif POS == 'bottom':
        image = img_black

    x, y = PageSizes.xy_drawMarker_credit_card(POS, LR, PAGESIZE)
    
    draw_credit_card(pdf,x,y,fill)
    insertText_credit_card(page,pdf,text_to_add,POS, PageSizes)
    insertImage(page,pdf,image,x,y)
    
    

def generateQRCode(page,QRpath,data,dirLevel):
    qr = qrcode.QRCode(version=page.QR_DENSITY,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=10,border=4)
    qr.add_data(data)
    # qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white",
        image_factory=StyledPilImage, embeded_image_path=dirLevel)

    #img = qr.make_image(fill_color="black", back_color="white")
    img.save(QRpath)

def insertQRCode(page, pdf, QRname, data, POS, PageSizes):
    x, y = PageSizes.xy_insertQRCode(page, POS)
    # if SAVE_QR:
    QRpath = os.path.abspath(os.path.join(page.DIR_QR,QRname+'.png'))
    # else:
        # QRpath = os.path.abspath(os.path.join(DIR_QR,'TEMP.png'))
    generateQRCode(page,QRpath,data)
    pdf.image(QRpath,x,y,30,30)
    if page.SAVE_QR == 0:
        os.remove(QRpath)

def parseData(data): #varNames labels
    max_chars = 60
    max_chars_per_row = 10
    max_rows = 6
    sep = '_'
    sep1 = ':'
    sep2 = '|'
    text = data.split(sep2)

    textToShow = ()

    for i in range(len(text)):
        newLabel = text[i]
        newLabel = newLabel.split(sep1)[1]
        textToShow = textToShow + (newLabel,)

    textToShow_str = textToShow[0]
    # print(len(str(textToShow_str)))

    if len(str(textToShow_str)) > max_chars:
        textToShow_str = textToShow_str[0:max_chars]

    if len(str(textToShow_str)) >= max_chars_per_row:
        # see if splitting along "-" or "_" results in pieces less than 10 chars long
        part = re.split(r'_|-',textToShow_str)
        part_max = max(len(item) for item in part)

        if len(part) <= max_rows:
            if part_max <= max_chars_per_row:
                textToShow = part
            else:
                textToShow = [textToShow_str[i:i+max_chars_per_row] for i in range(0, len(textToShow_str), max_chars_per_row)]
        else:
            textToShow = [textToShow_str[i:i+max_chars_per_row] for i in range(0, len(textToShow_str), max_chars_per_row)]

    return textToShow

def cleanLabelName(labelName):
    sep = '_'
    sep1 = ':'
    sep2 = '|'
    sep3 = '__'
    sep4 = '-'
    sep5 = ''
    # labelName = labelName.replace(' ',sep)
    labelName = labelName.replace('/',sep4)
    labelName = labelName.replace(';',sep)
    labelName = labelName.replace('!',sep5)
    labelName = labelName.replace('@',sep5)
    labelName = labelName.replace('#',sep5)
    labelName = labelName.replace('$',sep5)
    labelName = labelName.replace('%',sep5)
    labelName = labelName.replace('^',sep5)
    labelName = labelName.replace('&',sep5)
    labelName = labelName.replace('*',sep5)
    labelName = labelName.replace('(',sep5)
    labelName = labelName.replace(')',sep5)
    labelName = labelName.replace('+',sep5)
    labelName = labelName.replace('=',sep5)
    labelName = labelName.replace('[',sep5)
    labelName = labelName.replace(']',sep5)
    labelName = labelName.replace('{',sep5)
    labelName = labelName.replace('}',sep5)
    labelName = labelName.replace('"',sep5)
    labelName = labelName.replace('<',sep4)
    labelName = labelName.replace('>',sep4)
    labelName = labelName.replace('?',sep5)
    labelName = labelName.replace('`',sep5)
    labelName = labelName.replace('~',sep5)
    labelName = labelName.replace(',',sep5)
    labelName = labelName.replace('.',sep5)
    return labelName


def compileData(labels,varNames,pageNumber): #varNames labels
    sep = '_'
    sep1 = ':'
    sep2 = '|'
    sep3 = '__'
    sep4 = '-'
    data = ()

    for i in range(len(varNames)):
        if type(varNames[i]) == str:
            labelName = str(varNames[i])
            labelName = cleanLabelName(labelName)
        else:
            if isnan(labels.loc[pageNumber].at[labelName]):
                labelName = str(varNames[i])
            else:
                labelName = str(int(labelName))
                labelName = cleanLabelName(labelName)
            
        if type(labels.loc[pageNumber].at[labelName]) == str:
            label = str(labels.loc[pageNumber].at[labelName])
            label = cleanLabelName(label)
        else:
            if isnan(labels.loc[pageNumber].at[labelName]):
                label = str(labels.loc[pageNumber].at[labelName])
            else:
                label = str(int(labels.loc[pageNumber].at[labelName]))
                label = cleanLabelName(label)
        wholeLabel = (labelName,label)
        wholeLabel = sep1.join(wholeLabel)
        data = data + (wholeLabel,)
    data = sep2.join(data)
    dataMod = data.replace(':',sep)
    dataMod = dataMod.replace(' ',sep)
    QRname = dataMod.replace('|',sep3)
    return data, QRname

def compileDataLevels(labels,varNames,pageNumber): #varNames labels
    sep = '_'
    sep1 = ':'
    sep2 = '|'
    sep3 = '__'
    sep4 = '-'
    data = ()


    if type(varNames) == str:
        labelName = str(varNames)
        labelName = cleanLabelName(labelName)
    else:
        if isnan(labels.loc[pageNumber].at[labelName]):
            labelName = str(varNames)
        else:
            labelName = str(int(labelName))
            labelName = cleanLabelName(labelName)
        
    if type(labels.loc[pageNumber].at[labelName]) == str:
        label = str(labels.loc[pageNumber].at[labelName])
        label = cleanLabelName(label)
    else:
        if isnan(labels.loc[pageNumber].at[labelName]):
            label = str(labels.loc[pageNumber].at[labelName])
        else:
            label = str(int(labels.loc[pageNumber].at[labelName]))
            label = cleanLabelName(label)
    wholeLabel = (labelName,label)
    wholeLabel = sep1.join(wholeLabel)
    data = data + (wholeLabel,)

    data = sep2.join(data)
    dataMod = data.replace(':',sep)
    dataMod = dataMod.replace(' ',sep)
    QRname = dataMod.replace('|',sep3)
    return data, QRname

def insertDataText(page, pdf, data, pos, PageSizes):
    x, y = PageSizes.xy_insertDataText( page, pos)
    
    textToShow = parseData(data)

    for i in range(len(textToShow)):
        padding = y+(i*page.SPACE)
        pdf.text(x, padding, textToShow[i])
    # pdf.text(95, y+SPACE, B)
    # pdf.text(95, y+2*SPACE, C)
    # pdf.text(95, y+3*SPACE, D)
    # pdf.text(95, y+4*SPACE, E)
    
def newPage(page, labels, pdf, varNames, pageNumber, PageSizes):
    if page.QR_LOCATION == "imbed":
        print(f"{bcolors.OKGREEN}       Creating Page {pageNumber + 1} / {labels.shape[0]}{bcolors.ENDC}")
    elif page.QR_LOCATION == "solo":
        print(f"{bcolors.OKGREEN}       Creating Template Page{bcolors.ENDC}")
    pdf.add_page()

    drawMarker(pdf,page.COLOR,'top','left',page.PAGESIZE_TEMPLATE, PageSizes)
    drawMarker(pdf,page.COLOR,'top','right',page.PAGESIZE_TEMPLATE, PageSizes)
    drawMarker(pdf,page.COLOR,'bottom','left',page.PAGESIZE_TEMPLATE, PageSizes)
    drawMarker(pdf,page.COLOR,'bottom','right',page.PAGESIZE_TEMPLATE, PageSizes)

    data,QRname = compileData(labels,varNames,pageNumber)

    if page.QR_LOCATION == "imbed":
        if page.POS == 'both':
            insertQRCode(page,pdf,QRname,data,'top', PageSizes)
            insertQRCode(page,pdf,QRname,data,'bottom', PageSizes)
            draw10cm(pdf,'top',6,page.FONT,page.STYLE,page.SIZE,page.PAGESIZE_TEMPLATE, PageSizes)
            draw10cm(pdf,'bottom',6,page.FONT,page.STYLE,page.SIZE,page.PAGESIZE_TEMPLATE, PageSizes)
            insertDataText(page, pdf, data, 'top', PageSizes)
            insertDataText(page, pdf, data, 'bottom', PageSizes)
        else:
            insertQRCode(page,pdf,QRname,data,page.POS, PageSizes)
            draw10cm(pdf,page.POS,6,page.FONT,page.STYLE,page.SIZE,page.PAGESIZE_TEMPLATE, PageSizes)
            insertDataText(page, pdf, data, page.POS, PageSizes)
    elif page.QR_LOCATION == "solo":
        # insertQRCode(pdf,page.DIR_QR,QRname,page.SAVE_QR,data,'top',page.PAGESIZE_TEMPLATE)
        # insertQRCode(pdf,page.DIR_QR,QRname,page.SAVE_QR,data,'bottom',page.PAGESIZE_TEMPLATE)
        draw10cm(pdf,'top',6,page.FONT,page.STYLE,page.SIZE,page.PAGESIZE_TEMPLATE, PageSizes)
        draw10cm(pdf,'bottom',6,page.FONT,page.STYLE,page.SIZE,page.PAGESIZE_TEMPLATE, PageSizes)
        # insertDataText(page,pdf,data,'top')
        # insertDataText(page,pdf,data,'bottom')


def newPage_size(page, pdf, PageSizes):
    print(f"{bcolors.OKGREEN}       Creating Size Check{bcolors.ENDC}")
    pdf.add_page()
    text_to_add = 'Standard credit card should fit inside the lines with no white space: 86mm. x 54 mm.'
    drawMarker_credit_card(text_to_add, page, pdf,False,'top','left',page.PAGESIZE_TEMPLATE, PageSizes)
    text_to_add = 'Standard credit card should cover all black, except the corner tips: 86mm. x 54 mm.'
    drawMarker_credit_card(text_to_add, page, pdf,True,'bottom','left',page.PAGESIZE_TEMPLATE, PageSizes)
    


def insertDataText_QR(page,pdf,data,TALL,WIDE):
    # A3.....297 x 420 mm  for A4: top:x=95y=23 bottom:x=95y=243
    # A4.....210 x 297 mm  for A4: top:x=95y=23 bottom:x=95y=366

    x = page.PAGE_MARGIN_LEFT + page.QR_TEXT_X + (page.QR_DIM_X + page.QR_BUFFER_X)*WIDE #page.QR_TEXT_X + (page.QR_DIM_X + page.QR_BUFFER_X*WIDE) + (page.QR_DIM_X + page.QR_BUFFER_X)*WIDE
    y = page.PAGE_MARGIN_TOP + page.LABELSHIFT + (page.QR_DIM_Y + page.QR_BUFFER_Y)*TALL #page.LABELSHIFT + (page.QR_DIM_Y + page.QR_BUFFER_Y) + (page.QR_DIM_Y + page.QR_BUFFER_Y)*TALL
    
    textToShow = parseData(data)

    for i in range(len(textToShow)):
        padding = y+(i*page.SPACE)
        pdf.text(x, padding, textToShow[i])

def insertQRCode_QR(page,pdf,QRname,data,TALL,WIDE,dirLevel):
    # A3.....297 x 420 mm 
    # A4.....210 x 297 mm

    x = page.PAGE_MARGIN_LEFT + (page.QR_DIM_X + page.QR_BUFFER_X)*WIDE#(page.QR_DIM_X + page.QR_BUFFER_X*WIDE) + (page.QR_DIM_X + page.QR_BUFFER_X)*WIDE
    y = page.PAGE_MARGIN_TOP + (page.QR_DIM_Y + page.QR_BUFFER_Y)*TALL#(page.QR_DIM_Y + page.QR_BUFFER_Y) + (page.QR_DIM_Y + page.QR_BUFFER_Y)*TALL
    # print(f"x: {x} y: {y}")

    # if SAVE_QR:
    dir_QR_builder = os.path.dirname(os.path.dirname(__file__))
    QRpath = os.path.join(dir_QR_builder,page.DIR_QR,QRname+'.png')
    # else:
        # QRpath = os.path.abspath(os.path.join(DIR_QR,'TEMP.png'))
    generateQRCode(page,QRpath,data,dirLevel)
    pdf.image(QRpath,x,y,page.QR_DIM_X,page.QR_DIM_Y)
    if page.SAVE_QR == 0:
        try:
            os.remove(QRpath)
        except:
            time.sleep(1)
            os.remove(QRpath)
    return x,y

def getLevelDir(page,level):
    sep = ""
    name = ['L',str(level+1),'.jpg']
    dir_QR_builder = os.path.dirname(__file__)
    dirLevel = os.path.join(dir_QR_builder,page.IMG_LEVEL,sep.join(name))
    return dirLevel

def buildCSVpath(fname) -> str:
    splitName = fname.split(".")
    if len(splitName) == 1:
        fname = fname + ".csv"
    else:
        fname = fname
    return fname

def newPage_QR(page, labels, pdf, varNames, PageSizes):
    pdf.add_page()

    indX = 0
    indY = 0
    indPage = 1
    indQR = 0
    print(f"{bcolors.OKGREEN}       Creating QR Codes{bcolors.ENDC}")
    if page.USE_LEVELS == False:
        num_rows = page.LABELS_DF.shape[0]
        for pageNumber in range(num_rows):
            print(f"{bcolors.OKGREEN}              Adding QR Code {pageNumber + 1} / {labels.shape[0]}{bcolors.ENDC}")
            if pageNumber > ((page.QR_TOTAL*indPage)-1):
                indPage += 1
                indX = 0
                indY = 0
                pdf.add_page()

            data,QRname = compileData(labels,varNames,pageNumber)

            insertQRCode_QR(page,pdf,QRname,data,indY,indX)
            insertDataText_QR(page,pdf,data,indY,indX)

            if page.PRINT_ORDER == "col":
                if indY < page.QR_TALL:
                    indY += 1
                elif indY >= page.QR_TALL:
                    indY = 0
                    indX += 1
            elif page.PRINT_ORDER == "row":
                if indX < page.QR_WIDE:
                    indX += 1
                elif indX >= page.QR_WIDE:
                    indX = 0
                    indY += 1
                
    elif page.USE_LEVELS == True:
        num_cols = page.LABELS_DF.shape[1]
        for level in range(num_cols):
            dirLevel = getLevelDir(page,level)
            num_rows = page.LABELS_DF.iloc[:,[level]].dropna().shape[0]
            varName = varNames[level]
            for pageNumber in range(num_rows):
                indQR += 1
                print(f"{bcolors.OKGREEN}              Adding QR Code Level {level+1} Cell {pageNumber + 1} / {num_rows}{bcolors.ENDC}      {indQR}")

                if indQR > (page.QR_TOTAL):
                    indQR = 1
                    indPage += 1
                    indX = 0
                    indY = 0
                    pdf.add_page()

                data,QRname = compileDataLevels(labels.iloc[:,[level]],varName,pageNumber)

                insertQRCode_QR(page,pdf,QRname,data,indY,indX,dirLevel)
                insertDataText_QR(page,pdf,data,indY,indX)

                if page.PRINT_ORDER == "col":
                    if indY < page.QR_TALL:
                        indY += 1
                    elif indY >= page.QR_TALL:
                        indY = 0
                        indX += 1
                elif page.PRINT_ORDER == "row":
                    if indX < page.QR_WIDE:
                        indX += 1
                    elif indX >= page.QR_WIDE:
                        indX = 0
                        indY += 1
            previousLevel = (page.QR_TOTAL*indPage) - pageNumber + indPage

if __name__ == '__main__':
    Size = PageInfo()

    POS = 'top' # 'top' 'bottom' 
    LR = 'right' # 'left' 'right'
    PAGESIZE = 't'
    
    x, y = Size.xy_drawMarker(POS, LR, PAGESIZE)
    print(f'x: {x}')
    print(f'y: {y}')