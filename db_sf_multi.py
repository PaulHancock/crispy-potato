"""
Look for sources in the master catalog that were found by only a subset of the source finders.

Paul Hancock 24 May 2011
"""


import sqlite3
import sys,os
from mirpy import miriad
from math import cos,pi
from CherryPy import convert
from convert import ra2dec,dec2dec
import static as st

sf_progs=['imsad','selavy','sex','sfind','tesla','fndsou']

class MirImage():
    def __init__(self,image_name):
        self.name=image_name
        self.nx=4801
        self.ny=4801
        self.dra=-6/3600.0
        self.ddec=6/3600.0
        self.ra_ref=180.0
        self.dec_ref=-0.0
        self.ra_ref_pix=2401
        self.dec_ref_pix=2401
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


def olay(c,src,dist):
    """
    Prepare an overlay for use with cgdisp.
    The overlay has a red dot at the master source location and
    various sized circles at the location of sources within
    a given distance
    Source in the master list with fluxes over 3sigma are also plotted.
    src = master source
    dist = distance in ra,dec (degrees) 
    """
    sf_sizes={'master':1,'imsad':2,'sex':3,'sfind':4,'selavy':5,'tesla':6}
    sf_colours={'master':2,'imsad':6,'sex':3,'sfind':7,'selavy':8,'tesla':13}
    fmt_col='COLOUR {0}\n'
    fmt_master='sym absdeg absdeg x no {0} {1} 1 {2}\n' #sym 1 = filled in circle
    fmt_source='sym absdeg absdeg x no {0} {1} 4 {2}\n' #sym 4 = empty circle
    txt_fmt='clear absdeg absdeg {2} yes {0} {1} \n'

    #grab the sources that are nearby
    cat_sources=c.execute("""SELECT ra,dec,sf FROM catalog
    WHERE ra BETWEEN ? AND ?
    AND dec BETWEEN ? AND ?""",(src.ra-dist[0],src.ra+dist[0], src.dec-dist[1],src.dec+dist[1]) )
    print src.name, src.ra-dist[0],src.ra+dist[0], src.dec-dist[1],src.dec+dist[1]

    #draw a filled in red circle for the source of interest
    out_file=open('olay.temp','w')
    out_file.write(fmt_col.format(sf_colours['master']))
    out_file.write(fmt_master.format(src.ra,src.dec,sf_sizes['master']*8))
   
    for ra,dec,sf in cat_sources: #draw circles where the found sources are
        out_file.write(fmt_col.format(sf_colours[sf]))
        out_file.write(fmt_source.format(ra,dec,sf_sizes[sf]))

    master_sources=c.execute("""SELECT ra,dec FROM master
    WHERE ra BETWEEN ? AND ?
    AND dec BETWEEN ? AND ?
    AND flux > 75e-6""",(src.ra-dist[0],src.ra+dist[0], src.dec-dist[1],src.dec+dist[1]) )
    
    for ra,dec in master_sources: # draw an empty circle for the other injected sources
        out_file.write(fmt_col.format(sf_colours['master']))
        out_file.write(fmt_source.format(ra,dec,sf_sizes['master']))
                      
    for sf in sf_sizes: #draw a key for the different circles
        out_file.write(fmt_col.format(sf_colours[sf]))
        out_file.write(fmt_source.format(src.ra+0.40/60.0*15, src.dec-3.0/60-sf_sizes[sf]*0.5/60,sf_sizes[sf]))
        out_file.write(fmt_col.format(1))
        text=sf
        if sf=='master':
            text='SRC_{0}'.format(src.name)
        out_file.write(txt_fmt.format(src.ra+0.30/60.0*15, src.dec-3.0/60-sf_sizes[sf]*0.5/60,text))

    out_file.close()
    return 'olay.temp'

def image2eps(c,image,src,out_name=None):
    """
    Take an image and a master source_id and create an eps file with an overlay.
    The overlay contains all the sources found within the extent of the image.
    The overlaid sources are coded by the source finder from which they came.
    """
    if out_name is None:
        out_name="SFM_SRC_{0}.eps".format(src.name)
    region=image.get_region(center=[src.ra,src.dec],size=[128,128])
    range="{0},{1},lin,1".format(-src.flux,src.flux) #use the source flux as the -min,max
    device="plots/{0}/cps".format(out_name)
    dist=[128*abs(image.dra),128*abs(image.ddec)]
    miriad.cgdisp(_in_=image.name,range=range,device=device,labtyp='hms,dms',csize='0 0 1 0',
                  options='blacklab,full,wedge',olay=olay(c,src,dist),region=region)
    return device[:-4]
    

def detail(c,src_id):
    """Get some details about the master source with the given id.
    Details = ra/dec/flux/image and which sources it was matched."""
    mfmt="Source  {0:05d} {3} {4} {5:5.3e} {6:5.2f} {7:5.2f} {8:6.2f}"
    cfmt=":{0:6s} {1:05d} {4} {5} {6:5.3e} {7:5.2f} {8:5.2f} {9:6.2f}"
    found =[]
    master_src=c.execute("SELECT * FROM master WHERE src_id = ?",(src_id,)).next()
    print mfmt.format(*master_src)
    
    cat_src=c.execute("SELECT c.sf, src_id, ra, dec, ra_str, dec_str, flux, bmaj, bmin, pa FROM catalog c INNER JOIN links l ON l.catalog_id = c.src_id AND l.direction=1 WHERE l.master_id = ?",(src_id,))
    for c in cat_src:
        print cfmt.format(*c)
        found.append(c[0])
    for s in sf_progs:
        if not (s in found):
            print ":{0:6s} <--not found-->".format(s)

        
def master_sources(c,lim=10):
    data=c.execute("SELECT matches, ra, dec, src_id, flux FROM (SELECT count(m.src_id) matches, src_id, ra, dec, flux  FROM master m LEFT OUTER JOIN links l ON l.master_id = m.src_id  AND l.direction=0 GROUP BY m.src_id) WHERE matches <6 ORDER BY -flux LIMIT ?", (lim,))
    for src in data:
        bla,ra,dec,id,flux=src
        yield Source(ra,dec,id,flux=flux)

if __name__=="__main__":
    conn=sqlite3.connect(st.db_file)

    image=MirImage('../../DATA/SfSim/field7.mir')
    
    c1=conn.cursor() #i need a cursor for each query that is to be run
    c2=conn.cursor() # only because of the nested structure below
    os.popen('rm plots/SFM*.eps')
    os.popen('rm -r stamps/SFM*.mir')
    for src in master_sources(c1,lim=50):
        detail(c2,src.name) #i start a new query before the old query is complete
        print src.cut_region(image,size=[64,64],out_name='stamps/SFM_SRC_{0}.mir'.format(src.name))
        print image2eps(c2,image,src)
    os.popen('psmerge  -oSFM.eps plots/SFM_SRC*.eps')
    os.popen('psnup -n 6 SFM.eps SFM.6.eps')
