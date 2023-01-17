from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class PageInfo:
    # dimension in mm
    A5_x: int = 148
    A5_y: int = 210

    A4_x: int = 210
    A4_y: int = 297

    A3_x: int = 297
    A3_y: int = 420

    Tabloid_x: int = 279
    Tabloid_y: int = 432

    Letter_x: int = 216
    Letter_y: int = 279

    Legal_x: int = 216
    Legal_y: int = 356

    A5: list[str] = field(init=False,default_factory=list)
    A4: list[str] = field(init=False,default_factory=list)
    A3: list[str] = field(init=False,default_factory=list)
    Tabloid: list[str] = field(init=False,default_factory=list)
    Letter: list[str] = field(init=False,default_factory=list)
    Legal: list[str] = field(init=False,default_factory=list)

    def __post_init__(self) -> None:
        self.A5 = [self.A5_x, self.A5_y]
        self.A4 = [self.A4_x, self.A4_y]
        self.A3 = [self.A3_x, self.A3_y]
        self.Tabloid = [self.Tabloid_x, self.Tabloid_y]
        self.Letter = [self.Letter_x, self.Letter_y]
        self.Legal = [self.Legal_x, self.Legal_y]

    def get_dim(self, PAGESIZE):
        if PAGESIZE == 'A3':
            dim = self.A3
            dim_x = dim[0]
            dim_y = dim[1]
            return dim_x, dim_y
        elif PAGESIZE == 'A4':
            dim = self.A4
            dim_x = dim[0]
            dim_y = dim[1]
            return dim_x, dim_y
        elif PAGESIZE == 'A5':
            dim = self.A5
            dim_x = dim[0]
            dim_y = dim[1]
            return dim_x, dim_y
        elif PAGESIZE in ['Legal', 'legal', 'L']:
            dim = self.Legal
            dim_x = dim[0]
            dim_y = dim[1]
            return dim_x, dim_y
        elif PAGESIZE in ['Letter', 'letter', 'LETTER']:
            dim = self.Letter
            dim_x = dim[0]
            dim_y = dim[1]
            return dim_x, dim_y
        elif PAGESIZE in ['Tabloid', 'tabloid', 'TABLOID','t','T']:
            dim = self.Tabloid
            dim_x = dim[0]
            dim_y = dim[1]
            return dim_x, dim_y
        elif PAGESIZE == 'Custom':
            dim = self.A4
            dim_x = dim[0]
            dim_y = dim[1]
            return dim_x, dim_y

    def xy_drawMarker(self, POS, LR, PAGESIZE):
        constant_x = 50
        constant_y = 54
        x_init_top = 20
        y_init_top = 23  

        dim_x, dim_y = self.get_dim(PAGESIZE)

        y_pagesize = dim_y - y_init_top - constant_y
        y_init_bottom = y_init_top + y_pagesize

        if POS == 'top':
            y = y_init_top
        elif POS == 'bottom':
            y = y_init_bottom
        
        x_pagesize = dim_x - x_init_top - constant_x
        x_init_bottom = x_init_top + x_pagesize
        
        if LR == 'left':
            x = x_init_top
        elif LR == 'right':
            x = x_init_bottom
        
        return x, y
    
    def xy_draw10cm(self, POS, PAGESIZE):
        '''
            A5_x: int = 148
            A5_y: int = 210

            A4_x: int = 210
            A4_y: int = 297
        '''
        y_init_top = 55
        constant_y = 22

        dim_x, dim_y = self.get_dim(PAGESIZE)

        y_pagesize = dim_y - y_init_top - constant_y

        y_init_bottom = y_init_top + y_pagesize

        if POS == 'top':
            y = y_init_top
        elif POS == 'bottom':
            y = y_init_bottom

        return y

    def xy_insertText_credit_card(self, page, pos):
        x = 20
        y_init_top = 80
        constant_y = 97

        dim_x, dim_y = self.get_dim(page.PAGESIZE_TEMPLATE)

        y_pagesize = dim_y - y_init_top - constant_y
        y_init_bottom = y_init_top + y_pagesize
        
        if pos == 'top':
            y = y_init_top + page.LABELSHIFT
        elif pos == 'bottom':
            y = y_init_bottom + page.LABELSHIFT

        return x, y

    def xy_drawMarker_credit_card(self, POS, LR, PAGESIZE):
        x_init_top = 20
        y_init_top = 28
        constant_x = 50
        constant_y = 149

        dim_x, dim_y = self.get_dim(PAGESIZE)

        y_pagesize = dim_y - y_init_top - constant_y
        y_init_bottom = y_init_top + y_pagesize

        if POS == 'top':
            y = y_init_top
        elif POS == 'bottom':
            y = y_init_bottom
        
        x_pagesize = dim_x - x_init_top - constant_x
        x_init_bottom = x_init_top + x_pagesize
        
        if LR == 'left':
            x = x_init_top
        elif LR == 'right':
            x = x_init_bottom

        return x, y
    '''
        A5_x: int = 148
        A5_y: int = 210

        A4_x: int = 210
        A4_y: int = 297

        A3_x: int = 297
        A3_y: int = 420

        Tabloid_x: int = 279
        Tabloid_y: int = 432

        Letter_x: int = 216
        Letter_y: int = 279

        Legal_x: int = 216
        Legal_y: int = 356
    '''
    def xy_insertDataText(self, page, pos):
        x = 95
        y_init_top = 23
        constant_y = 54

        dim_x, dim_y = self.get_dim(page.PAGESIZE)

        y_pagesize = dim_y - y_init_top - constant_y
        y_init_bottom = y_init_top + y_pagesize
        
        if pos == 'top':
            y = y_init_top + page.LABELSHIFT
        elif pos == 'bottom':
            y = y_init_bottom + page.LABELSHIFT

        return x, y

    def xy_insertQRCode(self, page, POS):
        x = 95
        y_init_top = 23
        constant_y = 54

        dim_x, dim_y = self.get_dim(page.PAGESIZE)

        y_pagesize = dim_y - y_init_top - constant_y
        y_init_bottom = y_init_top + y_pagesize

        if POS == 'top':
            y = y_init_top
        elif POS == 'bottom':
            y = y_init_bottom
        
        return x, y