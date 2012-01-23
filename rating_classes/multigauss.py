import numpy as np
import scipy.stats
import mpfit
import psr_utils

import utils
from rating_classes import profile

"""
Multiple Gaussian component fitting to pulse profiles.

Copied from Ryan Lynch's code for the orignal Ratings project.
"""

class MultipleGaussianProfileClass(profile.ProfileClass):
    data_key = "multigaussfit"
    
    # The maximum number of Gaussian components to fit
    max_gaussians = 5

    # The threshold probability that the improvement in a fit from an additional
    # profile component is due to chance (as calculated via an F-test) for
    # rejecting additinal Gaussian profiles
    F_stat_threshold = 0.01
    
    def _compute_data(self, cand):
        """Fit the candidate's profile with mulitple gaussian
            components and return the fit's parametrs.

            Input:
                cand: A ratings2.0 Candidate object.

            Output:
                multigaussfit: The corresponding fit. A MultiGaussFit object.
        """
        data = cand.profile.copy()
        data /= np.sqrt(cand.pfd.varprof)
        data -= data.mean()

        # Initialize some starting values
        nbins      = len(data)
        ngaussians = 0
        # After normalization the first parameter (offset) should be close to zero
        prev_params = [0.0]
        # Nothing fit yet, so residuals are just the data values
        prev_residuals = data - np.zeros_like(data) 
        # No need to normalize chi^2 by variance since we already did that to the
        # data
        prev_chi2  = sum(prev_residuals*prev_residuals)
        prev_dof   = nbins
        fit        = True
 
        # We will now start fitting Gaussian profile components until the
        # additional components are no longer statistically needed to improve the
        # fit.  The starting parameter guesses for each new component will come
        # from the highest remaining residual and from the previous best-fit values
        # for previous components
        while fit:
            ngaussians  += 1
            # Update values based on results of previous run
            trial_params = list(prev_params)
 
            # Guess the parameters for the next profile component
            amplitude = max(prev_residuals)
            # Base std_dev on stats.norm normalization
            std_dev   = 1/(np.sqrt(2*np.pi)*amplitude)
            phase     = np.argmax(prev_residuals)/float(nbins)
            trial_params.append(amplitude)
            trial_params.append(std_dev)
            trial_params.append(phase)
            if 0:
                # params_dict is used by mpfit to get initial values and constraints on
                # parameters
                params_dict = []
                for ii,param in enumerate(trial_params):
                    if ii == 0:
                        # The first parameter is the offset, which can be negative and
                        # should be allowed to vary more
                        params_dict.append({"value"  : param,
                                            "fixed"  : False,
                                            "limited": [False,False],
                                            "limits" : [0.0,0.0]})
                    else:
                        # Limits are set assuming that our initial guesses were correct
                        # to within 25%...
                        params_dict.append({"value"  : param,
                                            "fixed"  : False,
                                            "limited": [True,True],
                                            "limits" : [0.25*param,1.75*param]})

                # Define the fitting function for mpfit
                def func(params, fjac=None, errs=None):
                    fit = utils.multigaussfit_from_paramlist(params)
                    # Return values are [status, residuals]
                    return [0, fit.get_resids(data)]
             
                # Now fit
                mpfit_out     = mpfit.mpfit(func, parinfo=params_dict, quiet=True)
                # Store the new best-fit parameters
                new_params    = mpfit_out.params
            else:
                import scipy.optimize
                def func(params):
                    #print "DEBUG: params", params
                    fit = utils.multigaussfit_from_paramlist(params)
                    return fit.get_resids(data)

                new_params, status = scipy.optimize.leastsq(func, trial_params)
                if status not in (1,2,3,4):
                    raise utils.RatingError("Status returned by " \
                                        "scipy.optimize.leastsq (%d) " \
                                        "indicates the fit failed!" % status)

            # Calculate the new residuals and statistics
            new_fit = utils.multigaussfit_from_paramlist(new_params)
            #print "DEBUG: new_fit", new_fit
            new_residuals = new_fit.get_resids(data)
            new_chi2      = new_fit.get_chisqr(data)
            new_dof       = new_fit.get_dof(len(data)) # Degrees-of-freedom
            # Calculate the F-statistic for the fit, i.e. the probability that the
            # additional profile component is /not/ required by the data
            F_stat        = psr_utils.Ftest(prev_chi2, prev_dof, \
                                                new_chi2, new_dof)
 
            # If the F-test probability is greater than some threshold, then the
            # additional Gaussian did not significantly improve the fit and we
            # should stop.  The nan test is needed because if the fit is /worse/
            # then Ftest doesn't return a valid number.  Also stop if we reach
            # the maximum number of Gaussian profile components
            if F_stat > self.F_stat_threshold or np.isnan(F_stat) \
                   or ngaussians > self.max_gaussians:
                fit    = False
            # Otherwise, keep fitting and update the parameters for the next pass
            else:
                fit            = True
                prev_params    = new_params
                prev_residuals = new_residuals
                prev_chi2      = new_chi2
                prev_dof       = new_dof
 
        # We stop when a fit is no longer needed, so we have to return the values
        # from the /previous/ run (otherwise we return the unneeded fit)
        #print "DEBUG: prev_params", prev_params
        finalfit = utils.multigaussfit_from_paramlist(prev_params)
        #print "DEBUG: finalfit", finalfit
        return finalfit 
