registered_raters = ["duty_cycle", \
                     "gaussian_width", \
                     "gaussian_height", \
                     "known_pulsar", \
                     "mains_rfi"]

__all__ = registered_raters

for rater_name in registered_raters:
    __import__(rater_name, globals())
