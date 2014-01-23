import warnings

import utils

registered_raters = ["duty_cycle", \
                     "pulse_width", \
                     "wiggle", \
                     "known_pulsar", \
                     "mains_rfi", \
                     "peak_over_rms", \
                     "dm_comparison_std", \
                     "dm_comparison_chisqr", \
                     "dm_comparison_peak", \
                     "gaussian_amplitude", \
                     "gaussian_goodness", \
                     "gaussian_fwhm", \
                     "frac_good_subbands", \
                     "frac_good_intervals", \
                     "subbands_snrstd", \
                     "subints_snrstd", \
                     "multigauss_number", \
                     "multigauss_goodness", \
                     "ubc_pfd_ai", \
                     "peace_bb_gauss", \
                     "peace_bb_progcnt", \
                     "peace_dmsmear", \
                     "peace_gauss_score", \
                     "peace_persistence_gauss", \
                     "peace_persistence_progcnt", \
                     "peace_progcnt_score", \
                     "peace_pulsewidth_gauss", \
                     "peace_pulsewidth_progcnt", \
                     "peace_snr", \
                     "peace_score"]

__all__ = registered_raters

for ii in reversed(range(len(registered_raters))):
    rater_name = registered_raters[ii]
    try:
        __import__(rater_name, globals())
    except:
        warnings.warn("The rater '%s' could not be loaded!" % rater_name, \
                utils.RaterLoadWarning)
        registered_raters.pop(ii)
