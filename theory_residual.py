#!/usr/bin/env python

#from matplotlib import pyplt as plt
import numpy as np



y=np.logspace(-6,0,100)
x=np.logspace(-6,0,100)

def fxoyo(x,y):
    return ((1+2*x-x**2)**(1/(1/(2*x)-1/x**2)+1)-(1+2*x-x**2)**(1/(1/(2*x)-1/x**2)))*((1+2*y-y**2)**(1/(1/(2*y)-1/y**2)+1)-(1+2*y-y**2)**(1/(1/(2*y)-1/y**2)))


xy=np.array([ [ fxoyo(i,j) for i in np.logspace(-3,0,10)] for j in np.logspace(-3,0,10)])

print xy.shape
print xy[0:2,0:2]
