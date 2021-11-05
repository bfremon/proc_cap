#!/usr/bin/env python3.7

from Log import *
import pandas as pd
import numpy as np
from scipy.stats import shapiro, anderson, kstest
import random
import string

set_dbg_lvl(False)

def _prep_dat(x, dist='norm'):
    shp = np.shape(x)
    ret = None
    if len(shp) == 1:
        if shp[0] == 0:
            raise ValueError('Non null data vector needed')
        if dist == 'norm':
            ret = x
        elif dist == 'lognormal':
            ret = np.log(x)
        else:
            raise NotImplementedError
    else:
        ret = {}
        dbg(x.columns)
        for i in x.columns:
            dbg(i)
            if len(x[i]) == 0:
                raise ValueError('Non null data vector needed')
            ret[i] = _prep_dat(x[i], dist=dist)
        ret = pd.DataFrame(ret)
    return ret


def shap_wilk(x, stat=False):
    '''
    Return p-value and test stat (if stat set to True) for x 
    using Shapiro-Wilk test
    '''
    ret = shapiro(x)
    ret = _is_stat_set(stat, ret)
    return ret


def AD(x, dist='norm', stat=False):
    '''
    Return p-value and test stat (if stat set to True) for x 
    using Anderson-Darling test. dist can be used to test for alternate 
    statistical laws
    '''
    # source: https://www.spcforexcel.com/knowledge/basic-statistics/anderson-darling-test-for-normality
    dat = _prep_dat(x, dist)
    AD, crit, sig = anderson(dat, dist=dist)
    if AD >= .6:
        pval = np.exp(1.2937 - 5.709*AD - .0186*(AD**2))
    elif AD >=.34:
        pval = np.exp(.9177 - 4.279*AD - 1.38*(AD**2))
    elif AD >.2:
        pval = 1 - np.exp(-8.318 + 42.796*AD - 59.938*(AD**2))
    else:
        pval = 1 - np.exp(-13.436 + 101.14*AD - 223.73*(AD**2))
    ret = _is_stat_set(stat, (pval, AD))
    return ret


def kolgomorov(x, dist='norm', stat=False):
    '''
    Return p-value and test stat (if stat set to True) for x 
    using Anderson-Darling test. dist can be used to test for alternate 
    statistical laws
    '''
    dat = _prep_dat(x, dist)
    ret = tuple(list(reversed(list(kstest(dat, dist)))))
    ret = _is_stat_set(stat, ret)
    return ret


def norm_test(x, dist='norm', ad=True, kolg=True, shap=True, stat=False):
    ''' 
    Return p-values and test stats (if stat set to True) for x 
    x can be a 1D vector or array of 1D vectors
    '''
    if not ad and not kolg and not shap:
        raise SyntaxError('At least one normality test needed')
    ret = {}
    dat = _prep_dat(x, dist)
    if len(np.shape(dat)) == 1:
        if ad:
            anderson_ret = AD(x, dist=dist, stat=True)
            ret['AD'] = _is_stat_set(stat, anderson_ret)
        if kolg:
            kolg_ret = kolgomorov(x, dist=dist, stat=True)
            ret['kolgomorov'] = _is_stat_set(stat, kolg_ret)
        if shap:
            shap_ret = shap_wilk(x, stat=True)
            ret['shap_wilk'] = _is_stat_set(stat, shap_ret)
    else:
        for v in dat:
            ret[v] = norm_test(dat[v], dist=dist, ad=ad,
                               kolg=kolg, shap=shap, stat=stat)
    return ret


def _is_stat_set(stat, res):
    if len(res) != 2:
        raise SyntaxError('res must have a len equal to 2')
    if stat:
        ret = res
    else:
        ret = res[0]
    return ret
    
