import numpy as np
import scipy.stats

import psr_utils

import utils

class TimeVsPhase(object):
    def __init__(self, data, p, pd, pdd, dm, starttimes, \
                    ref_f, ref_fd, ref_fdd, pdelays_bins):
        self.data = data
        self.curr_p = p
        self.curr_pd = pd
        self.curr_pdd = pdd
        self.dm = dm
        self.start_secs = starttimes
        self.ref_f = ref_f
        self.ref_fd = ref_fd
        self.ref_fdd = ref_fdd
        self.pdelays_bins = pdelays_bins
    
        self.nsubint, self.nbin = self.data.shape

    def adjust_period(self, p=None, pd=None, pdd=None):
        """
        adjust_period(p=*currp*, pd=*currpd*, pdd=*currpdd*):
            Rotate (internally) the profiles so that they are adjusted
                the given period and period derivatives
        """
        if p is None:
            p = self.curr_p
        if pd is None:
            pd = self.curr_pd
        if pdd is None:
            pdd = self.curr_pdd
        
        # Cast to single precision and back to double precision to
        # emulate prepfold_plot.c, where parttimes is of type "float"
        # but values are upcast to "double" during computations.
        # (surprisingly, it affects the resulting profile occasionally.)
        parttimes = self.start_secs.astype('float32').astype('float64')

        # Get delays
        ref_p, ref_pd, ref_pdd = psr_utils.p_to_f(self.ref_f, \
                                                  self.ref_fd, \
                                                  self.ref_fdd)
        
        #print "DEBUG: in dataproducts.py -- ref_p, ref_pd, pdd", ref_p, ref_pd, pdd
        fdd = psr_utils.p_to_f(ref_p, ref_pd, pdd)[2]
        fd = psr_utils.p_to_f(ref_p, pd)[1]
        f = 1.0/p
        
        f_diff = f - self.ref_f
        fd_diff = fd - self.ref_fd
        if pdd != 0.0:
            fdd_diff = fdd - self.ref_fdd
        else:
            fdd_diff = 0.0
        #print "DEBUG: in dataproducts.py -- self.ref_f, self.ref_fd, self.ref_fdd", self.ref_f, self.ref_fd, self.ref_fdd
        #print "DEBUG: in dataproducts.py -- f, fd, fdd", f, fd, fdd
        #print "DEBUG: in dataproducts.py -- f_diff, fd_diff, fdd_diff", f_diff, fd_diff, fdd_diff
        #print "DEBUG: in dataproducts.py -- parttimes", parttimes
        delays = psr_utils.delay_from_foffsets(f_diff, fd_diff, fdd_diff, \
                                                parttimes)

        # Convert from delays in phase to delays in bins
        bin_delays = np.fmod(delays * self.nbin, self.nbin) - self.pdelays_bins
        new_pdelays_bins = np.floor(bin_delays+0.5)

        # Rotate subintegrations
        for ii in range(self.nsubint):
            tmp_prof = self.data[ii,:]
            # Negative sign in num bins to shift because we calculated delays
            # Assuming +ve is shift-to-right, psr_utils.rotate assumes +ve
            # is shift-to-left
            self.data[ii,:] = psr_utils.rotate(tmp_prof, \
                                            -new_pdelays_bins[ii])
        
        # Save new p, pd, pdd
        self.curr_p, self.curr_pd, self.curr_pdd = p, pd, pdd
        self.pdelays_bins += new_pdelays_bins

    def get_profile(self):
        prof = self.data.sum(axis=0).squeeze()
        return prof


class FreqVsPhase(object):
    def __init__(self, data, p, pd, pdd, dm, subfreqs, binspersec, \
                    ref_dm, subdelays_bins):
        self.data = data
        self.p = p
        self.pd = pd
        self.pdd = pdd
        self.curr_dm = dm
        self.subfreqs = subfreqs
        self.binspersec = binspersec
        self.ref_dm = ref_dm
        self.subdelays_bins = subdelays_bins

        self.nchan, self.nbin = self.data.shape

    def get_delaybins(self, dm):
        subdelays = psr_utils.delay_from_DM(dm, self.subfreqs)
        hifreqdelay = subdelays[-1]
        subdelays = subdelays-hifreqdelay
        delaybins = subdelays*self.binspersec
        return np.floor(delaybins+0.5)
        

    def dedisperse(self, DM):
        """
        dedisperse(DM=self.bestdm, interp=0, doppler=0):
            Rotate (internally) the profiles so that they are de-dispersed
                at a dispersion measure of DM.
        """
        new_subdelays_bins = self.get_delaybins(DM) - \
                                self.subdelays_bins
        
        #print "DEBUG: in dataproducts -- DM, self.curr_dm, new_subdelays_bins:", DM, self.curr_dm, new_subdelays_bins
        #print "DEBUG: in dataproducts -- DM, self.get_delaybins(self.curr_dm)-self.subdelays_bins:", DM, self.curr_dm, self.get_delaybins(self.curr_dm)-self.subdelays_bins
        for ii in range(self.nchan):
            tmp_prof = self.data[ii,:]
            self.data[ii,:] = psr_utils.rotate(tmp_prof, \
                                            new_subdelays_bins[ii])
        self.curr_dm = DM
        self.subdelays_bins += new_subdelays_bins
    
    def get_profile(self):
        prof = self.data.sum(axis=0).squeeze()
        return prof


