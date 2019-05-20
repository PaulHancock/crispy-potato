###
# Get the strongest few sources that were not found by a source finder
# and produce a list of the parameters in a table, along with a plot of
# each source.
#
# V1.0 Paul Hancock 2011-03-20
# V1.1 pjh 2011-03-28
# make use of links table
###


import sqlite3
from mirpy import miriad
import mirpy_filters as mf
from CherryPy import convert
from CherryPy.SimulationTools import MirImage
import static as st
from optparse import OptionParser

import os,sys
from math import pi,cos




def within(x,xmin,xmax):
    return min(max(x,xmin),xmax)

if __name__=="__main__":

    parser = OptionParser()
    parser.add_option("-s", "--sourcefinder", dest="sf_name", help="the name of the source finding program that produced the catalog")
    #parser.add_option("-m","--mapname",dest="mapname",help="The image from which the catalog was derived")
    (op, arg) = parser.parse_args()

    if not op.sf_name:# and op.mapname):
        print "I need source finder."# and the name of the map to process."
        sys.exit(1)
    
    if not op.sf_name in st.sf_names:
        print "catalog ",op.sf_name," doesn't work"
        print "Valid catalog names:", ' '.join(st.sf_names)
        sys.exit(1)
        
    #field,junk=st.get_field_epoch(op.mapname)
    conn=sqlite3.connect(st.db_file)
    c=conn.cursor()

    #set the image flux range
    smin=-1e-4
    smax=1e-3

    data=[]
    for field in range(1):
        data.extend(c.execute("""SELECT c.src_id,c.ra,c.dec,c.pflux,c.bmaj,c.bmin,c.pa,c.field
        FROM
        (SELECT * FROM catalog WHERE sf=? AND field=?) c
        LEFT OUTER JOIN
        (SELECT * FROM links WHERE direction=1 AND field=?) l
        ON l.catalog_id = c.src_id
        WHERE l.master_id IS NULL ORDER BY -c.pflux""",(op.sf_name,field,field)).fetchall())
        
    prefix='{0}-M'.format(op.sf_name.upper())
    print len(data),'false detections'
    print "src_id   RA         DEC        mJy"
    out=open("{0}-FalseDetections.ann".format(op.sf_name),'w')
    out.write("PA SKY\n")
    out.write("COLOUR YELLOW\n")
    for (src_id,ra,dec,flux,bmaj,bmin,pa,field) in data:
        out.write("ELLIPSE {0} {1} {2} {3} {4}\n".format(ra,dec,bmaj/3600,bmin/3600,pa))
    
    
    
        continue #STOP HERE!
        
        
        #figure out the image stats
        im=MirImage(st.data_dir+'MapF{0:02d}E07'.format(int(field)))
        halfsize=int(128*im.dra/2)
        sizex=im.dra*im.nx
        sizey=im.ddec*im.ny
        border=15*max(im.dra,im.ddec)
        
        print '{0:05d} {1:10.6f} {2:+10.6f} {3:8.4f}'.format(src_id,ra,dec,flux*1e3)
        imname='{0}plots/{1}_{2:05d}.eps'.format(st.temp_dir, prefix,src_id)

        
        if os.path.exists(imname):
            continue
        
        #set the region command using the offset between ra/dec and the ref pixel
        raoff=(ra-im.ra_ref)*3600 *cos(dec*pi/180) 
        decoff=(dec-im.dec_ref)*3600
        xmin,ymin,xmax,ymax=raoff-halfsize,decoff-halfsize,raoff+halfsize,decoff+halfsize
        #don't let the subregion extend outside the main image
        xmin=within(xmin,-sizex/2.0+border,sizex/2.0-border)
        ymin=within(ymin,-sizey/2.0+border,sizey/2.0-border)
        xmax=within(xmax,-sizex/2.0+border,sizex/2.0-border)
        ymax=within(ymax,-sizey/2.0+border,sizey/2.0-border)
        region='arcsec,boxes({0},{1},{2},{3})'.format(xmin,ymin,xmax,ymax)
        #create an overlay of the object morphology
        olay=open('olay.temp','w')
        olay.write('oellipse absdeg absdeg x no {0:f} {1:f} {2:f} {3:f} {4:f}\n'.format(ra,dec, bmaj/3600, bmin/3600, pa))
        olay.write('clear  absdeg absdeg ID{0}_{1:06.3f}mJy yes {2:f} {3:f}\n'.format(src_id,flux*1e3,ra,dec+halfsize/3600.0*3/4))
        if True: #add in some of the master sources in the same region (~10 arcmin circle)
            min_flux=1.25e-4
            radius=15.0/60
            olay.write("colour 5")
            for mrow in c.execute("SELECT ra,dec,bmaj,bmin,pa FROM master WHERE flux >? AND (ra BETWEEN ? AND ?) AND (dec BETWEEN ? AND ?) AND field=? ORDER BY -flux",(min_flux,ra-radius/cos(45*pi/180),ra+radius/cos(45*pi/180),dec-radius,dec+radius,field)):
                mra,mdec,mbmaj,mbmin,mpa = mrow
                olay.write('line absdeg absdeg x no {0:f} {1:f} {2:f} {3:f}\n'.format(mra+1/120.0, mdec+1/120.0, mra-1/120.0, mdec-1/120.0))
                
            for crow in c.execute("SELECT ra,dec,bmaj,bmin,pa FROM catalog c WHERE c.sf=? AND pflux >? AND (ra BETWEEN ? AND ?) AND (dec BETWEEN ? AND ?) AND field=? ORDER BY -flux",(op.sf_name,min_flux,ra-radius/cos(45*pi/180),ra+radius/cos(45*pi/180),dec-radius,dec+radius,field)):
                mra,mdec,mbmaj,mbmin,mpa = crow
                olay.write('line absdeg absdeg x no {0:f} {1:f} {2:f} {3:f}\n'.format(mra+1/120.0, mdec-1/120.0, mra-1/120.0, mdec+1/120.0))
                
        olay.close()
        print imname
        miriad.cgdisp(_in_=im.name+'.mir', type='pixel', region=region, range='%s,%s,log'%(smin,smax), device=imname+'/cps', labtyp='hms,dms', options='blacklab', olay='olay.temp',csize='0,0,2,0')
    #os.popen('psmerge -o{0}plots/Strongest_F{1:02d}_{2}.eps {0}plots/{2}_*.eps'.format(st.temp_dir, field,prefix))
    #os.popen('rm {0}plots/{1}_*.eps'.format(st.temp_dir, prefix))
    #os.popen('psnup -n 12 -b-30 {0}plots/Strongest_F{1:02d}_{2}.eps {0}plots/Strongest_F{1:02d}_{2}.12.eps'.format(st.temp_dir, field,prefix))
    #os.popen('rm {0}plots/Strongest_F{1:02d}_{2}.eps'.format(st.temp_dir, field,prefix))
    

