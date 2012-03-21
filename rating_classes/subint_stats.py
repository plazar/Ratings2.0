import numpy as np

import dataproducts
import gaussian
import time_vs_phase

class SubintPulseWindowStats(gaussian.SingleGaussianProfileClass, \
                                    time_vs_phase.TimeVsPhaseClass):
    data_key = "subint_stats"

    def _compute_data(self, cand):
        """Compute statistics for sub-ints and return an object storing them.

            Input:
                cand: A ratings2.0 Candidate object.

            Output:
                subint_stats: The resulting PulseWindowStats object.
        """
        sgauss = cand.singlegaussfit
        tvph = cand.time_vs_phase

        onpulse_phs = sgauss.get_onpulse_region()
        print "On pulse (phase):", onpulse_phs
        onpulse_bin = np.round(onpulse_phs*tvph.nbin).astype(int)
        print "On pulse (bin):", onpulse_phs*tvph.nbin
        onpulse_length = (onpulse_bin[1] - onpulse_bin[0]) % tvph.nbin
        onpulse_indices = np.arange(onpulse_bin[0], \
                            onpulse_bin[0]+onpulse_length) % tvph.nbin
        onpulse_region = np.zeros(tvph.nbin, dtype=bool)
        onpulse_region[onpulse_indices] = True
        offpulse_region = np.bitwise_not(onpulse_region)

        zapped_profs = np.zeros(tvph.nsubint, dtype=bool)
        snrs = np.empty(tvph.nsubint)
        peak_snrs = np.empty(tvph.nsubint)
        corr_coefs = np.empty(tvph.nsubint)
        gaussprof = sgauss.make_gaussians(tvph.nbin)
        for isub in np.arange(tvph.nsubint):
            profile = tvph.data[isub,:].copy()
            offpulse = profile[offpulse_region]
            
            stddev = np.std(offpulse)
            if stddev == 0:
                zapped_profs[isub] = True
                continue

            # Scale profile
            profile -= np.mean(offpulse)
            profile /= stddev
            
            # Calculate snrs
            onpulse = profile[onpulse_region] # Get on-pulse now so it is scaled
            snrs[isub] = np.sum(onpulse)
            peak_snrs[isub] = np.mean(onpulse)
            
            # Determine correlation coeff
            corr_coefs[isub] = np.corrcoef(gaussprof, profile)[0][1]
        
        snrs = np.ma.masked_array(snrs, zapped_profs)
        peak_snrs = np.ma.masked_array(peak_snrs, zapped_profs)
        corr_coefs = np.ma.masked_array(corr_coefs, zapped_profs)
        pwstats = dataproducts.PulseWindowStats(snrs, peak_snrs, corr_coefs)
        return pwstats