class GaussianFit(object):
    def __init__(self, k, mu=0.0, a=1.0, b=0.0):
        if k < 0:
            raise ValueError("Negative values of k simply shift the phase " \
                                "by 0.5; please do not supply them")
        self.k = float(k)
        self.mu = float(mu)
        self.a = float(a)
        self.b = float(b)

    def __repr__(self):
        return "<%s k=%g mu=%g a=%g b=%g>" % \
                    (type(self), self.k, self.mu, self.a, self.b)

    def max(self):
        return self(self.mu)

    def min(self):
        return self(self.mu + 0.5)

    def amplitude(self, n=None, peak_to_peak=True):
        if n is None:
            if peak_to_peak:
                return self.max() - self.min()
            else:
                return self.max() - self.b
        else:
            h = self.histogram(n)
            if peak_to_peak:
                return np.amax(h) - np.amin(h)
            else:
                return np.amax(h) - self.b

    def area(self, peak_to_peak=True):
        if peak_to_peak:
            return self.a - self.min()
        else:
            return self.a

    def histogram(self, n):
        return self.a*utils.vonmises_histogram(self.k, self.mu, n) + self.b

    def __call__(self, x):
        return self.a*utils.vonmises_values(self.k, self.mu, x) + self.b

    def fwhm(self):
        s_height = (np.exp(-2*self.k) + 1)/2.
        return 2*np.arccos(1 + np.log(s_height)/self.k)/(2*np.pi)


class MultiGaussComponent(object):
    def __init__(self, amp, std, phs):
        """Constructor for MultiGaussComponent, an object to represent
            a single gaussian component of a multiple-gaussian fit to
            a profile.

            Inputs:
                amp: The amplitude of the gaussian component.
                std: The standard deviation of the gaussian component.
                phs: The phase of the gaussian component.

            Output:
                component: The MultiGaussComponent object.
        """
        self.amp = amp
        self.std = std
        self.phs = phs

    def __str__(self):
        s = "Amplitude: %g, Std Dev: %g, Phase: %g" % \
                    (self.amp, self.std, self.phs)
        return s

    def make_gaussian(self, nbins):
        """Return an aray of length 'nbins' containing the gaussian component.

           Inputs:
               nbins: The number of bins in the profile
 
           Output:
               gaussian: Array of data
           
        """
        # Create an array of phase bins going from 0 --> 1
        bins = np.arange(nbins, dtype=np.float)/nbins

        # Create an array for the Gaussian profile
        gaussian = self.amp*np.sqrt(2*np.pi*self.std**2) * \
                    scipy.stats.vonmises.pdf(bins, 1/self.std, loc=self.phs, \
                                                scale=1.0/(2.0*np.pi))
                    #scipy.stats.norm.pdf(bins, loc=self.phs, scale=self.std)
        return gaussian


class MultiGaussFit(object):
    def __init__(self, offset=0.0, components=[]):
        """Constructor for MultiGaussFit, a multiple-gaussian fit to
            a profile.

            Inputs:
                offset: The DC offset of the fit. (Default: 0.0)
                components: A list of MultiGaussComponents making up the
                    fit to the profile. (Default: No components)

            Output:
                fit: The MultiGaussFit object.
        """
        self.offset = offset
        self.components = components

    def __str__(self):
        lines = ["Multi-Gaussian fit with %d components" % \
                    len(self.components)]
        lines.append("    Offset: %g" % self.offset)
        for ii, comp in enumerate(self.components):
            lines.append("    Component %d: %s" % (ii+1, str(comp)))
        return '\n'.join(lines)

    def add_component(self, comp):
        """Add a component to the MultiGaussianFit.
            
            Input:
                comp: A MulitGaussComponent to add.

            Outputs:
                None
        """
        self.components.append(comp)

    def make_gaussians(self, nbins):
        """Return an array of length 'nbins' containing the gaussian fit.

           Inputs:
               nbins: The number of bins in the profile
 
           Output:
               gaussian: Array of data
           
        """
        # Determine the number of Gaussian profiles to make
        ngaussians = len(self.components)
        
        # Create an array of phase bins going from 0 --> 1
        bins = np.arange(nbins, dtype=np.float)/nbins

        # Create an array for the Gaussian profile
        gaussians = np.zeros_like(bins) + self.offset

        # Add each individual Gaussian to the full profile
        for comp in self.components:
            #print "DEBUG: comp.amp, comp.std, comp.phs", comp.amp, comp.std, comp.phs
            gaussians += comp.make_gaussian(nbins)
        return gaussians

    def get_resids(self, data):
        model = self.make_gaussians(len(data))
        resids = data - model
        return resids 
    
    def get_chisqr(self, data):
        resids = self.get_resids(data)
        return np.sum(resids**2)

    def get_dof(self, nbins):
        return nbins - self.get_num_params()

    def get_num_params(self):
        return 1 + 3*len(self.components)

    def plot_comparison(self, data, individual=False, show=False):
        import matplotlib.pyplot as plt
        fig = plt.figure()
        phases = np.linspace(0.0, 1.0, len(data), endpoint=False)
        phases_10x = np.linspace(0.0, 1.0, len(data)*10, endpoint=False)

        ax = plt.axes([0.1, 0.1, 0.85, 0.65])
        plt.plot(phases, data, c='k', label="Profile")
        
        plt.plot(phases_10x, self.make_gaussians(len(data)*10), c='r', label="Fit")
        if individual:
            for comp in self.components:
                plt.plot(phases_10x, self.offset+comp.make_gaussian(len(data)*10), ls='--')
        plt.xlabel("Phase")
        plt.ylabel("Intensity (arbitrary units)")
        plt.legend(loc='best')
        
        ax = plt.axes([0.1, 0.75, 0.85, 0.15], sharex=ax)
        plt.plot(phases, self.get_resids(data), c='k')
        plt.axhline(0.0, color='k', ls='--')
        plt.ylabel("Residuals")
        plt.setp(ax.xaxis.get_ticklabels(), visible=False)
        if show:
            plt.show()

