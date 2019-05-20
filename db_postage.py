"""
Extract a set of sources from the stage3.fits file and
export them as a set of postage stamps.

Paul Hancock
2011-05-16
"""

import os,sys
import sqlite3
from mirpy import miriad
from math import cos,pi
from CherryPy import convert
from convert import ra2dec,dec2dec

class MirImage():
    def __init__(self,image_name):
        self.name=image_name
        self.nx=2401
        self.ny=2401
        self.dra=-6/3600.0
        self.ddec=6/3600.0
        self.ra_ref=182.5
        self.dec_ref=-45.0
        self.ra_ref_pix=1201
        self.dec_ref_pix=1201
        self._bounds()

    def _bounds(self):
        #use impos to find the bounds of the image!
        xmin,ymin=self.get_coords(xy=[0,0],types=['abspix','abspix'])['world_str']
        xmin=ra2dec(xmin)
        ymin=dec2dec(ymin)

        xmax,ymax=self.get_coords(xy=[self.nx,self.ny],types=['abspix','abspix'])['world_str']
        xmax=ra2dec(xmax)
        ymax=dec2dec(ymax)
        self.bounds=(xmin,ymin,xmax,ymax)

    def impos_filter(self,data):
        """Filter the output of impos into a dict that is useful"""
        coords={}
        lines=data.split('\n')
        #print lines
        coords['world_str']=( lines[3].split()[4], lines[4].split()[4] )
        coords['offset_arcsec']=( float(lines[7].split()[4]), float(lines[8].split()[4]) )
        #int() truncates decimals, this is probably not what i want.
        coords['abspix']=( int(float(lines[11].split()[4])), int(float(lines[12].split()[4])) )
        coords['relpix']=( int(float(lines[15].split()[4])), int(float(lines[16].split()[4])) )
        return coords
    
    def get_coords(self,xy,types=['abspix']):
        if len(types)==1:
            types.append(types[-1])
        miriad.set_filter('impos',self.impos_filter)
        #print "in={0} coord={1},{2} types={3},{4}".format(self.name,xy[0],xy[1],types[0],types[1])
        return miriad.impos(_in_=self.name,coord='{0},{1}'.format(*xy),type='{0},{1}'.format(*types))

    def within(self,x,mn,mx):
        x=max(mn,x)
        x=min(mx,x)
        return x
        
    def get_region(self,center=[0,0],size=[1,1]):
        """
        Returns a region command that represents a given region
        input: center=[ra,dec] in degrees
               size = [dra,ddec] in pixels
        output: 'abspix,boxes(xmin,ymin,xmax,ymax)'
        """
        #non ideal version => use impos to find the pixel numbers for the center
        #                  => clip the values to be in (0,2401)
        #output: 'abspix,boxes(bla)'

        #center in pixels:
        xo,yo=self.get_coords(xy=center,types=['absdeg'])['abspix']

        (xmin,ymin,xmax,ymax)=(xo-size[0]/2,yo-size[1]/2,xo+size[0]/2,yo+size[1]/2)
        xmin=self.within(xmin,0,self.nx)
        xmax=self.within(xmax,0,self.nx)
        ymin=self.within(ymin,0,self.ny)
        ymax=self.within(ymax,0,self.ny)
        return "abspix,boxes({0},{1},{2},{3})".format(*[int(x) for x in [xmin,ymin,xmax,ymax]])

    def get_range(self,region=""):
        """
        Returns the min and max of the image within the given region
        """
        print "TBA"
        return

class Source():
    def __init__(self,ra,dec,name,flux=0):
        self.ra=ra
        self.dec=dec
        self.name=name
        self.flux=flux

    def __repr__(self):
        return "{0} {1} {2}".format(self.name,self.ra,self.dec)
    
    def cut_region(self,image,size=[512,512],out_name=None):
        if out_name is None:
            out_name="stamps/{0}.mir".format(self.name)
        if out_name[-4:] !='.mir':
            out_name+='.mir'
        if not os.path.exists(out_name):
            region=image.get_region(center=[self.ra,self.dec],size=size)
            #print region
            miriad.imsub(_in_=image.name,out=out_name, region=region)
            return out_name
        else:
            return "skipped"


def sources(c,max=10):
    data=c.execute("""SELECT ra,dec,src_id FROM master WHERE flux >125e-6 ORDER BY -flux""")
    num=0
    for d in data:
        num+=1
        if num>max:
            break
        name="Src_{0:05d}".format(d[2])
        yield Source(d[0],d[1],name)


if __name__=="__main__":
    print "OLD"
    sys.exit(1)
    db_file='SfSim_20110601.db'
    conn=sqlite3.connect(db_file)
    c=conn.cursor()

    image=MirImage('../../DATA/SfSim/field7.mir')
    os.popen('rm -r stamps/*.mir')
    for s in sources(c,max=1000):
        print s.name, s.cut_region(image,size=[128,128])

