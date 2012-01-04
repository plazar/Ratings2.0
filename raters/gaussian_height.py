import base
from rating_classes import gaussian

class GaussianHeightRater(base.BaseRater):
    short_name = "gaussheight"
    long_name = "Gaussian Height Rating"
    description = "Compute the height of the best-fit Gaussian divided " \
                  "by the RMS of the post-fit residuals. The function " \
                  "being fit is not actually a Gaussian, it's a von Mises " \
                  "distribution (exp(k*cos(theta)))"
    version = 6

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
        resids = cand.profile-cand.gaussfit.histogram(nbins)
        rms = resids.std()
        return cand.gaussfit.amplitude(nbins)/rms

Rater = GaussianHeightRater
    
