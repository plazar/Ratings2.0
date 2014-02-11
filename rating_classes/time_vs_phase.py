import copy
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
        pfd = cand.get_from_cache('pfd')
        pfd.dedisperse(pfd.bestdm, doppler=1)
        data = pfd.profs.sum(axis=1).squeeze()
        #
        # NOTE: pfd.fold_p[123] are actually frequencies!
        #
        tvph = dataproducts.TimeVsPhase(data, pfd.curr_p1, pfd.curr_p2, \
                                        pfd.curr_p3, pfd.bestdm, \
                                        pfd.start_secs, pfd.fold_p1, \
                                        pfd.fold_p2, pfd.fold_p3, \
                                        copy.deepcopy(pfd.pdelays_bins))
        return tvph
