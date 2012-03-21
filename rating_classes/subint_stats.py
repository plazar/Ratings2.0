import numpy as np

import dataproducts
import multigauss
import time_vs_phase

class SubintPulseWindowStats(multigauss.MultipleGaussianProfileClass, \
                                    time_vs_phase.TimeVsPhaseClass):
    data_key = "subint_stats"

    def _compute_data(self, cand):
        """Compute statistics for sub-ints and return an object storing them.

            Input:
                cand: A ratings2.0 Candidate object.

            Output:
                subint_stats: The resulting PulseWindowStats object.
        """
        mgauss = cand.multigaussfit
        tvph = cand.time_vs_phase

        onpulse_region = mgauss.get_onpulse_region(tvph.nbin)
        offpulse_region = np.bitwise_not(onpulse_region)

        zapped_profs = np.zeros(tvph.nsubint, dtype=bool)
        snrs = np.empty(tvph.nsubint)
        peak_snrs = np.empty(tvph.nsubint)
        corr_coefs = np.empty(tvph.nsubint)
        gaussprof = mgauss.make_gaussians(tvph.nbin)
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
