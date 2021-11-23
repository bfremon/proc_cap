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
        self.nominal = self.__calc_nom()
        self.mean_hat = None
        self.std_hat = None
        self.Ppk_min = None
        if std_hat:
            if PPk_min:
                self.__err_ppk_std()
            self.std_hat = std_hat
        if Ppk_min:
            if std_hat:
                self.__err_ppk_std()
            self.Ppk_min = Ppk_min
            self.std_hat = self.__calc_std()

            
    def __must_be_sup(self, mini, maxi):
        if mini >= maxi:
            raise SyntaxError('mini must be strictly inferior to maxi')

        
    def __calc_nom(self):
        return (self.lsl + self.usl) / 2


    def __calc_std(self):
        if self.mean_hat:
            print('off center mean not supported')
            pass
        ret = abs(self.usl - self.nominal) / (3 * self.Ppk_min)
        return ret        

    
    def __err_ppk_std(self):
            raise SyntaxError('PPk_min and std_hat can\'t be set at the same time')

        
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
        self.nominal = self.nominal()

        
    def compare(self):
        '''
        Compare different stackup options
        '''
        print('Stackup: %s ' % self.name)
        print('Nominal: %1.3f' % self.nominal)
        print('Worst case - min: %1.3f, max: %1.3f' % self.worst_case())
        tol_ti = self.stats('ti')
        print('Statistical (tolerance interval) - min %1.3f, max %1.3f' %
              (self.nominal - tol_ti, self.nominal + tol_ti))
        tol_ppk = self.stats('std')
        print('Statistical (std) - min %1.3f, max %1.3f' %
              (self.nominal - tol_ppk, self.nominal + tol_ppk))

              
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

    
    def nominal(self):
        '''
        return nominal stakup
        '''
        ret = 0
        for dim in self.dims:
            ret += dim.direction * dim.nominal
        return ret


    def stats(self, type='std'):
        '''
        return statistical tolerance interval
        type: either-
             - ti - tolerance interval,
             - std - observed standard deviation, 
        '''
        ret = 0
        for dim in self.dims:
            if type == 'ti':
                ti = (dim.usl - dim.lsl) / 2
                ret += ti ** 2
            elif type == 'std':
                ret += dim.std_hat ** 2
            else:
                raise SyntaxError('Unknown statistical stackup: %s' % str(type))
        return np.sqrt(ret)

    
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
    dim_a = stkup_dim('a', 1,  5, 10, Ppk_min=1.33)
    dim_b = stkup_dim('b', 1, 6, 12, Ppk_min=1.0)
    dim_c = stkup_dim('c', -1, 9, 11, Ppk_min=1.5)
    stkup(dim_a, dim_b, dim_c).compare()
