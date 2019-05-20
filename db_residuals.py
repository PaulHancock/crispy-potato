"""
For a list of 'problem' sources:
 find all sources within r'' of the source for each source finding
 create an image/model/residual .mir file for each source finder

Created: Paul Hancock 15-Jun-2011
"""

import os, sys
from mirpy import miriad
import sqlite3
from CherryPy.SimulationTools import MirImage,Source
import static as st

def rm(out_name):
    if os.path.exists(out_name):
        os.popen('rm -r {0}'.format(out_name))

def fits(name):
    rm(name+'.fits')
    miriad.fits(_in_=name+'.mir',out=name+'.fits',op='xyout')

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

def gen_ann(src_list,out_name):
    """
    Generates an annotation file that Kvis can read.
    Each of the sources in src_list will be represented
    """
    ann_fmt="ellipse {0} {1} {2} {3} {4}"
    out=open(out_name,'w')
    print >>out,'PA SKY'
    print >>out,'colour red'
    for src in src_list:
        src[2]/=3600 # arcsec to degrees
        src[3]/=3600
        print >>out, ann_fmt.format(*src)
    out.close()
    return out_name

def diff_img(data_file,model_file,out_file):
    """
    Create data-model=residual
    uses miriad, doesn't do any checking
    """
    exp="<{0}>-<{1}>".format(data_file,model_file)
    rm(out_file)
    miriad.maths(exp=exp,out=out_file)
    return out_file

def get_nearby(ra,dec,ra_ref,dec_ref,radius,sf,field,limit=10):
    if sf=='master':
        sources=c.execute("""SELECT flux,(ra-?)*3600,(dec-?)*3600,bmaj,bmin,pa,ra,dec,src_id FROM master
        WHERE
        ra BETWEEN ? AND ?
        AND
        dec BETWEEN ? AND ?
        AND
        field=?
        ORDER BY -flux
        """,(ra_ref,dec_ref,ra-radius,ra+radius,dec-radius,dec+radius,field))
    else:
        sources=c.execute("""SELECT pflux,(ra-?)*3600,(dec-?)*3600,bmaj,bmin,pa,ra,dec,src_id FROM catalog
        WHERE
        ra BETWEEN ? AND ?
        AND
        dec BETWEEN ? AND ?
        AND
        sf=?
        AND
        field=?
        ORDER BY -flux
        LIMIT ?
        """,(ra_ref,dec_ref,ra-radius,ra+radius,dec-radius,dec+radius,sf,field,limit))
        print ra_ref,dec_ref,ra-radius,ra+radius,dec-radius,dec+radius,sf,field
    l=[]
    for s in sources:
        #print s
        l.append([float(a) for a in s])
    #return the flux, ra/dec offsets in arcseconds, bmaj,bmin,pa
    return l


def make_eps(file,outname,min=0,max=125e-6):
    miriad.cgdisp(_in_=file,type='pix',range=(min,max),device='{0}.ps/ps'.format(outname),options='blacklab')

if __name__=="__main__":
    
    conn=sqlite3.connect(st.db_file)
    c=conn.cursor()

    fmt="{0:8.6f} {1:7.2f} {2:7.2f} {3:5.2f} {4:5.2f} {5:5.2f}"

    sources=[2,10085,30173,40234,40235,40239,70362,90446]
    #[70,196,10084,10141,10657,20850,20389,30243,30278,90649, \
    #        1176, 1154, 1230]#this line are just sources that were not detected

    sfnames=st.sf_names
    sfnames=['tesla']
    sfnames.extend(['master'])
    for src_id in sources:
        ra,dec,field=c.execute("SELECT ra,dec,field FROM master WHERE src_id=?",(src_id,)).next()
        flux=c.execute("SELECT flux FROM master WHERE ra BETWEEN ? and ? AND dec BETWEEN ? and ? ORDER BY -flux",(ra-6/60.0,ra+6/60.0,dec-6/60.0,dec+6/60.0)).next()[0]
        im=MirImage('{0}MapF{1:02d}E07'.format(st.data_dir,field))
        print "#Src_id:",src_id
        src = Source(ra,dec,src_id)

        #create a cut out of this source
        data_file=src.cut_region(im,size=[121,121],out_name='stamps/{0}_data.mir'.format(src.name),clobber=True)
        fits('stamps/{0}_data'.format(src.name))
        make_eps(data_file,data_file[:-4],min=-flux*0.2,max=flux*1.2)
        #now make a 'model' file
        #continue #actually... don't
        for sf in sfnames:
            print "Sf:",sf
            found_sources= get_nearby(ra,dec,im.ra_ref,im.dec_ref,6/60.0,sf,field)
            gen_sources=[]
            ann_sources=[]
            for f in found_sources:
                #print '{0:5.0f}'.format(f[-1]),
                print fmt.format(*f[:6])
                gen_sources.append(f[:6]) #flux, dra,ddec, a, b, pa
                ann_sources.append([f[a] for a in [6,7,3,4,5]]) # ra,dec,a,b,pa
            model_file=gen_img(data_file,gen_sources,'stamps/{0}_{1}_model.mir'.format(src.name,sf))
            ann_file=gen_ann(ann_sources,'stamps/{0}_{1}_src.ann'.format(src.name,sf))
            fits('stamps/{0}_{1}_model'.format(src.name,sf))

            ##now make a residual image
            #resid_file=diff_img(data_file,model_file,out_file='stamps/{0}_{1}_residual.mir'.format(src.name,sf))
            #fits('stamps/{0}_{1}_residual'.format(src.name,sf))

            ##and make some .eps files for including in my paper
            #make_eps(resid_file,resid_file[:-4],min=-flux*0.2,max=flux*1.2)
            #make_eps(model_file,model_file[:-4],min=-flux*0.2,max=flux*1.2)
            
            
