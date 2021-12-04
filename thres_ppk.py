#!/usr/bin/python3

import numpy as np
import scipy
import pandas as pd
from pl0t import *
import seaborn as sns
import matplotlib.pyplot as plt
import proc_cap.Ppk as pcap

def meet_ppk(x, target_Ppk, dist='norm', usl=None, lsl=None, ret_ppk=False):
    '''
    Fit x vector with dist statistical distribution calculate Ppk
    with USL and / or LSL
    return True if Ppk >= target_ppk, False otherwise.
    x: 1D vector
    dist: 'norm' only.
    target_Ppk: minimum required process capability
    usl: Upper Spec Limit
    lsl: Lower Spec Limit
    ret_ppk: if set to True, return (True/False, ppk)
    '''
    ret = True
    if not usl and not lsl:
        raise SyntaxError('LSL and / or USL needed')
    __chk_specs(lsl, usl)
    if target_Ppk <= 0:
        raise SyntaxError('Target Ppk must be stricly superior to 0')
    if dist == 'norm':
        ppk = pcap.norm_ppk(x, usl=usl, lsl=lsl)
        if ppk < target_Ppk:
            ret = False
    else:
        raise SyntaxError('%s statistical law: not supported'% str(dist))
    if ret_ppk:
        return (ret, ppk)
    return ret


def uniform_between(vmin, vmax):
    __must_be_sup(vmin, vmax)
    ret = vmin + scipy.stats.uniform.rvs(size=1) * (vmax - vmin)
    return ret


def thres_norm_ppk(mu_min, mu_max, s_min, s_max,
                             lsl=None, usl=None, mc_draws=10**4):
    '''
    Evaluate normal law Ppk using lsl and usl, 
    with mean in [mu_min, mu_max] and standard
    deviation in [s_min, s_max] picked randomly
    mu_min: minimum mean
    mu_max: maximum mean
    s_min: minimum stdev
    s_max: maximum stdev
    lsl: Lower Specification Limit
    usl: Upper Specification Limit
    '''
    __must_be_sup(lsl, usl)
    i = 0
    r = {}
    while i < mc_draws:
        mu = uniform_between(mu_min, mu_max)[0]
        s = uniform_between(s_min, s_max)[0]
        x = scipy.stats.norm.rvs(loc=mu, scale=s, size=200)
        r[i] = (mu, s, meet_ppk(x, ppk_thres, lsl=lsl, usl=usl, ret_ppk=True)[1])
        i += 1
    ret = pd.DataFrame(r).transpose()
    ret.columns = ('mu', 's', 'Ppk')
    return ret


def plt_ppks(thres_ppk_out):
    '''Plot a flat 3D scatter plot from thres_norm_ppk() output''' 
    cmap = sns.cubehelix_palette(as_cmap=True)
    f, ax = plt.subplots()
    points = ax.scatter(df['mu'], df['s'], c=df['Ppk'], cmap=cmap) 
    f.colorbar(points)
    shw()

    
def upper_norm_std(mu, Ppk, lsl=None, usl=None):
    '''
    Return the maximum standard deviation to meet Ppk 
    with mean mu and specifications limits lsl and usl
    mu: mean
    Ppk: Long Term process capability
    lsl: Lower Specification Limit
    usl: Upper Specification Limit
    '''
    __must_be_sup(lsl, usl)
    nominal = (lsl + usl) / 2
    if mu <= nominal:
        ret = abs(lsl - mu) / (3 * Ppk)
    else:
        ret = abs(usl - mu) / (3 * Ppk)
    return ret


def gen_rnd_gennorm(x_min, x_max, s=None, x_shift=None, smpl_size=200, smpl_nb=50):
    '''
    Return a generalized normal law (type I) fit between bounds mu_min and mu_max
    x_min, x_max: bounds
    s: stdev
    x_shift: step used to shift gaussian from x_min to x_max
    smpl_size: number of samples per random gaussian
    smpl_nb: number of random gaussian to be generated
    '''
    ret = []
    __must_be_sup(x_min, x_max)
    if not s:
        s = (x_max - x_min) / smpl_size
    if not x_shift:
        x_shift = (x_max - x_min) / smpl_nb
    gauss = scipy.stats.norm.rvs(loc=x_min, scale=s, size=smpl_size)
    for shift in np.linspace(0, x_max - x_min, smpl_nb):
        ret += np.ndarray.tolist(gauss + shift)
    return ret


def fit_gennorm(dat, retparm=False, size=1000):
    '''
    Fit dat with generalized normal law and return a pdf vector
    dat: data to be fitted 
    retparm: return fit params if set to True, otherwise return pdf vector
    size: number of points of the returned pdf
    '''
    beta, loc, scale = scipy.stats.gennorm.fit(dat)
    print(beta, loc, scale)
    x = np.linspace(np.min(dat), np.max(dat), size)
    ret = scipy.stats.gennorm.pdf(x, beta=beta, loc=loc, scale=scale)
    #    hist(dat)
    #    lplt(x, y)
    #shw()
    if retparm:
        return (beta, loc, scale)
    else:
        return ret
        

def __must_be_sup(mini, maxi): 
    if mini > maxi:
        raise SyntaxError('minimum must be strictly inferior to maximum')

    
if __name__ == '__main__':
    lsl = 6
    usl = 14
    mu_min = lsl
    mu_max = usl
    s_min = 0.1
    s_max = (usl - lsl) / 3
    ppk_thres = 1.33
    # df = thres_norm_ppk(mu_min, mu_max, s_min, s_max, lsl, usl)
    # plt_ppks(df)
    # x = np.linspace(lsl, usl, 500)
    # lplt(x, crit_s)
    # shw()
    # x = gen_rnd_gennorm(8, 12)
    # y = fit_gennorm(x)
    # lplt(np.linspace(np.min(x), np.max(x), 1000), y)
    # shw()
    # hist(x)
    # shw()
    x = np.linspace(lsl, usl, 200)
    crit_s = []
    for v in x:
        crit_s.append(upper_norm_std(v, ppk_thres, lsl, usl))
    # lplt(x, crit_s)
    # shw()
    r = np.array([])
    for i in range(len(x)):
        mu = x[i]
        s = crit_s[i]
        rnd_dat = scipy.stats.norm.rvs(loc=mu, scale=s, size=200)
        r = np.concatenate((r, rnd_dat))
    print(len(r))
    hist(r)
    shw()
