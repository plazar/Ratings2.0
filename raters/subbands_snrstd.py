import base
from rating_classes import subband_stats

class SubbandsSNRStdev(base.BaseRater):
    short_name = "subbands_snrstd"
    long_name = "Subband SNR Std Dev"
    description = "Determines the standard deviation of the subband " \
                  "signal-to-noise ratios."
    version = 4
    rat_cls = subband_stats.SubbandPulseWindowStats()

    def _compute_rating(self, cand):
        """Return a rating for the candidate. The rating value is the
            standard deviation of the sub-band SNRs.

            Input:
                cand: A Candidate object to rate.

            Output:
                value: The rating value.
        """
        chanstats = cand.subband_stats
        return max((chanstats.get_snr_stddev(), chanstats.get_peak_snr_stddev()))


Rater = SubbandsSNRStdev 
