#! python

import sys,os


five_sigma=150e-6
cat=sys.argv[-1]

if not cat in ['sex','imsad','sfind','osfind']:
    print "use only: sex, imsad, sfind, osfind"
    sys.exit(0)

if cat=='sex':
    #sextractor
    data=open('MasterList-Sextractor.cat','r').readlines()
elif cat=='imsad':
    #imsad
    data=open('MasterList-IMSAD.cat','r').readlines()
elif cat=='sfind':
    #sfind
    data=open('MasterList-Sfind.cat','r').readlines()
    data=data[3:]
elif cat=='osfind':
    #sfind with no fdr
    data=open('MasterList-oSfind.cat','r').readlines()
    data=data[3:] #cut out the header

fluxes=[ float(a.split()[11])/25 for a in data]
for i in range(len(data)):
    if fluxes[i]>five_sigma:
        print data[i],
