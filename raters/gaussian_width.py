import base
from rating_classes import gaussian

class GaussianWidthRater(base.BaseRater):
    name = "Gaussian Width"
    description = "Compute the full width at half maxiumum of the best-fit " \
                  "Gaussian. The function being fit is not actually a " \
                  "Gaussian, it's a von Mises distribution " \
                  "(exp(k*cos(theta)))"
    version = 5

    rat_cls = gaussian.GaussianProfileClass()

    def _compute_rating(self, cand):
        """Return a rating for the candidate. The rating value is the
            FWHM of the von Mises function fit to the candidate's profile.
        
            Input:
                cand: A Candidate object to rate.

            Output:
                value: The rating value.
        """
        return cand.gaussfit.fwhm()
