import sys
import pprint
import subprocess
import os

import numpy as np
import matplotlib.pyplot as plt

import myprepfold
import psr_utils

import candidate


def test_img(img1, img2, threshold=0.001):
    mean_img = (img1+img2)/2.0
    return np.all(np.abs(img1-img2)/mean_img<threshold)


def main():
    pfdfn = sys.argv[1]

    pfd = myprepfold.pfd(pfdfn)

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

    from rating_classes import time_vs_phase
    time_vs_phase.TimeVsPhaseClass().add_data(cand)
    tvph = cand.time_vs_phase

    print "Added time vs phase data to cand"
    pprint.pprint(cand.__dict__)
    print "-"*10

    pprint.pprint(cand.time_vs_phase.__dict__)

    print "DEBUG: tvph.pdelays_bins", tvph.pdelays_bins
    print "DEBUG: pfd.pdelays_bins", pfd.pdelays_bins
    
    pfd.dedisperse(doppler=1)
    print "DEBUG: tvph.dm, pfd.currdm", tvph.dm, pfd.currdm
    
    if pfd.fold_pow == 1.0:
        bestp = pfd.bary_p1
        bestpd = pfd.bary_p2
        bestpdd = pfd.bary_p3
    else:
        bestp = pfd.topo_p1
        bestpd = pfd.topo_p2
        bestpdd = pfd.topo_p3

    pfd.adjust_period()
    tvph.adjust_period(bestp, bestpd, bestpdd)
    mypfd_tvph = pfd.time_vs_phase()
    print test_img(tvph.data, mypfd_tvph, 1e-6)
    plt.figure()
    plt.plot(tvph.data.sum(axis=0), label='TvPh')
    plt.plot(mypfd_tvph.sum(axis=0), label='PFD')
    plt.title("P=%g s, Pd=%g s/s, Pdd=%g s/s^2" % (bestp, bestpd, bestpdd))
    plt.legend(loc='best')
    for ii in range(10):
        frac_p = 1+(np.random.rand(1)*2-1)/100.0
        frac_pd = 1+(np.random.rand(1)*2-1)/100.0
        frac_pdd = 1+(np.random.rand(1)*2-1)/100.0
        p = frac_p*bestp
        pd = frac_pd*bestpd
        pdd = frac_pdd*bestpdd
        print "Shuffling for the %dth time" % ii
        print "frac_p, frac_pd, frac_pdd", frac_p, frac_pd, frac_pdd

        tvph.adjust_period(p, pd, pdd)
        mypfd_tvph = pfd.time_vs_phase(p, pd, pdd)
        print test_img(tvph.data, mypfd_tvph, 1e-9)

        plt.figure()
        plt.plot(tvph.data.sum(axis=0), label='TvPh')
        plt.plot(mypfd_tvph.sum(axis=0), label='PFD')
        plt.title("P=%g s, Pd=%g s/s, Pdd=%g s/s^2" % (p, pd, pdd))
        plt.legend(loc='best')
    plt.show()
    sys.exit(1)

    print "Check if time_vs_phase rotates out and back to same array"
    orig = cand.time_vs_phase.data.copy()
    orig_p = cand.time_vs_phase.curr_p
    orig_pd = cand.time_vs_phase.curr_pd
    orig_pdd = cand.time_vs_phase.curr_pdd
    cand.time_vs_phase.adjust_period(p=orig_p-0.00123, pd=0, pdd=0)
    mod = cand.time_vs_phase.data.copy()
    cand.time_vs_phase.adjust_period(p=orig_p, pd=orig_pd, pdd=orig_pdd)
    new = cand.time_vs_phase.data.copy()

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
    prof = np.loadtxt(os.path.split(cand.pfd.pfd_filename+".bestprof")[-1], usecols=(1,))

    pfd = cand.pfd
    if pfd.fold_pow == 1.0:
        bestp = pfd.bary_p1
        bestpd = pfd.bary_p2
        bestpdd = pfd.bary_p3
    else:
        bestp = pfd.topo_p1
        bestpd = pfd.topo_p2
        bestpdd = pfd.topo_p3
    cand.time_vs_phase.adjust_period(bestp, bestpd, bestpdd)
    tvph = pfd.time_vs_phase()
    print test_img(cand.time_vs_phase.data, tvph, 1e-6)
    plt.plot(cand.time_vs_phase.get_profile())
    plt.plot(tvph.sum(axis=0).squeeze())
    plt.show()

if __name__ == '__main__':
    main()
