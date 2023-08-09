#!/usr/bin/env python3

import os
import sys
import pandas as pd
import scipy
import numpy as np
import matplotlib.pyplot as plt
from pl0t import *
import Ppk
import norm_tests


def gen_pops(lsl, usl, n_pops, n_vals, rand_var = True):
    '''
    Generate n_pops populations of n_vals with a random mean and sd
    within roughly usl - lsl range if rand_var is true, more homogeneous
    stdev is rand_var = False
    '''
    ret = {}
    for i in range(n_pops):
        sd_pop = (usl - lsl) / n_vals 
        if rand_var:
            sd_pop *= np.random.random()
        mu_pop = lsl + np.random.random() * (usl - lsl) 
        vals = scipy.stats.norm.rvs(mu_pop, sd_pop, n_vals)
        ret[i] = vals
    ret = pd.DataFrame(ret).melt()
    return ret


def overall_sd(data):
    '''Return overall stdev (a.k.a pooled variance, or arithmetic 
    mean of individual samples stdev'''
    ret = []
    for pop in data['variable'].unique():
        ret.append(np.std(data[ data['variable'] == pop ]))
    return np.mean(ret)


def samples_normality(data):
    '''Return p-value for Anderson-Darling normality test 
    for category in data['variable']
    '''
    ret = {}
    for smpl in data['variable'].unique():
        x = data[ data['variable'] == smpl]['value']
        ret[smpl] = norm_tests.norm_test(x, 'norm', stat = False)['AD']
    return ret


def chk_norm_pvals(pvals, thres = 0.05):
    ret = False
    mask = ( np.array(list(pvals)) < thres )
    if True in mask:
        ret = True
    return ret


def equal_variances(data):
    '''Return p-value from Levene's test equal variance
    for categories in data[variable]
    '''
    samples = []
    for smpl in data['variable'].unique():
        samples.append(data[ data['variable'] == smpl]['value'].to_list())
    stat, p = scipy.stats.levene(*samples)
    return p


def calc_ppk(smpl, lsl, usl, sd = None):
    if sd is None:
        mu, sd_pop = scipy.stats.norm.fit(smpl)
    else:
        mu = np.mean(smpl)
        sd_pop = sd
    ret = Ppk.Ppk(mu, sd_pop, lsl, usl)
    return ret

    
lsl = 25
usl = 30
pop = gen_pops(lsl, usl, 16, 100, False)
bplt('value', 'variable', pop, orient = 'vertical')
hline(25)
hline(30)
xtitle('Pseudo-cavity')
ytitle('Random dim (mm)')
title('Random dim for different pseudo-cavities')
save('pseudo-pop')
clr()

norm_pvals = samples_normality(pop)
if not chk_norm_pvals(norm_pvals.values()):
    print('One of the sample is not normal')
    
x = [ i for i in sorted(norm_pvals) ]
y = [ norm_pvals[i] for i in x ]
scat(x = x, y = y)
xtitle('Pseudo-cavity')
ytitle('Anderson-Darling normality test p-value')
hline(0.05)
save('norm_pvals')
clr()

print('Pooled std (a.k.a overall std): %2.3f' % overall_sd(pop))
# for smpl in pop['variable'].unique():
#     dat = pop[ pop['variable'] == smpl ]
#     print(np.var(dat['value'], ddof = 1))
    
print('Equal variance (p > 0.05): %1.3f' % equal_variances(pop))

for smpl in pop['variable'].unique():
    dat = pop [ pop['variable'] == smpl ]
    print(calc_ppk(dat, lsl, usl))
