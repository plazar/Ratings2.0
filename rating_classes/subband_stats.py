import numpy as np

import dataproducts
import gaussian
import freq_vs_phase

class SubbandPulseWindowStats(gaussian.SingleGaussianProfileClass, \
                                    freq_vs_phase.FreqVsPhaseClass):
    data_key = "subband_stats"

    def _compute_data(self, cand):
        """Compute statistics for sub-bands and return an object storing them.

            Input:
                cand: A ratings2.0 Candidate object.

            Output:
                subband_stats: The resulting PulseWindowStats object.
        """
        sgauss = cand.gaussian
        fvph = cand.freq_vs_phase

        onpulse_phs = sgauss.get_onpulse_region()
        onpulse_bin = np.round(onpulse_phs*fvph.nbin).astype(int)

        onpulse_length = (onpulse_bin[1] - onpulse_bin[0]) % fvph.nbin
        onpulse_indices = np.range(onpulse_bin[0], \
                            onpulse_bin[0]+onpulse_length) % fvph.nbin
        onpulse_region = np.zeros(fvph.nbin, dtype=bool)
        onpulse_region[onpulse_indices] = True
        offpulse_region = np.bitwise_not(onpulse_region)

        counts = 0
        counts_peak = 0
        snrs = []
        peak_snrs = []
        num_zapped_profs = 0
        corr_coef_sum = 0

        zapped_profs = np.zeros(fvph.nsubint, dtype=bool)
        snrs = np.empty(fvph.nsubint)
        peak_snrs = np.empty(fvph.nsubint)
        corr_coefs = np.empty(fvph.nsubint)
        gaussprof = sgauss.make_gaussians(fvph.nbin)
        for ichan in np.arange(fvph.nchan):
            profile = fvph.data[isub,:].copy()
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
            peak_snrs[ichan] = np.meax(onpulse)
            
            # Determine correlation coeff
            corr_coefs[ichan] = np.corrcoef(gaussprof, profile)[0][1]
        
        snrs = np.ma.masked_array(snrs, zapped_profs)
        peak_snrs = np.ma.masked_array(peak_snrs, zapped_profs)
        corr_coefs = np.ma.masked_array(corr_coefs, zapped_profs)
        pwstats = dataproducts.PulseWindowStats(snrs, peak_snrs, corr_coefs)
        return pwstats
