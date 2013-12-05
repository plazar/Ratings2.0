from rating_classes import multigauss

"""
Single Gaussian component fitting to pulse profiles.

This is just a Multiple Gaussian fit with max_gaussians = 1.
"""

class SingleGaussianProfileClass(multigauss.MultipleGaussianProfileClass):
    data_key = "singlegaussfit"
    
    # The maximum number of Gaussian components to fit
    max_gaussians = 1

    USE_MPFIT = False # The alternative is scipy.optimize.leastsq

