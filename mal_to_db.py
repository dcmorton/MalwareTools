#!/usr/bin/python
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Add malware files and their hashes to a MySQL database, saving them as LONGBLOBs in the database structure

import sys
import os
import re
import hashlib
from optparse import OptionParser

try:
    import MySQLdb
except ImportError:
    print "Cannot import MySQLdb, fix it."
    sys.exit()

#MySQL Connection Info
host = '' 
username = '' 
password = '' 
database = ''

def initdb():

    conn = MySQLdb.connect(host=host, user=username, passwd=password, db=database)
    curs = conn.cursor()

    curs.execute("""
        CREATE TABLE files (
            id   INTEGER PRIMARY KEY AUTO_INCREMENT,
            md5  TEXT,
            sha1  TEXT,
            sha256  TEXT,
            malware  LONGBLOB,
            time  DATETIME
            ) ENGINE=INNODB, ROW_FORMAT=DYNAMIC;
        """)
    curs.close()
    conn.commit()
    conn.close()

def savetodb(filename, force):

    conn = MySQLdb.connect(host=host, user=username, passwd=password, db=database)
    curs = conn.cursor()
    
    md5 = hashlib.md5(open(filename, 'rb').read()).hexdigest()
    sha1 = hashlib.sha1(open(filename, 'rb').read()).hexdigest()
    sha256 = hashlib.sha256(open(filename, 'rb').read()).hexdigest()#
    file = open(filename, 'rb').read()
    
    curs.execute("SELECT id FROM files WHERE md5=%s", (md5,))
    ids = curs.fetchall()
   
    if len(ids):
        if not force:
            ids = ["%d" % id[0] for id in ids]
            print "The sample exists in the database with ID %s" % (','.join(ids))
            print "Use the -o or --overwrite option to force"
            return
        else:
            curs.execute("DELETE FROM files WHERE md5=%s", (md5,))

    curs.execute("INSERT INTO files VALUES (NULL,%s,%s,%s,%s,NOW())", (md5,sha1,sha256,file))
    curs.close()
    conn.commit()
    conn.close()


def main():
    parser = OptionParser()
    parser.add_option("-i", "--init", action="store_true", 
                       dest="init", default=False, help="initialize database")
    parser.add_option("-o", "--overwrite", action="store_true",
                       dest="force", default=False,
                      help="overwrite existing DB entry")
    parser.add_option("-f", "--file", action="store", dest="filename",
                      type="string", help="save FILENAME")
    parser.add_option("-u", "--upload", action="store_true",
                       dest="savetodb", default=False,
                      help="Save file to database")

    (opts, args) = parser.parse_args()

    if opts.init:
        initdb()
        sys.exit()

    if opts.filename == None:
        parser.print_help()
        parser.error("You must supply a filename!")
    if not os.path.isfile(opts.filename):
        parser.error("%s does not exist" % opts.filename)
    if opts.savetodb:
        print "Saving  " + opts.filename + " to the database"
        savetodb(opts.filename, opts.force)
        print "Done"
        print

if __name__ == '__main__':
    main()