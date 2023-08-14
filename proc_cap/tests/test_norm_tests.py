#!/usr/bin/env python3

from scipy import stats
import numpy as np
import pandas as pd
import unittest
import random
import string
from proc_cap import norm_tests

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
        self.assertRaises(ValueError, norm_tests._prep_dat, ())
        self.assertRaises(ValueError, norm_tests._prep_dat, self.zero_len)
        r = norm_tests._prep_dat(self.multiple)
        self.assertTrue(np.shape(r)[0] == 200)
        self.assertTrue(np.shape(r)[1] == 10)

        
    def test_is_stat_set(self):
        st = True
        res = (1, 2)
        self.assertRaises(SyntaxError, norm_tests._is_stat_set, st, (1, 2, 3))
        self.assertTrue(norm_tests._is_stat_set(st, res) == res)
        self.assertTrue(norm_tests._is_stat_set(False, res) == res[0])

        
    def test_shap_wilk(self):
        r = norm_tests.shap_wilk(self.single, stat=False)
        self.assertTrue(isinstance(r, float))
        self.assertTrue(0 <= r <= 1)
        r = norm_tests.shap_wilk(self.single, stat=True)
        self.assertTrue(isinstance(r, tuple))

        
    def test_AD(self):
        r = norm_tests.AD(self.single, stat=False)
        self.assertTrue(isinstance(r, float))
        self.assertTrue(0 <= r <= 1)
        r = norm_tests.AD(self.single, stat=True)
        self.assertTrue(isinstance(r, tuple))
        self.assertRaises(NotImplementedError, norm_tests.AD, self.single, dist='weibull')

        
    def test_kolgomorov(self):
        r = norm_tests.kolgomorov(self.single, stat=False)
        self.assertTrue(isinstance(r, float))
        self.assertTrue(0 <= r <= 1)
        r = norm_tests.kolgomorov(self.single, stat=True)
        self.assertTrue(isinstance(r, tuple))
        self.assertRaises(NotImplementedError, norm_tests.kolgomorov, self.single, dist='weibull')

        
    def test_norm_test(self):
        self.assertRaises(NotImplementedError, norm_tests.norm_test, self.single, dist='weibull')
        self.assertRaises(SyntaxError, norm_tests.norm_test, self.single,
                          ad=False, kolg=False, shap=False)
            
        r = norm_tests.norm_test(self.single, stat=False)
        self.assertTrue(len(r) == 3)
        for v in r.keys():
            print(r[v])
            self.assertTrue(isinstance(r[v], np.float))
        r = norm_tests.norm_test(self.single, stat=True)
        self.assertTrue(len(r) == 3)
        for v in r.keys():
            self.assertTrue(len(r[v]) == 2)
        r = norm_tests.norm_test(self.multiple, stat=False)
        self.assertTrue(len(r) == len(self.multiple.columns))
        for col in r.keys():
            self.assertTrue(len(r[col]) == 3)
        r = norm_tests.norm_test(self.multiple, stat=True)
        self.assertTrue(len(r) == len(self.multiple.columns))
        for col in r.keys():
            self.assertTrue(len(r[col]) == 3)
            for test in r[col]:
                self.assertTrue(len(r[col][test]) == 2)
                    
        self.multiple.columns = self.cols
        r = norm_tests.norm_test(self.multiple, stat=False)
        self.assertTrue(len(r) == len(self.multiple.columns))
        self.assertTrue(list(r.keys()) == self.cols)
        for col in r.keys():
            self.assertTrue(len(r[col]) == 3)
        r = norm_tests.norm_test(self.multiple, stat=True)
        self.assertTrue(len(r) == len(self.multiple.columns))
        for col in r.keys():
            self.assertTrue(len(r[col]) == 3)
            for test in r[col]:
                self.assertTrue(len(r[col][test]) == 2)

    
unittest.main()

