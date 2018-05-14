#!/usr/bin/python2.7

"""
Extract number of stations per year and plot against time or space

RJHD - Exeter - April 2018

"""

import numpy as np
import matplotlib.pyplot as plt
import os
import cartopy

INLOC = "/group_workspaces/jasmin2/c3s311a_lot2/data/level1/land/zscratch_ajk/Diagnostic/Count_by_year/"
OUTLOC = "/group_workspaces/jasmin2/c3s311a_lot2/data/level1/land/RD_review/"


NETPLATS = ["wmo", "icao", "cmans", "afwa"]

COMPLETENESS = 365*4  # = 1460

log = True

for netplat in NETPLATS:

    print netplat

    outfile = file(os.path.join(OUTLOC, "{}_counts_per_year.dat".format(netplat)), "w")

    outfile.write("Number of stations in each year which have more than {} observations\n".format(COMPLETENESS))

    # read in the data
    if log:
        indata = np.genfromtxt(os.path.join(INLOC, "inventory_{}_yearcntlog.dat".format(netplat)), skip_header = 10, dtype = (str))
    else:
        indata = np.genfromtxt(os.path.join(INLOC, "inventory_{}_yearcntlin.dat".format(netplat)), skip_header = 10, dtype = (str))

    # in case these are useful later
    station_ids = indata[:, 0]
    lats = indata[:, 1].astype(float)
    lons = indata[:, 2].astype(float)
        
    # files available in space saving logarithm form or in human readable form
    if log:
        # mask where no counts, and convert from string
        data_count = np.ma.masked_where(indata[:, 3:] == "-9", indata[:, 3:].astype(int))
        
        # undo logarithm
        good = np.where(data_count.mask == False)
        data_count[good] = np.power(10, data_count[good]/10.)

    else:
        # mask where no counts, and convert from string
        data_count = np.ma.masked_where(indata[:, 3:] == "0", indata[:, 3:].astype(int))
        
    # use 1/0 data presence, absence to get completeness and then sum
    binary_data_count = np.zeros(data_count.shape)
    binary_data_count[data_count > COMPLETENESS] = 1
    final_stations = np.sum(binary_data_count, axis = 0)
    
    # mock up years to plot
    years = np.arange(1901, 1901 + final_stations.shape[0], 1)

    # and do the station timeseries plot
    plt.clf()
    plt.plot(years, final_stations, "ro", ls = "-")
    plt.ylabel("Stations with at least {} observations/year".format(COMPLETENESS))
    plt.title(netplat.upper())
    plt.savefig(os.path.join(OUTLOC, "Counts_per_year", "{}_station_counts_per_year.png".format(netplat.upper())))
    plt.close()


    # now for each year
    for y, year in enumerate(years):

        plt.clf()
        # set up axes
        ax = plt.axes([0.05, 0.10, 0.90, 0.90], projection=cartopy.crs.Robinson())

        # prettify
        ax.gridlines() #draw_labels=True)
        ax.add_feature(cartopy.feature.LAND, zorder = 0, facecolor = "0.9", edgecolor = "k")
        ax.coastlines()

        ext = ax.get_extent() # save the original extent

        # extract this year, and scatter plot
        this_year, = np.where(binary_data_count[:, y] == 1)
        if this_year.shape[0] > 0:
            scatter = plt.scatter(lons[this_year], lats[this_year], c = "r", s=20, \
                        transform = cartopy.crs.Geodetic(), linewidth = 0.1)

        # reset extent if necessary
        ax.set_extent(ext, ax.projection) # fix the extent change from colormesh

        # add metadata
        plt.title("{} = {}".format(netplat.upper(), year))
        plt.text(0.01, 0.98, "#stations: {}".format(this_year.shape[0]), transform = ax.transAxes, fontsize = 10)

        plt.savefig(os.path.join(OUTLOC, "Map_{}".format(netplat.upper()), "{}_stations_in_{}.png".format(netplat.upper(), year)))
        plt.close()

        # print to log.
        print year, this_year.shape[0]
        outfile.write("{}  {}\n".format(year, this_year.shape[0]))


#********************
# END
#********************
