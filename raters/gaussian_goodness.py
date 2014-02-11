import utils
import base
from rating_classes import gaussian

class GaussianGofRater(base.BaseRater):
    short_name = "gaussgoodness"
    long_name = "Gaussian Goodness Rating"
    description = "The reduced chi2 of a single-Gaussian fit to the best " \
                  "profile. Good fits should have a reduced chi2 of ~1"
    version = 2

    rat_cls = gaussian.SingleGaussianProfileClass()

    def _compute_rating(self, cand):
        """Return a rating for the candidate. The rating value is the
            reduced chi2 of the gaussian function fit to the candidate's 
            profile.
        
            Input:
                cand: A Candidate object to rate.

            Output:
                value: The rating value.
        """
        prof = cand.get_from_cache('profile')
        pfd = cand.get_from_cache('pfd')
        sgauss = cand.get_from_cache('singlegaussfit')
        
        profile = utils.get_scaled_profile(prof, pfd.varprof)
        chi2 = sgauss.get_chisqr(profile)
        dof = sgauss.get_dof(len(profile))
        return chi2/dof


Rater = GaussianGofRater
