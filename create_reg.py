#! python

###
# Create a .ann file for a catalog which is stored in a database.
###

import sqlite3

from math import sqrt
import os,sys
import static as st

if __name__== '__main__':
    conn = sqlite3.connect(st.db_file)
    c=conn.cursor()
    c.execute("SELECT ra,dec,bmaj/3600,bmin/3600,pa FROM master WHERE flux>1e-4 and field=7")
    #print "color yellow"
    #print "pa sky"
    print "fk5"
    
    for row in c:
        ra,dec,a,b,pa = row
        print "ellipse {0} {1} {2}d {3}d {4}d".format(ra,dec,a,b,pa-90)
    c.close()
        
