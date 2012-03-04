import numpy as np
import base
from rating_classes import multigauss

class MultiGaussGoodnessOfFitRater(base.BaseRater):
    short_name = "multigauss_goodness"
    long_name = "Multi-Gauss Goodness of Fit"
    description = "Fit the profile with multiple Gaussians and " \
                  "report the goodness of the fit (reduced " \
                  "chi-square."
    version = 1

    rat_cls = multigauss.MultipleGaussianProfileClass()

    def _compute_rating(self, cand):
        """
        """
        profile = cand.profile.copy()
        profile /= np.sqrt(cand.pfd.varprof)
        profile -= profile.mean()
        nbins = len(profile)
        mgauss = cand.multigaussfit
        return mgauss.get_chisqr(profile)/mgauss.get_dof(nbins)

Rater = MultiGaussGoodnessOfFitRater

