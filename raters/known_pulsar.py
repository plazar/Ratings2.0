import config

import numpy as np

import base
from rating_classes import cand_info

# Initialise constants
M = 99
MAX_NUMERATOR = 33
MAX_DENOMINATOR = 5
KNOWNPSR_FILENM = config.knownpsr_filenm


class KnownPulsarRater(base.BaseRater):
    short_name = "knownpsr"
    long_name = "Known Pulsar Rating"
    description = "Evaluate how close the barycentric period is to a known " \
                  "pulsar, its harmonics (up to 99th), or an integer-ratio-" \
                  "multiple of a known pulsar period.\n" \
                  "    The known pulsar P (in seconds), Ra and Dec (both in " \
                  "degrees), and DM are stored in knownpulsars_periods.txt, " \
                  "knownpulsars_ra.txt, knownpulsars_dec.txt, and " \
                  "knownpulsars_dm.txt, respectively.\n" \
                  "    1. If both the RA -and- Dec separations between the " \
                  "candidate and a pulsar are less than 0.3 degrees, the " \
                  "fractional difference between the candidate's period and " \
                  "pulsar period (or one of its harmonics, up to the 99th) " \
                  "is computed. Otherwise the candidate is given a 0 rating.\n" \
                  "    2. If this fractional period difference is less than " \
                  "0.001, the fractional difference between the candidate " \
                  "and known pulsar DM is calculated. The rating is then " \
                  "just the inverse of the smallest DM fractional difference.\n" \
                  "    3. Otherwise, if the fractional difference between the " \
                  "candidate period and an integer-ratio-multiple of a known " \
                  "pulsar period [e.g. (3/16)*P_psr, (5/33)*P_psr] is less " \
                  "than 0.02, the fractional difference in DM is computed. " \
                  "The rating is the inverse of the smallest fractional " \
                  "difference.\n" \
                  "    Known pulsars should have very high ratings (~>10) " \
                  "and most (but not all) non-pulsars should be rated with " \
                  "a zero."
    version = 0

    rat_cls = cand_info.CandInfoRatingClass()

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
        candp = cand.info['bary_period']
        canddm = cand.info['dm']
        ra = cand.info['raj_deg']
        decl = cand.info['decj_deg']

        diff_ra = np.abs(self.known_ras - ra)
        diff_dec = np.abs(self.known_decls - decl)

        ii_nearby = (diff_ra < 0.2) & (diff_dec < 0.2)
        knownps = self.known_periods[ii_nearby]
        knowndms = self.known_dms[ii_nearby]

        knownness = 0.0
        for b in range(1, M):
            pdiff = (2.0*np.abs(candp*b-knownps)/(candp*b+knownps))

            for knowndm in knowndms[pdiff < 0.002]:
                pdiff_dm = 1.0/(2.0*np.abs(((knowndm)-canddm)/((knowndm)+canddm)))
                knownness=np.max([pdiff_dm,knownness])
        for rat in self.ratios:
            pdiff = 2.0*np.abs(((candp*rat)-knownps)/((candp*rat)+knownps))
            for knowndm in knowndms[pdiff < 0.02]:
                pdiff_dm=1.0/(2.0*np.abs(((knowndm)-canddm)/((knowndm)+canddm)))
                knownness=np.min([pdiff_dm,knownness])
        return knownness

Rater = KnownPulsarRater
