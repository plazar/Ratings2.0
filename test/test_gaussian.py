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
from rating_classes import gaussian

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

    gauss.add_data(cand)

    print "Added gaussian fit to cand"
    pprint.pprint(cand.__dict__)
    print "-"*10
    fit_and_plot(cand)


def fake_profile(cand):
    # Modify profile data and remove existing gaussian fit
    print "create fake profile to fit"
    true_k = 8
    n = 128
    s = 10
    a = 10
    mu = 0.1

    k2 = 30
    a2 = 10
    mu2 = 0.5
    
    true_prof = a*utils.vonmises_histogram(true_k,mu,n) + a2*utils.vonmises_histogram(k2,mu2,n)
    data = true_prof + s*np.random.randn(n)
        
    import copy
    modcand = copy.deepcopy(cand)
    modcand.profile = data
    del modcand.gaussfit
    return modcand

def fit_and_plot(cand):
    data = cand.profile
    n = len(data)
    xs = np.linspace(0.0, 1.0, n, endpoint=False)
    G = gauss._compute_data(cand)
    print "k: %g, log(k): %g" % (G.k, np.log10(G.k))
    test_ks = np.logspace(np.log10(G.k)-2, np.log10(G.k)+1, 1e3)
    #test_ks = np.exp(np.linspace(np.log(1e-1),np.log(1e3),1e3))
    
    plt.figure(1)
    resids = [gauss._rms_residual(k,data) for k in test_ks]
    plt.loglog(test_ks,resids,color="green", label="_nolabel_")
    #plt.axvline(true_k,color="red", label="true k")
    best_k = test_ks[np.argmin(resids)]
    plt.axvline(best_k,color="green", label="best k")
    plt.axvline(G.k,color="cyan", label="k from fit")
    plt.ylabel("RMS of residuals")
    plt.xlabel("Value of k used (i.e. held fixed) when fitting")
    plt.legend(loc="best")

    plt.figure(2)
    mue, ae, be = gauss._fit_all_but_k(best_k, data)
    #plt.plot(xs, true_prof, color="red", label="true")
    plt.plot(xs, data, color="black", label="data")
    plt.plot(xs, (ae*utils.vonmises_histogram(best_k,mue,n)+be), color="green", label="exhaustive best fit")
    plt.plot(xs, G.histogram(n), color="cyan", label="best fit")

    plt.legend(loc="best")
    plt.show()

if __name__=='__main__':
    gauss = gaussian.GaussianProfileClass()
    main()
