import utils
import base
from rating_classes import peace

class PeaceGaussWidthRater(base.BaseRater):
    short_name = "peace_width_gauss"
    long_name = "PEACE Pulse Width (Gauss)"
    description = "Width of the pulse profile as determined by " \
                    "fitting Gaussian components. The value is " \
                    "fractional width of the pulse (between 0 and 1)."
                    
    version = 1

    rat_cls = peace.PeaceRatingClass()

    def _compute_rating(self, cand):
        """
        """
        return cand.peace['pulsewidth_gauss']

Rater = PeaceGaussWidthRater

