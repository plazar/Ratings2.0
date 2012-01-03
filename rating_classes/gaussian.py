import scipy.optimize
import numpy as np

import profile
import dataproducts
import utils

class GaussianProfileClass(profile.ProfileClass):
    data_key = "gaussfit"

    def _compute_data(self, cand):
        """Fit the candidate's profile and return the fit's parameters.

            Input:
                cand: A ratings2.0 Candidate object.

            Output:
                gaussfit: The corresponding fit. A GaussianFit object.
        """
        k_for_fwhm_approx = lambda fwhm: np.log(2)/(1-np.cos(np.pi*fwhm))
        
        profile = cand.profile
        ks = [k_for_fwhm_approx(fwhm/float(len(profile))) for fwhm in range(1,len(profile)//2)]
        pos = int(np.argmin([self._rms_residual(k,profile) for k in ks]))

        if pos==0:
            mid = ks[0]
            left = ks[1]
            right = 10*ks[0]
        elif pos==len(ks)-1:
            left = 0
            mid = ks[-1]
            right = ks[-2]
        else:
            left = ks[pos+1]
            mid = ks[pos]
            right = ks[pos-1]
 
        k = scipy.optimize.fminbound(lambda k: self._rms_residual(k, profile), \
                                                left, right)
        mu, a, b = self._fit_all_but_k(k, profile)
        return dataproducts.GaussianFit(k, mu, a, b)

    @classmethod
    def _fit_all_but_k(cls, k, data):
        n = len(data)
        fft = np.fft.rfft(data)
        nup = 16*n
        corr = np.fft.irfft(fft*utils.vonmises_coefficient(k, np.arange(len(fft))), nup)
        mu = np.argmax(corr)/float(nup)

        x = utils.vonmises_histogram(k, mu, n)

        data = data - np.mean(data)
        x = x - np.mean(x)
        a = np.dot(data, x)/np.dot(x, x)

        b = np.mean(data) - a*np.mean(x)

        return mu, a, b

    @classmethod
    def _rms_residual(cls, k, data):
        n = len(data)
        mu, a, b = cls._fit_all_but_k(k, data)
        return np.sqrt(np.mean((data-(a*utils.vonmises_histogram(k,mu,n)+b))**2))
