#!/usr/bin/python3

import numpy as np
import scipy
from statsmodels import distributions
from pl0t import *
import ppf_scale
import norm_tests

np.random.seed(1)

norm_x = np.random.normal(100, 10, 20)

def calc_pplot_stats(x, dist='norm',ptype='percent', alpha=0.05):
    '''
    Plot probability plot of x fitted with dist statistical law
    x: column vector
    dist: statistical law
    ptype: percentile, quantile or 
    alpha: confidence
    '''
    allowed_dists = ['norm']
    x_shape = np.shape(x)
    if x_shape[0] < 5:
        raise InputError('Not enough value in x')
    if len(x_shape) > 1:
        raise InputError('Only column vectors are allowed')
    # https://support.minitab.com/en-us/minitab/18/help-and-how-to/quality-and-process-improvement/quality-tools/how-to/individual-distribution-identification/methods-and-formulas/probability-plot/
    # https://www.storyofmathematics.com/normal-probability-plot
    #     
    ret = {}
    x.sort()    
    exp_prob = distributions.empirical_distribution.ECDF(x)(x)
    if dist == 'norm':
        loc, scale = scipy.stats.norm.fit(x)
        pffit = scipy.stats.norm(loc=loc,scale=scale)
        th_x = np.linspace(x.min(), x.max(), 10)
        th_prob = pffit.cdf(th_x)
    ret['dist'] = dist
    ret['exp_x'] = x
    ret['exp_prob'] = exp_prob
    ret['th_x'] = th_x
    ret['th_prob'] = th_prob
    pvals = norm_tests.norm_test(x, dist=dist)
    for k in pvals:
        pkey = 'pval_' + k 
        ret[pkey] = pvals[k]
    return ret


def plt_norm(vec):
    # ax = plt.subplot(111)
    # ax.plot(vec['exp_x'], vec['exp_prob'], 'go', alpha=0.7, markersize=5)
    # ax.plot(vec['th_x'], vec['th_prob'],'-',label='mean: {:.2f}'.format(vec['mean_hat']))
    # ax.set_yscale('ppf')
    # ax.set_ylim(0.001, 0.999)
    # ax.grid(True)
    # ax.legend(loc=0)
    # plt.show()
    g = lplt(vec['th_x'], vec['th_prob'], color='coral')
    g.set_ylim(0.001, 0.999)
    g.set_yscale('ppf')
    scat(vec['exp_x'], vec['exp_prob'], alpha=1.0, size=8, ax=g)
    pval_xpos = np.min(vec['exp_x']) + 0.015 * (np.max(vec['exp_x']) - np.min(vec['exp_x']))
    plt.text(pval_xpos, 0.985,
             'AD: {0:1.3f}\nKolg: {1:1.3f}\nShap-Wilk: {2:1.3f}'.format(vec['pval_AD'],
                                                                        vec['pval_kolgomorov'],
                                                                        vec['pval_shap_wilk']))
    shw()
    
def calc_pi(rank):
    '''
    Calculate cumulative probability associated with each value in rank
    '''
    # a = float(3/8)
    # if len(rank) <= 10:
    #     a = 0.5
    # return (rank - a) / (len(rank) + 1 - 2 * a)
    return (rank - 0.3) / (len(rank) + 0.4)

def normalize(x):
    ''' 
    Normalize x between 0 and 1
    '''
    return (x - np.min(x)) / (np.max(x) - np.min(x))


def denormalize(unit_v, norm_v):
    ''' 
    Scale unit_v (values in [0;1]) to norm_v scale
    '''
    if np.max(unit_v) > 1 or np.min(unit_v) < 0:
        raise InputError('unit_v values should be in [0, 1]')
    return np.array(unit_v) * (np.max(norm_v) - np.min(norm_v)) + np.min(norm_v)


def plt_normality_line(x, g, centiles=None, alpha=0.05):
    '''
    Fit x with gaussian func and plot 1 - alpha confidence interval on graph g
    x: column vector
    g: graph to be used
    centiles: centiles
    alpha: confidence
    '''
    mu_hat, s_hat = scipy.stats.norm.fit(x)
    if centiles == None:
        centiles = np.arange(0.1, 1.0, 0.1)
        centiles = np.append(centiles, [0.01, 0.05, 0.95, 0.99])
    z_score = scipy.stats.norm.ppf(centiles)
    norm_z_score = normalize(z_score)
    #    print(denormalize(x_percents, x))
    #    scat(x_percents, norm_z_score, color='r')
    #    scat(denormalize(x_percents, x), norm_z_score, color='r')
    scat(denormalize(centiles, x),  norm_z_score, color='r')

    
def norm_henry(x):
    '''
    Return points corresponding to the normal Henry line for x
    25 % and 75 % quantiles are used to calculate the line equation
    x: column vector
    '''
    q = np.array([0.25, 0.75])
    x1 = np.quantile(x, q)
    y1 = scipy.stats.norm.ppf(q)
    slope = np.diff(y1) / np.diff(x1)
    intercept = y1[1] - slope * x1[1]
    return slope * x + intercept
    
    
r = calc_pplot_stats(norm_x)
plt_norm(r)
