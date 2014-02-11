import utils
import base
from rating_classes import peace

class PeaceGaussBroadbandednessRater(base.BaseRater):
    short_name = "peace_bb_gauss"
    long_name = "PEACE Broadbandedness (Gauss)"
    description = "Broadbandedness of the signal. The shape of " \
                    "the profile is determined by fitting a Gaussian."
                    
    version = 1

    rat_cls = peace.PeaceRatingClass()

    def _compute_rating(self, cand):
        """
        """
        peace = cand.get_from_cache('peace')
        return peace['broadbandedness_gauss']

Rater = PeaceGaussBroadbandednessRater

