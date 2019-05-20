"""
Plot the completeness of each of the surveys on a single graph

Paul Hancock
May-11-2011
"""

import sqlite3
import sys,os
import numpy as np
from math import pi,cos,exp,sqrt,log
import matplotlib
import matplotlib.pyplot as plt

import static as st
from scipy.special import erf, erfc

class Catalog:

    def __init__(self,cat_name,cursor):
        self.name=cat_name
        self.c=cursor
        self.completeness_x=np.logspace(np.log10(125e-6),-1,50)
        self.completeness_x[0]=125e-6
        self.completeness_x[5]=25e-5
        self.completeness_x[17]=125e-5
        self.completeness_y=None
        self.source_counts_x=np.logspace(np.log10(125e-6),-1,50)
        self.source_counts_y=None
        self.reliability_x=np.logspace(np.log10(125e-6),-1,50) #[10**(a/100.0) for a in range(-450,10,1)]
        self.reliability_y=None

    def __repr__(self):
        return self.name

    def get_completeness_x(self):
        if not self.completeness_y:
            self.get_completeness()
        return self.completeness_x

    def get_completeness_y(self):
        if not self.completeness_y:
            self.get_completeness()
        return self.completeness_y

    def get_completeness(self):
        """Calculate and return the completeness of this catalog.
        Returns: x - a list of fluxes
                 y - the completeness at each flux level"""
        if self.completeness_y: #if we already calculated this before
            return self.completeness_x,self.completeness_y
        print "#completeness {0}".format(self.name)
        
        self.completeness_y=[]
        for flux in self.completeness_x:
            print flux
            comp=self.c.execute("""
            SELECT count(ml.catalog_id)/(0.0+count(ml.src_id)) 
            FROM ( master m LEFT OUTER JOIN links l 
            ON l.master_id = m.src_id AND l.sf=? and l.direction=0) ml WHERE ml.flux>?
            """,(self.name,flux)).next()[0]
            input=0
            output=0
            for field in range(10):
                if field==5:
                    continue #sfind breaks on this so don't include it in the analysis
                (out,inp)=self.c.execute("""
            SELECT count(ml.catalog_id)+0.0,0.0+count(ml.src_id)
            FROM (
            (SELECT * FROM master WHERE field=?) m
            LEFT OUTER JOIN
            (SELECT * FROM links WHERE field=? AND direction=0 AND sf=?) l 
            ON l.master_id = m.src_id ) ml WHERE ml.flux>?
            """,(field,field,self.name,flux)).next()
                input+=inp
                output+=out
            if input<1:
                comp=0 #
            else:
                comp=output/input
            self.completeness_y.append(comp or 0)
        return self.completeness_x,self.completeness_y
    
    def get_reliability_x(self):
        if not self.reliability_y:
            self.get_reliability()
        return self.reliability_x
    
    def get_reliability_y(self):
        if not self.reliability_y:
            self.get_reliability()
        return self.reliability_y

    def get_reliability(self):
        if self.reliability_y:
            return self.reliability_x, self.reliability_y
        self.reliability_y=[]
        print "#reliability {0}".format(self.name)
        for i in range(len(self.completeness_x)-1):
            print i, 
            rel=self.c.execute("""SELECT count(cl.catalog_id)/(0.0+count(cl.src_id))
            FROM
            ((SELECT * FROM catalog WHERE sf=? AND flux BETWEEN ? AND ?) c LEFT OUTER JOIN links l
            ON c.src_id = l.catalog_id AND direction=1
            ) cl""",(self.name,self.completeness_x[i],self.completeness_x[i+1])).next()[0]
            print (rel or 0)
            self.reliability_y.append(rel or 0)
        self.reliability_y.append(1) # to make the two arrays the same length.
        return self.reliability_x,self.reliability_y

    def get_source_counts_x(self):
        if not self.source_counts_y: #not a mistake this should be y
            self.get_source_counts()
        return self.source_counts_x

    def get_source_counts_y(self):
        if not self.source_counts_y:
            self.get_source_counts()
        return self.source_counts_y
    
    def get_source_counts(self):
        if self.source_counts_y:
            return self.source_counts_x, self.source_counts_y
        
        self.source_counts_y=[]
        for i in range(len(self.source_counts_x)-1):
            comp=self.c.execute("SELECT count(*) FROM catalog WHERE sf=? AND pflux BETWEEN ? AND ?",
                                (self.name,self.source_counts_x[i],self.source_counts_x[i+1])).next()[0]
            self.source_counts_y.append(comp or 1e-9)
        self.source_counts_x=self.source_counts_x[:-1] #chop off the last entry so x,y are the same length

