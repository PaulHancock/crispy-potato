"""
A module to store constants that I need to use for the db_*.py files

Paul Hancock 5-July-2011
"""

import sys

db_file='SfSim_20170518.db'
sf_names=['sfind','sex','selavy','imsad','tesla','fndsou']

def get_field_epoch(filename):
    """Return the field number and epoch that corresponds to the given filename"""
    field=int(filename[4:6])
    epoch=int(filename[7:9])
    return field,epoch

temp_dir = '~/temp/'
data_dir = 'DATA'
