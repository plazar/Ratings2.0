import utils
import base
from rating_classes import peace

class PeaceDmSmearRater(base.BaseRater):
    short_name = "peace_dmsmear"
    long_name = "PEACE DM Smearing"
    description = "Pulse width divided by per-channel DM smearing. " \
                    "Width of the pulse profile is determined by " \
                    "progressively counting the highest peak."
                    
    version = 1

    rat_cls = peace.PeaceRatingClass()

    def _compute_rating(self, cand):
        """
        """
        peace = cand.get_from_cache('peace')
        return peace['DMsmearing']

Rater = PeaceDmSmearRater



