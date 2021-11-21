#!/usr/bin/python3

import numpy as np

lsl_a = 5
usl_a = 10
lsl_b = 6
usl_b = 12
lsl_c = 15
usl_c = 16

class stkup_dim():

    
    def __init__(self, name, direction, lsl, usl, std_hat=None, Ppk_min=None):
        self.name = name
        self.direction = direction
        if not isinstance(direction, int) or self.direction == 0:
            raise SyntaxError('direction must be a non null signed integer')
        self.__must_be_sup(lsl, usl)
        self.lsl = lsl
        self.usl = usl
        self.std_hat = None
        if std_hat:
            self.std_hat = std_hat
        self.Ppk_min = None
        if Ppk_min:
            self.Ppk_min = Ppk_min
            self.nominal = self.__calc_nominal()

            
    def __must_be_sup(self, mini, maxi):
        if mini >= maxi:
            raise SyntaxError('mini must be strictly inferior to maxi')

        
    def __calc_nom(self):
        self.nominal = (self.lsl + self.usl) / 2

        
class stkup():
    
    
    def __init__(self, *dims):
        '''
        *dims: stkup_dim objects 
        '''
        self.name = ''
        i = 0
        for dim in dims:
            coef = self.__set_name_coef(dim, i)
            self.name += coef + dim.name + ' '
            i += 1
        print(self.name)


    def __set_name_coef(self, dim, i):
        ret = ''
        if dim.direction < -1:
            ret = '- ' + str(abs(dim.direction)) + '*'
        elif dim.direction == -1:
                ret = '- '
        elif dim.direction == 1:
            if i > 0:
                ret = '+ '
            else:
                ret = ''
        else:
            if i > 0:
                ret = '+ ' + str(dim.direction) + '*'
            else:
                ret = str(dim.direction) + '*' 
        return ret 

        
dim_a = stkup_dim('a', -3,  5, 10)
dim_b = stkup_dim('b', 2, 6, 12)
dim_c = stkup_dim('c', -1, 15, 16)
stkup(dim_a, dim_b, dim_c)
