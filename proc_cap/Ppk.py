#!/usr/bin/env python3

from pl0t import *
import scipy
import numpy as np
import Log
import random
import string
import pandas as pd

def norm(x, lsl = None, usl = None):
    '''
    Return Ppk with normal law
    x: 1D sample vector
    lsl: Lower Specification Limit
    usl: Upper Specification Limit
    '''
    ret = 0.0
    if not lsl and not usl:
        raise SyntaxError('LSL and / or USL needed')
    if lsl > usl:
        raise SyntaxError('LSL must be stricly inferior to USL')
    mu, std = scipy.stats.norm.fit(x)
    if lsl and not usl:
        ret = PpX(mu, std, lsl)
    elif not lsl and usl:
        ret = PpX(mu, std, usl)
    else:
        ret = Ppk(mu, std, lsl, usl) 
    return ret

def PpX(mu, std, spec, mul = 3):
    '''
    Return Long Term Process Capability on spec
    mu: mean of normal fitted data
    std: std of normal fitted data
    spec: specification limit (can be Lower or Upper)
    mul: 6 sigma multiplier
    '''
    ret = np.abs(mu - spec) / (mul * std)
    return ret

def Ppk(mu, std, usl, lsl, mul = 3):
    '''
    Return Long Term Process Capability
    mu: mean of normal fitted data
    std: std of normal fitted data
    lsl: Lower Specification Limit
    usl: Upper Specification Limit
    mul: 6 sigma multiplier
    '''
    PpU = PpX(mu, std, usl)
    PpL = PpX(mu, std, lsl)
    if PpU >= PpL:
        return PpL
    return PpU

def Ppk2ppm(ppk):
    pass

def batch_ppk(dat, cat, val, lsl, usl, mul=3, dist='norm'):
    ret = {}
    if dist == 'norm':
        for c in dat[cat].unique():
            x = dat[dat[cat] == c]['value']
            ret[c] = norm(x, lsl=lsl, usl=usl)
    else:
        raise NotImplementedError
    ret = pd.DataFrame(list(ret.items()))
    ret.columns = ('cat', 'Ppk')  
    return ret


def plt_ppk(dat, cat, val, lsl, usl, outfile, ppk_target=None, dist='norm'):
    ppks = batch_ppk(dat=dat, cat=cat, val=val, lsl=lsl, usl=usl)
    fig, axes = plt.subplots(1,2, sharey=False)
    ind(ppks, cat='cat', val='Ppk', ax=axes[0])
    if ppk_target:
        vline(ppk_target, color='b', linestyle='--', ax=axes[0])
    bplt('variable', 'value', pop, ax=axes[1])
    vline(usl, color='r', linestyle='--', ax=axes[1])
    vline(lsl, color='r', linestyle='--', ax=axes[1])
    save(outfile, dpi=1200)
 

if __name__ == '__main__':

    def gen_rand_norm_pop(mu, std, nval=200, nsamples=50, noise=0.3):
        ret = {}
        for i in range(nsamples):
            sample_name = rnd_str()
            s = std + rnd_sign() * noise * np.random.uniform()
            m = mu + rnd_sign() * noise * np.random.uniform()
            x = s * np.random.normal(size=nval) + m
            ret[sample_name] = x
        return ret
    
    def rnd_sign():
        if  np.random.uniform() > 0.5:
            return 1
        return -1
    
    def rnd_str(str_len=8):
        ret = ''
        for k in range(str_len):
            ret += random.choice(string.ascii_lowercase)
        return ret

    pop = pd.DataFrame(gen_rand_norm_pop(20, 1, noise=0.2, nsamples=150)).melt()
  
    plt_ppk(pop, 'variable', 'value', 4, 30, 'PPk', ppk_target=0.9)
    # save('Ppk' , transparent=False)
