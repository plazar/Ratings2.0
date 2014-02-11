import base
from rating_classes import cand_info

N = 10
MAINS_FREQ = 60.0

class MainsRFIRater(base.BaseRater):
    short_name = "mainsrfi"
    long_name = "Mains RFI Rating"
    description = "Evaluate how close the topocentric frequency is to a " \
                  "harmonic or subharmonic of 60 Hz. Considers all " \
                  "frequencies 60 Hz * a/b where a and b are integers " \
                  "adding up to less than 10. The fractional difference " \
                  "between the candidate's frequency and this frequency " \
                  "is computed, and an exponential is taken so that the " \
                  "result lies between zero and one, reaching 1/2 at a " \
                  "tenth of a percent."
    version = 0

    rat_cls = cand_info.CandInfoRatingClass() 

    def _compute_rating(self, cand):
        """Return a rating for the candidate. The rating value encodes 
            how close the candidate's topocentric frequency is to 60 Hz
            or a harmonic.

            Input:
                cand: A Candidate object to rate.

            Output:
                value: The rating value.
        """
        info = cand.get_from_cache('info')
        topo_freq = 1.0/info['topo_period']
        fdiff_min = 1e10
        for aa in range(1, 9):
            for bb in range(1, 10-aa):
                rf = (MAINS_FREQ * aa)/bb
                fdiff = 2*abs(topo_freq-rf)/(topo_freq+rf)
                fdiff_min = min(fdiff, fdiff_min)
        return 2.0**(-fdiff_min/1e-3)

Rater = MainsRFIRater
