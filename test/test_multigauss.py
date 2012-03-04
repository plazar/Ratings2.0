import pprint
import sys
import numpy as np

import candidate
from rating_classes import multigauss

def main():
    pfdfn = sys.argv[1]

    cand = candidate.read_pfd_file(pfdfn)

    print "Loaded %s" % cand.pfdfn
    print "    Best topo period (s): %f" % cand.topo_period
    print "    Best bary period (s): %f" % cand.bary_period
    print "    Best DM (cm^-3/pc): %f" % cand.dm
    print "    RA (J2000 - deg): %f" % cand.raj_deg
    print "    Dec (J2000 - deg): %f" % cand.decj_deg

    #print "-"*10
    #pprint.pprint(cand.__dict__)
    #print "-"*10

    mgauss.add_data(cand)

    print "Added multi-gaussian fit to cand"
    #pprint.pprint(cand.__dict__)
    #print "-"*10

    print cand.multigaussfit

    data = cand.profile.copy()
    data /= np.sqrt(cand.pfd.varprof)
    data -= data.mean()
    cand.multigaussfit.plot_comparison(data, True)


if __name__ == '__main__':
    mgauss = multigauss.MultipleGaussianProfileClass()
    main()
