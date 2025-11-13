#!/usr/bin/env python3

'''
YooperNet - A package for handling data from the YooperNet observatories.
'''

from datetime import datetime

import numpy as np
import h5py


timefmt = '%Y_%m_%d_%H_%M_%S'


class YooperData(dict):
    '''
    The default class for reading YooperNet data files in HDF5 format.
    '''

    def __init__(self, filename):
        '''
        Load a YooperNet HDF5 file.
        '''

        self.h5file = h5py.File(filename, 'r')

        # Convert time:
        self['time'] = np.array([datetime.strptime(x.decode('UTF8'), timefmt)
                                 for x in self.h5file['date'][...]])

        # Extract timeseries data:
        for vfile, vsave in zip(['magnetic field', 'pressure', 'temperature'],
                                ['b', 'p', 't']):
            self[vsave] = self.h5file[vfile][...]

