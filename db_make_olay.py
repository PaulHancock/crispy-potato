#! python

###
# Create an olay file for use in cgdisp from one of the tables
# in the database
#
# V1.0
# Paul Hancock 2011-03-23
###

import sqlite3
import os,sys

if __name__=="__main__":
    min_flux=1e-4
    db_file="SfSim_20110323.db"
    conn=sqlite3.connect(db_file)
    c=conn.cursor()
    olay=open('master.olay','w')
    for row in c.execute("SELECT ra,dec,bmaj,bmin,pa FROM master WHERE flux >?",(min_flux,)):
        ra,dec,bmaj,bmin,pa = row
        olay.write('oellipse absdeg absdeg x no {0:f} {1:f} {2:f} {3:f} {4:f}\n'.format(ra,dec, bmaj/3600, bmin/3600, pa))
    olay.close()
