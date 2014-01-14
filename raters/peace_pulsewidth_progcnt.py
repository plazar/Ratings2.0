import utils
import base
from rating_classes import peace

class PeaceProgCountWidthRater(base.BaseRater):
    short_name = "peace_width_progcount"
    long_name = "PEACE Pulse Width (Progressive Counting)"
    description = "Width of the pulse profile as determined by " \
                    "progressively counting the highest peak." \
                    "The value is " \
                    "fractional width of the pulse (between 0 and 1)."

                    
    version = 1

    rat_cls = peace.PeaceRatingClass()

    def _compute_rating(self, cand):
        """
        """
        return cand.peace['pulsewidth_progcnt']

Rater = PeaceProgCountWidthRater

