###
# Plot parameters that are best analysed by a comparison
# with the sf catalog as the source
#
# Uses database access and is based on plotarama.py
#
# V1.0 Paul Hancock 2011-02-18
# initial version
# V1.1 pjh 2011-03-28
# database now uses a links table
# use of zip(*data) to make a lot of things easier
###

import sqlite3
import sys,os
import numpy as np
from math import pi,cos,sqrt,log
import math
import static as st
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import scipy.stats.mstats as ms

#################################### FINAL PLOTS FOR THE PAPER ########################################

def rflux_accuracy(c):
    print "rflux_accuracy"
    cat_meds=[]
    cat_stds=[]
    bins=np.logspace(math.log10(125e-6),0,num=40) #flux bin edges
    for cat_name in st.sf_names[:-1]:
        print cat_name
        (fluxes,offsets)=zip(*c.execute("""SELECT c.pflux,(m.flux-c.pflux)/c.pflux FROM (SELECT * FROM catalog c INNER JOIN links l ON l.catalog_id=c.src_id AND l.sf=? AND direction=1) c INNER JOIN master m ON c.master_id = m.src_id""",(cat_name,)).fetchall())
        
        meds=[]
        stds=[]
        for i in range(len(bins)-1):
            lower,upper=bins[i],bins[i+1]
            l=[]
            theory=[]
            for flux,off in zip(fluxes,offsets):
                if not off:
                    continue
                if lower<flux and flux<=upper:
                    l.append(abs(off))
            meds.append(np.median(l))
            stds.append(np.std(l))
        cat_meds.append(meds)
        cat_stds.append(stds)
    
    factor=1
    (fluxes,bmaj,bmin)=zip(*c.execute("""SELECT m.flux,m.bmaj,m.bmin FROM master m """).fetchall())
    tmeds=[]
    tstds=[]
    for i in range(len(bins)-1):
        lower,upper=bins[i],bins[i+1]
        theory=[]
        for flux,a,b in zip(fluxes,bmaj,bmin):
            if lower<flux and flux<=upper:
                #theoretical variance in amp for correlated noise with maximal smoothing - Condon '97
                theory.append(math.sqrt(2/( a*b/(4*30**2)* (1+(30/a)**2)**1.5 * (1+(30/b)**2)**1.5 *(flux/25e-6)**2 )))
        tmeds.append(np.median(theory))
        tstds.append(np.std(theory))

    #tmeds=np.array(tmeds)
    #tstds=np.array(tstds)
    #shift the fluxes to be at the center of the bin.
    bratio=bins[1]/bins[0]
    fluxes=np.array(bins[:-1]*((1+bratio)/2))/25e-6
    
    #make the shaded region for the theoretical curve.
    #verts=zip(fluxes,tmeds-tstds)
    #verts.reverse()
    #verts+=zip(fluxes,tmeds+tstds) 
    #poly=Polygon(verts,facecolor='0.8')

    #make the actual plot
    plt.clf()
    fig=plt.figure(1,(4,4))
    ax=fig.add_subplot(111)
    #ax.add_patch(poly)
    ax.loglog(fluxes,cat_meds[0],'b-',
                fluxes,cat_meds[1],'g-',
                fluxes,cat_meds[2],'r-',
                fluxes,cat_meds[3],'c-',
                fluxes,cat_meds[4],'y-',
                fluxes,tmeds,'k:')
    names=[a for a in st.sf_names[:-1]]
    names.append('Ideal')
    names[0]='paaadding'
    ax.legend(names,loc=3)
    ax.set_title('Median absolute flux deviation')
    ax.set_ylabel('%')
    ax.set_xlabel('Measured SNR')
    ax.set_ylim((1e-5,1))
    ax.set_xlim((5,5e4))
    ax.set_yticklabels(['','0.01','0.1','1','10','100'])
    ax.set_xticklabels(['a','10','100','1,000','10,000'])
    plt.savefig('flux_accuracy.eps',orientation='landscape',papertype='a4',dpi=600)
    print 'flux_accuracy.eps'
  

