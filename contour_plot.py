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

if __name__=='__main__':
    colours={0:'r',1:'y',11:'y',100:'c',1000:'c'}
    for i in range(1,6):
        hdulist=pyfits.open('ATLAS/ATLAS{0}.fits'.format(i))
        hdulist=pyfits.open('ATLAS/ATLAS{0}.resid.mir.fits'.format(i))
        wcs=pywcs.WCS(hdulist[0].header)
        data=hdulist[0].data
        #set up the color bar and figure out the max/min of each map
        cmap=mpl.cm.Greys
        sigma=50e-6
        dmin= -10*sigma
        dmax= 10*sigma
        norm=mpl.colors.Normalize(vmin=dmin,vmax=dmax)

        #get the sources from the catalog file
        sources=[ [ float(b) for b in np.array(a.split())[[5,7,11,13,15,17]] ] for a in open('ATLAS/tesla_atlas{0}.cat'.format(i)) if not a.startswith('#')]

        ax=pyplot.axes()
        ax.imshow(data,cmap=cmap,origin='lower',norm=norm,interpolation='nearest')
        ax.contour(data,colors='white',origin='lower',norm=norm,levels=[5*sigma], antialiased=True,hold='on')
        #ax.text(45,5,'q',ha='center',size=14)
        for src in sources:
            #print src
            ra,dec,a,b,pa,flags=src
            x,y=wcs.wcs_sky2pix(np.array([[ra,dec]]),1)[0]
            #print x,y
            e=Ellipse(xy=(x,y),width=b,height=a,angle=pa, fill=False, ec=colours[int(flags)])
            ax.add_artist(e)
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        
        pyplot.savefig('ATLAS/ATLAS{0}.resid.eps'.format(i),transparent=True)
        pyplot.clf()  
