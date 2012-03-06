import base
from rating_classes import multigauss

class NumberOfGaussiansRater(base.BaseRater):
    short_name = "numberofgaussians"
    long_name = "Number of Gaussians Rating"
    description = "The number of gaussians needed to obtain a statistically " \
                  "acceptable fit to the best profile. A maximum of 5 gaussians " \
                  "is used. An unsuccessful fit returns 0 gaussains."
    version = 1

    rat_cls = multigauss.MultipleGaussianProfileClass()

    def _compute_rating(self, cand):
        """Return a rating for the candidate. The rating value is the
            number of gaussian functions fit to the candidate's 
            profile.
        
            Input:
                cand: A Candidate object to rate.

            Output:
                value: The rating value.
        """
        mgauss = cand.multigaussfit
        return len(mgauss.components)


Rater = NumberOfGaussiansRater
