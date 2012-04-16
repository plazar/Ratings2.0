import numpy as np

import dataproducts
import multigauss
import freq_vs_phase

class SubbandPulseWindowStats(multigauss.MultipleGaussianProfileClass, \
                                    freq_vs_phase.FreqVsPhaseClass):
    data_key = "subband_stats"

    def _compute_data(self, cand):
        """Compute statistics for sub-bands and return an object storing them.

            Input:
                cand: A ratings2.0 Candidate object.

            Output:
                subband_stats: The resulting PulseWindowStats object.
        """
        mgauss = cand.multigaussfit
        fvph = cand.freq_vs_phase

        onpulse_region = mgauss.get_onpulse_region(fvph.nbin)
        offpulse_region = np.bitwise_not(onpulse_region)

        zapped_profs = np.zeros(fvph.nchan, dtype=bool)
        snrs = np.empty(fvph.nchan)
        peak_snrs = np.empty(fvph.nchan)
        corr_coefs = np.empty(fvph.nchan)
        gaussprof = mgauss.make_gaussians(fvph.nbin)
        for ichan in np.arange(fvph.nchan):
            profile = fvph.data[ichan,:].copy()
            offpulse = profile[offpulse_region]
            
            stddev = np.std(offpulse)
            if stddev == 0:
                zapped_profs[ichan] = True
                continue

            # Scale profile
            profile -= np.mean(offpulse)
            profile /= stddev
            
            # Calculate snrs
            onpulse = profile[onpulse_region] # Get on-pulse now so it is scaled
            snrs[ichan] = np.sum(onpulse)
            peak_snrs[ichan] = np.mean(onpulse)
            
            # Determine correlation coeff
            corr_coefs[ichan] = np.corrcoef(gaussprof, profile)[0][1]
        
        snrs = np.ma.masked_array(snrs, zapped_profs)
        peak_snrs = np.ma.masked_array(peak_snrs, zapped_profs)
        corr_coefs = np.ma.masked_array(corr_coefs, zapped_profs)
        pwstats = dataproducts.PulseWindowStats(snrs, peak_snrs, corr_coefs)
        return pwstats
