#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
############################################################################
#
# MODULE:       v.streams.netid
# AUTHOR(S):    Jason Lessels
# PURPOSE:      Determine and assign network ids to each stream reach.
#
# COPYRIGHT:
#
#               This program is free software under the GNU General Public
#               License (>=v2). Read the file COPYING that comes with GRASS
#               for details.
#
#############################################################################


#%module
#% description: Determines contributing area and statistics for multiple points along a stream network.
#% keyword: vector
#%end

#%option G_OPT_V_MAP
#%  key: input
#%  description: Name of vector map of edges.
#%  required: yes
#%  multiple: no
#%end
#%option G_OPT_M_DIR
#%  key: location
#%  description: Location of the folder to save the netword ID files to.
#%  required: yes
#%  multiple: no
#%end
#%flag
#% key:c
#% description: Ignore complex influences
#% defualt: False
#%end


##TODO:: Add the directory option.




"""
Created on 12 March 2015

@author: Jason Lessels <jlessels gmail.com>
"""

import sys
import os
import csv


import grass.script as grass
from grass.pygrass import vector
from pygrass.modules import Module
from pygrass.modules import stdout2dict
from pygrass import raster
from grass.exceptions import CalledModuleError

if not os.environ.has_key("GISBASE"):
    grass.message( "You must be in GRASS GIS to run this program." )
    sys.exit(1)


def map_exists(map_name, type = "raster"):
    if(type == "raster"):
        result = grass.find_file(name = map_name, element = 'cell')
        if not result['file']:
            grass.fatal("Raster map <%s> not found" % map_name)
    else:
        result = grass.find_file(name = map_name, element = 'vector')
        if not result['file']:
            grass.fatal("Vector map <%s> not found" % map_name)


def get_coords(map_name,layer):
    ## Load the vector with the points in it.
    data = vector.VectorTopo(map_name) # Create a VectorTopo object
    data.open('r', layer = int(layer)) # Open this object for reading
    coords = []
    for i in range(len(data)):
        coords.append(data.read(i+1).coords()) # gives a tuple
    data.close()
    return coords

def get_table_name(map_name, layer):
    ### Test to make sure the vector has the correct layer - and get the table name from it
    try:
        table_name = grass.vector_layer_db(map_name, layer)['name']
    except:
        grass.fatal("Map <%s> does not have layer number %s" % (map_name,layer))
    return table_name


def add_netID_to_edges(vect_name,table_name, layer, netIDs, ridIDs):
    ## Create the new column.
    Module('v.db.addcolumn', map=vect_name, columns='netID',layer=layer)
    ## This has to be good to run for a list of lists.
    for i in range(len(netIDs)):
        for j in range(len(netIDs[i])):
            query = "UPDATE " + table_name + " SET " + 'netID' + "=" + str(netIDs[i][j]) + " WHERE rid = " + str(ridIDs[i][j])
            grass.run_command('db.execute', sql=str(query))

def get_column_ints(vect_name, layer, col_name):
    raw = grass.read_command("v.db.select", map=vect_name, layer=layer, col=col_name, flags='c')
    raw = raw.split("\n")
    return map(int, raw[0:len(raw)-1])

def check_for_columns(table_name, stop_with_complex):
# Get the column names in the table
    raw = grass.read_command("db.columns", table=table_name)
    raw = raw.split("\n")
    required_cols = ['rid', 'prev_str01', 'prev_str02', 'nxt_str']
    # Check that the required columns are in the table
    for i in range(len(required_cols)):
        if ((required_cols[i] in raw) == False):
            grass.fatal("Map <%s> does not have column named %s" % (map_name,required_cols[i]))
    # Check to make sure that there are no complex influences.
    if 'prev_str03' in raw:
        if ignore_complex:
            grass.message("A column containing complex influences was found. Module is proceeding as -c flag is set." )
        else:
            grass.fatal("A column containing complex influences was found. Check the map and use -c flag to continue.")




def main():
    ## Load the inputs from the user
    streams = options['input']
    ## get the layer number to obtain the table from.
    layer = options['layer']
                        ## get the directory where to save everything.
    directory = options['directory']
    ignore_complex = flags['c']

    # For testing only
    # streams = "stream_order"
    # layer = "1"
    # directory = "/Users/jasonlessels/Desktop/testing/"

    ## Check to make sure the vector map exists
    map_exists(streams, "vector")
    ## Check to make sure the layer exists and return the table name of that layer
    table_name = get_table_name(streams, layer)
    

    check_for_columns(table_name, ignore_complex)
    rid = get_column_ints(streams, layer, 'rid')
    prev_str1 = get_column_ints(streams, layer, 'prev_str01')
    prev_str2 = get_column_ints(streams, layer, 'prev_str02')
    nxt_str = get_column_ints(streams, layer, 'nxt_str')




    ## Create a binaryID list. - with a stream index to for splitting up later on
    binaryID = [''] * len(nxt_str)
    netID_number = 1
    for i in range(len(nxt_str)):
        if nxt_str[i] == -1:
            binaryID[i] = str(netID_number) + '_1'
            netID_number = netID_number + 1
        else:
            binaryID[i] = ''


    for j in range(len(nxt_str)):
        for i in range(len(nxt_str)):
            if(len(binaryID[i])>0):
                if(prev_str1[i] > 0):
                    binaryID[rid.index(prev_str1[i])]  = binaryID[i] + "0"
                if(prev_str2[i] > 0):
                    binaryID[rid.index(prev_str2[i])]  = binaryID[i] + "1"

    #TODO: split the binaryID list based on the network id and write out csv files with rid,binaryID.
    netID = [''] * len(nxt_str)
    for i in range(len(nxt_str)):
        netID[i] = binaryID[i].split("_")[0]
        binaryID[i] = binaryID[i].split("_")[1]

    ## Seperate all of the networks
    total_networks = sum([i==-1 for i in nxt_str])

    rid_list = []
    binaryID_list = []
    netID_list = []

    for i in range(total_networks):
        binaryID_list.append([])
        rid_list.append([])
        netID_list.append([])
        for j in range(len(binaryID)):
            if netID[j] == str(i+1):
                rid_list[i].append(rid[j])
                netID_list[i].append(str(i+1))
                binaryID_list[i].append(binaryID[j])


    ## fix up the directory string
    if directory[-1] == '/':
        directory = directory[0:-1]


    for i in range(len(rid_list)):
        file_name = directory + '/netID' + str(netID_list[i][0]) + '.dat'
        with open(file_name, 'wb') as outcsv:
            writer = csv.writer(outcsv, delimiter=',')
            writer.writerow(['rid','binaryID'])
            for row in range(len(binaryID_list[i])):
                writer.writerow([rid_list[i][row],binaryID_list[i][row]])


    ## Now update the columns in the stream order vector.
    add_netID_to_edges(streams,table_name, layer, netID_list, rid_list)


if __name__ == "__main__":
    options, flags = grass.parser()
    main()




