#!/usr/bin/python3

import numpy as np
import scipy.stats as stats
from matplotlib import scale as mscale
from matplotlib import transforms as mtransforms
from matplotlib.ticker import Formatter, Locator

# Adapted from :
# https://matplotlib.org/stable/gallery/scales/custom_scale.html
# https://stackoverflow.com/questions/31174139/python-recreate-minitab-normal-probability-plot?noredirect=1&lq=1

class PPFScale(mscale.ScaleBase):
    name = 'ppf'

    def __init__(self, axis, thresh=1 * 10**(-4), **kwargs):
        if thresh < 0.0 or thresh > 1.0:
            raise ValueError('thresh must be in [0; 1]')
        self.thresh = thresh
        mscale.ScaleBase.__init__(self, axis=axis, **kwargs)

        
    def get_transform(self):
        return self.PPFTransform()

    
    def set_default_locators_and_formatters(self, axis):
        class PercFormatter(Formatter):
            def __call__(self, x, pos=None):
                # \u00b0 : degree symbol
                return "%2.1f %%" % (x*100)

        class PPFLocator(Locator):
            def __call__(self):
                return np.array([0.1, 0.5, 1, 5, 10, 20, 30, 40,
                                 50, 60, 70, 80, 90, 95, 99, 99.5, 99.9]) / 100.0

        axis.set_major_locator(PPFLocator())
        axis.set_major_formatter(PercFormatter())
        axis.set_minor_formatter(PercFormatter())

        
    def limit_range_for_scale(self, vmin, vmax, minpos):
#        return max(vmin, -self.thresh), min(vmax, 1 - self.thresh)
        return max(vmin, 1e-6), min(vmax, 1-1e-6)

    
    class PPFTransform(mtransforms.Transform):
        input_dims = 1
        output_dims = 1
        is_separable = True

        
        def ___init__(self, thresh):
            mtransforms.Transform.__init__(self)
            self.thresh = thresh

            
        def transform_non_affine(self, a):
            out = stats.norm.ppf(a)
            return out

        
        def inverted(self):
            return PPFScale.IPPFTransform()

        
    class IPPFTransform(mtransforms.Transform):
        input_dims = 1
        output_dims = 1
        is_separable = True

        
        def transform_non_affine(self, a):
            return stats.norm.cdf(a)

        
        def inverted(self):
            return PPFScale.PPFTransform()

        
mscale.register_scale(PPFScale)
