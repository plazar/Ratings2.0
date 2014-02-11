import base
from rating_classes import gaussian

class GaussianFWHMRater(base.BaseRater):
    short_name = "gaussfwhm"
    long_name = "Gaussian FWHM Rating"
    description = "The full-width at half-maximum of a single-Gaussian " \
                  "fit to the best profile."
    version = 2

    rat_cls = gaussian.SingleGaussianProfileClass()

    def _compute_rating(self, cand):
        """Return a rating for the candidate. The rating value is the
            FWHM of the gaussian function fit to the candidate's 
            profile.
        
            Input:
                cand: A Candidate object to rate.

            Output:
                value: The rating value.
        """
        sgauss = cand.get_from_cache('singlegaussfit')
        ncomp = len(sgauss.components)
        if ncomp == 1:
            fwhm = sgauss.components[0].fwhm
        elif ncomp  == 0:
            fwhm = 0.0
        else:
            raise utils.RatingError("Bad number of components for single " \
                                    "gaussian fit (%d)" % ncomp)
        return fwhm


Rater = GaussianFWHMRater