def theory_mad(c):
    #print "rflux_dist_hist"
    #cat_meds=[]
    #cat_stds=[]
    bins=np.logspace(math.log10(125e-6),0,num=40) #flux bin edges
    #for cat_name in st.sf_names[:-1]:
    #    print cat_name
    #    (fluxes,offsets)=zip(*c.execute("""SELECT c.pflux,l.dist*3600 FROM catalog c INNER JOIN links l ON l.catalog_id=c.src_id AND l.sf=? AND direction=0""",(cat_name,)).fetchall())
    #    #(fluxes,offsets)=zip(*c.execute("""SELECT m.flux,l.dist*3600 FROM master m INNER JOIN links l ON l.master_id=m.src_id AND l.sf=? AND direction=1""",(cat_name,)).fetchall())
    #    meds=[]
    #    stds=[]
    #    for i in range(len(bins)-1):
    #        lower,upper=bins[i],bins[i+1]
    #        l=[]
    #        for flux,off in zip(fluxes,offsets):
    #            if lower<flux and flux<=upper:
    #                l.append(off)
    #        meds.append(np.median(l))
    #        stds.append(np.std(l))
    #    cat_meds.append(meds)
    #    cat_stds.append(stds)
        
    def rho2(parname):
        if parname=='x':
            alpha_M = 5.0/2
            alpha_m = 1.0/2
        elif parname=='y':
            alpha_M = 1.0/2
            alpha_m = 5.0/2
        def func(a,b,flux):
            return a*b/(4*30**2) *(1+(30/a)**2)**alpha_M * (1+(30/b)**2)**alpha_m * (flux/25e-6)**2
        return func

    (fluxes,bmaj,bmin)=zip(*c.execute("""SELECT m.flux,m.bmaj,m.bmin FROM master m """).fetchall())
    tmeds=[]
    rho2x=rho2('x')
    rho2y=rho2('y')
    factor=1/(4*np.log(2))
    for i in range(len(bins)-1):
        lower,upper=bins[i],bins[i+1]
        theory=[]
        for flux,a,b in zip(fluxes,bmaj,bmin):
            if lower<flux and flux<=upper:
                theory.append( math.sqrt( a**2*factor/rho2x(a,b,flux) + b**2*factor/rho2y(a,b,flux) )  )
        tmeds.append(np.median(theory))
    madPos=tmeds
    
    factor=1
    tmeds=[]
    for i in range(len(bins)-1):
        lower,upper=bins[i],bins[i+1]
        theory=[]
        for flux,a,b in zip(fluxes,bmaj,bmin):
            if lower<flux and flux<=upper:
                #theoretical variance in amp for correlated noise with maximal smoothing - Condon '97
                theory.append(math.sqrt(2/( a*b/(4*30**2)* (1+(30/a)**2)**1.5 * (1+(30/b)**2)**1.5 *(flux/25e-6)**2 )))
        tmeds.append(np.median(theory))
    madFlux= tmeds
    
    #shift the fluxes to be at the center of the bin.
    bratio=bins[1]/bins[0]
    fluxes=np.array(bins[:-1]*((1+bratio)/2))
    
    print "#  FLUX |  MAD   |   MAD  "
    print "#   bin |position|  flux  "
    print "#   Jy  | arcsec |    %   "
    print "#-------------------------"

    for f,pos,flux in zip(fluxes,madPos,madFlux):
        print '{0:5.2e} {1:5.2e} {2:5.2e}'.format(f,pos,flux)
    #plt.clf()
    #fig=plt.figure(1,(4,4))
    #ax=fig.add_subplot(111)
    #ax.loglog(fluxes,cat_meds[0],'b-',
    #            fluxes,cat_meds[1],'g-',
    #            fluxes,cat_meds[2],'r-',
    #            fluxes,cat_meds[3],'c-',
    #            fluxes,cat_meds[4],'y-',
    #            fluxes,tmeds,'k:')
    #names=st.sf_names[:-1]
    #names.append('Ideal')
    #names[0]='paaadding'
    #ax.legend(names,loc=3)
    #ax.set_title('Median absolute position deviation')
    #ax.set_ylabel('arcsec')
    #ax.set_xlabel('Measured SNR')
    #ax.set_ylim((1e-3,10))
    #ax.set_xlim((5,5e4))
    #ax.set_xticklabels(['a','10','100','1,000','10,000','b'])
    #ax.set_yticklabels(['','0.01','0.1','1','10'])
    #plt.savefig('flux_dra.eps',orientation='landscape',papertype='a4',dpi=600)
    #print 'flux_dra.eps'



if __name__=="__main__":
    conn=sqlite3.connect(st.db_file)
    c=conn.cursor()

    theory_mad(c)

