import base
from rating_classes import profile

class DutyCycleRater(base.BaseRater):
    name = "Duty Cycle Rating"
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
        nbin = float(len(cand.profile))
        thresh = np.amax(cand.profile)+np.median(cand.profile))/2.0
        dutycycle = np.sum(cand.profile>thresh)/nbin
        return dutycycle
