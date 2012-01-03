registered_raters = ["duty_cycle", \
                     "gaussian_width", \
                     "known_pulsar", \
                     "mains_rfi"]

__all__ = registered_raters

# If True, automatically import all registered rater classes
# when 'raters' is imported.
auto_import_registered = True

if auto_import_registered:
    for classname in registered_toa_classes:
        __import__(classname, globals())
