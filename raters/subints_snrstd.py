import base
from rating_classes import subint_stats

class SubintsSNRStdev(base.BaseRater):
    short_name = "subints_snrstd"
    long_name = "Subint SNR Std Dev"
    description = "Determines the standard deviation of the subint " \
                  "signal-to-noise ratios."
    version = 4
    rat_cls = subint_stats.SubintPulseWindowStats()

    def _compute_rating(self, cand):
        """Return a rating for the candidate. The rating value is the
            standard deviation of the sub-int SNRs.

            Input:
                cand: A Candidate object to rate.

            Output:
                value: The rating value.
        """
        intstats = cand.get_from_cache('subint_stats')
        return max((intstats.get_snr_stddev(), intstats.get_peak_snr_stddev()))


Rater = SubintsSNRStdev 
