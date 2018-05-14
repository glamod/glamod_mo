#!/usr/bin/python2.7

"""
Extract number of stations per year for 4 netplats and show montage

RJHD - Exeter - April 2018

"""

import numpy as np
import matplotlib.pyplot as plt
import os
import cartopy

INLOC = "/group_workspaces/jasmin2/c3s311a_lot2/data/level1/land/zscratch_ajk/Diagnostic/Count_by_year/"
OUTLOC = "/group_workspaces/jasmin2/c3s311a_lot2/data/level1/land/RD_review/"


# list of names to run through
NETPLAT_NAMES = ["wmo", "icao", "cmans", "afwa"]

# dictionaries to hold information
NETPLATS = {"wmo" : [], "icao" : [], "cmans" : [], "afwa" : []}
COLOURS = {"Combined" : "r", "wmo" : "b", "icao" : "m", "cmans" : "c", "afwa" : "k"}

COMPLETENESS = 365*4  # = 1460

log = True

#********************
class Station(object):
    '''
    Class for Station object
    '''
    
    def __init__(self, ID, lat, lon, years, obs):

        self.ID = ID
        self.lat = lat
        self.lon = lon
        self.years = years
        self.obs = obs
        

    def __str__(self):
        return "station {}, lat {}, lon {}".format(self.ID, self.lat, self.lon)
    
    __repr__ = __str__

#********************
def plot_map(ax, lat, lon, title, year):
    """
    Plot the map on existing set of axes

    :param axes ax: the axes object on which to plot
    :param list lat: latitudes to plot
    :param list lon: longitudes to plot
    :param str title: title of the plot
    :param int year: the year plotted
    """

    # prettify the axes
    ax.gridlines() #draw_labels=True)
    ax.add_feature(cartopy.feature.LAND, zorder = 0, facecolor = "0.9", edgecolor = "k")
    ax.coastlines()
    
    ext = ax.get_extent() # save the original extent

    # only try to plot if there is data
    if len(lat) > 0:
        scatter = ax.scatter(lon, lat, c = COLOURS[title], s=20, \
                        transform = cartopy.crs.Geodetic())

    ax.set_extent(ext, ax.projection) # fix the extent change from colormesh
    
    # metadata
    ax.set_title("{} = {}".format(title.upper(), year))
    ax.text(-0.05, 1.05, "#stations: {}".format(len(lat)), transform = ax.transAxes, fontsize = 10)

    return # plot_map


#********************
#********************

# spin through each net plat and read in the data
for netplat in NETPLAT_NAMES:

    print netplat

    # read in the data
    if log:
        indata = np.genfromtxt(os.path.join(INLOC, "inventory_{}_yearcntlog.dat".format(netplat)), skip_header = 10, dtype = (str))
    else:
        indata = np.genfromtxt(os.path.join(INLOC, "inventory_{}_yearcntlin.dat".format(netplat)), skip_header = 10, dtype = (str))

    # in case these are useful later
    station_ids = indata[:, 0]
    lats = indata[:, 1].astype(float)
    lons = indata[:, 2].astype(float)
        
    if log:
        # mask where no counts, and convert from string
        data_count = np.ma.masked_where(indata[:, 3:] == "-9", indata[:, 3:].astype(int))
        
        # undo logarithm (which has a x10 as well)
        good = np.where(data_count.mask == False)
        data_count[good] = np.power(10, data_count[good]/10.)

    else:
        # mask where no counts, and convert from string
        data_count = np.ma.masked_where(indata[:, 3:] == "0", indata[:, 3:].astype(int))
        
    # mask where less than completeness
    masked_data_count = np.ma.masked_where(data_count < COMPLETENESS, data_count)

    years = np.arange(1901, 1901 + masked_data_count.shape[1], 1)

    # create station objects to store information
    netplat_list = []
    for s, stn in enumerate(station_ids):

        netplat_list += [Station(stn, lats[s], lons[s], years, masked_data_count[s])]
        
    # and store these lists in the dictionary.
    NETPLATS[netplat] = netplat_list

                    
# have read in all Netplat data.  Now can write out per year.        

for y, year in enumerate(years):
    print year
    
    # for each year, need a 5 panel plot
    fig = plt.figure(figsize = (8,10))
    plt.clf()

    # manually set up 5 axes
    ax1 = plt.axes([0.025, 0.05, 0.45, 0.25], projection=cartopy.crs.Robinson())
    ax2 = plt.axes([0.525, 0.05, 0.45, 0.25], projection=cartopy.crs.Robinson())
    ax3 = plt.axes([0.025, 0.30, 0.45, 0.25], projection=cartopy.crs.Robinson())
    ax4 = plt.axes([0.525, 0.30, 0.45, 0.25], projection=cartopy.crs.Robinson())
    ax5 = plt.axes([0.05, 0.55, 0.90, 0.45], projection=cartopy.crs.Robinson())

    # list of the 4 small ones
    axes = [ax1, ax2, ax3, ax4]

    # to hold the combined latitudes and longitudes
    combined_lats = []
    combined_lons = []

    for n, netplat in enumerate(NETPLAT_NAMES):

        # to hold the latitudes and longitudes
        lats = []
        lons = []

        # extract the information
        for stn in NETPLATS[netplat]:
            
            if stn.obs.mask[y] == False:
                lats += [stn.lat]
                lons += [stn.lon]
                combined_lats += [stn.lat]
                combined_lons += [stn.lon]

        # plot each panel
        plot_map(axes[n], lats, lons, netplat, year)
    
    # plot main axis (in subroutine, with extra data)
    plot_map(ax5, combined_lats, combined_lons, "Combined", year)
        
    plt.savefig(os.path.join(OUTLOC, "Combined_maps", "Combined_stations_in_{}.png".format(year)))
    plt.close()

#********************
# END
#********************
