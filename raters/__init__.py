registered_raters = ["duty_cycle", \
                     "gaussian_width", \
                     "gaussian_height", \
                     "gaussian_phase", \
                     "gaussian_significance", \
                     "known_pulsar", \
                     "mains_rfi", \
                     "peak_over_rms", \
                     "prepfold_sigma", \
                     "dm_comparison_std", \
                     "dm_comparison_chisqr", \
                     "dm_comparison_peak", \
                     "multivonmises_goodness"]

__all__ = registered_raters

for rater_name in registered_raters:
    __import__(rater_name, globals())
