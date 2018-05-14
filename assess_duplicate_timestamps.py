#!/usr/bin/python2.7

"""
Process duplicates file into categories

RJHD - Exeter - May 2018

"""

import numpy as np
import os

INLOC = "/group_workspaces/jasmin2/c3s311a_lot2/data/level1/land/zscratch_ajk/Diagnostic/Timestamp_duplic/"
OUTLOC = "/group_workspaces/jasmin2/c3s311a_lot2/data/level1/land/RD_review/"

NETPLATS = ["wmo", "icao", "afwa", "cmans"]

HEADER = "platformId,networkType,NCDC_ob_time,reportTypeCode,latitude,longitude,month,securityId,distributionCd,STATIONMODE,PLATFORMHEIGHT,CALLLETTER,VERSION,WINDDIRECTION,WINDDIRECTIONQC,WINDCONDITIONS,WINDCONDITIONSQC,WINDSPEED,WINDSPEEDQC,STARTDIRECTION,ENDDIRECTION,WINDGUSTSPEED,WINDGUSTSPEEDQC,WINDMEASUREMENTMODE,CLOUDCEILING,CLOUDCEILINGQC,CEILINGDETERMINATION,CEILINGDETERMINATIONQC,CLOUDCAVOK,CLOUDCAVOKQC,VISIBILITY,VISIBILITYQC,VISIBILITYTYPE,VISIBILITYTYPEQC,AIRTEMPERATURE,AIRTEMPERATUREQC,DEWPOINTTEMPERATURE,DEWPOINTTEMPERATUREQC,SEALEVELPRESSURE,SEALEVELPRESSUREQC,OBSERVATIONPERIODPP1,OBSERVATIONPERIODPP1QC,PRECIPAMOUNT1,PRECIPAMOUNT1QC,PRECIPCONDITION1,PRECIPCONDITION1QC,OBSERVATIONPERIODPP2,OBSERVATIONPERIODPP2QC,PRECIPAMOUNT2,PRECIPAMOUNT2QC,PRECIPCONDITION2,PRECIPCONDITION2QC,OBSERVATIONPERIODPP3,OBSERVATIONPERIODPP3QC,PRECIPAMOUNT3,PRECIPAMOUNT3QC,PRECIPCONDITION3,PRECIPCONDITION3QC,OBSERVATIONPERIODPP4,OBSERVATIONPERIODPP4QC,PRECIPAMOUNT4,PRECIPAMOUNT4QC,PRECIPCONDITION4,PRECIPCONDITION4QC,PRECIPHISTDUR,PRECIPHISTDURQC,PRECIPHISTCHAR,PRECIPHISTCHARQC,PRECIPDISC,PRECIPDISCQC,PRECIPBOGUS,PRECIPBOGUSQC,PRECIPAMOUNTSD,PRECIPAMOUNTSDQC,PRECIPCONDITIONSD,PRECIPCONDITIONSDQC,DEPTHWTREQUIV,DEPTHWTREQUIVQC,DEPTHWECOND,DEPTHWECONDQC,HAILSIZE,PRECIPAMOUNTSF1,PRECIPAMOUNTSF1QC,PRECIPCONDITIONSF1,PRECIPCONDITIONSF1QC,OBSERVATIONPERIODSF1,OBSERVATIONPERIODSF1QC,PRECIPAMOUNTSF2,PRECIPAMOUNTSF2QC,PRECIPCONDITIONSF2,PRECIPCONDITIONSF2QC,OBSERVATIONPERIODSF2,OBSERVATIONPERIODSF2QC,PRECIPAMOUNTSF3,PRECIPAMOUNTSF3QC,PRECIPCONDITIONSF3,PRECIPCONDITIONSF3QC,OBSERVATIONPERIODSF3,OBSERVATIONPERIODSF3QC,PRECIPAMOUNTSF4,PRECIPAMOUNTSF4QC,PRECIPCONDITIONSF4,PRECIPCONDITIONSF4QC,OBSERVATIONPERIODSF4,OBSERVATIONPERIODSF4QC,PRESENTMANUAL1,PRESENTMANUAL1QC,PRESENTMANUAL2,PRESENTMANUAL2QC,PRESENTMANUAL3,PRESENTMANUAL3QC,PRESENTMANUAL4,PRESENTMANUAL4QC,PRESENTMANUAL5,PRESENTMANUAL5QC,PRESENTMANUAL6,PRESENTMANUAL6QC,PRESENTMANUAL7,PRESENTMANUAL7QC,PRESENTAUTOMATED1,PRESENTAUTOMATED1QC,PRESENTAUTOMATED2,PRESENTAUTOMATED2QC,PRESENTAUTOMATED3,PRESENTAUTOMATED3QC,PASTMANUAL1,PASTMANUAL1QC,WXPASTPERIOD1,WXPASTPERIOD1QC,PASTMANUAL2,PASTMANUAL2QC,WXPASTPERIOD2,WXPASTPERIOD2QC,PASTAUTOMATED1,PASTAUTOMATED1QC,WXPASTAUTOPERIOD1,WXPASTAUTOPERIOD1QC,PASTAUTOMATED2,PASTAUTOMATED2QC,WXPASTAUTOPERIOD2,WXPASTAUTOPERIOD2QC,CLOUDCOVER,CLOUDCOVERQC,CLOUDCOVERLO,CLOUDCOVERLOQC,CLOUDBASEHEIGHT,CLOUDBASEHEIGHTQC,CLOUDTYPELO,CLOUDTYPELOQC,CLOUDTYPEMID,CLOUDTYPEMIDQC,CLOUDTYPEHI,CLOUDTYPEHIQC,SUNSHINE,SURFACECODE,SURFACECODEQC,SOILTEMPERATURE,SOILTEMPERATUREQC,SOILDEPTH,OBSERVATIONPERIODSOILT,OBSERVATIONPERIODSOILTQC,ALTIMETERSETTING,ALTIMETERSETTINGQC,STATIONPRESSURE,STATIONPRESSUREQC,PRESSURETENDENCY,PRESSURETENDENCYQC,PRESSURE3HOURCHG,PRESSURE3HOURCHGQC,PRESSURE24HOURCHG,PRESSURE24HOURCHGQC,PRESSURETREND,ISOBARICSURFACE,ISOBARICSURFACEQC,ISOBARICSURFACEHEIGHT,ISOBARICSURFACEHEIGHTQC,SEASURFACETEMP,SEASURFACETEMPQC,REMARKSYN,REMARKMET,REMARKAWY,HORIZONTALDATUM,VERTICALDATUM,LIGHTNINGFREQUENCY".split(",")
HEADER = np.array(HEADER)

