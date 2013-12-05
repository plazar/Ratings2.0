#!/usr/bin/env python
import sys
import argparse
import copy
import multiprocessing
import traceback
import textwrap
import tempfile
import shutil
import subprocess
import os
import os.path
import numpy as np

import candidate
import raters
import database
import utils
import config

DBNAME = "common3"
#DBNAME = "common-copy"

def rate_pfd(pfdfn, rater_instances):
    """Given the name of a *.pfd file and a list of Rater instances
        compute the ratings.

        Inputs:
            pfdfn: Name of the *.pfd file.
            rater_instances: A list of Rater instances to compute ratings.

        Outputs:
            cand: The resulting (rated) Candidate object.

        ***NOTE: RatingValues are added directly to the Candidate object.
    """
    cand = candidate.read_pfd_file(pfdfn)
    for rater in rater_instances:
        ratval = rater.rate(cand)
        cand.add_rating(ratval)
    return cand


def download_many(ftpfns, outdir):
    """Download multiple files from the cornell FTP server to
        the specified output directory.

        Input:
            ftpfns: A list of files on the FTP server to get.
            outdir: The directory to put downloaded files in.

        Outputs:
            None
    """ 
    lftp_cmd = '"get -e -O %s %s"' % (outdir, " ".join(ftpfns))
    cmd = "lftp -c 'open -e %s -u %s,%s -p 31001 arecibo.tc.cornell.edu'" % \
             (lftp_cmd, config.ftp_username, config.ftp_password)
    if subprocess.call(cmd, stdout=open(os.devnull), shell=True) != 0:
        raise ValueError("FTPing files failed (%s)" % cmd)


def get_beams_to_rate(rat_inst_id):
    """Given a pdm_rating_instance_id value from the database
        return a list of header_id values that have candidates
        that need to be rated by this rating instance.

        Input:
            rat_inst_id: Rating instance ID value.
        
        Output:
            header_ids: Header ID values for beams that have candidates
                to be rated by this rating instance.
    """
    db = database.Database(DBNAME)

    # get header IDs of candidates that are missing this rating
    db.execute("SELECT h.header_id " \
               "FROM pdm_candidates AS c WITH(NOLOCK) " \
               "LEFT JOIN headers AS h WITH(NOLOCK) " \
                   "ON c.header_id=h.header_id " \
               "LEFT JOIN pdm_rating AS r WITH(NOLOCK) " \
                   "ON c.pdm_cand_id=r.pdm_cand_id " \
                       "AND r.pdm_rating_instance_id=? " \
               "WHERE r.pdm_rating_instance_id IS NULL " \
               "GROUP BY h.header_id", rat_inst_id)
    rows = db.fetchall()
    header_ids = [row[0] for row in rows]
    return header_ids
   

def get_pfds_from_db(header_id):
    """Given a header ID value download the associated candidates'
        pfds from the database to a temporary directory. 
        Return the path to the temp dir.

        Input:
            header_id: The header ID value to download pfds for.

        Output:
            tempdir: The temporary directory containing the pfds.
            fn_mapping: A dictionary mapping pdm_cand_id to pfd filename.
    """
    db = database.Database(DBNAME)
    # Get paths/filenames for uploaded pfds
    query = "SELECT c.pdm_cand_id, cpl.filename, cpl.filedata " \
            "FROM PDM_Candidate_plots AS cpl WITH(NOLOCK) " \
            "LEFT JOIN pdm_candidates AS c WITH(NOLOCK) " \
                "ON c.pdm_cand_id=cpl.pdm_cand_id " \
            "WHERE c.header_id=?"
    db.execute(query, header_id)
    
    # Create temporary directory
    tempdir = tempfile.mkdtemp(suffix='ratings2')
   
    try:
        fn_mapping = {}
        pfds_to_get = []
        for cand_id, fn, data in db.fetchall():
            fn_mapping[cand_id] = fn
            # Download the file
            f = open(os.path.join(tempdir, fn), 'w')
            f.write(data)
            f.close()
    except:
        shutil.rmtree(tempdir)
        raise

    return tempdir, fn_mapping


