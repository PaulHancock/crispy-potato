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

def rflux_counts(c):
    print "rflux_counts"
    names=st.sf_names[:-1]
    plt.clf()
    fig=plt.figure(1,(4,4))
    (fluxes,master_counts)=zip(*c.execute("""SELECT flux,counts FROM stats WHERE sf='master' ORDER BY flux""").fetchall())
    fluxes=np.array(fluxes)/25e-6
    master_counts=np.array(master_counts)
    counts=[]
    for i in range(len(names)):
        counts.append(np.array(zip(*c.execute("""SELECT counts FROM stats WHERE sf=? ORDER BY flux""",(names[i],)).fetchall())[0]))
    ax=fig.add_subplot(111)
    ax.loglog(fluxes,counts[0],'b-',
              fluxes,counts[1],'g-',
              fluxes,counts[2],'r-',
              fluxes,counts[3],'c-',
              fluxes,counts[4],'y-',
              fluxes,master_counts,'k:',
              drawstyle='steps')
    names.append('True')
    names[0]='paaadding'
    ax.legend(names,loc=3)
    ax.set_title('Source Counts')
    ax.set_ylabel('Number')
    ax.set_xlabel('Measured SNR')
    ax.set_yticklabels(['1','10','100','1 000','10 000'])
    ax.set_xlim((5,2000))
    ax.set_xticklabels(['a','10','100','1 000','10 000','b'])
    #ax.set_yticklabels(['','0.01','0.1','1','10'])
    plt.savefig('SourceCount.eps',orientation='landscape',papertype='a4',dpi=600)
    print "SourceCount.eps"
    return
        

def rflux_dist_hist(c):
    print "rflux_dist_hist"
    cat_meds=[]
    cat_stds=[]
    bins=np.logspace(math.log10(125e-6),0,num=40) #flux bin edges
    for cat_name in st.sf_names[:-1]:
        print cat_name
        (fluxes,offsets)=zip(*c.execute("""SELECT c.pflux,l.dist*3600 FROM catalog c INNER JOIN links l ON l.catalog_id=c.src_id AND l.sf=? AND direction=0""",(cat_name,)).fetchall())
        #(fluxes,offsets)=zip(*c.execute("""SELECT m.flux,l.dist*3600 FROM master m INNER JOIN links l ON l.master_id=m.src_id AND l.sf=? AND direction=1""",(cat_name,)).fetchall())
        meds=[]
        stds=[]
        for i in range(len(bins)-1):
            lower,upper=bins[i],bins[i+1]
            l=[]
            for flux,off in zip(fluxes,offsets):
                if lower<flux and flux<=upper:
                    l.append(off)
            meds.append(np.median(l))
            stds.append(np.std(l))
        cat_meds.append(meds)
        cat_stds.append(stds)
        
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
        
    #shift the fluxes to be at the center of the bin.
    bratio=bins[1]/bins[0]
    fluxes=np.array(bins[:-1]*((1+bratio)/2))/25e-6
    plt.clf()
    fig=plt.figure(1,(4,4))
    ax=fig.add_subplot(111)
    ax.loglog(fluxes,cat_meds[0],'b-',
                fluxes,cat_meds[1],'g-',
                fluxes,cat_meds[2],'r-',
                fluxes,cat_meds[3],'c-',
                fluxes,cat_meds[4],'y-',
                fluxes,tmeds,'k:')
    names=st.sf_names[:-1]
    names.append('Ideal')
    names[0]='paaadding'
    ax.legend(names,loc=3)
    ax.set_title('Median absolute position deviation')
    ax.set_ylabel('arcsec')
    ax.set_xlabel('Measured SNR')
    ax.set_ylim((1e-3,10))
    ax.set_xlim((5,5e4))
    ax.set_xticklabels(['a','10','100','1,000','10,000','b'])
    ax.set_yticklabels(['','0.01','0.1','1','10'])
    plt.savefig('flux_dra.eps',orientation='landscape',papertype='a4',dpi=600)
    print 'flux_dra.eps'


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


