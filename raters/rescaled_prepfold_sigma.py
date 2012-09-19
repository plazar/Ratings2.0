import numpy as np
import scipy as sp

import presto

import base
from rating_classes import profile

class RescaledPrepfoldSigmaRater(base.BaseRater):
    short_name = "rescaledpfdsigma"
    long_name = "Rescaled Prepfold Sigma Rating"
    description = "Rescale the sigma value reported in the " \
                  "prepfold plots using a better estimate of" \
                  "the off-pulse chi-square."
    version = 1
    
    rat_cls = profile.ProfileClass()

    def _compute_rating(self, cand):
        """Return a rating for the candidate. The rating value is 
            the prepfold sigma value.

            Input:
                cand: A Candidate object to rate.

            Output:
                value: The rating value.
        """
        prof = cand.time_vs_phase.get_profile()
        pfd = cand.pfd

        prof_avg = np.sum(pfd.stats[:,:,4][:pfd.npart])
        prof_var = np.sum(pfd.stats[:,:,5][:pfd.npart])
        chisqr = presto.chisqr(prof, pfd.proflen, prof_avg, prof_var)
        df = pfd.proflen - 1
        
        redchisqr = chisqr/df

        off_redchisqr = pfd.estimate_offsignal_redchi2()
        rescaled_redchisqr = redchisqr / off_redchisqr

        
        #print "DEBUG: prof_avg, prof_var, chisqr/df", prof_avg, prof_var, chisqr/df
        
        prob = sp.stats.chi2.sf(rescaled_redchisqr*df, df)
        sig = -sp.stats.norm.ppf(prob)
        return sig 


Rater = RescaledPrepfoldSigmaRater
