import numpy as np

import base
from rating_classes import freq_vs_phase

class DMComparisonStddevRater(base.BaseRater):
    short_name = "dmcmpstd"
    long_name = "DM Comparison (Stddev)"
    description = "Compute the ratio of std deviation for the profile " \
                  "dedispersed at DM 0 divided by that for the profile " \
                  "dedispersed at the best-fit DM."
    version = 5

    rat_cls = freq_vs_phase.FreqVsPhaseClass()

    def _compute_rating(self, cand):
        """Return a rating for the candidate. The rating value is the
            stddev of the DM=0 profile divided by the stddev of the 
            best-fit DM's profile.

            Input:
                cand: A Candidate object to rate.

            Output:
                value: The rating value.
        """
        fvph = cand.get_from_cache('freq_vs_phase')
        pfd = cand.get_from_cache('pfd')

        fvph.dedisperse(DM=0)
        prof_dm0 = fvph.get_profile()
        stddev_dm0 = np.std(prof_dm0)

        fvph.dedisperse(DM=pfd.bestdm)
        prof_bestdm = fvph.get_profile()
        stddev_bestdm = np.std(prof_bestdm)

        return stddev_dm0/stddev_bestdm
    

Rater = DMComparisonStddevRater
