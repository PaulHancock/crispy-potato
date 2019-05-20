###
# Convert entries in the data base into ASCII formatted files.
#
###


import sqlite3
import sys

import static as st

if __name__=="__main__":
    #connect to the database
    conn = sqlite3.connect(st.db_file)
    c=conn.cursor()
    #c.execute("DROP TABLE master") #overwrite the previous table
    c.execute("SELECT ra,dec,ra_str,dec_str,flux,bmaj,bmin,pa,src_id,epoch,field FROM master")
    print "#Databse file: {0}".format(st.db_file)
    print "# Src      ra         dec       ra_str       dec_str      flux   bmaj bmin   pa   epoch     field"
    print "#  Id     (deg)       (deg)                               (Jy)   (\")  (\")  (deg) 6543210 "
    print "#================================================================================================"
    for d in c:
        print "{8:05d} {0:11.7f} {1:9.6f} {2:12s} {3:12s} {4:8.6f} {5:5.2f} {6:5.2f} {7:>+5.1f} {9:07b} {10:02d}".format(*d)
    c.close()
