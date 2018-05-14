#!/usr/bin/python2.7

"""
Process Chronologies file into good, bad and incomplete.

RJHD - Exeter - May 2018

"""

import numpy as np
import os

INLOC = "/group_workspaces/jasmin2/c3s311a_lot2/data/level1/land/zscratch_ajk/Diagnostic/Mcneill_chrono/"
OUTLOC = "/group_workspaces/jasmin2/c3s311a_lot2/data/level1/land/RD_review/Chronology_revie"

infilename = "email20180327_ncei_mcneill_SRC_USAF_CHRONOLOGY_FULL_20180327.txt"

DEGREE_SEP = 0.1
ELEVATION_SEP = 10.

class Chronology(object):
    '''
    Class for Chronology object
    '''
    
    def __init__(self, indata):

        networktype, platformid, begin_date, end_date, station_status, wmo_id, icao_id, faa_id, nwsli_id, cmans_id, transmittal_id, name, lat_dec, lon_dec, elev_m, state_province, country_fips_code, utc_offset = indata

        # fix missing values
        if lat_dec == "":
            lat_dec = -9999
        else:
            lat_dec = float(lat_dec)

        if lon_dec == "":
            lon_dec = -9999
        else:
            lon_dec = float(lon_dec)

        if elev_m == "":
            elev_m = -9999
        else:
            elev_m = float(elev_m)
        


        self.networktype = networktype
        self.platformid = platformid
        self.begin_date = begin_date
        self.end_date = end_date
        self.station_status = station_status
        self.wmo_id = wmo_id
        self.icao_id = icao_id
        self.faa_id = faa_id
        self.nwsli_id = nwsli_id
        self.cmans_id = cmans_id
        self.transmittal_id = transmittal_id
        self.name = name
        self.lat_dec = lat_dec
        self.lon_dec = lon_dec
        self.elev_m = elev_m
        self.state_province = state_province
        self.country_fips_code = country_fips_code
        self.utc_offset = utc_offset

        
    def __str__(self):
        return "station {}, lat {}, lon {}, elevation {}".format(self.name, self.lat_dec, self.lon_dec, self.elev_m)
    
    __repr__ = __str__
    


#********************
def write_lines(outfile, entries):

    for entry in entries:
    
        write_str = "|".join([entry.networktype, entry.platformid, entry.begin_date, entry.end_date, entry.station_status, entry.wmo_id, entry.icao_id, entry.faa_id, entry.nwsli_id, entry.cmans_id, entry.transmittal_id, entry.name, str(entry.lat_dec), str(entry.lon_dec), str(entry.elev_m), entry.state_province, entry.country_fips_code, entry.utc_offset])
        
        outfile.write("{}\n".format(write_str))

    return # write_lines


#********************
infile = file(os.path.join(INLOC, infilename), "r")

goods_outfile = file(os.path.join(OUTLOC, "good_chronologies.txt"), "w")
bads_outfile = file(os.path.join(OUTLOC, "bad_chronologies.txt"), "w")
incompl_outfile = file(os.path.join(OUTLOC, "incomplete_chronologies.txt"), "w")

good, bad, incompl = 0, 0, 0

previous_platformid = ""
all_entries = []

for l, line in enumerate(infile):

    splitline = line.split("|")

    if splitline[0] == "NETWORKTYPE":
        continue

    entry = Chronology(splitline)

    # if new station
    if entry.platformid != previous_platformid:

        # do something
        
        if len(all_entries) == 1:
            if all_entries[0].lat_dec == 0.0 or all_entries[0].lon_dec == 0.0 or all_entries == 0.0:
                write_lines(incompl_outfile, all_entries)
                incompl += 1
            elif all_entries[0].lat_dec == -9999 or all_entries[0].lon_dec == -9999 or all_entries == -9999:
                write_lines(incompl_outfile, all_entries)
                incompl += 1
            else:
                # these are good as single entry
                write_lines(goods_outfile, all_entries)
                good += 1
        
        elif len(all_entries) > 1:
            # check whether these entries are within tolerance
            lats = [e.lat_dec for e in all_entries]
            lons = [e.lon_dec for e in all_entries]
            elev = [e.elev_m for e in all_entries]
            
            max_lat_delta = np.max(np.diff(np.array(lats)))
            max_lon_delta = np.max(np.diff(np.array(lons)))
            max_elv_delta = np.max(np.diff(np.array(elev)))

            if 0. in lats or 0. in lons or 0. in elev:
                # missing information, so unknown
                write_lines(incompl_outfile, all_entries)
                incompl += 1

            elif -9999 in lats or -9999 in lons or -9999 in elev:
                # missing information, so unknown
                write_lines(incompl_outfile, all_entries)
                incompl += 1

            # test first differences of lats, lons and elevs
            elif max_lat_delta > DEGREE_SEP or max_lon_delta > DEGREE_SEP or max_elv_delta > ELEVATION_SEP:
                # one of the differences is too much
                write_lines(bads_outfile, all_entries)
                bad += 1

            else:
                # if all data present and within tolerance, then good
                write_lines(goods_outfile, all_entries)
                good += 1

            # raw_input("stop")

        # reset
        all_entries = [entry]
    
    elif entry.platformid == previous_platformid:
        # append
        all_entries += [entry]

    previous_platformid= entry.platformid
    

print "processed file"
print "Good station Chronologies      : {}".format(good)
print "Incomplete station Chronologies: {}".format(incompl)
print "Bad station Chronologies       : {}".format(bad)

summary_outfile = file(os.path.join(OUTLOC, "chronology_summary.txt"), "w")

summary_outfile.write("Good station Chronologies      : {}\n".format(good))
summary_outfile.write("Incomplete station Chronologies: {}\n".format(incompl))
summary_outfile.write("Bad station Chronologies       : {}\n".format(bad))

summary_outfile.write("\nThresholds used for lat/lon/elev differences:\n")
summary_outfile.write("Lat/Lon delta : {} (degrees)\n".format(DEGREE_SEP))
summary_outfile.write("Elev. delta   : {} (metres)\n".format(ELEVATION_SEP))

summary_outfile.close()
goods_outfile.close()
incompl_outfile.close()
bads_outfile.close()

#END


