class TimeVsPhase(object):
    def __init__(data, p, pd, pdd, dm, starttimes):
        self.data = data
        self.curr_p = p
        self.curr_pd = pd
        self.curr_pdd = pdd
        self.dm = dm
        self.start_secs = starttimes

        self.nsubint, self.nbin = self.data.shape

    def adjust_period(self, p=None, pd=None, pdd=None):
        """
        adjust_period(p=*currp*, pd=*currpd*, pdd=*currpdd*):
            Rotate (internally) the profiles so that they are adjusted
                the given period and period derivatives
        """
        if p is None:
            p = self.curr_p1
        if pd is None:
            pd = self.curr_p2
        if pdd is None:
            pdd = self.curr_p3
        
        # Cast to single precision and back to double precision to
        # emulate prepfold_plot.c, where parttimes is of type "float"
        # but values are upcast to "double" during computations.
        # (surprisingly, it affects the resulting profile occasionally.)
        parttimes = self.start_secs.astype('float32').astype('float64')

        # Get delays
        f, fd, fdd = psr_utils.p_to_f(p, pd, pdd)
        fcurr, fdcurr, fddcurr = psr_utils.p_to_f(self.curr_p1, \
                                                  self.curr_p2, \
                                                  self.curr_p3)
        f_diff = f - fcurr
        fd_diff = fd - fdcurr
        fdd_diff = fdd - fddcurr
        delays = psr_utils.delay_from_foffsets(f_diff, fd_diff, fdd_diff, \
                                                parttimes)

        # Convert from delays in phase to delays in bins
        bin_delays = Num.fmod(delays * self.nbin, self.nbin)
        new_pdelays_bins = Num.floor(bin_delays+0.5)

        # Rotate subintegrations
        for ii in range(self.nsubint):
            tmp_prof = self.profs[ii,:]
            # Negative sign in num bins to shift because we calculated delays
            # Assuming +ve is shift-to-right, psr_utils.rotate assumes +ve
            # is shift-to-left
            self.data[ii,:] = psr_utils.rotate(tmp_prof, \
                                            -new_pdelays_bins[ii])
        
        # Save new p, pd, pdd
        self.curr_p1, self.curr_p2, self.curr_p3 = p, pd, pdd
    

class FreqVsPhase(object):
    def __init__(data, p, pd, pdd, dm, subfreqs):
        self.data = data
        self.p = p
        self.pd = pd
        self.pdd = pdd
        self.curr_dm = dm
        self.subfreqs = subfreqs

        self.nchan = self.nbin = self.data.shape

    def dedisperse(self, DM):
        """
        dedisperse(DM=self.bestdm, interp=0, doppler=0):
            Rotate (internally) the profiles so that they are de-dispersed
                at a dispersion measure of DM.
        """
        dDM = DM - self.curr_dm
        freqs = self.subfreqs
        binspersec = self.nbin/self.p
        
        subdelays = psr_utils.delay_from_DM(dDM, freqs)
        hifreqdelay = subdelays[-1]
        subdelays = subdelays-hifreqdelay
        delaybins = subdelays*binspersec
        new_subdelays_bins = Num.floor(delaybins+0.5)

        for ii in range(self.nchan):
            tmp_prof = self.data[ii,:]
            self.data[ii,:] = psr_utils.rotate(tmp_prof, \
                                            -new_subdelays_bins[ii])
        self.curr_dm = DM
