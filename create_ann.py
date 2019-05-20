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
    #c.execute("SELECT ra,dec,bmaj/3600,bmin/3600,pa FROM master WHERE flux > 100e-6 AND field=1")
    #c.execute("SELECT ra,dec,bmaj/3600,bmin/3600,pa FROM master m LEFT OUTER JOIN links l on m.src_id = l.master_id AND direction=0 AND l.sf='tesla' WHERE l.catalog_id IS null AND m.field=0 AND m.flux BETWEEN 6*25e-6 AND 10*25e-6")
    c.execute("SELECT ra,dec,bmaj/3600,bmin/3600,pa FROM catalog WHERE sf='sex2' AND field=0")
    #print "color yellow"
    #c.execute("SELECT ra,dec,bmaj/3600,bmin/3600,pa,flux/25e-6 snr FROM master m LEFT OUTER JOIN links l ON m.src_id = l.master_id AND l.sf='tesla' WHERE l.sf is null AND snr > 8")
    print "color red"
    print "pa sky"
    
    for row in c:
        print "ellipse {0} {1} {2} {3} {4}".format(*row)
        