def completeness(c):
    names=[]
    for s in st.sf_names:
        if not s=='fndsou':
            names.append(s)
            
    plt.clf()
    fig=plt.figure(1,(4,4))
    ax=fig.add_subplot(111)
    comps=[ zip(*c.execute("""SELECT flux,1-comp FROM stats WHERE sf=? ORDER BY flux""",(names[i],)).fetchall())[1] for i in range(len(names))]
    (fluxes,master_comp)=zip(*c.execute("""SELECT flux,1-comp FROM stats WHERE sf='master' ORDER BY flux""").fetchall())
    comps.append( master_comp)
    snrs=np.array(fluxes)/25e-6
    comps=np.array(comps)
    comps+=1e-6
    ax.loglog(  snrs,comps[0],'b--', #sfind
                snrs,comps[3],'c-',  #imsad
                drawstyle='steps-post')
    ax.loglog(  snrs,comps[2],'r--',  #selavy
                snrs,comps[4],'y-',  #aegean
                snrs,comps[1],'g-.', #sex
                drawstyle='steps-post',linewidth=2)
    ax.loglog(  snrs,master_comp,'k:', #theory
                drawstyle='steps-post')
    ax.set_ylim((0.1,1e-4))
    ax.set_yticklabels(['99.99','99.9','99','90'])
    ax.set_xlim((5,150))
    ax.set_xticklabels(['a','10','100'],minor=False)
    ax.set_xlabel("Input SNR")
    ax.set_ylabel("Completeness %",ha='center')
    names=['SFIND','IMSAD','Selavy','AEGEAN','SE']
    ax.legend(names,loc=4)
    #fig.suptitle("Completeness")
    plt.savefig('completeness.eps')
    print "completeness.eps"
    
    
def reliability(c):
    names=[]
    for s in st.sf_names:
        if not s=='fndsou':
            names.append(s)
            
    plt.clf()
    fig=plt.figure(1,(4,4))
    ax=fig.add_subplot(111)
    data=[zip(*c.execute("""SELECT counts,rel FROM stats WHERE sf=? ORDER BY flux""",(names[i],)).fetchall()) for i in range(len(names))]
    (fluxes,junk)=zip(*c.execute("""SELECT flux,rel FROM stats WHERE sf='master' ORDER BY flux""").fetchall())
    snrs=np.array([i/25e-6 for i in fluxes])
    rels=[]
    for c,r in data:
        c=np.array(c)
        r=np.array(r)
        rels.append([ sum(c[i:]*r[i:])/sum(c[i:]) for i in range(len(r))])
        
    rels=np.array(rels)
    rels=1-rels
    for i in range(len(snrs)):
        s=snrs[i]
        if (4<s and s<5.5) or (9<s and s<10) or (45<s and s<55):
            for sfi in range(len(names)):
                print "{0} {1:3.0f} {2:5.2f}".format(names[sfi],s,rels[sfi][i]*100)
    ax.semilogx(snrs*0.99,rels[0],'b--', #sfind
                snrs,rels[3],'c-',       #imsad
                drawstyle='steps-post')
    ax.semilogx(snrs,rels[2],'r--',      #selavy
                snrs,rels[4],'y-',       #aegean
                snrs,rels[1],'g-.',      #sex
                drawstyle='steps-post',linewidth=2)
    ax.set_ylim((-0.005,0.04))
    ax.set_yticklabels(['','0 ','','1 ','','2 ','','3 ','','4 '])
    ax.set_xlim((5,2000))
    ax.set_xticklabels(['a','10','100','1,000'],minor=False)
    ax.set_xlabel("Input SNR")
    ax.set_ylabel("False detection rate %",ha='center')
    names=['SFIND','IMSAD','Selavy','AEGEAN','SE']
    ax.legend(names,loc=1)
    #fig.suptitle("False detection rate")
    plt.savefig('fdr.eps')
    print 'fdr.eps'

    
if __name__=="__main__":
    
##     cat_name= sys.argv[-1].lower()
##     if not cat_name in st.sf_names:
##         print "catalog ",cat_name," doesn't work"
##         sys.exit(1)
        
    conn=sqlite3.connect(st.db_file)
    c=conn.cursor()

    #rflux_counts(c)
    reliability(c)
    completeness(c)
    #rflux_dist_hist(c)
    #rflux_accuracy(c)
