import numpy as np
import scipy as sp

import presto

import base
from rating_classes import profile

class PrepfoldSigmaRater(base.BaseRater):
    short_name = "prepfoldsigma"
    long_name = "Prepfold Sigma Rating"
    description = "Re-compute the sigma value reported in the " \
                  "prepfold plots."
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
        tvph = cand.get_from_cache('time_vs_phase')
        prof = tvph.get_profile()
        pfd = cand.get_from_cache('pfd')

        prof_avg = np.sum(pfd.stats[:,:,4][:pfd.npart])
        prof_var = np.sum(pfd.stats[:,:,5][:pfd.npart])
        chisqr = presto.chisqr(prof, pfd.proflen, prof_avg, prof_var)
        df = pfd.proflen - 1
        
        #print "DEBUG: prof_avg, prof_var, chisqr/df", prof_avg, prof_var, chisqr/df
        
        prob = sp.stats.chi2.sf(chisqr, df)
        sig = -sp.stats.norm.ppf(prob)
        return sig 


Rater = PrepfoldSigmaRater
