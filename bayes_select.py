#! /usr/bin/env python

###
# This module is designed to be a set of tools for selecing the correct
#  links between two sets of sources.
#
# V1.0 Paul Hancock 2001-03-28
# first try
###

from math import sqrt, exp

def flux_weight(s1,s2):
    """The weight of the link between two fluxes.
    s1=(flux1,eflux1)
    s2=(flux2,eflux2)"""
    flux1,err1=s1
    flux2,err2=s2
    return exp( - (flux1-flux2)**2/ sqrt(err1**2+err2**2))

def pos_weight(pos1,pos2):
    """The weight of the link between two positions."""
    ra1,era1,dec1,edec1 = pos1
    ra2,era2,dec2,edec2 = pos2
    ra_weights=exp( - (ra1-ra2)**2 / sqrt(era1**2+era2**2))
    dec_weights = exp( -(dec1-dec2)**2 / sqrt(edec1**2+edec2**2))
    return ra_weights*dec_weights

def all_perms(str):
    """Generator + Recursion = Awesome."""
    if len(str) <=1:
        yield str
    else:
        for perm in all_perms(str[1:]):
            for i in xrange(len(perm)+1):
                yield perm[:i] + str[0:1] + perm[i:]

def cross_iter(list1,list2):
    """Iterate over all the possible combinations of list 1 and list 2
    Allowing for each item in list1 to be linked to an item in list 2 uniquely
    or to not be linked at all.
    """
    for perm in all_perms(list2):
        yield zip(list1,perm)

def dual_cal_121(cat1,cat2):
    """
    Given two catalogs of sources determine the most likely
    combination of linkages between them.
    Each catalog entry should contain positions and fluxes.
    cat_n = { id:(ra,era,dec,edec,flux,eflux) }

    Allow only a 1-to-1 mapping between the catalogs.
    """
    max_weight=0
    best=[]
    for links in cross_iter(cat1.keys(),cat2.keys()):
        weight=0
        for k1,k2 in links:
            fweight=flux_weight(cat1[k1][4:6],cat2[k2][4:6])
            pweight=pos_weight(cat1[k1][0:4],cat2[k2][0:4])
            weight+=fweight*pweight
        if weight>max_weight:
            max_weight=weight
            best=links
    return best


if __name__ == "__main__":
    #test cases
    pos_err=2/3600.0
    flux_err = 25e-6
    import sqlite3
    conn=sqlite3.connect('SfSim_20110323.db')
    c=conn.cursor()
    data=c.execute("""SELECT src_id,ra,dec,flux FROM catalog WHERE src_id BETWEEN 1970 AND 1975""")
    cat1=dict([ (a[0],(a[1],pos_err,a[2],pos_err,a[3],flux_err)) for a in data ])
    data=c.execute("""SELECT src_id,ra,dec,flux
     FROM
      (master m
       INNER JOIN
       links l
       ON m.src_id = l.master_id AND direction=1
      )
     WHERE catalog_id BETWEEN 1970 and 1975""")
    cat2=dict([ (a[0],(a[1],pos_err,a[2],pos_err,a[3],flux_err)) for a in data ])
    best=dual_cal_121(cat1,cat2)
    for k1,k2 in best:
        print "{0[0]} {0[2]} {0[4]} :: {1[0]} {1[2]} {1[4]}".format(cat1[k1],cat2[k2])
    #for a in cross_iter([1,2,3,4],['a','b','c','d']):
    #    print a
