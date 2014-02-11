import cand_info
import myprepfold as prepfold

class PfdRatingClass(cand_info.CandInfoRatingClass):
    data_key = "pfd"

    def _compute_data(self, cand):
        """Create a prepfold.pfd object for the candidate's 
            *.pfd file, and dedisperse it to the best DM found.

            Input:
                cand: A ratings2.0 Candidate object.

            Output:
                pfd: The corresponding (dedispersed) prepfold.pfd object.
        """
        info = cand.get_from_cache('info')
        pfdfn = info['pfdfn']
        pfd = prepfold.pfd(pfdfn)
        pfd.dedisperse(doppler=1)
        return pfd
