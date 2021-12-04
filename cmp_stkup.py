#!/usr/bin/python3

import numpy as np
from scipy import stats
import pandas as pd
import matplotlib.pyplot as plt
from pl0t import *


class stkup_dim():

    
    def __init__(self, name, direction, lsl, usl, dist='norm',
                 mu_hat=None, std_hat=None, Ppk_min=None,
                 rnd_size = 10**6):
        '''
        Create a stackup dimension object
        name: dimension name
        direction: dimension direction / coefficient
        lsl: Lower Spec Limit
        usl: Upper Spec Limit
        dist: either normal, uniform or generalized normal type 1 statistical distributions.
        mu_hat: estimated mean
        std_hat: estimated standard deviation
        Ppk_min: minimum process capability
        rndm_size: len() of random values
        '''

        self.name = name
        self.direction = direction
        if not isinstance(direction, int) or self.direction == 0:
            raise SyntaxError('direction must be a non null signed integer')
        self.__must_be_sup(lsl, usl)
        self.lsl = lsl
        self.usl = usl
        self.dist = dist
        self.nominal = self.__calc_nom()
        self.mu_hat = None
        self.std_hat = None
        self.Ppk_min = None
        if dist == 'equiprobable':
            if std_hat or Ppk_min:
                raise SyntaxError("Ppk_min, std_hat or mu_hat can\'t be set with equiprobable law")
            self.std_hat = self.__calc_std()
        if std_hat:
            if PPk_min:
                self.__err_ppk_std()
            self.std_hat = std_hat
        if Ppk_min:
            if std_hat:
                self.__err_ppk_std()
            self.Ppk_min = Ppk_min
            self.std_hat = self.__calc_std()
        if not mu_hat:
            self.mu_hat = self.__calc_nom()
        else:
            self.mu_hat = mu_hat

            
    def __must_be_sup(self, mini, maxi):
        if mini >= maxi:
            raise SyntaxError('mini must be strictly inferior to maxi')

        
    def __calc_nom(self):
        return (self.lsl + self.usl) / 2


    def __calc_std(self):
        if self.dist == 'equiprobable':
            ret = np.sqrt((self.usl - self.lsl)**2 / 12)
        elif self.dist == 'norm':
            if self.mu_hat == self.__calc_nom():
                print('off center mean not supported')
                pass
            ret = abs(self.usl - self.nominal) / (3 * self.Ppk_min)
        elif dist == 'gennorm':
            pass
        return ret        

    
    def rndm_scal(self):
        ''' 
        Return a random scalar based on the location / scale given at creation
        '''
        if self.dist == 'norm':
            if not self.mu_hat and not self.std_hat:
                raise SyntaxError('mean and std or Ppk  must be specified to draw random number')
            ret = stats.norm.rvs(loc=self.mu_hat, scale=self.std_hat)
        elif self.dist == 'equiprobable':
            ret = stats.uniform.rvs(loc=self.lsl, scale=self.usl - self.lsl)
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

        
    def get_inputs(self):
        '''
        Return a dataframe with inputs given at creation
        '''
        ret = {'name': [], 'dist': [], 'direction': [],'lsl': [], 'usl': [],
               'nominal': [], 'mu_hat': [], 'std_hat': [],
               'Ppk_min': []}
        for dim in self.dims:
            ret['name'].append(str(dim.name))
            ret['direction'].append(str(dim.direction))
            ret['dist'].append(str(dim.dist))
            ret['lsl'].append(str(dim.lsl))
            ret['usl'].append(str(dim.usl))
            ret['nominal'].append(str(dim.nominal))
            ret['mu_hat'].append(str(dim.mu_hat))
            ret['std_hat'].append(str(dim.std_hat))
            ret['Ppk_min'].append(str(dim.Ppk_min))
        return pd.DataFrame(ret).transpose()
    
                        
    def compare(self, lsl=None, usl=None):
        '''
        Compare different stackup options
        '''
        print('Stackup: %s ' % self.name)
        print('Nominal: %1.3f' % self.nominal)
        print('Worst case - min: %1.3f, max: %1.3f' % self.worst_case())
        tol_ti = self.stats('ti')
        print('Statistical (tolerance interval) - mu %1.3f, s %1.3f' %
              (self.nominal, tol_ti))
        tol_ppk = self.stats('std')
        print('Statistical (std) - mu %1.3f, s %1.3f' %
              (self.nominal, tol_ppk))
        if lsl or usl:
            stat_pop = stats.norm.rvs(loc=self.nominal, scale=tol_ppk, size = 10**4)
            print('Statistical (std) - defects: %6.2f' % 
                  self.calc_dppm(stat_pop, lsl=lsl, usl=usl))
        mc_pop = self.monte_carlo()
        mc_pop_std = np.std(mc_pop)
        mc_pop_mu = np.mean(mc_pop)
        print('Monte Carlo - mu %1.3f, std %1.3f' %
              (mc_pop_mu, mc_pop_std))
        if lsl or usl:
            print('Statistical (Monte Carlo) - defects: %6.2f' % 
                  self.calc_dppm(mc_pop, lsl=lsl, usl=usl))
        
              
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


    def stats(self, stk='std'):
        '''
        return statistical tolerance interval
        stk: either-
             - ti - tolerance interval,
             - std - observed standard deviation, 
        '''
        ret = 0
        for dim in self.dims:
            if stk == 'ti':
                ti = (dim.usl - dim.lsl) / 2
                ret += ti ** 2
            elif stk == 'std':
                ret += dim.std_hat ** 2
            else:
                raise SyntaxError('Unknown statistical stackup: %s' % str(stk))
        return np.sqrt(ret)

    
    def monte_carlo(self, draws = 10**4):
        '''
        Stackup Monte Carlo simulation
        '''
        cnt = 0
        ret = []
        for i in range(draws):
            stk = 0
            for dim in self.dims:
                stk += dim.direction * dim.rndm_scal()
            ret.append(stk)
        return ret


    def calc_dppm(self, pop, lsl=None, usl=None, dist='norm', pval=True):
        '''
        Return total defect occurrence (in dppm) for data using lsl and usl
        pop: sample
        lsl: Lower Specification Limit
        usl: Upper Specification Limit
        dist: distribution to be used (normal)
        pval: if True, assess normality of data with dist
        '''
        ret = 0
        usl_dppm = 0
        lsl_dppm = 0
        if lsl != None and usl != None:
            self.__must_be_sup(lsl, usl)
        if dist == 'norm':
            if pval:
                pass
            mu_hat, std_hat = stats.norm.fit(pop)
            if usl:
                usl_dppm = 1.0 - stats.norm.cdf(usl, loc=mu_hat, scale=std_hat)
            if lsl:
                usl_dppm = 1.0 - stats.norm.cdf(lsl, loc=mu_hat, scale=std_hat)
        else:
            raise SyntaxError('dist not supported')
        ret = (lsl_dppm + usl_dppm) * 10**6
        return ret
                
        
    def __must_be_sup(self, mini, maxi):
        if mini >= maxi:
            raise SyntaxError('mini must be strictly inferior to maxi')
        
                    
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
    stk = stkup(dim_a, dim_b, dim_c)
    stk.compare()
    print(stk.get_inputs())

    dim_a = stkup_dim('a', 1,  5, 10, dist='equiprobable')
    dim_b = stkup_dim('b', 1, 6, 12, Ppk_min=1.0)
    dim_c = stkup_dim('c', -1, 9, 11, Ppk_min=1.5)
    stk = stkup(dim_a, dim_b, dim_c)
    stk.compare(lsl=6, usl=10)
    print(stk.get_inputs())
