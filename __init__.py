#!/usr/bin/env python3

'''
YooperNet - A package for handling data from the YooperNet observatories.
'''

from datetime import datetime

import numpy as np
import h5py
import matplotlib.pyplot as plt


timefmt = '%Y_%m_%d_%H_%M_%S'


class YooperData(dict):
    '''
    The default class for reading YooperNet data files in HDF5 format.
    '''

    def __init__(self, filename, cycle_count=200):
        '''
        Load a YooperNet HDF5 file.
        '''

        # Store arguments as object attributes:
        self.file = filename
        self.cycle_count = cycle_count

        # Open data file:
        self.h5file = h5py.File(filename, 'r')

        # Convert times:
        strptime = datetime.strptime
        self['time'] = np.array([strptime(x.decode('UTF8'), timefmt)
                                 for x in self.h5file['date'][...]])
        raw_imtime = self.h5file['images']['date'][...]
        self['img_time'] = np.array([strptime(x.decode('UTF8'), timefmt)
                                     for x in raw_imtime])

        # Link to, but do not load, all-sky imager.
        self['images'] = self.h5file['images']['aurora img']

        # Extract timeseries data:
        for vfile, vsave in zip(['magnetic field', 'pressure', 'temperature'],
                                ['b', 'p', 't']):
            self[vsave] = self.h5file[vfile][...]

        # Scale magnetometer readings
        sensitivity = 1000 / (0.3671 * self.cycle_count + 1.5)
        self['b'] *= sensitivity

    def show_image(self, index=0, **kwargs):
        '''
        For image index `index`, use Matplotlib's `imshow()` to display the
        all-sky image corresponding to `self['img_time'][index]`.

        This is a convenience wrapper, all extra kwargs are passed to
        `imshow()`.

        Parameters
        ----------


        Returns
        -------
        fig, ax : Matplotlib Figure/Axes objects
            The resulting figure and axes object.
        '''

        fig, ax = plt.subplots(1, 1)

        ax.imshow(self['images'][index, :, :, :], **kwargs)
        ax.set_title(f"T={self['img_time'][index].isoformat()}UTC")

        return fig, ax
