import base
from rating_classes import subband_stats

class FractionGoodSubbands(base.BaseRater):
    short_name = "frac_goodsubbands"
    long_name = "Fraction of Good Subbands"
    description = "Determines the fraction of freq subbands, above a set " \
                  "S/N threshold, that contain the signal. Does this for " \
                  "both cumulative and peak S/N and returns the highest "\
                  "fraction of the two. (On-pulse region is based on a " \
                  "multiple-gaussian component fit to the integrated profile.)"
    version = 2
    rat_cls = subband_stats.SubbandPulseWindowStats()
    
    def _compute_rating(self, cand):
        """Return a rating for the candidate. The rating value is the
            the fraction of sub-bands that contain the pulsar signal. 

            Input:
                cand: A Candidate object to rate.

            Output:
                value: The rating value.
        """
        chanstats = cand.subband_stats
        return max((chanstats.get_on_frac(), chanstats.get_peak_on_frac()))


Rater = FractionGoodSubbands 
