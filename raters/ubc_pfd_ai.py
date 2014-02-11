import numpy as np
import scipy as sp

import presto

import base
from rating_classes import profile
import config

#### setup UBC AI
from ubc_AI.data import pfdreader
import cPickle
clfer = config.pfd_classifier
classifier = cPickle.load(open(clfer, 'rb'))
####

class ubc_pfd_ai(base.BaseRater):
    short_name = "pfd_AI"
    long_name = "UBC pfd AI"
    description = "compute the prediction from the pulsar classifier " \
                  "based on pfd files."
    version = 4
    
    rat_cls = profile.ProfileClass()

    def _compute_rating(self, cand):
        """Return a rating for the candidate. The rating value is 
            the prepfold sigma value.

            Input:
                cand: A Candidate object to rate.

            Output:
                value: The rating value.
        """
        pfd_fn = cand.get_from_cache('pfd').pfd_filename

        pred = classifier.report_score([pfdreader(pfd_fn)])
        return pred


Rater = ubc_pfd_ai 
