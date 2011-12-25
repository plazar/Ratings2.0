import sys
import pprint
import subprocess
import os

import numpy as np
import matplotlib.pyplot as plt

import prepfold
import psr_utils

import candidate

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

from rating_classes import time_vs_phase
tvph = time_vs_phase.TimeVsPhaseClass()
tvph.add_data(cand)

print "Added time vs phase data to cand"
pprint.pprint(cand.__dict__)
print "-"*10

pprint.pprint(cand.time_vs_phase.__dict__)

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
prof3 = tvph.sum(axis=0).squeeze()
print (cand.time_vs_phase.data == tvph).all()
prof2 = cand.time_vs_phase.data.sum(axis=0).squeeze()
prof4 = np.array([float("%.7g" % x) for x in prof2])
print (prof == prof2).all()
print (prof == prof3).all()
print (prof2 == prof3).all()
print (prof == prof4).all()

plt.plot(prof)
plt.plot(prof2)
plt.plot(prof4)
plt.show()
