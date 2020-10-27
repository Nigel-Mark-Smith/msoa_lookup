# retrieve_files.py
#
# Description
# ===========
#
# This utility will retrieve all source data files necessary to create file
# 'lookup_data.csv' containing information relating to the MSOA ( Middle Super Output Area ) 
# and LTLA (Lower Tier Local Authority ) in which each UK postcode resides. All files are 
# stored in temporay storage on c:\temp from where the necessary information is
# extracted and stored as data files in the ..\data directory by batch file 'msoa_lookup.bat'
# The contents, web sources and destination files of each type of information required are as follows:
#
# MSOA names and codes
# --------------------
# https://visual.parliament.uk/msoanames
# csv file MSOA Names (csv)
#
# c:\temp\msoa_names.csv
# ..\data\msoa_names.csv
#
# MSOA codes and populations
# --------------------------
# https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/datasets/middlesuperoutputareamidyearpopulationestimates
# zip file for Mid-2019: SAPE22DT4 editiion of dataset
#
# c:\temp\msoa_populations.zip
# ..\data\msoa_populations.csv
#
# LTLA names and codes
# --------------------
# https://digital.nhs.uk/services/organisation-data-service/data-downloads/office-for-national-statistics-data 
# zip file 'names_and_codes' , sub file 'LA_UA names and codes UK as at 04_20.csv'
#
# c:\temp\authority_data.zip
# ..\data\authority_data.csv
# 
# MSOA code relating to each UK postcode:
# ---------------------------------------
# https://digital.nhs.uk/services/organisation-data-service/data-downloads/office-for-national-statistics-data 
# zip file 'gridall'
#
# c:\temp\postcode_data.zip
# ..\data\postcode_data.csv
# 
# Usage
# =====
#
# This script requires no command line arguments and can be invoked as follows:
#
# python retrieve_files.py
# 
# Data and configuration files
# ============================
#
# This utility will create the following data files.
#
# c:\temp\msoa_names.csv
# c:\temp\msoa_populations.zip
# c:\temp\authority_data.zip
# c:\temp\postcode_data.zip
#
# This utility requires configuration file ..\config\retrieve_files.csv which contains 4 lines
# each specifying the url of a source data file. The urls should be specified in the following
# order:
#
# line 1: MSOA names and codes file
# line 2: MSOA population data file
# line 3: LTLA names and codes file
# line 4: MSOA code relating to each UK postcode file:
#
# This file is delivered with the followig default configuration:
#
# https://visual.parliament.uk/msoanames/static/MSOA-Names-1.6.0.csv
# https://www.ons.gov.uk/file?uri=%2fpeoplepopulationandcommunity%2fpopulationandmigration%2fpopulationestimates%2fdatasets%2fmiddlesuperoutputareamidyearpopulationestimates%2fmid2019sape22dt4/sape22dt4mid2019msoasyoaestimatesunformatted.zip
# http://files.digital.nhs.uk/assets/ods/current/Names and Codes.zip
# https://files.digital.nhs.uk/assets/ods/current/gridall.zip
#
# Logging
# =======
#
# This script logs error and status messages to the file .\log\log.txt an to the user console.

import calendar
from datetime import date,timedelta
import os
import re
import requests
import subprocess
import sys
import time
import utils as Utils

# File names and modes
Currentdir = os.getcwd()
LogDir = Currentdir + '\\log'
ErrorFilename = LogDir + '\\' + 'log.txt'
ConfigDir = Currentdir + '\\config'
ConfigurationFilename = ConfigDir + '\\' + 'retrieve_files.csv'
DataDir = Currentdir + '\\data'
TempDir = 'c:\\temp'
MsoaNameFileName = 'msoa_names.csv'
TempMsoaNameFileName = TempDir + '\\' + MsoaNameFileName
MsoaPopulationFileName = 'msoa_populations.zip'
TempMsoaPopulationFileName = TempDir + '\\' + MsoaPopulationFileName 
AuthorityDataFileName = 'authority_data.zip'
TempAuthorityDataFileName = TempDir + '\\' + AuthorityDataFileName 
PostcodeDataFileName = 'postcode_data.zip'
TempPostcodeDataFileName = TempDir + '\\' + PostcodeDataFileName 

append = 'a'
read = 'r'
overwrite = 'w'
overwritebinary = 'wb'

# Function return values
invalid = failure = 0
empty = ''
success = 1

# Error levels
error = 'ERROR'
warning = 'WARNING'
info = 'INFO'

# Script names
module = 'retrieve_files.py'

# Create/open log file
ErrorFileObject = Utils.Open(ErrorFilename,append,failure)
ErrorMessage = 'Could not open ' + ErrorFilename
if ( ErrorFileObject == failure ) : Utils.Logerror(ErrorFileObject,module,ErrorMessage,error)

# Log start of script
Utils.Logerror(ErrorFileObject,module,'Started',info)

# Log progress messages
ErrorMessage = 'Reading configuration file %s ' % ConfigurationFilename
Utils.Logerror(ErrorFileObject,module,ErrorMessage,info)

# Open and parse configuration file
ConfigurationFileObject = Utils.Open(ConfigurationFilename,read,failure)
ErrorMessage = 'Could not open configuration file ' + ConfigurationFilename
if ( ConfigurationFileObject == failure ) : Utils.Logerror(ErrorFileObject,module,ErrorMessage,error)

