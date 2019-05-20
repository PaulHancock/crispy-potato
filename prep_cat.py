"""
Reformats some of the more stupid source finding catalogs.
"""


data=open('FndSou.cat').readlines()[4:]

out=open('FndSou.cat','w')

for nl in data:
    l=list(nl)
    l[10]=':'
    l[13]=':'
    if l[14]==' ':
        l[14]='0'
    l[26]=':'
    l[29]=':'
    if l[30]==' ':
        l[30]='0'
    print ''.join(l)
    out.write(''.join(l))
out.close()
