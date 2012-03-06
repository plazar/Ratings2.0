import numpy as np

import base
from rating_classes import gaussian


class GaussianSignificanceRater(base.BaseRater):
    short_name = "gausssig"
    long_name = "Gaussian Significance Rating"
    description = "Compute the significance of the best-fit Gaussian. " \
                  "The function being fit is not actually a Gaussian, " \
                  "it's a von Mises distribution (exp(k*cos(theta)))"
    version = 2

    rat_cls = gaussian.GaussianProfileClass()

    def _compute_rating(self, cand):
        """Return a rating for the candidate. The rating value is the
            amplitude of the von Mises function fit to the candidate's 
            profile divided by the RMS of the post-fit residuals.
        
            Input:
                cand: A Candidate object to rate.

            Output:
                value: The rating value.
        """
        nbins = len(cand.profile)
        std = np.sqrt(np.mean(np.var(cand.pfd.profs,axis=-1))) * \
                    np.sqrt(cand.pfd.nsub*cand.pfd.npart)
        return cand.gaussfit.amplitude(nbins) / \
                    (std/np.sqrt(max(cand.gaussfit.fwhm()/(1.0/nbins), 1)))


Rater = GaussianSignificanceRater

