import utils
import base
from rating_classes import peace

class PeaceCompositeProgCountScoreRater(base.BaseRater):
    short_name = "peace_progcount_score"
    long_name = "Composite PEACE Score (Progressive Counting)"
    description = "A composite score using information from all " \
                    "progressive-counting-based PEACE ratings. " \
                    "Values are smaller than 0. " \
                    "Usually score > -5 indicates a very good candidate."
                    
    version = 1

    rat_cls = peace.PeaceRatingClass()

    def _compute_rating(self, cand):
        """
        """
        peace = cand.get_from_cache('peace')
        return peace['score_progcnt']

Rater = PeaceCompositeProgCountScoreRater



