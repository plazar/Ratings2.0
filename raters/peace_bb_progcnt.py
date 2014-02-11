import utils
import base
from rating_classes import peace

class PeaceProgCountBroadbandednessRater(base.BaseRater):
    short_name = "peace_bb_progcount"
    long_name = "PEACE Broadbandedness (Progressive Counting)"
    description = "Broadbandedness of the signal. The shape of " \
                    "the profile is determined by progressively " \
                    "counting the highest peak."
                    
    version = 1

    rat_cls = peace.PeaceRatingClass()

    def _compute_rating(self, cand):
        """
        """
        peace = cand.get_from_cache('peace')
        return peace['broadbandedness_peak']

Rater = PeaceProgCountBroadbandednessRater

