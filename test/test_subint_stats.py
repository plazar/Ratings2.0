import sys
import pprint
import subprocess
import os

import numpy as np
import matplotlib.pyplot as plt

import prepfold
import psr_utils

import candidate
import utils
from rating_classes import subint_stats

def main():
    pfdfn = sys.argv[1]

    pfd = prepfold.pfd(pfdfn)

    cand = candidate.Candidate(pfd.topo_p1, pfd.bary_p1, pfd.bestdm, \
                        psr_utils.ra_to_rad(pfd.rastr)*psr_utils.RADTODEG, \
                        psr_utils.dec_to_rad(pfd.decstr)*psr_utils.RADTODEG, \
                        pfdfn)

    print "Loaded %s" % cand.pfdfn
    print "    Best topo period (s): %f" % cand.topo_period
    print "    Best bary period (s): %f" % cand.bary_period
    print "    Best DM (cm^-3/pc): %f" % cand.dm
    print "    RA (J2000 - deg): %f" % cand.raj_deg
    print "    Dec (J2000 - deg): %f" % cand.decj_deg

    print "-"*10
    pprint.pprint(cand.__dict__)
    print "-"*10

    intstats.add_data(cand)

    print "Added subint stats to cand"
    pprint.pprint(cand.__dict__)
    print "-"*10


if __name__=='__main__':
    intstats = subint_stats.SubintPulseWindowStats()
    main()

