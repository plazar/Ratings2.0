import scipy.stats
import scipy.special
import numpy as np

def vonmises_coefficient(k,m):
    return scipy.special.ive(m,k)/scipy.special.ive(0,k)


def vonmises_values(k,mu,xs):
    distribution = scipy.stats.vonmises(k,scale=1./(2*np.pi))
    return distribution.pdf((xs-mu)%1)


def vonmises_histogram(k,mu,n,factor=2):
    if n % 2:
        raise ValueError("n (%d) must be even" % n)
    m = ((n*factor)//2+1)
    coeffs = vonmises_coefficient(k,np.arange(m)) * \
                np.exp(-2.0j*np.pi*mu*np.arange(m))*n*factor
    longhist = 1.0 + np.fft.irfft(coeffs*(np.exp(2.0j * \
                                   np.pi*1.0/n*np.arange(m))-1) / \
                   (np.maximum(np.arange(m), 1)*2.0j*np.pi))*n*factor
    return np.mean(np.reshape(longhist, (n,factor)), axis=-1)/factor

