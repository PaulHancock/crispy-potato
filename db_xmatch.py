###
# Compare two catalogs and output the intersection and exclusion sets for both directions of the matching.
# V1.0 Paul Hancock 9/11/10
#
# V2.0 PJH 2011-03-15
#  extract the catalogs from a sql database
###

import sqlite3
import sys,os
from optparse import OptionParser
from CherryPy import Xmatch as xm
import static as st

def gen_ids(ids):
    for id in ids:
        yield (id[0][1],id[1][1],id[2])#the keys are (ra,src_id) and the ids are (key1,key2,distance)

if __name__=="__main__":
    parser = OptionParser()
    parser.add_option("-s", "--sourcefinder", dest="sf_name", help="the name of the source finding program that produced the catalog")
    parser.add_option("-f", "--field", dest="field", default=0, help="Restrict analysis to this field number\nDefault=0")
    parser.add_option("-e", "--epoch", dest="epoch", default=2**8-1, help="Restrict analysis to some epochs only.\nDefault=2**8-1 = all epochs\nCurrently ignored")
    parser.add_option("-r", "--refresh", dest="refresh", default=False, action="store_true", help="Reset the links table")
    (op, arg) = parser.parse_args()    

    conn=sqlite3.connect(st.db_file)
    c=conn.cursor()
    
    if op.refresh:
        c.execute("DELETE FROM links")
        print "TABLE links refreshed"
        sys.exit(0)
    
    if not op.sf_name:
        print "-s, --sourcefinder is required"
        sys.exit(1)
    if op.sf_name not in st.sf_names:
        print "catalog ",op.sf_name," doesn't work"
        sys.exit(1)
    # To use my Xmatch program to do the cross-matching
    # I need dictionaries in the following format:
    # _cat: {(key): (anything i want as it's not use in the
    #        matching only in the following data retrival)}
    # _coords: { (key):(ra,dec) }
    # the keys need to be such that they will fall into ra order
    # when .sort() is run on the dictionary.
    #
    # I chose to use (ra,src_id) as the key for the dict


    #direction = 1 for src1 -> master1
    #                  src1 -> master2
    #                  etc
    #          = 0 for master1 -> src1
    #                  master1 -> src2
    #                  etc
        
    master=dict([ ((row[1],row[0]),(row[1],row[2],row[3])) for row in c.execute('SELECT src_id,ra,dec,flux FROM master WHERE flux > 75e-6 AND field=? ORDER BY ra',(op.field,)) ])
    print len(master)
    
    slave= dict([ ((row[1],row[0]),(row[1],row[2],row[3])) for row in c.execute('SELECT src_id,ra,dec,pflux FROM catalog WHERE sf=? AND field=? ORDER BY ra',(op.sf_name,op.field)) ])
    print len(slave)
    
    radius= 30/3600.0 #arcsec ->degrees
    #print "Matching..."
    sigma_d=15/3600.0 #1sigma deviation in position ~1/2 a beam
    sigma_f=25e-6 #1sigma deviation in flux = background rms of my images
    matched,unmatched= xm.crossmatch_flux_weighted(slave,master,radius,sigma_d,sigma_f) #slave sources with a master counterpart
    print len(matched),len(unmatched)
    c.execute("DELETE FROM links WHERE direction=1 AND sf=? AND field=?",(op.sf_name,op.field))
    c.executemany("INSERT INTO links (catalog_id,master_id,direction,sf,field,dist) VALUES (?,?,1,'{0}',{1},?)".format(op.sf_name,op.field),gen_ids(matched))

    matched,unmatched= xm.crossmatch_flux_weighted(master,slave,radius,sigma_d,sigma_f) #master sources with a slave counterpart
    print len(matched),len(unmatched)
    c.execute("DELETE FROM links WHERE direction=0 AND sf=? AND field=?",(op.sf_name,op.field))
    c.executemany("INSERT INTO links (master_id,catalog_id,direction,sf,field,dist) VALUES (?,?,0,'{0}',{1},?)".format(op.sf_name,op.field),gen_ids(matched))
    
    
    conn.commit()
    c.close()
