import pfd
import dataproducts

class TimeVsPhaseClass(pfd.PfdRatingClass):
    data_key = "time_vs_phase"

    def _compute_data(self, cand):
        """Create a TimeVsPhase object for the candidate.

            Input:
                cand: A ratings2.0 Candidate object.

            Output:
                tvph: The corresponding TimeVsPhase object.
        """
        pfd = cand.pfd
        pfd.dedisperse(pfd.bestdm, doppler=1)
        data = pfd.profs.sum(axis=1).squeeze()
        tvph = dataproducts.TimeVsPhase(data, pfd.curr_p1, pfd.curr_p2, \
                                        pfd.curr_p3, self.bestdm, \
                                        self.start_secs)
        return tvph