def get_pfds_from_ftp(header_id):
    """Given a header ID value download the associated candidates'
        pfds from the FTP server to a temporary directory. 
        Return the path to the temp dir.

        Input:
            header_id: The header ID value to download pfds for.

        Output:
            tempdir: The temporary directory containing the pfds.
            fn_mapping: A dictionary mapping pdm_cand_id to pfd filename.
    """
    db = database.Database(DBNAME)
    # Get paths/filenames for uploaded pfds
    query = "SELECT cbf.pdm_cand_id, " \
                "cbf.file_location, " \
                "cbf.filename " \
            "FROM pdm_candidate_binaries_filesystem AS cbf WITH(NOLOCK) " \
            "LEFT JOIN pdm_candidates AS c WITH(NOLOCK) " \
                "ON c.pdm_cand_id=cbf.pdm_cand_id " \
            "WHERE c.header_id=? AND cbf.uploaded=1"
    db.execute(query, header_id)
    
    # Create temporary directory
    tempdir = tempfile.mkdtemp(suffix='ratings2')
    
    try:
        fn_mapping = {}
        pfds_to_get = []
        for cand_id, ftp_path, fn in db.fetchall():
            fn_mapping[cand_id] = fn
            pfds_to_get.append(os.path.join(ftp_path, fn))

        if pfds_to_get:
            # Download files
            download_many(pfds_to_get, tempdir)
    except:
        shutil.rmtree(tempdir)
        raise

    return tempdir, fn_mapping


def main():
    if args.num_procs > 1:
        warning.warn("Multithreading not implemnted (%d threads requested)" % \
                            args.num_procs)
    
    if not args.raters:
        print "No raters are loaded."
        args.list_raters = True

    if args.list_raters:
        utils.print_raters_list(args.verbosity)
        sys.exit(0)

    rat_inst_id_cache = utils.RatingInstanceIDCache(DBNAME)
    loaded_raters = {}
    for rater_name in args.raters:
        rater_module = getattr(raters, rater_name)
        rater = rater_module.Rater()
        loaded_raters[(rater.long_name, rater.version)] = rater
  
    db = database.Database(DBNAME)
    try:
        for rater in loaded_raters.values():
            rating_instance_id = rat_inst_id_cache.get_id(rater.long_name, \
                                                          rater.version, \
                                                          rater.description)
            header_ids = get_beams_to_rate(rating_instance_id)
            print "For rater %s have %d beams to rate." % (rater.long_name,len(header_ids))

            for header_id in header_ids:
                # For candidates with this header_id find which current ratings 
                # are not computed.
                #
                # NOTE: We use 'r.pdm_rating_instance_id' in the WHERE clause
                # because it will be NULL if a rating does not exist in
                # the 'pdm_rating' table. However, it _will_ be set if the rating
                # exists, but has a value of NULL (i.e. the rating failed). 
                # If we were used 'r.value' instead, we would try to re-compute
                # failed ratings.
                query = "SELECT c.pdm_cand_id, " \
                            "rt.name, " \
                            "ri.version " \
                        "FROM pdm_candidates AS c WITH(NOLOCK) " \
                        "CROSS JOIN (SELECT rt.pdm_rating_type_id, " \
                                        "MAX(ri.pdm_rating_instance_id) " \
                                            "AS current_instance_id " \
                                    "FROM pdm_rating_instance AS ri WITH(NOLOCK) " \
                                    "LEFT JOIN pdm_rating_type AS rt WITH(NOLOCK) " \
                                        "ON ri.pdm_rating_type_id=rt.pdm_rating_type_id " \
                                    "GROUP BY rt.pdm_rating_type_id) AS ci " \
                        "LEFT JOIN pdm_rating_instance AS ri WITH(NOLOCK) " \
                            "ON ri.pdm_rating_instance_id=ci.current_instance_id " \
                        "LEFT JOIN pdm_rating AS r WITH(NOLOCK) " \
                            "ON r.pdm_cand_id=c.pdm_cand_id " \
                                "AND ri.pdm_rating_instance_id=r.pdm_rating_instance_id " \
                        "LEFT JOIN pdm_rating_type AS rt WITH(NOLOCK) " \
                            "ON rt.pdm_rating_type_id=ri.pdm_rating_type_id " \
                        "WHERE c.header_id=? AND r.pdm_rating_instance_id IS NULL"
                db.execute(query, header_id)
                missing_ratings = db.fetchall()
 
                if not missing_ratings:
                    raise utils.RatingError("At least the current rating (%s) should " \
                                        "be missing for header_id=%d. (This is how the header "
                                        "IDs were selected.)" % (rater.long_name, header_id))
 
                # Get pfds for this header_id
                if DBNAME == 'common2' or DBNAME == 'common3':
                    tmpdir, fn_mapping = get_pfds_from_ftp(header_id)
                else:
                    tmpdir, fn_mapping = get_pfds_from_db(header_id)
 
                try:
                    rated_cands = []
                    # Rate pfds for this header_id
                    for cand_id, pfd_fn in fn_mapping.iteritems():
                        raters_to_use = [loaded_raters[(x[1], x[2])] for x in missing_ratings \
                                            if x[0]==cand_id and (x[1], x[2]) in loaded_raters]
                        cand = rate_pfd(os.path.join(tmpdir, pfd_fn), raters_to_use)
                        
                        # Add candidate ID number to facilitate uploading
                        cand.id = cand_id
                        rated_cands.append(cand)
                 
                    # Upload rating values
                    query_args = []
                    for cand in rated_cands:
                        if len(cand.rating_values):
                            query = "INSERT INTO pdm_rating " + \
                                    "(value, pdm_rating_instance_id, pdm_cand_id, date) "
                            for ratval in cand.rating_values:
                                if not ratval.value is None and np.abs(ratval.value) < 1e-307:
                                    ratval.value = 0.0

                                if not ratval.value is None and np.isinf(ratval.value):
                                    ratval.value = 9999.0
                                instance_id = rat_inst_id_cache.get_id(ratval.name, \
                                                                       ratval.version, \
                                                                       ratval.description)            

                                value = np.float(ratval.value) if not ratval.value is None else None

                                if value is None or np.isnan(value):
                                    query += "SELECT NULL, %d, %d, GETDATE() UNION ALL " % \
                                              (instance_id, cand.id)
                                else:
                                    query += "SELECT '%.12g', %d, %d, GETDATE() UNION ALL " % \
                                              (ratval.value, instance_id, cand.id)

                            query = query.rstrip('UNION ALL') # remove trailing 'UNION ALL' from query

                            db.execute(query)

                finally:    
                    # Remove the temporary directory containing pfd files
                    shutil.rmtree(tmpdir)
    finally:
        db.close()


class RemoveAllRatersAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, [])


class AddAllRatersAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        ratlist = copy.deepcopy(raters.registered_raters)
        setattr(namespace, self.dest, ratlist)


class RemoveOneRaterAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        rater_name = values[0]
        if rater_name not in raters.registered_raters:
            sys.stderr.write("Unrecognized rater: %s\nThe following " \
                             "raters are registered:\n    %s\n" % \
                             (rater_name, "\n    ".join(raters.registered_raters)))
            sys.exit(1)
        curr_raters = getattr(namespace, self.dest)
        # Remove any instances of 'values' from curr_raters
        while rater_name in curr_raters:
            curr_raters.remove(rater_name)
        setattr(namespace, self.dest, curr_raters)


class AddOneRaterAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        rater_name = values[0]
        if rater_name not in raters.registered_raters:
            sys.stderr.write("Unrecognized rater: %s\nThe following " \
                             "raters are registered:\n    %s\n" % \
                             (rater_name, "\n    ".join(raters.registered_raters)))
            sys.exit(1)
        curr_raters = getattr(namespace, self.dest)
        # Add 'rater_name' to curr_raters
        if rater_name not in curr_raters:
            curr_raters.append(rater_name)
        setattr(namespace, self.dest, curr_raters)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Rate PFD files.")
    parser.add_argument('-v', '--more-verbose', dest='verbosity', \
                         default=0, action='count', \
                         help="Turn up verbosity by one notch. " \
                                "(Default: Don't be verbose (verbosity=0).)")
    parser.add_argument('-d', '--debug', dest='debug', \
                         default=False, action='store_true', \
                         help="Turn on debugging output. " \
                                "(Default: Don't print debugging info.)")
    parser.add_argument('-L', '--list-raters', dest='list_raters', \
                        default=False, action='store_true', \
                        help="List registered raters and exit.")
    parser.add_argument('-x', '--exclude', dest='raters', \
                         type=str, default=[], nargs=1, \
                         action=RemoveOneRaterAction, \
                         help="Remove rater from list of ratings to apply.")
    parser.add_argument('--exclude-all', dest='raters', \
                         default=[], nargs=0, \
                         action=RemoveAllRatersAction, \
                         help="Clear list of ratings to apply.")
    parser.add_argument('-i', '--include',  dest='raters', \
                         type=str, default=[], nargs=1, \
                         action=AddOneRaterAction, \
                         help="Include rater from list of ratings to apply.")
    parser.add_argument('--include-all', dest='raters', \
                         default=[], nargs=0, \
                         action=AddAllRatersAction, \
                         help="Include all registered ratings in list " \
                                "of ratings to apply.")
    parser.add_argument('-P', '--num-procs', dest="num_procs", \
                        type=int, default=1, \
                        help="The number of rater processes to use. " \
                                "Each thread rates a separate candidate. " \
                                "(Default: use one rater thread.)")
    args = parser.parse_args()
    main()
