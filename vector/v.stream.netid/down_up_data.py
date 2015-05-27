#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
############################################################################
#
# AUTHOR(S):    Jason Lessels
# PURPOSE:      It grabs files from an ftp server and uploads them to thingSpeak.com
# DESCRIPTION: Not great having the ftp password in plain text (big no no!!!). The script will
#               download files from an ftp server. Load the file using pandas to tidy them up.
#               Upload the data to thingSpeak.com website.
#
# COPYRIGHT:
#
#               This program is free software under the GNU General Public
#               License (>=v2). Read the file COPYING that comes with GRASS
#               for details.
#
#############################################################################



import ftputil, os, httplib, urllib, time, shutil
import pandas as pd
import datetime as dt

## Login to the ftp server
host = ftputil.FTPHost('194.105.166.3', 'matthew', 'eddie666')
## Change the ftp directory
host.chdir('/marjolein')
## Get a list of the files on the server
files = host.listdir(host.curdir)
## Set the directory to directory of files which have already been downloaded off the ftp server and uploaded to thingspeak.com
os.chdir('/Users/jasonlessels/work/Projects/data_logger_files/uploaded')
## Get a list of the local files.
local_files = os.listdir(os.getcwd())
## Set the directory to the new file directory
os.chdir('/Users/jasonlessels/work/Projects/data_logger_files/fresh')
## Loop through the files on the ftp server
for file in files:
    # Check if the file on the server is on the local machine
    if (file in local_files) == False:
        # If not then download teh file from the server
        host.download(file, file)

## Close the ftp connection
host.close()

## Get a list of the file to load.
##TODO: move the files to a new directory of uploaded files.
local_files = os.listdir(os.getcwd())

## Load the file with pandas
all_dat = pd.DataFrame()
for file in local_files:
    dat = pd.read_table(file, delimiter = ",", skiprows=1)
    shutil.move(file, '../uploaded/' + file)
    ## Remove the first two rows - as they are just the units of the columns
    dat = dat.ix[2:]
    ## Format the date time column
    dat['TIMESTAMP'] = pd.to_datetime(dat['TIMESTAMP'], format = "%Y-%m-%d %H:%M:%S")
    ## Add the date as the key for the dataframe.
    dat = dat.set_index('TIMESTAMP', drop = False)
    all_dat = all_dat.append(dat)



headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}

for i in range(all_dat.shape[0]):
    try:
        params = urllib.urlencode([('field1', all_dat['AirTemp_Avg'].ix[i])] + [('field2', all_dat['Rain_mm_Tot'].ix[i])] + [('field3', all_dat['BattV_Avg'].ix[i])] + [('key', 'ZC8J9RFG53YY61UY')] + [('created_at',str(all_dat['TIMESTAMP'].ix[i]))])
        conn = httplib.HTTPConnection("api.thingspeak.com:80")
        conn.request("POST", "/update", params, headers)
        #thingspeak limits the uploads to one point per 20 seconds - therefore, the for loop has to wait for atleast 15 seconds before uploading the next point.
        time.sleep(20)
        conn.close()
    except:
        print 'oh no something went wrong'



