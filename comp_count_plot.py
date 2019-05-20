"""
"""
import os,sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

import sqlite3
import static as st

if __name__=="__main__":
    conn=sqlite3.connect(st.db_file)
    c=conn.cursor()
    names=[]
    for s in st.sf_names:
        if not s=='fndsou':
            names.append(s)


    plt.clf()
    fig=plt.figure(1,(4,4))
    ylim=(0.15,4.5)
    xlim=(5,200)
    (fluxes,master_counts)=zip(*c.execute("""SELECT flux,counts FROM stats WHERE sf='master' ORDER BY flux""").fetchall())
    fluxes=np.array(fluxes)/25e-6
    master_counts=np.array(master_counts)
    counts=[]
    for i in range(len(names)):
        counts.append(=np.array(zip(*c.execute("""SELECT counts FROM stats WHERE sf=? ORDER BY flux""",(names[i],)).fetchall())[0])
    ax=figure.add_subplot(111)
    ax.loglog(fluxes,counts[0]/master_counts,''

              )
    
    if True:
        #source counts
        plt.clf()
        fig=plt.figure(1,(4,4))
        gs=gridspec.GridSpec(len(names),1,height_ratios=np.ones(len(names)))
        ax=[]
        ylim=(0.15,4.5)
        xlim=(5,200)
        (fluxes,master_counts)=zip(*c.execute("""SELECT flux,counts FROM stats WHERE sf='master' ORDER BY flux""").fetchall())
        fluxes=np.array(fluxes)/25e-6
        master_counts=np.array(master_counts)
        for i in range(len(names)):
            counts=np.array(zip(*c.execute("""SELECT counts FROM stats WHERE sf=? ORDER BY flux""",(names[i],)).fetchall())[0])
            ax.append(fig.add_subplot(gs[i]))
            ax[i].loglog(fluxes,counts/master_counts,'k-',
                         xlim,(1,1), 'k:',
                         (125e-6,125e-6),ylim, 'k:',
                         drawstyle='steps')
            ax[i].set_ylim(ylim)
            ax[i].set_xlim(xlim)
            ax[i].set_yticks([0.5,1,2])
            ax[i].set_yticklabels(['0.5','','2'])
            ax[i].text(100, 0.4 , names[i])
            ax[i].set_xticklabels([])

        ax[-1].set_xticklabels(['','10','100'])
        ax[-1].set_xlabel("Measured SNR")
        #ax[2].set_ylabel("Ratio",rotation=0,ha='center')
        fig.subplots_adjust(hspace=0)
        fig.suptitle("Fraction of sources relative to input catalog")
        plt.savefig('SourceCount.eps')
        sys.exit(0)
    #completeness
    plt.clf()
    fig=plt.figure(1,(4,4))
    ax=fig.add_subplot(111)
    comps=[ zip(*c.execute("""SELECT flux,comp FROM stats WHERE sf=? ORDER BY flux""",(names[i],)).fetchall())[1] for i in range(len(names))]
    (fluxes,master_comp)=zip(*c.execute("""SELECT flux,comp FROM stats WHERE sf='master' ORDER BY flux""").fetchall())
    comps.append( master_comp)
    snrs=[i/25e-6 for i in fluxes]
    ax.semilogx(snrs,comps[0],'b-',
                snrs,comps[1],'g-',
                snrs,comps[2],'r-',
                snrs,comps[3],'c-',
                snrs,comps[4],'y-',
                snrs,master_comp,'k:')
    ax.set_ylim((0.8,1.05))
    ax.set_xlim((3,50))
    ax.set_xlabel("Input SNR")
    ax.set_ylabel("%",rotation=0,ha='center')
    ax.legend(names,location=4)
    fig.suptitle("Completeness")
    plt.savefig('completeness.eps')

            
    
    sys.exit(0)
    #completeness
    plt.clf()
    fig=plt.figure(1,(4,4))
    gs=gridspec.GridSpec(len(names),1,height_ratios=np.ones(len(names)))
    ax=[]
    ylim=(0.8,1.1)
    comps=[]
    (fluxes,master_comp)=zip(*c.execute("""SELECT flux,comp FROM stats WHERE sf='master' ORDER BY flux""").fetchall())
    for i in range(len(names)):
        (junk,comps) = zip(*c.execute("""SELECT flux,comp FROM stats WHERE sf=? ORDER BY flux""",(names[i],)).fetchall())
        ax.append(fig.add_subplot(gs[i]))
        ax[i].set_ylim(ylim)
        ax[i].set_xlim(xlim)
        ax[i].semilogx(fluxes,comps,'k-',
                     fluxes,master_comp, 'k:',
                     (125e-6,125e-6),ylim, 'k:',
                     drawstyle='steps')
        ax[i].set_yticks([0.8,0.85,0.9,0.95,1.0],minor=True)
        ax[i].set_yticks([])
        ax[i].set_yticklabels([],minor=False)
        ax[i].set_yticklabels(['80','','90','','100'],minor=True)
        ax[i].text( 0.4, 0.9, names[i])
        ax[i].set_xticklabels([])
        
    ax[-1].set_xticklabels(['a','0.1mJy','1mJy','10mJy','100mJy','1Jy'])
    ax[-1].set_xlabel("Input Flux")
    ax[2].set_ylabel("%",rotation=0,ha='center')
    fig.subplots_adjust(hspace=0)
    fig.suptitle("Completeness")
    plt.savefig('completeness.eps')

    #reliability
    plt.clf()
    fig=plt.figure(1,(4,4))
    gs=gridspec.GridSpec(len(names),1,height_ratios=np.ones(len(names)))
    ax=[]
    ylim=(0.8,1.1)
    (fluxes,junk)=zip(*c.execute("""SELECT flux,rel FROM stats WHERE sf='master' ORDER BY flux""").fetchall())
    for i in range(len(names)):
        (junk,rels)= zip(*c.execute(""" SELECT flux,rel FROM stats WHERE sf=? ORDER BY flux""",(names[i],)).fetchall())
        ax.append(fig.add_subplot(gs[i]))
        ax[i].set_ylim(ylim)
        ax[i].set_xlim(xlim)
        ax[i].semilogx(fluxes,rels,'k-',
                     (125e-6,125e-6),ylim, 'k:',
                     xlim,(1,1),'k:',
                     drawstyle='steps')
        ax[i].set_yticks([0.8,0.85,0.9,0.95,1.0],minor=True)
        ax[i].set_yticks([])
        ax[i].set_yticklabels([],minor=False)
        ax[i].set_yticklabels(['80','','90','','100'],minor=True)
        ax[i].text( 0.4, 0.9, names[i])
        ax[i].set_xticklabels([])
        
    ax[-1].set_xticklabels(['a','0.1mJy','1mJy','10mJy','100mJy','1Jy'])
    ax[-1].set_xlabel("Catalog Flux")
    ax[2].set_ylabel("%",rotation=0,ha='center')
    fig.suptitle("Reliability")
    fig.subplots_adjust(hspace=0)
    plt.savefig('reliability.eps')
    
    sys.exit(0)
    #fscore
    plt.clf()
    fig=plt.figure(1,(4,4))
    gs=gridspec.GridSpec(len(names),1,height_ratios=np.ones(len(names)))
    ax=[]
    ylim=(0.9,1.05)
    xlim=(75e-6,0.01)
    rels=[]
    fscores=[]
    #fscore is 2*c*r/(c+r)
    for i in range(len(names)):
        comps.append(np.array([float(a[i+1+8]) for a in data]))
        rels.append(np.array([float(a[i+1+15]) for a in data]))
        fscores.append([ 2*c*r/(c+r) for c,r in zip(comps[-1],rels[-1])]) 
        ax.append(fig.add_subplot(gs[i]))
        ax[i].set_ylim(ylim)
        ax[i].set_xlim(xlim)
        ax[i].semilogx(fluxes,fscores[i],'k-',
                     (125e-6,125e-6),ylim, 'k:',
                     xlim,(1,1),'k:',
                     drawstyle='steps')
        ax[i].set_yticks([0.9,0.95,1.0],minor=True)
        ax[i].set_yticks([])
        ax[i].set_yticklabels([],minor=False)
        ax[i].set_yticklabels(['90','95','100'],minor=True)
        ax[i].text( 0.004, 0.95, names[i])
        ax[i].set_xticklabels([])
        
    ax[-1].set_xticklabels(['a','0.1mJy','1mJy','10mJy'])
    ax[-1].set_xlabel("Input Flux")
    ax[2].set_ylabel("F-Score",rotation=0,ha='center')
    fig.subplots_adjust(hspace=0)
    plt.savefig('fscore.eps')
