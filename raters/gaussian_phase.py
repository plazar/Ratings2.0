import base
from rating_classes import gaussian

class GaussianPhaseRater(base.BaseRater):
    short_name = "gaussphase"
    long_name = "Gaussian Phase Rating"
    description = "Compute the phase of the best-fit Gaussian. The function " \
                  "being fit is not actually a Gaussian, it's a von Mises " \
                  "distribution (exp(k*cos(theta)))"
    version = 5

    rat_cls = gaussian.GaussianProfileClass()

    def _compute_rating(self, cand):
        """Return a rating for the candidate. The rating value is the
            phase of the von Mises function fit to the candidate's 
            profile.
        
            Input:
                cand: A Candidate object to rate.

            Output:
                value: The rating value.
        """
        return cand.gaussfit.mu

Rater = GaussianPhaseRater

