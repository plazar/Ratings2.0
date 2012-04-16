import base
from rating_classes import subint_stats

class FractionGoodIntervals(base.BaseRater):
    short_name = "frac_goodints"
    long_name = "Fraction of Good Intervals"
    description = "Determines the fraction of time intervals, above a set " \
                  "S/N threshold, that contain the signal. Does this for " \
                  "both cumulative and peak S/N and returns the highest "\
                  "fraction of the two. (On-pulse region is based on a " \
                  "multiple-gaussian component fit to the integrated profile.)"
    version = 2
    rat_cls = subint_stats.SubintPulseWindowStats()
    
    def _compute_rating(self, cand):
        """Return a rating for the candidate. The rating value is the
            the fraction of sub-ints that contain the pulsar signal. 

            Input:
                cand: A Candidate object to rate.

            Output:
                value: The rating value.
        """
        intstats = cand.subint_stats
        return max((intstats.get_on_frac(), intstats.get_peak_on_frac()))


Rater = FractionGoodIntervals 
