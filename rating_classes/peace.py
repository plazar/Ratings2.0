import subprocess

import cand_info

KEYS = ['snr', \
        'pulsewidthA', \
        'pulsewidthB', \
        'persistenceA', \
        'persistenceB', \
        'broadbandednessA', \
        'broadbandednessB', \
        'DM', \
        'unused', \
        'DMsmearing', \
        'period', \
        'scoreA', \
        'scoreB', \
        'scoreC']

class PeaceRatingClass(cand_info.CandInfoRatingClass):
    data_key = "peace"

    def _compute_data(self, cand):
        """Run KJ Lee's PEACE on the pfd file. Parse the
            output and store the scores.

            NOTES: 
                - PEACE can be found on sourceforge at
                    http://sourceforge.net/p/pulsareace/wiki/Home/
                - PEACE's bin directory needs to be found in the
                    PATH environment variable.

            Input:
                cand: A ratings2.0 Candidate object.

            Output:
                peace: A dictionary of PEACE scores.
        """
        pfdfn = cand.info['pfdfn']
        cmd = ['autos2.exe', '-f', pfdfn, '-ostd']
        pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, \
                                    stderr=subprocess.PIPE)
        stdoutdata, stderrdata = pipe.communicate()
        retcode = pipe.returncode 
        if retcode < 0:
            raise utils.RatingError("Execution of command (%s) " \
                                        "terminated by signal (%s)!" % \
                                    (cmd, -retcode))
        elif retcode > 0:
            raise utils.RatingError("Execution of command (%s) failed " \
                                    "with status (%s)!\nError output:\n%s" % \
                                    (cmd, retcode, stderrdata))
        else:
            # Exit code is 0, which is "Success". Do nothing.
            pass
        scores = [float(xx) for xx in stdoutdata.strip().split()[1:]]
        peace = dict(zip(KEYS, scores))
        return peace
