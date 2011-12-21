import psr_utils
import pfd
import dataproducts

class FreqVsPhaseClass(pfd.PfdRatingClass):
    data_key = "freq_vs_phase"

    def _compute_data(self, cand):
        """Create a FreqVsPhase object for the candidate.

            Input:
                cand: A ratings2.0 Candidate object.

            Output:
                fvph: The corresponding FreqVsPhase object.
        """
        pfd = cand.pfd
        if pfd.fold_pow == 1.0:
            bestp = pfd.bary_p1
            bestpd = pfd.bary_p2
            bestpdd = pfd.bary_p3
        else:
            bestp = pfd.topo_p1
            bestpd = pfd.topo_p2
            bestpdd = pfd.topo_p3
        pfd.adjust_period(bestp, bestpd, bestpdd)
        data = pfd.profs.sum(axis=0).squeeze()
        freqs = psr_utils.doppler(pfd.subfreqs, pfd.avgvoverc)
        fvph = dataproducts.FreqVsPhase(data, bestp, bestpd, bestpdd, \
                                        pfd.curr_dm, freqs)
        return fvph
