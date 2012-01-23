import numpy as np
import base
from rating_classes import multivonmises

class MultiVonMisesGoodnessOfFitRater(base.BaseRater):
    short_name = "multivonmises_goodness"
    long_name = "Multi-vonMises Goodness of Fit"
    description = "Fit the profile with multiple von Mises components " \
                  "and report the goodness of the fit (reduced " \
                  "chi-square."
    version = 1

    rat_cls = multivonmises.MultipleVonMisesProfileClass()

    def _compute_rating(self, cand):
        """
        """
        profile = cand.profile.copy()
        profile /= np.sqrt(cand.pfd.varprof)
        profile -= profile.mean()
        nbins = len(profile)
        vm = cand.multivonmisesfit
        return vm.get_chisqr(profile)/vm.get_dof(nbins)

Rater = MultiVonMisesGoodnessOfFitRater

