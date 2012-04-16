import numpy as np

import presto

import base
from rating_classes import freq_vs_phase

class DMComparisonChiSquareRater(base.BaseRater):
    short_name = "dmcmpchisqr"
    long_name = "DM Comparison (Chi Square)"
    description = "Compute the ratio of chi-square for the profile " \
                  "dedispersed at DM 0 divided by that for the profile " \
                  "dedispersed at the best-fit DM."
    version = 1

    rat_cls = freq_vs_phase.FreqVsPhaseClass()

    def _compute_rating(self, cand):
        """Return a rating for the candidate. The rating value is the
            Chi-square of the DM=0 profile divided by the chi-square 
            of the best-fit DM's profile.

            Input:
                cand: A Candidate object to rate.

            Output:
                value: The rating value.
        """
        fvph = cand.freq_vs_phase
        pfd = cand.pfd

        prof_avg = np.sum(pfd.stats[:,:,4][:pfd.npart])
        prof_var = np.sum(pfd.stats[:,:,5][:pfd.npart])

        fvph.dedisperse(DM=0)
        prof_dm0 = fvph.get_profile()
        chisqr_dm0 = presto.chisqr(prof_dm0, pfd.proflen, prof_avg, prof_var)

        fvph.dedisperse(DM=cand.pfd.bestdm)
        prof_bestdm = fvph.get_profile()
        chisqr_bestdm = presto.chisqr(prof_bestdm, pfd.proflen, prof_avg, prof_var)

        return chisqr_dm0/chisqr_bestdm
    

Rater = DMComparisonChiSquareRater