ConfigurationData = Utils.Read(ConfigurationFileObject,failure)
ErrorMessage = 'Could not read data in ' + ConfigurationFilename
if ( ConfigurationFileObject == failure ) : Utils.Logerror(ErrorFileObject,module,ErrorMessage,error)

ConfigurationDataLines = ConfigurationData.splitlines()
if ( len(ConfigurationDataLines) != 4 ) :
    ErrorMessage = 'Configuration file %s does not consist of exactly 4 lines ' % ConfigurationFilename
    Utils.Logerror(ErrorFileObject,module,ErrorMessage,error)

ConfigurationLineCount = 1   
for ConfigurationDataLine in ConfigurationDataLines :
    if ( len(ConfigurationDataLine) == 0 ) :
        ErrorMessage = 'Configuration line %d in %s is empty ' % (ConfigurationLineCount,ConfigurationFilename)
        Utils.Logerror(ErrorFileObject,module,ErrorMessage,error)
        
    ConfigurationLineCount += 1
    
MsoaNameFileUrl =  ConfigurationDataLines[0]
MsoaPopulationFileUrl = ConfigurationDataLines[1]
AuthorityDataFileUrl = ConfigurationDataLines[2]
PostcodeDataFileUrl = ConfigurationDataLines[3]
    
# Close Configuration file
ErrorMessage = 'Could not close ' + ConfigurationFilename
if ( Utils.Close(ConfigurationFileObject,failure) == failure ) : Utils.Logerror(ErrorFileObject,module,ErrorMessage,warning)

# Log progress messages
ErrorMessage = 'Downloading file %s ' % MsoaNameFileUrl
Utils.Logerror(ErrorFileObject,module,ErrorMessage,info)

# Open Msoa name output file
MsoaNameFileObject = Utils.Open(TempMsoaNameFileName,overwritebinary,failure)
ErrorMessage = 'Could not open ' + TempMsoaNameFileName
if ( MsoaNameFileObject == failure ) : Utils.Logerror(ErrorFileObject,module,ErrorMessage,error)

# Download Msoa name spreadsheet contents.
Response = requests.get(MsoaNameFileUrl)
if ( Response.status_code != 200 ) :
    ErrorMessage = 'GET operation for %s failed' % MsoaNameFileUrl
    Utils.Logerror(ErrorFileObject,module,ErrorMessage,error)

# Write Msoa name output file. 
Utils.Write(MsoaNameFileObject,Response.content,failure)

# Log progress messages
ErrorMessage = 'Downloading file %s ' % MsoaPopulationFileUrl
Utils.Logerror(ErrorFileObject,module,ErrorMessage,info)

# Open Msoa population output file
MsoaPopulationFileObject = Utils.Open(TempMsoaPopulationFileName,overwritebinary,failure)
ErrorMessage = 'Could not open ' + TempMsoaPopulationFileName
if ( MsoaPopulationFileObject == failure ) : Utils.Logerror(ErrorFileObject,module,ErrorMessage,error)

# Download Msoa population spreadsheet contents.
Response = requests.get(MsoaPopulationFileUrl)
if ( Response.status_code != 200 ) :
    ErrorMessage = 'GET operation for %s failed' % MsoaPopulationFileUrl
    Utils.Logerror(ErrorFileObject,module,ErrorMessage,error)
    
# Write Msoa population output. 
Utils.Write(MsoaPopulationFileObject,Response.content,failure)

# Log progress messages
ErrorMessage = 'Downloading file %s ' % AuthorityDataFileUrl
Utils.Logerror(ErrorFileObject,module,ErrorMessage,info)

# Open authority data output file
AuthorityDataFileObject = Utils.Open(TempAuthorityDataFileName,overwritebinary,failure)
ErrorMessage = 'Could not open ' + TempAuthorityDataFileName
if ( AuthorityDataFileObject == failure ) : Utils.Logerror(ErrorFileObject,module,ErrorMessage,error)

# Download authority data spreadsheet contents.
Response = requests.get(AuthorityDataFileUrl)
if ( Response.status_code != 200 ) :
    ErrorMessage = 'GET operation for %s failed' % AuthorityDataFileUrl
    Utils.Logerror(ErrorFileObject,module,ErrorMessage,error)
    
# Write authority. 
Utils.Write(AuthorityDataFileObject,Response.content,failure)

# Log progress messages
ErrorMessage = 'Downloading file %s ' % PostcodeDataFileUrl
Utils.Logerror(ErrorFileObject,module,ErrorMessage,info)

# Open authority data output file
PostcodeDataFileObject = Utils.Open(TempPostcodeDataFileName,overwritebinary,failure)
ErrorMessage = 'Could not open ' + TempPostcodeDataFileName
if ( PostcodeDataFileObject == failure ) : Utils.Logerror(ErrorFileObject,module,ErrorMessage,error)

# Download authority data spreadsheet contents.
Response = requests.get(PostcodeDataFileUrl)
if ( Response.status_code != 200 ) :
    ErrorMessage = 'GET operation for %s failed' % PostcodeDataFileUrl
    Utils.Logerror(ErrorFileObject,module,ErrorMessage,error)
    
# Write authority. 
Utils.Write(PostcodeDataFileObject,Response.content,failure)

# Log end of script
Utils.Logerror(ErrorFileObject,module,'Completed',info)

# Close error log file
ErrorMessage = 'Could not close ' + ErrorFilename
if ( Utils.Close(ErrorFileObject,failure) == failure ) : Utils.Logerror(ErrorFileObject,module,ErrorMessage,warning)