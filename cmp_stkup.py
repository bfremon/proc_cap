#!/usr/bin/python3

import numpy as np

lsl_a = 5
usl_a = 10
lsl_b = 6
usl_b = 12
lsl_c = 15
usl_c = 16

class stkup_dim():

    
    def __init__(self, name, direction, lsl, usl,
                 mu_hat=None, std_hat=None, Ppk_min=None):
        '''
        Create a stackup dimension object
        name: dimension name
        direction: dimension direction / coefficient
        lsl: Lower Spec Limit
        usl: Upper Spec Limit
        mu_hat: estimated mean
        std_hat: estimated standard deviation
        Ppk_min: minimum process capability
        '''

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
        self.dims = dims

        
    def compare(self):
        '''
        Compare different stackup options
        '''
        print('Stackup: %s ' % self.name)
        print('Worst case - min: %1.3f, max: %1.3f' % self.worst_case())


    def worst_case(self):
        '''
        Worst case stackup
        '''
        mini = 0
        maxi = 0
        for dim in self.dims:
            if dim.direction > 0:
                mini += dim.direction * dim.lsl
                maxi += dim.direction * dim.usl
            else:
                mini += dim.direction * dim.usl
                maxi += dim.direction * dim.lsl
        return (mini, maxi)
    
                
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

if __name__ == '__main__':
    dim_a = stkup_dim('a', 1,  5, 10)
    dim_b = stkup_dim('b', 1, 6, 12)
    dim_c = stkup_dim('c', -1, 9, 11)
    stkup(dim_a, dim_b, dim_c).compare()
