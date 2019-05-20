"""
Take the catalogs produced by various source finders and put them into a dabase
V1.0 Paul Hancock 2011-03-15
"""

import sqlite3
import sys,os
from CherryPy import convert

from optparse import OptionParser

import static as st

from math import sqrt,log

#################################### FILE FORMATS ########################################
### DESIGNED TO GIVE
##  FLUXES IN JY,
##  BMAJ,BMIN AND ERRORS in arcsec
##  Positions and position angles in decimal degrees
##  Position errors in arcsec

flux=lambda x: float(x)
mjflux=lambda x : float(x)*1e-3
deg2arcsec=lambda x: float(x)*3600
convolve_deg=lambda x: sqrt(deg2arcsec(x)**2+30**2) #for convolving the source with the beam
convolve_arcsec=lambda x: sqrt(float(x)**2+30**2)

tesla_cols={'ra':5,'era':6,'dec':7,'edec':8,'flux':9,'eflux':10,'pflux':9,'epflux':10,'bmaj':11,'ebmaj':12,'bmin':13,'ebmin':14,'pa':15,'epa':16}
tesla_funcs={'flux':flux,'eflux':flux,'pflux':flux,'epflux':flux}


sex_cols ={'ra':0,'dec':1,'bmaj':2,'bmin':4,'pa':6,'flux':11,'eflux':12, 'pflux':21}
sex_flux=lambda x: float(x)/25.0
sex_funcs={'flux':sex_flux,
           'eflux':sex_flux,
           'pflux':flux,
           'bmaj':convolve_deg,
           'bmin':convolve_deg,
           'pa': lambda x : 90-float(x)}

#using background rms as the peak flux error since the reported error is always zero.
sfind_cols={'ra_str':0,'dec_str':1,'era':2,'edec':3,'pflux':4,'epflux':11,'flux':6,'bmaj':7,'bmin':8,'pa':9,'eflux':11}
sfind_funcs={'flux':mjflux,
             'eflux':mjflux,
             'pflux':mjflux,
             'epflux':mjflux}

duchamp_cols={'ra':5,'dec':6,'flux':13,'pflux':15}
duchamp_funcs={'flux':flux,
               'pflux':flux}

selavy_cols={'ra':1,'dec':2,'flux':5,'pflux':6,'bmaj':7,'bmin':8,'pa':9}
selavy_funcs={'flux':flux,
              'pflux':flux}

imsad_cols={'ra_str':2,'dec_str':3,'pflux':4,'flux':5,'bmaj':6,'bmin':7,'pa':8}
imsad_funcs={'flux':flux,
             'bmaj':convolve_arcsec,
             'bmin':convolve_arcsec,
             'pflux':flux}

fndsou_cols={'ra_str':1, 'dec_str':2,'pflux':3,'bmaj':4,'bmin':5,'pa':6}
fndsou_funcs={'pflux':mjflux,
              'bmaj':deg2arcsec,
              'bmin':deg2arcsec}

formats={'imsad':(imsad_cols,imsad_funcs),'sex':(sex_cols,sex_funcs), 'selavy':(selavy_cols,selavy_funcs), 'sfind':(sfind_cols,sfind_funcs),'tesla':(tesla_cols,tesla_funcs),'fndsou':(fndsou_cols,fndsou_funcs)}

if __name__=="__main__":

    parser = OptionParser()
    parser.add_option("-c", "--cfile", dest="cat_fname", help="catalog file", metavar="FILE")
    parser.add_option("-s", "--sourcefinder", dest="sf_name", help="the name of the source finding program that produced the catalog")
    parser.add_option("-r","--refresh",dest="refresh",action="store_true", default=False, help="delete the cata log table")
    parser.add_option("-m","--mapname",dest="mapname",help="The image from which the catalog was derived")
    (op, arg) = parser.parse_args()
    
    conn=sqlite3.connect(st.db_file)
    c=conn.cursor()
    
    if op.refresh:#delete all the current entries in catalog
        c.execute("DELETE FROM catalog")
        print "TABLE catalog refreshed"
        sys.exit(0)
    
    if not (op.sf_name and op.cat_fname and op.mapname):
        print "I need more options"
        sys.exit(1)

    
    if not os.path.exists(op.cat_fname):
        print op.cat_fname, "doesn't exist"
        sys.exit(1)
        
    print "Ingesting catalog "+op.sf_name+" from file "+op.cat_fname

    if formats.has_key(op.sf_name):
        cols,funcs=formats[op.sf_name]
    else:
        print op.sf_name+" is not yet supported"
        sys.exit(1)
    data= [a.split() for a in open(op.cat_fname,'r').readlines() if not a.startswith('#')]
    
    #figure out which field and epoch this map corresponds to
    field,epoch=st.get_field_epoch(op.mapname)
            
    #remove the current cat_name entries as we are going to put some new ones in
    c.execute('DELETE FROM catalog WHERE sf=? AND field=?',(op.sf_name,field))

    #add all the new sources to the catalog, with as many of the available columns as possible
    for d in data:
        vals=[]
        col_list=[]
        for param in cols.keys():
            if funcs.has_key(param):
                vals.append( funcs[param](d[cols[param]]) )
            else:
                vals.append( d[cols[param]] )
            col_list.append( param )
        col_names = ','.join(col_list)
        
        if 'ra_str' in cols: #if we are given the str convert to decimal
            ra=convert.ra2dec(d[cols['ra_str']])
            dec=convert.dec2dec(d[cols['dec_str']])
            vals.append(ra)
            vals.append(dec)
            col_names+=',ra'
            col_names+=',dec'
        else: #if we are given the decimal then convert to str
            ra_str = convert.dec2hms(float(d[cols['ra']]))
            dec_str = convert.dec2dms(float(d[cols['dec']]))
            #ra_str, dec_str = convert.radec2str(float(d[cols['ra']]),float(d[cols['dec']])).split()
            vals.append(ra_str)
            vals.append(dec_str)
            col_names+=',ra_str'
            col_names+=',dec_str'
        vals.append(op.sf_name)
        col_names+=',sf'
        vals.append(field)
        col_names+=',field'
        vals.append(epoch)
        col_names+=',epoch'
        c.execute("INSERT INTO catalog ("+col_names+") VALUES("+','.join(['?' for a in vals])+")", vals)
    conn.commit()
    c.close()
        
    
