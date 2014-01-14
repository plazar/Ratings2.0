import utils
import base
from rating_classes import peace

class PeaceSnrRater(base.BaseRater):
    short_name = "peace_snr"
    long_name = "PEACE SNR"
    description = "A PEACEful version of signal-to-noise ratio. " \
                    "The higher the better."
                    
    version = 1

    rat_cls = peace.PeaceRatingClass()

    def _compute_rating(self, cand):
        """
        """
        return cand.peace['snr']

Rater = PeaceSnrRater

