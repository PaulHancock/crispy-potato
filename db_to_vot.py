###
# Convert entries in the data base into ASCII formatted files.
#
###

import astropy
from astropy.table.table import Table
from astropy.io import ascii
import numpy as np

import sqlite3
import sys

import static as st

if __name__=="__main__":
    #connect to the database
    conn = sqlite3.connect(st.db_file)
    c=conn.cursor()
    #c.execute("DROP TABLE master") #overwrite the previous table
    c.execute("SELECT ra,dec,flux,bmaj,bmin,pa,epoch,field FROM master")
    data = np.array([ map(float,r) for r in c])
    tab_dict={}
    for i,name in enumerate(['ra','dec','flux','a','b','pa', 'epoch', 'field']):
        tab_dict[name] = data[:,i]
    t = Table(tab_dict)
    print "writing csv"
    ascii.write(t, 'db.csv')
    #vot = from_table(t)
    #writetoVO(vot, 'db.vot')
    c.close()
