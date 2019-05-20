"""
Make some plots that show the reference, model, and residual image for a bunch of sources
and for a list of source finders.

Created: Paul Hancock 26 June 2011
"""


from matplotlib import pyplot, mpl
from matplotlib.patches import Ellipse
import numpy as np
import math
import pyfits
import pywcs

#make a nice colour bar, with min/max values as required

def round(a,b):
    return b*math.trunc(a/b)

def c_bar(ax,cmap,norm,vmin,vmax,label=''):
    cb= mpl.colorbar.ColorbarBase(ax,cmap=cmap,norm=norm,orientation='horizontal')
    cb.set_label(label)
    xts=np.linspace(vmin,vmax,11)
    cb.set_xticks(xts)
    cb.set_xticklabels(['{0:3.0f}'.format(x*1e6) for x in xts])
    return cb

def cont_plot(ax,data,cmap,norm,levels,sources):
    ax.imshow(data,cmap=cmap,origin='lower',norm=norm,interpolation='nearest')
    ax.contour(data,colors='blue',origin='lower',norm=norm,levels=levels, antialiased=True,hold='on')
    ax.text(75,5,'q',ha='center',size=14)
    for x,y,a,b,pa in sources:
        e=Ellipse(xy=(x,y),width=b,height=a,angle=pa, fill=False, ec='r')
        ax.add_artist(e)
    ax.set_xticklabels([])
    ax.set_yticklabels([])

def im_plot(ax,data,cmap,norm):
    ax.imshow(data,cmap=cmap,origin='lower',norm=norm, interpolation='nearest')
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    


if __name__=='__main__':
    srcs={70:{},196:{}}
    for src in [90649]: #10084,10141,10657,196,20389,20850,30243,30278,70,90649,1176, 1154, 1230]:
        hdulist=pyfits.open('stamps/{0}_data.fits'.format(src))
        wcs=pywcs.wcs(hdulist[0].header)
        data=hdulist[0].data
        #set up the color bar and figure out the max/min of each map
        cmap=mpl.cm.Greys
        dmin=-75e-6
        dmax=125e-6*2
        norm=mpl.colors.Normalize(vmin=dmin,vmax=dmax)

        ax=pyplot.axes()
        #im_plot(ax,data,cmap,norm)
        sources=[(20,20,5,5,45)] 
        cont_plot(ax,data[20:100,20:100],cmap,norm,[125e-6],sources)
        pyplot.savefig('stamps/{0}_data.eps'.format(src),transparent=True)
        pyplot.clf()  
        
        #ax=pyplot.axes([0.05,0.1,0.90,0.05])
        #cb=c_bar(ax,cmap,norm,dmin,dmax,label='uJy/Beam')
        #pyplot.savefig('stamps/{0}_cbar.eps'.format(src),transparent=True)
        #pyplot.clf()
        continue #don't make any of the residual images
        for sf in ['tesla','imsad','sfind','sex','selavy','fndsou']:
            fname='{0}_{1}'.format(src,sf)
            print fname
            
            model=pyfits.open('stamps/{0}_model.fits'.format(fname))[0].data
            residual=pyfits.open('stamps/{0}_residual.fits'.format(fname))[0].data
            ax=pyplot.axes()
            im_plot(ax,model,cmap,norm)
            pyplot.savefig('stamps/{0}_model.eps'.format(fname),transparent=True)
            pyplot.clf()

            ax=pyplot.axes([0.05,0.1,0.90,0.05])
            cb=c_bar(ax,cmap,norm,dmin,dmax,label='uJy/Beam')
            pyplot.savefig('stamps/{0}_cbar.eps'.format(fname),transparent=True)
            pyplot.clf()

            ax=pyplot.axes()
            levels=list(np.logspace(0,np.log10(50),50)*dmax*-0.1)
            levels.extend([-a for a in levels])
            cont_plot(ax,residual,cmap,norm,levels)
            pyplot.savefig('stamps/{0}_resid_contour.eps'.format(fname),transparent=True)
            pyplot.clf()

    