class Master(Catalog):
    
    def get_completeness(self):
        if not self.completeness_y:
            self.get_completeness_y()
        return self.completeness_x,self.completeness_y
    
    def get_source_counts(self):
        if self.source_counts_y:
            return self.source_counts_x, self.source_counts_y
        
        self.source_counts_y=[]
        for i in range(len(self.source_counts_x)-1):
            comp=self.c.execute("SELECT count(*) FROM master WHERE flux BETWEEN ? AND ?",
                                (self.source_counts_x[i],self.source_counts_x[i+1])).next()[0]
            self.source_counts_y.append(comp or 0.1)
        self.source_counts_x=self.source_counts_x[:-1] #chop off the last entry so x,y are the same length

    def get_completeness_y(self):
        """Calculate the theoretical completeness, when considering the addition of noise."""
        print "Completeness master"
        if self.completeness_y:
            return self.completeness_y
        else:
            self.completeness_y=[]

        fac = sqrt(4*log(2))
        def p(s,s0,r2c):
            #return 0.5*erfc(fac* (s0-s)/r2c)
            return 0.5*erfc( (s0-s)/sigma  )

        sigma=25e-6
        r2c=2*sigma/sqrt(log(2))
        
        for s0 in self.completeness_x:
            #number of injected sources brighter than s0
            fluxes=zip(*self.c.execute("SELECT flux FROM master WHERE flux>?",(s0,)).fetchall())[0]
            denomenator = len(fluxes)
            #number of injected sources brighter than s0 that have
            # a recovered flux of >5sigma
            ned= sum( [ p(s,5*sigma,r2c) for s in fluxes])
            print ned,denomenator
            self.completeness_y.append( ned/denomenator )
        return self.completeness_y
        
    def get_reliability_x(self):
        if not self.reliability_y:
            self.get_reliability()
        return self.reliability_x
    
    def get_reliability_y(self):
        if not self.reliability_y:
            self.get_reliability()
        return self.reliability_y

    def get_reliability(self):
        if self.reliability_y:
            return self.reliability_x, self.reliability_y
        self.reliability_y=[]
        print "#reliability {0}".format(self.name)
        
        def fd(s,ds):
            ln2=np.log(2)
            return (erfc(2*s*ln2) - erfc(2*(s+ds)*ln2))
        
        sigma=25e-6
        factor=(2*3600)**2*(2*np.pi +3*np.sqrt(3))/(225*np.pi) * sigma/4*np.sqrt(np.pi/np.log(2))
        for i in range(len(self.reliability_x)-1):
            s=self.reliability_x[i]
            ds=self.reliability_x[i+1]-s
            nsrc=self.c.execute("""SELECT count(flux) FROM master WHERE flux BETWEEN ? AND ?""",(s,s+ds)).next()[0]
            rel=1+fd(s/sigma,ds/sigma)*factor*10/nsrc #calculation is for 1 field and there are 10 in the database
            self.reliability_y.append(rel)
            
            
        self.reliability_y.append(1) # to make the two arrays the same length.
        return self.reliability_x,self.reliability_y

def test_theory_completeness(c):
    master=Master('master',c)
    plt.clf()
    fig=plt.figure(1,(4,4))
    ax=fig.add_subplot(111)
    ax.loglog(master.get_completeness_x(),master.get_completeness_y(),'k-')
    ax.set_ylabel('Completeness')
    ax.set_xlabel('Input Flux (Jy)')
    ax.set_xlim((5e-5,0.1))
    ax.set_ylim((0.9,1))
    plt.savefig('{0}plots/temp.eps'.format(st.temp_dir),orientation='landscape',papertype='a4',dpi=600)
    sys.exit()

if __name__=="__main__":

    
    conn=sqlite3.connect(st.db_file)
    c=conn.cursor()
    #test the theoretical completeness calculation
    #test_theory_completeness(c)
    #sys.exit()
    
    cats=[]
    for cat_name in st.sf_names:
        if cat_name=='fndsou':
            continue
        cats.append(Catalog(cat_name,c))
        print '#',cats[-1]
    #for when you have only updated a single source finding algorithm
    cats=[Catalog('sex',c)]
    master=Master('master',c)

    fluxes=master.get_completeness_x()
   
    c.execute("""DELETE FROM stats WHERE sf='master'""")
    for (f,comp,sc,r) in zip(fluxes,master.get_completeness_y(),master.get_source_counts_y(),master.get_reliability_y()):
        c.execute("""INSERT INTO stats (sf, flux, comp, counts, rel) VALUES ('master',?,?,?,?)  """,(f,comp,sc,r))
        print 'master',f,comp,sc,r

    #for i in range(len(cats)):
    #    c.execute("""DELETE FROM stats WHERE sf=?""",(cats[i].name,))
    #    for (f,comp,sc,r) in zip(fluxes,cats[i].get_completeness_y(),cats[i].get_source_counts_y(),cats[i].get_reliability_y()):
    #        c.execute("""INSERT INTO stats (sf,flux,comp,counts,rel) VALUES (?,?,?,?,?) """,(cats[i].name,f,comp,sc,r))
    #save and close the DB
    conn.commit()
    c.close()