if __name__ == '__main__':
    import unittest

    class test_norm_tests(unittest.TestCase):
                                  
        def setUp(self):
            mu = 81.3
            std = 0.1
            multiple_cnt = 10
            self.single = self._gen_norm_series(mu, std, 200, 1, 0.1, 0.1)[0]
            self.multiple = self._gen_norm_series(mu, std, 200, multiple_cnt, 0.1, 0.1)
            self.zero_len = pd.DataFrame({0: (), 1: ()})
            self.cols = [ self._rnd_str() for i in range(multiple_cnt) ]

        def _rnd_sign(self):
            '''
            Return randomly 1 or -1
            '''
            ret = 1
            if random.random() < 0.5:
                ret = -1
            return ret

        def _rnd_mul(self, est, ratio):
            ret = est * (1 + self._rnd_sign() * np.random.uniform() * ratio)
            return ret

        def _rnd_str(self, chars_nb=8):
            ret = ''
            for i in range(chars_nb):
                idx = int(random.random() * len(string.ascii_letters))
                ret += string.ascii_letters[idx]
            return ret
                
        def _gen_norm_series(self, mu, std, nsamples, nseries, mu_ratio, std_ratio):
            '''
            return nseries of nsamples randomly drawned from normal law 
            with mu and std as estimators 
            mu_ratio and std_ratio are max ratios used to shift randomly mu and std
            '''
            d = {}
            for i in range(nseries):
                m = self._rnd_mul(mu, mu_ratio)
                s = self._rnd_mul(std, std_ratio)
                d[i] = np.random.normal(m, s, nsamples)
            ret = pd.DataFrame(d)
#            ret = ret.melt()
#            ret.columns = ('cat', 'val')
            return ret

        def test__prep_dat(self):
            self.assertRaises(ValueError, _prep_dat, ())
            self.assertRaises(ValueError, _prep_dat, self.zero_len)
            r = _prep_dat(self.multiple)
            self.assertTrue(np.shape(r)[0] == 200)
            self.assertTrue(np.shape(r)[1] == 10)
        
        def test_is_stat_set(self):
            st = True
            res = (1, 2)
            self.assertRaises(SyntaxError, _is_stat_set, st, (1, 2, 3))
            self.assertTrue(_is_stat_set(st, res) == res)
            self.assertTrue(_is_stat_set(False, res) == res[0])
        
        def test_shap_wilk(self):
            r = shap_wilk(self.single, stat=False)
            self.assertTrue(isinstance(r, float))
            self.assertTrue(0 <= r <= 1)
            r = shap_wilk(self.single, stat=True)
            self.assertTrue(isinstance(r, tuple))
            
        def test_AD(self):
            r = AD(self.single, stat=False)
            self.assertTrue(isinstance(r, float))
            self.assertTrue(0 <= r <= 1)
            r = AD(self.single, stat=True)
            self.assertTrue(isinstance(r, tuple))
            self.assertRaises(NotImplementedError, AD, self.single, dist='weibull')
                    
        def test_kolgomorov(self):
            r = kolgomorov(self.single, stat=False)
            self.assertTrue(isinstance(r, float))
            self.assertTrue(0 <= r <= 1)
            r = kolgomorov(self.single, stat=True)
            self.assertTrue(isinstance(r, tuple))
            self.assertRaises(NotImplementedError, AD, self.single, dist='weibull')

        def test_norm_test(self):
            self.assertRaises(NotImplementedError, norm_test, self.single, dist='weibull')
            self.assertRaises(SyntaxError, norm_test, self.single,
                              ad=False, kolg=False, shap=False)
            
            r = norm_test(self.single, stat=False)
            self.assertTrue(len(r) == 3)
            for v in r.keys():
                self.assertTrue(isinstance(r[v], np.float))
            r = norm_test(self.single, stat=True)
            self.assertTrue(len(r) == 3)
            for v in r.keys():
                self.assertTrue(len(r[v]) == 2)
            r = norm_test(self.multiple, stat=False)
            self.assertTrue(len(r) == len(self.multiple.columns))
            for col in r.keys():
                self.assertTrue(len(r[col]) == 3)
            r = norm_test(self.multiple, stat=True)
            self.assertTrue(len(r) == len(self.multiple.columns))
            for col in r.keys():
                self.assertTrue(len(r[col]) == 3)
                for test in r[col]:
                    self.assertTrue(len(r[col][test]) == 2)
                    
            self.multiple.columns = self.cols
            r = norm_test(self.multiple, stat=False)
            self.assertTrue(len(r) == len(self.multiple.columns))
            self.assertTrue(list(r.keys()) == self.cols)
            for col in r.keys():
                self.assertTrue(len(r[col]) == 3)
            r = norm_test(self.multiple, stat=True)
            self.assertTrue(len(r) == len(self.multiple.columns))
            for col in r.keys():
                self.assertTrue(len(r[col]) == 3)
                for test in r[col]:
                    self.assertTrue(len(r[col][test]) == 2)
            
    unittest.main()
