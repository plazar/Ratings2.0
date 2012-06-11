import base
from rating_classes import multigauss

import numpy as np
import psr_utils

import utils

class PulseWidthRater(base.BaseRater):
    short_name = "pulsewidth"
    long_name = "Pulse Width Rating"
    description = "Fits a maximum of 5 Gaussian profile components and " \
                  "computes the contribution of DM Smearing and sampling " \
                  "time to the width of the narrowest component. Ideally, " \
                  "a real pulsar should have a rating < 1.0 (but the fits " \
                  "may not always be ideal!)."
    version = 1

    rat_cls = multigauss.MultipleGaussianProfileClass()

    def _compute_rating(self, cand):
        """Return a rating for the candidate. The rating value is the
            ratio of the width of the narrowest gaussian component 
            to the DM smearing.
        
            Input:
                cand: A Candidate object to rate.

            Output:
                value: The rating value.
        """
        pfd = cand.pfd
        mgauss = cand.multigaussfit
        ncomp = len(mgauss.components)
        if not ncomp:
            raise utils.RatingError("Bad number of components for single " \
                                    "gaussian fit (%d)" % ncomp)
        
        # Get the period
        period = pfd.bary_p1 or pfd.topo_p1
        if period is None:
            raise utils.RatingError("Bad period in PFD file (%f)" % period)
        f_ctr = (pfd.hifreq + pfd.lofreq)/2.0
        dm_smear = psr_utils.dm_smear(pfd.bestdm, pfd.chan_wid, f_ctr)
        width_phs = np.sqrt(dm_smear**2 + pfd.dt**2)/period

        minfwhm = min([comp.fwhm for comp in mgauss.components])
        return width_phs/minfwhm


Rater = PulseWidthRater
