"""# A simulation of the map that will be created by ASKAP.
# Starting basic, and getting more invovled as needed.
# V0.1 Paul Hancock 6/12/2010
#
# V1.0 Paul Hancock 2011-03-14
# Use a database as the source of the master catalog. 
"""
import sqlite3

from math import sqrt,cos,sin,pi
from mirpy import miriad
import os,sys

import static as st

def make_noise(ra,dec,field,epoch,size=2401):
    if abs(dec) <1e-3:
        dec=0
    #print('# Create the noise map')
    print '{0},{1}'.format(ra/15.0,dec)
    miriad.imgen(out='{0}stage1.mir'.format(st.temp_dir),
                 object='noise',
                 spar=rms,
                 seed=123456+field+epoch*100,
                 radec='{0},{1}'.format(ra/15.0,dec),
                 cell='6,6',
                 imsize='{0},{0}'.format(size))
    #now convolve the noise with a 30" beam
    miriad.convol(map='{0}stage1.mir'.format(st.temp_dir),
                  out='{0}stage2.mir'.format(st.temp_dir),
                  fwhm='30',
                  options='final')
    #fudge the noise back up to what it should be
    miriad.maths(exp='<{0}stage2.mir>*25/92.35'.format(st.temp_dir),
                 out='{0}stage3.mir'.format(st.temp_dir))

def make_image(object,spar):
    miriad.imgen(_in_='{0}stage3.mir'.format(st.temp_dir), 
                 out='{0}stage3.5.mir'.format(st.temp_dir), object=object[:-1], spar=spar[:-1])
    os.popen('rm -r {0}stage3.mir'.format(st.temp_dir))
    os.popen('mv {0}stage3.5.mir {0}stage3.mir'.format(st.temp_dir))


def get_centers(ra_cen,dec_cen,radius):
    """Create a list of field centers that are arrange in a flower pattern of 7"""
    field_centers=[(ra_cen,dec_cen)]
    field_centers.extend([ (ra_cen-radius*cos(i*pi/3), radius*sin(i*pi/3) ) for i in range(6)])
    return field_centers

if __name__== '__main__':
    #setup some parameters
    rms=25e-6 #uJy
    
    #print('#Load the master catalog')
    conn = sqlite3.connect(st.db_file)
    c=conn.cursor()
    
    field_centers=[ (180+4*f,0) for f in range(10) ]
    radius=2
    fc=field_centers #lazyness
    
    for f in range(len(fc)):
        ec=get_centers(fc[f][0],fc[f][1],radius)
        for e in range(len(ec) +1):
            map_name='MapF{0:02d}E{1:02d}'.format(f,e)
            print map_name
            #continue
            if os.path.exists('{0}{1}.fits'.format(st.data_dir,map_name) ):
                print "skipping ",e
                continue
            if e<7:
                continue #just make the large maps
            print "making ",map_name
            #print('#Clean up any previous runs')
            os.popen('rm -r {0}stage*.mir'.format(st.temp_dir))
            if e == 7:
                #make a big image with *all* the sources in it
                c.execute("SELECT flux,ra,dec,bmaj,bmin,pa FROM master WHERE field = ?",(f,))
                rc,dc=fc[f] #the center of the field
                make_noise(rc,dc,f,e,size=4801)
            else:
                #choose only sources from the given field
                c.execute("SELECT flux,ra,dec,bmaj,bmin,pa FROM master WHERE epoch & ? AND field=?",(2**e,f))
                #os.popen("rm -r stage[12].mir")
                rc,dc = ec[e] #the center of the epoch sub-field
                make_noise(rc,dc,f,e)
    
            N=15
            max=50e9 #stop after 50 images, for now
            count=0
            scount=0
            object=''
            spar=''
            for row in c:
                count+=1
                scount+=1
                object+='gaussian,'
                vals=[a for a in row]
                ra_off=(vals[1]-rc)*3600
                dec_off=(vals[2]-dc)*3600
                flux,junk,junk,bmaj,bmin,pa = vals
                spar+= "{0:10.8f},{1:10.6f},{2:9.6f},{3:7.4f},{4:7.4f},{5:7.4f},".format(flux,ra_off,dec_off,bmaj,bmin,pa)
                if count==15: #once you have 15 sources make a new image
                    make_image(object,spar)
                    print scount
                    object=''
                    spar=''
                    count=0
                if scount>max:
                    break
            print 
            if not spar=='': #if there are left over sources add them also
                make_image(object,spar)
            os.popen('head -24 {0}stage3.mir/history > {0}stage3.mir/temp'.format(st.temp_dir))
            os.popen('mv {0}stage3.mir/temp {0}stage3.mir/history'.format(st.temp_dir))
            miriad.puthd(_in_='{0}stage3.mir/date-obs'.format(st.temp_dir),
                        value='2011-{0:02d}-{0:02d}'.format(1+f,1+e),type='ascii')
            miriad.fits(_in_='{0}stage3.mir'.format(st.temp_dir),
                        out='{0}stage3.fits'.format(st.temp_dir),op='xyout')
            os.popen('mv {0}stage3.mir  {1}{2}.mir'.format(st.temp_dir, st.data_dir, map_name))
            os.popen('mv {0}stage3.fits {1}{2}.fits'.format(st.temp_dir, st.data_dir, map_name))

                     
