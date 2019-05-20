"""
For a list of 'problem' sources:
 find all sources within r'' of the source for each source finding
 create an image/model/residual .mir file for each source finder

Created: Paul Hancock 15-Jun-2011
"""

import os, sys
from mirpy import miriad
import numpy as np


def rm(out_name):
    if os.path.exists(out_name):
        os.popen('rm -r {0}'.format(out_name))

def fits(name):
    rm(name+'.fits')
    miriad.fits(_in_=name,out=name+'.fits',op='xyout')

def impos_filter(data):
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
    
def diff_image(inimg,outimg,object,spar):
    rm(outimg)
    miriad.imgen(_in_=inimg,out=outimg,factor=1,object=object,spar=spar)
    fits(outimg)

def gen_img(template,src_list,out_name):
    """
    Create a new image filled with sources from src_list.
    template: name of the file which is to be used as the template
    src_list: a list of [flux,ra_off,dec_off,bmaj,bmin,pa] for each source
    out_name: a filename for the output file
    """
    object=''
    spar=''
    spar_fmt="{0:10.8f},{1:10.6f},{2:9.6f},{3:7.4f},{4:7.4f},{5:7.4f},"
    
    for src in src_list:
        #flux, dra,ddec, a, b, pa
        if src[3]<3 or src[4]<3:
            continue
        object+='gaussian,'
        spar+=spar_fmt.format(*src)

    #print object,spar
    
    rm(out_name)
    #print "imgen in={0} out={1} factor=0 object={2} spar={3}".format(template,out_name,object[:-1],spar[:-1])
    miriad.imgen(_in_=template,out=out_name, factor=0, object=object[:-1],spar=spar[:-1])
    return out_name

if __name__=="__main__":

    miriad.set_filter('impos',impos_filter)
    for i in range(1,6):
        imname='ATLAS/ATLAS{0}.mir'.format(i)
        cat_name='ATLAS/tesla_atlas{0}.cat'.format(i)
        outname='ATLAS/ATLAS{0}.resid.mir'.format(i)
        print imname
        object=''
        spar=''
        for s in np.array([l.split() for l in open(cat_name).readlines() if not l.startswith('#')]):
            ra,dec,flux,a,b,pa=np.array(s)[[5,7,9,11,13,15]]
            print ra,dec,flux,a,b,pa
            object+='gaussian,'
            raoff,decoff=miriad.impos(_in_=imname,coord="{0},{1}".format(ra,dec),type="absdeg,absdeg")['offset_arcsec']
            spar+='-{0},{1},{2},{3},{4},{5},'.format(flux,raoff,decoff,a,b,pa)
        print object,spar
        diff_image(imname,outname,object[:-1],spar[:-1])
        print outname
