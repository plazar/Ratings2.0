import os.path

import numpy as np

import psr_utils

import base
import config
from rating_classes import pfd

# Initialise constants
M = 99
MAX_NUMERATOR = 33
MAX_DENOMINATOR = 5
KNOWNPSR_FILENM = os.path.join(os.path.split(__file__)[0], "../knownpulsars.txt")


class KnownPulsarRater(base.BaseRater):
    short_name = "knownpsr"
    long_name = "Known Pulsar Rating"
    description = "Evaluate how similar the period and DM are to a nearby " \
                    "pulsar. The rating value is an estimate in the smearing " \
                    "(in rotations) of the DM and period differences. " \
                    "integer and fractional harmonics are also checked. " \
                    "NOTES: " \
                        "1) low values of this rating indicate a higher " \
                            "change of the candidate being a known pulsar. " \
                        "2) rating values are constrained to be < 10."
    version = 1

    rat_cls = pfd.PfdRatingClass()

    def _setup(self):
        """A setup method to be called when the Rater is initialised
        
            Inputs:
                None

            Outputs:
                None
        """
        numerator = np.arange(1, MAX_NUMERATOR, dtype=float)
        denominator = np.arange(1, MAX_DENOMINATOR, dtype=float)
        outer = np.outer(numerator, 1/denominator)
        self.ratios = np.unique(outer[outer!=1])

        self.known_periods, self.known_dms, self.known_ras, self.known_decls = \
                np.loadtxt(KNOWNPSR_FILENM, usecols=(0,1,2,3), unpack=True)

    def _compute_rating(self, cand):
        """Return a rating for the candidate. The rating value encodes 
            how close the candidate's period and DM are to that of a
            known pulsar.

            Input:
                cand: A Candidate object to rate.

            Output:
                value: The rating value.
        """
        info = cand.get_from_cache('info')
        candp = info['bary_period']
        canddm = info['dm']
        ra = info['raj_deg']
        decl = info['decj_deg']
        pfd = cand.get_from_cache('pfd')

        diff_ra = np.abs(self.known_ras - ra)
        diff_dec = np.abs(self.known_decls - decl)

        ii_nearby = (diff_ra < 0.2) & (diff_dec < 0.2)
        knownps = self.known_periods[ii_nearby]
        knowndms = self.known_dms[ii_nearby]

        dp_smear_phase = np.inf*np.ones(knownps.size)
        ddms = np.abs(canddm-knowndms)
        bw = pfd.hifreq-pfd.lofreq
        fctr = 0.5*(pfd.hifreq+pfd.lofreq)
        ddm_smear_phase = psr_utils.dm_smear(ddms, bw, fctr)/knownps

        if knownps.size:
            for b in range(1, M):
                dp_smear_sec = np.abs(candp*b-knownps)*pfd.T
                dp_smear_phase = np.min(np.vstack((dp_smear_sec/knownps, dp_smear_phase)), axis=0)
            for rat in self.ratios:
                dp_smear_sec = np.abs(candp*b-knownps)*pfd.T
                dp_smear_phase = np.min(np.vstack((dp_smear_sec/knownps, dp_smear_phase)), axis=0)
            smear_phase = np.min(np.sqrt(dp_smear_phase**2+ddm_smear_phase**2))
            #if smear_phase > 1:
            #    print pfd.pfd_filename, smear_phase
            smear_phase = np.clip(smear_phase, 0, 10)
        else:
            # No nearby known pulsars
            smear_phase = 10
        return smear_phase

Rater = KnownPulsarRater
