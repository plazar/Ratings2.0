import pprint
import sys
import numpy as np
import matplotlib.pyplot as plt
import candidate
import utils

from rating_classes import multivonmises

import profile_tools

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

    vm.add_data(cand)

    print "Added multi-vonmises fit to cand"
    #pprint.pprint(cand.__dict__)
    #print "-"*10

    print cand.multivonmisesfit

    data = cand.profile.copy()
    data /= np.sqrt(cand.pfd.varprof)
    data -= data.mean()
    
    cand.multivonmisesfit.plot_comparison(data, True)
    plt.show()

if __name__ == '__main__':
    vm = multivonmises.MultipleVonMisesProfileClass()
    main()
