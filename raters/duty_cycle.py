import numpy as np

import base
from rating_classes import profile

class DutyCycleRater(base.BaseRater):
    short_name = "dutycycle"
    long_name = "Duty Cycle Rating"
    description = "Compute the duty cycle, that is, the fraction of " \
                  "profile bins in which the value is more than " \
                  "(max+median)/2."
    version = 4
    
    rat_cls = profile.ProfileClass()

    def _compute_rating(self, cand):
        """Return a rating for the candidate. The rating value is an 
            estimate of the profile's duty cycle.

            Input:
                cand: A Candidate object to rate.

            Output:
                value: The rating value.
        """
        profile = cand.get_from_cache('profile')
        nbin = float(len(profile))
        thresh = (np.amax(profile)+np.median(profile))/2.0
        dutycycle = np.sum(profile>thresh)/nbin
        return dutycycle

Rater = DutyCycleRater
