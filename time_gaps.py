#!/usr/bin/python2.7

"""
Process and plot information on the largest gap in a timeseries

RJHD - Exeter - April 2018

"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as mpl_cm
import matplotlib as mpl
import os
import cartopy
import datetime as dt

INLOC = "/group_workspaces/jasmin2/c3s311a_lot2/data/level1/land/zscratch_ajk/Diagnostic/Max_deltime/"
OUTLOC = "/group_workspaces/jasmin2/c3s311a_lot2/data/level1/land/RD_review/"

# list of names to run through
NETPLATS = ["wmo", "icao", "cmans", "afwa"]

for netplat in NETPLATS:

    print netplat

    indata = np.genfromtxt(os.path.join(INLOC, "inventory_{}_maxdeltime.dat".format(netplat)), skip_header = 8, dtype = (str))

    # using MDI to filter out bad locations
    locs, = np.where(indata[:, 3] != "-99")

    # separate the data
    station_ids = indata[:, 0]
    Nobs = indata[locs, 1].astype(int)
    max_gap = indata[locs, 2].astype(float)
    start = indata[locs, 4]
    end = indata[locs, 5]

    # convert to datetime objects
    starts = [dt.datetime.strptime(s, "%d/%m/%Y") for s in start]
    ends = [dt.datetime.strptime(e, "%d/%m/%Y") for e in end]

    
    years = np.array([s.year for s in starts])

    # plot distribution in time
    plt.clf()

    plt.hist(years, bins = np.arange(1901,2020))

    plt.ylabel("Number of stations")
    plt.title(netplat.upper())

    plt.savefig(os.path.join(OUTLOC, "Del_Time", "TimeGaps_time_{}.png".format(netplat.upper())))
    plt.close()

    # plot distribution in time
    plt.clf()

    plt.hist(max_gap, bins = np.logspace(-2, 2, num = 40))

    plt.ylabel("Gap Length (years)")
    plt.title(netplat.upper())
    plt.xscale("log")

    plt.savefig(os.path.join(OUTLOC, "Del_Time", "TimeGaps_length_{}.png".format(netplat.upper())))
    plt.close()

    # plot distribution of length and time

    plt.clf()

    # use numpy so that can adjust the log-scales of the plot
    hist, xedge, yedge = np.histogram2d(years, max_gap, bins = [np.arange(1901,2020), np.logspace(-2, 2, num = 40)])

    # convert to mesh
    ymesh, xmesh = np.meshgrid(yedge, xedge)

    # sort colorbar ranges and scales
    bounds = np.logspace(0,3,20)
    cmap = plt.cm.viridis
    norm=mpl.cm.colors.BoundaryNorm(bounds,cmap.N)
    
    # do the plot
    mesh = plt.pcolormesh(xmesh, ymesh, hist, cmap = plt.cm.viridis, norm = norm)
    
    cb = plt.colorbar(mesh, orientation = 'horizontal', pad = 0.05, fraction = 0.05, \
                        aspect = 30, ticks = bounds, label = "Number of Stations", drawedges=True)

    # remove every other colorbar label
    labels = cb.ax.get_xticklabels()
    for l,ll in enumerate(labels):
        if l%2 != 0:
            labels[l] = ""
    
    cb.ax.set_xticklabels(labels)

    # metadata
    plt.ylabel("Gap Length (years)")
    plt.title(netplat.upper())

    plt.yscale("log")
    plt.savefig(os.path.join(OUTLOC, "Del_Time", "TimeGaps2d_{}.png".format(netplat.upper())))
    plt.close()


#********************
# END
#********************