#************************************
def compare(first, second):
    """
    Compare the two lines and indicate roughly where the difference lies
    """

    # check for different elements in one versus the other
    if len(first) != len(second):

        # presume one and change if wrong
        longest = "first"
        if len(second) > len(first): longest = "second"

        # find min and max of two lengths
        minlen = min(len(first), len(second))
        maxlen = max(len(first), len(second))
        excess = range(minlen, maxlen)

        print "Extra elements in {}".format(longest)

        # print out extra elements and values
        for e in excess:
            if longest == "first":
                print "{:20s} = \'{}\'".format(HEADER[e], first[e])
            elif longest == "second":
                print "{:20s} = \'{}\'".format(HEADER[e], second[e])

    # go through element-wise and check for different values
    for i, (f, s) in enumerate(zip(first, second)):

        if f != s:
            print "{} differs:".format(HEADER[i])
            print "     First:  {}".format(f)
            print "     Second: {}".format(s)

    return  # compare

#********************************

# spin through each netplat
for netplat in NETPLATS:

    # read file
    infilename = "inventory_{}_equaldate.dat".format(netplat)
    infile = file(os.path.join(INLOC, infilename), "r")

    # lines come in pairs of pairs - label (case ID and line ID) and the raw line
    case = []
    entry = ""

    for l, line in enumerate(infile):

        # remove header
        if l <= 2:
            continue

        # remove blank lines
        if line.strip() == "":
            continue

        # read in the metadata about this instance
        if line[:4] == "Case":

            split_line = line.split()
            case += [split_line[1]]
            entry = split_line[2]

        else:
            # read the first line
            if entry == "first":
                first = line.rstrip().split(",")

            # read the second and process
            elif entry == "second":
                second = line.rstrip().split(",")

                # if part of the same case (redundant check)
                if case[0] == case[1]:
                    # and now can process
                    print "{} - {} - {}".format(netplat, first[0], case[0])
                    compare(first, second)

                # and reset
                case = []

                raw_input("\nnext case?\n")
                

