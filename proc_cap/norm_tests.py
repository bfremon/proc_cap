#!/usr/bin/env python3

from Log import *
import pandas as pd
import numpy as np
from scipy.stats import shapiro, anderson, kstest, normaltest
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


def omnibus(x, stat = False):
    '''
    Return p-value and test stat (if stat set to True) for x
    to determine if x differs from a normal law (conservative skewness)
    '''
    ret = list(reversed(normaltest(x)))
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
    using kolgomorov test. dist can be used to test for alternate 
    statistical laws
    '''
    dat = _prep_dat(x, dist)
    ret = tuple(list(reversed(list(kstest(dat, dist)))))
    ret = _is_stat_set(stat, ret)
    return ret


def batch(x, dist='norm', ad=True, kolg=True, shap=True, stat=False):
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
            ret[v] = batch(dat[v], dist=dist, ad=ad,
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

