#! /usr/bin/env python
"""
Make fixes to the database without having to remake it from the start.

V1 - Fix the ra_str column

Paul Hancock
Sep 23 2011
"""
import static as st
import sqlite3
from CherryPy import convert

if __name__=="__main__":
    conn = sqlite3.connect(st.db_file)
    c=conn.cursor()
    c2=conn.cursor()
    for row in c.execute("SELECT src_id,ra,ra_str,dec,dec_str FROM master"):
        id,ra,ra_str,dec,dec_str=row
        new_ra_str = convert.dec2hms(ra)
        new_dec_str = convert.dec2dms(dec)
        #print dec_str,new_dec_str
        c2.execute("UPDATE master SET ra_str=?,dec_str=? WHERE src_id = ?",(new_ra_str,new_dec_str,id))
        #print new_ra_str,id
    conn.commit()
