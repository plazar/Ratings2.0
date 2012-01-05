import numpy as np
import matplotlib.pyplot as plt
import base
from rating_classes import freq_vs_phase

class DMComparisonPeakRater(base.BaseRater):
    short_name = "dmcmppeak"
    long_name = "DM Comparison (Peak)"
    description = "Compute the ratio of peak height for the profile " \
                  "dedispersed at DM 0 divided by that for the profile " \
                  "dedispersed at the best-fit DM."
    version = 5

    rat_cls = freq_vs_phase.FreqVsPhaseClass()

    def _compute_rating(self, cand):
        """Return a rating for the candidate. The rating value is the
            Peak of the DM=0 profile divided by the peak of the 
            best-fit DM's profile.

            Input:
                cand: A Candidate object to rate.

            Output:
                value: The rating value.
        """
        fvph = cand.freq_vs_phase
        
        print "DEBUG: dedispersing freq vs phase"
        #fvph.dedisperse(DM=0)
        print "DEBUG: dedispersing pfd"
        cand.pfd.dedisperse(0, doppler=1)
        print "DEBUG: inside dm_comparison_peak.py -- cand.pfd.subdelays_bins", cand.pfd.subdelays_bins
        print "DEBUG: Running time vs phase method of pfd"
        prof_dm0_pfd = cand.pfd.time_vs_phase().sum(axis=0)
        prof_dm0 = fvph.get_profile(remove_offset=False)
        plt.plot(prof_dm0_pfd)
        plt.plot(prof_dm0)
        plt.show()
        peak_dm0 = np.amax(prof_dm0) - np.median(prof_dm0)

        fvph.dedisperse(DM=cand.pfd.bestdm)
        prof_bestdm = fvph.get_profile()
        peak_bestdm = np.amax(prof_bestdm) - np.median(prof_bestdm)

        return peak_dm0/peak_bestdm
    

Rater = DMComparisonPeakRater