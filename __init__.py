#!/usr/bin/env python3

'''
YooperNet - A package for handling data from the YooperNet observatories.
'''

from datetime import datetime

from spacepy import plot
from scipy import signal
import numpy as np
import h5py
import matplotlib.pyplot as plt

plot.style()

# String for time conversion:
timefmt = '%Y_%m_%d_%H_%M_%S'

# Station information:
info = {'lat': 42.397888888, 'lon': -83.93491666666667,    # geo lat/lon
        'bx0': 19179.0, 'by0': -2325.0, 'bz0': 49177.0,    # B0 in geo coords
        'bh': 19320.0, 'b': 52836.0}                       # H and total.


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

    def rotate_mag(self, istart=0, downsample=7, debug=True):
        '''Rotate field to correct orientation in magnetic coordinates.'''

        # Get target values from station info:
        H = info['bh']
        Z = info['bz0']

        # Start by getting median field values:
        x_obs = np.median(self['b'][istart:, 0])
        y_obs = np.median(self['b'][istart:, 1])
        z_obs = np.median(self['b'][istart:, 2])
        b = np.sqrt(x_obs**2 + y_obs**2 + z_obs**2)

        # Get declination adjustment:
        dec = np.arctan2(y_obs, x_obs)

        # Rotate X and Y; get rotated mean X:
        x_1 = x_obs * np.cos(dec) + y_obs * np.sin(dec)
        bx_1 = self['b'][:, 0]*np.cos(dec) + self['b'][:, 1]*np.sin(dec)
        self['by'] = -self['b'][:, 0]*np.sin(dec) + self['b'][:, 1]*np.cos(dec)

        # Find inclination:
        inc = np.arccos((Z + x_1/z_obs * H) / (x_1**2/z_obs + z_obs))

        # Final rotation:
        self['bx'] = bx_1*np.cos(inc) - self['b'][:, 2]*np.sin(inc)
        self['bz'] = bx_1*np.sin(inc) + self['b'][:, 2]*np.cos(inc)

        if downsample > 0:
            for x in 'xyz':
                self[f'b{x}'] = signal.medfilt(self[f'b{x}'], downsample)

        if not debug:
            return None

        b_final = np.median(np.sqrt(self['bx']**2 +
                                    self['by']**2 +
                                    self['bz']**2))

        # Debug time!
        print('Coordinate rotation: X, Y, Z magnetic')
        print(f'TOTAL FIELD COMPARISON: IGRF={info["b"]:.1f}\tOBS={b:.1f}' +
              f'\tFINAL={b_final:.1f}')
        print(f'TARGET VALUES   = {H:8.1f}\t{0:8.1f}\t{Z:8.1f}')
        print(f'STARTING VALUES = {x_obs:8.1f}\t{y_obs:8.1f}\t{z_obs:8.1f}')
        print(f'FINAL VALUES    = {self["bx"].mean():8.1f}\t' +
              f'{self["by"].mean():8.1f}\t{self["bz"].mean():8.1f}')

        # Create a nice figure:
        fig, axes = plt.subplots(3, 1, figsize=[8, 6], sharex=True)
        for x, b0, ax in zip('xyz', [H, 0, Z], axes):
            ax.plot(self['time'], self[f'b{x}'])
            ax.set_ylabel(f'$B_{x}$ ($nT$)')
            ax.hlines(b0, self['time'][0], self['time'][-1],
                      colors='k', linestyles='--')
        plot.applySmartTimeTicks(axes[-1], self['time'], dolabel=True)

        return fig

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
