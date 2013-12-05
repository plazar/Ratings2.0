import base
from rating_classes import gaussian

class GaussianAmplitudeRater(base.BaseRater):
    short_name = "gaussamplitude"
    long_name = "Gaussian Amplitude Rating"
    description = "The amplitude of a single-Gaussian fit to the best " \
                  "profile, normalized such that the profile standard " \
                  "deviation is 1."
    version = 2

    rat_cls = gaussian.SingleGaussianProfileClass()

    def _compute_rating(self, cand):
        """Return a rating for the candidate. The rating value is the
            amplitude of the gaussian function fit to the candidate's 
            profile.
        
            Input:
                cand: A Candidate object to rate.

            Output:
                value: The rating value.
        """
        sgauss = cand.singlegaussfit
        ncomp = len(sgauss.components)
        if ncomp == 1:
            amp = sgauss.components[0].amp
        elif ncomp  == 0:
            amp = 0.0
        else:
            raise utils.RatingError("Bad number of components for single " \
                                    "gaussian fit (%d)" % ncomp)
        return amp


Rater = GaussianAmplitudeRater
