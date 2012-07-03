#!/usr/bin/env python
import sys
import warnings
import traceback
import cmd

import prettytable
import pyodbc

from ratings2 import config

# Connecting from Linux
DATABASES = {
    'common': {
        'DATABASE': 'palfa-common',
        'UID':  config.username,
        'PWD':  config.password,
        'HOST': config.host,
        'DSN':  'FreeTDSDSN'
        },
    'common2': {
        'DATABASE': 'palfaCandDB2',
        'UID':  config.username,
        'PWD':  config.password,
        'HOST': config.host,
        'DSN':  'FreeTDSDSN'
        },
    'common-copy': {
        'DATABASE': 'palfa-common-copy',
        'UID':  config.username,
        'PWD':  config.password,
        'HOST': config.host,
        'DSN':  'FreeTDSDSN'
        },
    'tracking': {
        'DATABASE': 'palfatracking',
        'UID':  config.username,
        'PWD':  config.password,
        'HOST': config.host,
        'DSN':  'FreeTDSDSN'
        },
}


# Set defaults
DEFAULTDB = 'common2'
DATABASES['default'] = DATABASES[DEFAULTDB]


class Database:
    """Database object for connecting to databases using pyodbc.
    """
    def __init__(self, db="default", autocommit=True):
        """Constructor for Database object.
            
            Input:
                'db': database to connect to. (Default: 'default')
                        (gets passed to 'self.connect')
                'autocommit': boolean, determines if autocommit should
                                be turned on or off.
        """
        self.db = db
        self.connect(db, autocommit=autocommit)
    
    def connect(self, db="default", autocommit=True):
        """Establish a database connection. Set self.conn and self.cursor.
            
            Input:
                'db': databse to connect to. Must be a key in module's
                        DATABASES dict. (Default: 'default')
                'autocommit': boolean, determines if autocommit should
                                be turned on or off.
            Output:
                None
        """
        if db not in DATABASES:
            warnings.warn("Database (%s) not recognized. Using default (%s)." \
                            % (db, DEFAULTDB))
            db = 'default'
        try:
            self.conn = pyodbc.connect(autocommit=autocommit, **DATABASES[db])   
            self.cursor = self.conn.cursor()
        except:
            msg  = "Could not establish database connection.\n"
            msg += "\tCheck your connection options:\n"
            for key, val in DATABASES[db].iteritems():
                msg += "\t\t%s: %s\n" % (key, val)

            raise DatabaseConnectionError(msg)

    def execute(self, query, *args, **kwargs):
        try:
            self.cursor.execute(query.encode('ascii'), *args, **kwargs)
        except Exception, e:
            if "has been chosen as the deadlock victim. Rerun the transaction." in str(e):
                raise DatabaseDeadlockError(e)
            else:
                raise 

    def executemany(self, query, *args, **kwargs):
        try:
            self.cursor.executemany(query.encode('ascii'), *args, **kwargs)
        except Exception, e:
            if "has been chosen as the deadlock victim. Rerun the transaction." in str(e):
                raise DatabaseDeadlockError(e)
            else:
                raise 

    def commit(self):
        self.conn.commit()
  
    def rollback(self):
        self.conn.rollback()
  
    def close(self):
        """Close database connection.
        """
        try:
            self.conn.close()
        except ProgrammingError:
            # database connection is already closed
            pass

    def fetchall(self):
        return self.cursor.fetchall()

    def showall(self):
        desc = self.cursor.description
        if desc is not None:
            fields = [d[0] for d in desc] 
            table = prettytable.PrettyTable(fields)
            for row in self.cursor:
                table.add_row(row)
            table.printt()

    def insert(self, query):
        self.cursor.execute(query)
        self.commit()
    

class DatabaseError(Exception):
    pass


class DatabaseConnectionError(DatabaseError):
    pass


class DatabaseDeadlockError(DatabaseError):
    pass
