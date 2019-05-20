"""
# Create a source catalog and insert the sources into a Sqlite3 database
# Paul Hancock 2011-03-14
"""
import sys,os
import sqlite3
import numpy as np
import random
import convert

import static as st

from math import log10 as log
from math import cos, sin, pi



def flux_dist(num=100.0):
    """ Perform numerical integration of N(S) given
    n_bins, min_flux, max_flux
    and modify Nstar so that the total number of sources
    is equal to num. Return a list of size num from with
    fluxes can be drawn to produce the given source count model.
    """
    max_flux=10
    min_flux=25e-6
    n_bins=int(log(max_flux/min_flux)*10)
    Sstar= 1.09
    alpha= 2.3
    #source count function without normalization as per Hopkins2000
    f = lambda x: 1/(x/Sstar)**alpha
    
    #integrate the function and then normalize it
    sum=0
    ratio=10**(log(max_flux/min_flux)/(n_bins) )
    s = lambda i: min_flux*ratio **i
    for i in range(n_bins):
        bin_size = abs(s(i+1)-s(i))
        sum+=f(s(i+0.5))*bin_size
    Nstar = num/sum
    N = lambda x: Nstar* f(x)
    flux_list=[]
    #now create a list of num fluxes
    for i in range(n_bins):                 #for each bin
        num_src=int(np.ceil( N(s(i+0.5))*abs(s(i+1)-s(i)) ))
        for j in range(num_src): #add the required number of sources
            flux_list.append(s(i)+random.random()*(s(i+1)-s(i))) #fluxes are random within the flux range
    flux_list.reverse() #reverse the list so that when we have an excess of sources, we cut off the faint ones rather than the strong ones
    return flux_list
            
def get_source(max_num=100,racen=180,deccen=0,radius=4):
    random.seed(456789+racen+deccen)
    rand=random.random
    n_src=0
    flux_list=flux_dist(max_num)
    lfl = len(flux_list)
    while n_src < max_num:
        while True:
            dec_off= (rand()*2 -1)*radius
            ra_off = (rand()*2 -1)*radius
            if ( (ra_off*cos(pi/180*deccen))**2 + dec_off**2)<radius**2:
                ra=racen+ra_off
                dec=deccen+dec_off
                break
        if ra > 360:
            ra -=360
        if ra < 0:
            ra +=360
        ra_str,dec_str = convert.dec_to_hms(ra),convert.dec_to_dms(dec)
        #the following may need some consideration
        flux=flux_list[n_src]
        bmaj=30+30*rand()
        bmin=30+(bmaj-30)*rand() #bmin < bmaj
        pa=90-180*rand()
        n_src+=1
        yield [n_src,ra,dec,ra_str,dec_str,flux,bmaj,bmin,pa]
        
def get_centers(ra_cen,dec_cen,radius):
    """Create a list of field centers that are arrange in a flower pattern of 7"""
    field_centers=[(ra_cen,dec_cen)]
    field_centers.extend([ (ra_cen-radius*cos(i*pi/3), radius*sin(i*pi/3) ) for i in range(6)])
    return field_centers

def is_near(ra1,dec1,ra2,dec2,radius):
    return ((ra1-ra2)**2 + (dec1-dec2)**2) < radius**2
    

if __name__ == "__main__":
    #kill the database if it exists
    os.popen('rm {0}'.format(st.db_file))
    #connect to the database
    conn = sqlite3.connect(st.db_file)
    c=conn.cursor()
    c.execute("""CREATE TABLE master (
    src_id INT,
    ra FLOAT(10,7),
    'dec' FLOAT(8,6),
    ra_str VARCHAR(12),
    dec_str VARCHAR(12),
    flux FLOAT(7,6),
    bmaj FLOAT(4,2),
    bmin FLOAT(4,2),
    pa FLOAT(3,1),
    field INT,
    epoch INT,
    CONSTRAINT src_id PRIMARY KEY (src_id))
    """)

    src_id=0
    field_centers=[ (4+f,0) for f in range(300)]
    radius=2
    for i in range(len(field_centers)):
        print "field {0}".format(i)
        epoch_centers=get_centers(field_centers[i][0],field_centers[i][1],radius)
        
        for t in get_source(11000,field_centers[i][0],field_centers[i][1],2*radius):
            ra,dec=t[1],t[2]
            epoch=0
            for j in range(len(epoch_centers)):
                if is_near(ra,dec,epoch_centers[j][0],epoch_centers[j][1],radius):
                    epoch+=2**j
            if not epoch: #if the source isn't in any of the fields not include it in the table
                continue
            src_id+=1
            t[0]=src_id
            t.append(epoch)
            t.append(i)
            c.execute("""INSERT INTO master
            (src_id, ra ,'dec',ra_str, dec_str, flux, bmaj, bmin, pa, epoch, field)
            VALUES
            (?,?,?,?,?,?,?,?,?,?,?)
            """,t)
    #create an empty catalog table
    c.execute("""CREATE TABLE catalog (
        src_id INTEGER PRIMARY KEY,
        ra FLOAT(10,7),
        era FLOAT(10,7),
        'dec' FLOAT(8,6),
        edec FLOAT(8,6),
        ra_str VARCHAR(12),
        dec_str VARCHAR(12),
        flux FLOAT(7,6),
        eflux FLOAT(7,6),
        pflux FLOAT(7,6),
        epflux FLOAT(7,6),
        bmaj FLOAT(4,2),
        ebmaj FLOAT(4,2),
        bmin FLOAT(4,2),
        ebmin FLOAT(4,2),
        pa FLOAT(3,1),
        epa FLOAT(3,1),
        sf VARCHAR(10),
        field INT,
        epoch INT
        )""")
    #create a list of links between the catalog sources and the master sources
    c.execute("""CREATE TABLE links (
        catalog_id INT,
        master_id INT,
        direction BOOLEAN,
        sf VARCHAR(10),
        field INT,
        dist FLOAT(8,6),
        PRIMARY KEY (catalog_id,master_id,direction,field)
        )""")
        
    c.execute(""" CREATE TABLE stats (
        sf VARCHAR(10),
        flux FLOAT(7,6),
        comp FLOAT(7,6),
        rel FLOAT(7,6),
        counts FLOAT(7,6),
        PRIMARY KEY (sf,flux)
        )""")
    #make some index-es to speed up queries later on
    c.execute("""CREATE INDEX links_master_idx on links(master_id)""")
    #save and close
    conn.commit()
    c.close()
