import scipy.stats
import scipy.special
import numpy as np

import database

class RatingError(Exception):
    pass


class RatingIDCache(object):
    """A cache object to keep track of rating ID numbers.
        This object will query the database for ID numbers if
        they are not already cached. If not ID number is found
        in the database the cache obeject will add an entry
        to the DB.
    """
    def __init__(self, dbname='common-copy'):
        """Constructor for RatingIDCache objects.

            Input:
                dbname: The database to connect to.
                    (Default: common-copy).

            Output:
                cache: The RatingIDCache object.
        """
        self.dbname = dbname
        self.idcache = {}

    def get_id(self, name, version, description):
        """Return the pdm_rating_instance_id of the rating
            matching the arguments provided. If there is
            no match cached fetch from the DB. If there is
            no match in the DB insert it. Any newly added/fetched
            IDs are added to the cache.
            
            Inputs:
                name: The rating's name.
                version: The rating's version
                description: The rating's description

            Output:
                id: The pdm_rating_type_id from the DB.
        """
        if (name, version) in self.idcache:
            id = self.idcache[(name,version)]
        else:
            # Check database for a match
            id = self._get_id_from_db(name, version, description)
            self.idcache[(name, version)] = id
        return id

    def _get_id_from_db(self, name, version, description):
        """Get the rating instance from the DB.

            Inputs:
                name: The rating's name.
                version: The rating's version
                description: The rating's description

            Output:
                id: The pdm_rating_type_id from the DB.
        """
        db = database.Database(self.dbname)
        db.execute("SELECT ri.pdm_rating_instance_id, " \
                        "rt.name, " \
                        "ri.version " \
                   "FROM pdm_rating_instance AS ri WITH(NOLOCK) " \
                   "LEFT JOIN pdm_rating_type AS rt WITH(NOLOCK) " \
                        "ON rt.pdm_rating_type_id=ri.pdm_rating_type_id " \
                   "WHERE rt.name=? AND ri.version>=?" \
                   "ORDER BY ri.version DESC", (name, version))
        row = db.cursor.fetchone()
        db.close()
        if (row is not None) and (row[2] == version):
            id = row[0]
        elif (row is not None) and (row[2] > version):
            # We're considering a rating version that has
            # been superceded! Error...
            raise RatingError("This rating (%s (v%d)) is no longer " \
                              "current. It has been replaced by " \
                              "%s (v%d)" % \
                              (name, version, row[1], row[2]))
        else: # no row or row[2] < version
            id = self._add_id_to_db(name, version, description)
        return id

    def _add_id_to_db(self, name, version, description):
        """Add the rating instance (and type, if neccessary)
            to the database, and return the corresponding 
            pdm_rating_instance_id.

            Inputs:
                name: The rating's name.
                version: The rating's version
                description: The rating's description

            Output:
                id: The pdm_rating_type_id from the DB.
        """
        db = database.Database(self.dbname)
        # Check for rating type
        db.execute("SELECT pdm_rating_type_id FROM pdm_rating_type " \
                    "WHERE name=?", (name,))
        row = db.cursor.fetchone()
        
        # Add rating type if necessary
        if row is not None:
            type_id = row[0]
        else:
            db.execute("INSERT INTO pdm_rating_type " \
                        "(name, description) " \
                        "VALUES (?, ?)", (name, description))
            db.execute("SELECT pdm_rating_type_id " \
                        "FROM pdm_rating_type " \
                        "WHERE name=?" % (name,))
            type_id = db.cursor.fetchone()[0]

        # Check for rating instance
        db.execute("SELECT pdm_rating_instance_id FROM pdm_rating_instance " \
                    "WHERE pdm_rating_type_id=? " \
                        "AND version=?", (type_id, version))
        row = db.cursor.fetchone()

        # Add rating instance if necessary
        if row is not None:
            id = row[0]
        else:
            db.execute("INSERT INTO pdm_rating_instance " \
                        "(pdm_rating_type_id, version, description) " \
                        "VALUES (?, ?, ?)", (type_id, version, description))
            db.execute("SELECT pdm_rating_instance_id " \
                        "FROM pdm_rating_instance " \
                        "WHERE pdm_rating_type_id=? " \
                            "AND version=?", (type_id, version))
            id = db.cursor.fetchone()[0]
        db.close()

        # Return newly added rating instance id
        return id


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

