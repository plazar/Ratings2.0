import sys
import pprint
import subprocess
import os

import numpy as np
import matplotlib.pyplot as plt

import prepfold
import psr_utils

import candidate

def test_profiles(prof1, prof2, threshold=0.001):
    mean_prof = (prof1+prof2)/2.0
    return np.all(np.abs(prof1-prof2)/mean_prof<threshold)


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

    from rating_classes import freq_vs_phase
    fvph = freq_vs_phase.FreqVsPhaseClass()
    fvph.add_data(cand)

    print "Added freq vs phase data to cand"
    pprint.pprint(cand.__dict__)
    print "-"*10

    pprint.pprint(cand.freq_vs_phase.__dict__)

    print "Check if freq_vs_phase rotates out and back to same array"
    orig = cand.freq_vs_phase.data.copy()
    orig_dm = cand.freq_vs_phase.curr_dm
    cand.freq_vs_phase.dedisperse(0)
    mod = cand.freq_vs_phase.data.copy()
    cand.freq_vs_phase.dedisperse(orig_dm)
    new = cand.freq_vs_phase.data.copy()

    print "Compare orig/mod"
    print (orig == mod).all()
    print "Compare mod/new"
    print (mod == new).all()
    print "Compare orig/new"
    print (orig == new).all()

    print "Compare with best prof"
    # Create best prof file
    print "show_pfd -noxwin %s" % cand.info['pfdfn']
    subprocess.call("show_pfd -noxwin %s" % cand.info['pfdfn'], shell=True, stdout=open(os.devnull))
    pfd_bestprof = np.loadtxt(os.path.split(cand.pfd.pfd_filename+".bestprof")[-1], usecols=(1,))

    cand.freq_vs_phase.dedisperse(cand.pfd.bestdm)
    fvph_prof = cand.freq_vs_phase.data.sum(axis=0).squeeze()
    print test_profiles(pfd_bestprof, fvph_prof, 1e-6)
    
    print "Testing dedispersion"
    for dm in np.random.randint(0, 1000, size=10):
        print "DM: %g" % dm,
        cand.freq_vs_phase.dedisperse(dm)
        fvph_prof = cand.freq_vs_phase.get_profile(remove_offset=False)

        cand.pfd.dedisperse(dm, doppler=1)
        cand.pfd.adjust_period()
        pfd_prof = cand.pfd.time_vs_phase().sum(axis=0).squeeze()
        print test_profiles(fvph_prof, pfd_prof, 1e-6)
        #plt.figure(dm)
        #plt.plot(fvph_prof, label="FvsPh")
        #plt.plot(pfd_prof, label="PFD")
        #plt.title("DM: %g" % dm)
        #plt.legend(loc='best')
    #plt.show()

if __name__=='__main__':
    main()
