"""
A module part of the ratings2.0 package.

The module defines a candidate object that is rated by other
modules of this package.

Patrick Lazarus, Dec 15. 2011 - mid-flight
"""


class Candidate(object):
    """
    A candidate object wrapping a PRESTO prepfold.pfd object
    adding extra information and methods useful for automatic
    candidate rating as used in surveys.
    """
    add_to_cache = setattr
    get_from_cache = getattr
    is_in_cache = hasattr

    def __init__(self, topo_period, bary_period, dm, raj_deg, decj_deg, pfdfn):
        """Constructor for Candidate objects
            
            Inputs:
                topo_period: Topocentric period (in ms)
                bary_period: Barycentric period (in ms)
                dm: Dispersion measure (in pc cm^-3)
                raj_deg: Right Ascension (J2000 in degrees)
                decj_deg: Declination (J2000 in degrees)
                pfdfn: The *.pfd file for this candidate.
 
            Output:
                cand: Candidate object
        """
        self.topo_period = topo_period
        self.bary_period = bary_period
        self.dm = dm
        self.raj_deg = raj_deg
        self.decj_deg
        self.pfdfn = pfdfn
        self.rating_values = []

    def add_rating(self, ratval):
        self.rating_values.append(ratval)

    def get_ratings_string(self):
        return = "-----\n".join([str(rv) for rv in self.rating_values])
