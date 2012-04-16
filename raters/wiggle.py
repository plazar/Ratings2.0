import numpy as np
import psr_utils

import base
from rating_classes import time_vs_phase

TOL = 0.02
method = "GOODFRAC"

class WiggleRater(base.BaseRater):
    short_name = "wiggle"
    long_name = "Wiggle Rating"
    description = "The fraction of intervals (0.0 - 1.0) that 'wiggle' " \
                  "in phase by <= 0.02. The phase difference is calculated " \
                  "by cross-correlating each interval with the summed " \
                  "profile. (NOTE: 'waggles' are not considered)"
    version = 1

    rat_cls = time_vs_phase.TimeVsPhaseClass()

    def _compute_rating(self, cand):
        """Return a rating for the candidate. The rating value is the
            the fraction of sub-ints that deviate from the phase of
            the pulse.

            Input:
                cand: A Candidate object to rate.

            Output:
                value: The rating value.
        """
        tvph = cand.time_vs_phase
        pfd = cand.pfd

        bestprof = tvph.get_profile()
        new_template = np.zeros_like(bestprof)
        bin_offsets = np.empty(pfd.npart)

        # The following loop creates a better template by removing wiggle, but
        # it does not change the actual subints
        for ii, subint in enumerate(tvph.data):
            # Measure the phase offset
            phase_offset = psr_utils.measure_phase_corr(subint, bestprof)
            # The following is needed to put phase offsets on the interval
            # (-0.5,0.5]
            if phase_offset > 0.5: 
                phase_offset -= 1.0
            # Caclulate the offset in bins
            bin_offset = int(round(pfd.proflen*phase_offset))
            # Update the new template
            new_template += psr_utils.rotate(subint, -bin_offset)

        # Now calculate the wiggle using the updated template
        for ii, subint in enumerate(tvph.data):
            phase_offset = psr_utils.measure_phase_corr(subint, new_template)
            if phase_offset > 0.5:
                phase_offset -= 1.0
            bin_offsets[ii] = int(round(pfd.proflen*phase_offset))

        # Calculate the various metrics
        if method == "GOODFRAC":
            # good fraction 
            wigglescore = sum(abs(bin_offsets) < TOL*pfd.proflen)/ \
                        float(pfd.npart)
        elif method == "WANDER":
            # total wander
            wigglescore = sum(abs(bin_offsets))/(pfd.proflen*pfd.npart)
        elif method == "OFFSTD":
            # offset std
            wigglescore = bin_offsets.std()
        elif method == "OFFMAX":
            # offset max
            wigglescore = bin_offsets.max() 
        else:
            raise utils.RatingError("Unrecognized method for wiggle " \
                                    "rating (%s)" % method)

        return wigglescore
    

Rater = WiggleRater

