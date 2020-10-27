# generate_lookup.py
#
# Description
# ===========
#
# This script generates a file 'lookup_data.csv' which contains
# information relating to the MSOA ( Middle Super Output Area ) and LTLA (Lower 
# Tier Local Authority ) in which each UK postcode resides. Each row of this 
# file consists of the following fields:
# 
# <Post code>,<MSOA name><MSOA code>,<MSOA population>,<LTLA name><LTLA code>,<LTLA population>
#
# File 'lookup_data.csv' can be searched using 'findstr' to determine the 
# LTLA in which a postocode resides which maybe required when looking up data
# provided at an LTLA level on the government's COVID-19 portal at the address below
# A compressed version of this data file 'lookup_data.zip' is also generated to
# make distribution of this large file easier. 
#
# https://coronavirus.data.gov.uk/
#
# Example:
#
# findstr /C:"BN14 0BH" lookup_data.csv
# 
# Gives the following output.
#
# BN14 0BH,High Salvington & Findon Valley,E02006621,7648,Worthing,E07000229,110570
#
# Usage
# =====
#
# This script requires no command line arguments and can be invoked as follows:
#
# python generate_lookup.py
# 
# Data and configuration files
# ============================
#
# This utility requires configuration file ..\config\generate_lookup.csv which contains 4 lines
# each specifying the positions of a number of data fields in a csv input file. The format of the 
# file is as follows:
#
# line 1: Position of fields in msoa_names.csv file lines as follows:
#
# Code:<position of MSOA code field>,Name:<position of MSOA name field>
#
# line 2: Position of fields in msoa_populations.csv file lines as follows:
#
# Code:<position of MSOA code field>,Name:<position of MSOA name field>,Population:<position of MSOA population field>
#
# line 3: Position of fields in authority_data.csv file lines as follows:
#
# Code:<position of LTLA code field>,Name:<position of LTLA name field>
#
# line 4: Position of fields in postcode_data.csv file lines as follows:
#
# Postcode:<position of postcode field>,AuthorityCode:<position of LTLA code field>,MsoaCode:<position of LTLA code field>
#
# This file is delivered with the followig default configuration:
#
# Code:0,Name:3
# Code:0,Name:2,Population:3
# Code:0,Name:1
# Postcode:2,AuthorityCode:9,MsoaCode:41
#
# Logging
# =======
#
# This script logs error and status messages to the file .\log\log.txt an to the user console.

import calendar
from datetime import date,timedelta
import os
import re
import subprocess
import sys
import time
from uk_covid19 import Cov19API
import utils as Utils

############
### MAIN ###
############

# File names and modes
Currentdir = os.getcwd()
LogDir = Currentdir + '\\log'
ErrorFilename = LogDir + '\\' + 'log.txt'
DataDir = Currentdir + '\\data'
ConfigDir = Currentdir + '\\config'
ConfigurationFilename = ConfigDir + '\\' + 'generate_lookup.csv'
AuthoritiesFilename = DataDir + '\\' + 'authority_data.csv'
PopulationFilename = DataDir + '\\' + 'msoa_populations.csv'
PostcodeFilename = DataDir + '\\' + 'postcode_data.csv'
MsoasFilename = DataDir + '\\' + 'msoa_names.csv'
LookupFilename = DataDir + '\\' + 'lookup_data.csv'
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
module = 'generate_lookup.py'

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

# Read field positions  
MsoasFileFields = Utils.ReturnPositions(ConfigurationDataLines[0])
PopulationFields = Utils.ReturnPositions(ConfigurationDataLines[1])
AuthoritiesFields = Utils.ReturnPositions(ConfigurationDataLines[2])
PostcodeFields = Utils.ReturnPositions(ConfigurationDataLines[3])

# Close Configuration file
ErrorMessage = 'Could not close ' + ConfigurationFilename
if ( Utils.Close(ConfigurationFileObject,failure) == failure ) : Utils.Logerror(ErrorFileObject,module,ErrorMessage,warning)

# Log progress messages
ErrorMessage = 'Reading configuration file %s ' % AuthoritiesFilename
Utils.Logerror(ErrorFileObject,module,ErrorMessage,info)

# Open and parse authorities file
AuthoritiesFileObject = Utils.Open(AuthoritiesFilename,read,failure)
ErrorMessage = 'Could not open configuration file ' + AuthoritiesFilename
if ( AuthoritiesFileObject == failure ) : Utils.Logerror(ErrorFileObject,module,ErrorMessage,error)

# Read authorities file
AuthoritiesFileData = Utils.Read(AuthoritiesFileObject,empty)
if ( AuthoritiesFileData != empty ) : 
    AuthoritiesFileDataLines = AuthoritiesFileData.splitlines()
else:
    ErrorMessage = 'No data in ' + AuthoritiesFilename
    Utils.Logerror(ErrorFileObject,module,ErrorMessage,error)
if ( Utils.Close(AuthoritiesFileObject,failure) == failure ) : Utils.Logerror(ErrorFileObject,module,ErrorMessage,warning)

# Build authorities structure
Authorities = {}
AuthorityCodes = {}
AuthorityData = {}

for AuthoritiesFileDataLine in AuthoritiesFileDataLines :
    Data = Utils.ReturnData(AuthoritiesFileDataLine)
    
    # Build Authorities structure
    #
    # Key:   String Authority name.
    #
    # Value: Dictionary 
    #
    # Code:         Authority code
    # Name:         Authority name
    # Population:   Authority population
    
    # Build AuthorityCodes structure
    #
    # Key:   String Authority code.
    #
    # Value: Dictionary 
    #
    # Code:         Authority code
    # Name:         Authority name
    # Population:   Authority population
    
    AuthorityCode = Data[AuthoritiesFields['Code']]
    AuthorityData['Code'] = AuthorityCode
    AuthorityName = Data[AuthoritiesFields['Name']]
    AuthorityData['Name'] = AuthorityName
    AuthorityData['Population'] = 0
    Authorities[AuthorityName] = AuthorityData
    AuthorityCodes[AuthorityCode] = AuthorityData
    AuthorityData = {}

# Close Authorities file
ErrorMessage = 'Could not close ' + AuthoritiesFilename
if ( Utils.Close(AuthoritiesFileObject,failure) == failure ) : Utils.Logerror(ErrorFileObject,module,ErrorMessage,warning)

# Log progress messages
ErrorMessage = 'Reading configuration files %s and %s ' % (PopulationFilename,MsoasFilename)
Utils.Logerror(ErrorFileObject,module,ErrorMessage,info)

# Open population file
PopulationFileObject = Utils.Open(PopulationFilename,read,failure)
ErrorMessage = 'Could not open configuration file ' + PopulationFilename
if ( PopulationFileObject == failure ) : Utils.Logerror(ErrorFileObject,module,ErrorMessage,error)

# Open msoas file
MsoasFileObject = Utils.Open(MsoasFilename,read,failure)
ErrorMessage = 'Could not open configuration file ' + MsoasFilename
if ( MsoasFileObject == failure ) : Utils.Logerror(ErrorFileObject,module,ErrorMessage,error)

# Read and parse population and MSOA files.
PopulationFileDataLine = Utils.Readline(PopulationFileObject,empty)
Errormessage = 'No data in ' + PopulationFilename
if ( PopulationFileDataLine == empty ) : File.Logerror(ErrorFileObject,module,Errormessage,error)

MsoasFileDataLine = Utils.Readline(MsoasFileObject,empty)
Errormessage = 'No data in ' + MsoasFilename
if ( MsoasFileDataLine == empty ) : File.Logerror(ErrorFileObject,module,Errormessage,error)

# Build MSOA structure
Msoas = {}
MsoaData = {}

# Initiate population total count.
NewAuthorityName = ''
OldAuthorityName = ''
NewTotalPopulation = 0
OldTotalPopulation = 0

while ( ( PopulationFileDataLine != empty ) and ( MsoasFileDataLine != empty ) ):
    
    PopulationData = Utils.ReturnData(PopulationFileDataLine)
    NewAuthorityName = PopulationData[PopulationFields['Name']]  
    
    MsoasData = Utils.ReturnData(MsoasFileDataLine)
       
    # These files should consist of the same number of data lines in the
    # same alphabetic order with resepct to the first data value of each line.
    if ( PopulationData[PopulationFields['Code']] != MsoasData[MsoasFileFields['Code']] ) : 
        ErrorMessage = 'the contents of %s and %s do not align' % (PopulationFilename,MsoasFilename)
        Utils.Logerror(ErrorFileObject,module,ErrorMessage,error)
       
       
    # Build Msoas structure
    #
    # Key:   String MSOA code.
    #
    # Value: Dictionary 
    #
    # Code:         MSOA code
    # Name:         MSOA name
    # Population:   MSOA population
    # Authority:    MSOA local authority name
    
    MsoaCode = MsoasData[MsoasFileFields['Code']]
    MsoaData['Code'] = MsoaCode
    MsoaData['Name'] = MsoasData[MsoasFileFields['Name']]
    MsaoPopulationString = PopulationData[PopulationFields['Population']].replace(',','')
    MsaoPopulation = int(MsaoPopulationString)
    MsoaData['Population'] = MsaoPopulation
    MsoaData['Authority'] = NewAuthorityName
    Msoas[MsoaCode] = MsoaData
    MsoaData = {}
    
    # Derive population totals
    if ( NewAuthorityName == OldAuthorityName ) or ( OldAuthorityName == '' ):
        NewTotalPopulation = NewTotalPopulation + MsaoPopulation
    else :
    
        # MSOA's for some authorities do not have consecutive MSOA codes
        # so following is required.
        if ( OldAuthorityName in Authorities.keys() ) :
            Authorities[OldAuthorityName]['Population'] = Authorities[OldAuthorityName]['Population'] + OldTotalPopulation
        else:
            Authorities[OldAuthorityName]['Population'] = OldTotalPopulation
                
        NewTotalPopulation = MsaoPopulation
        
    OldAuthorityName = NewAuthorityName
    OldTotalPopulation = NewTotalPopulation
    
    PopulationFileDataLine = Utils.Readline(PopulationFileObject,empty)
    MsoasFileDataLine = Utils.Readline(MsoasFileObject,empty)

# Close population file
ErrorMessage = 'Could not close ' + PopulationFilename
if ( Utils.Close(PopulationFileObject,failure) == failure ) : Utils.Logerror(ErrorFileObject,module,ErrorMessage,warning)

# Close msoas file
ErrorMessage = 'Could not close ' + MsoasFilename
if ( Utils.Close(MsoasFileObject,failure) == failure ) : Utils.Logerror(ErrorFileObject,module,ErrorMessage,warning)

# Log progress messages
ErrorMessage = 'Reading configuration files %s ' % PostcodeFilename
Utils.Logerror(ErrorFileObject,module,ErrorMessage,info)

# Open postcode file
PostcodeFileObject = Utils.Open(PostcodeFilename,read,failure)
ErrorMessage = 'Could not open configuration file ' + PostcodeFilename
if ( PostcodeFileObject == failure ) : Utils.Logerror(ErrorFileObject,module,ErrorMessage,error)

# Open lookup file
LookupFileObject = Utils.Open(LookupFilename,overwrite,failure)
ErrorMessage = 'Could not open configuration file ' + LookupFilename
if ( LookupFileObject == failure ) : Utils.Logerror(ErrorFileObject,module,ErrorMessage,error)

# Read and parse postcode file.
PostcodeFileDataLine = Utils.Readline(PostcodeFileObject,empty)
Errormessage = 'No data in ' + PostcodeFilename
if ( PostcodeFileDataLine == empty ) : File.Logerror(ErrorFileObject,module,Errormessage,error)

# Log progress messages
ErrorMessage = 'Generating lookup file %s ' % LookupFilename
Utils.Logerror(ErrorFileObject,module,ErrorMessage,info)

# Track invalid Post codes / MSOA codes
InvalidMsoas = {}
InvalidData = []
PostcodeCount = 0
PostcodeErrorCount = 0
OldPostCodeMajorPart = ''
PostCodeMajorPartCount = 0

while ( PostcodeFileDataLine != empty ) :
    
    PostcodeData = Utils.ReturnData(PostcodeFileDataLine)
    Postcode = PostcodeData[PostcodeFields['Postcode']]
    
    # Count major postcode parts. 
    NewPostCodeMajorPart = Postcode.split()[0]
    if ( NewPostCodeMajorPart != OldPostCodeMajorPart ) : PostCodeMajorPartCount +=1
    OldPostCodeMajorPart = NewPostCodeMajorPart
        
    AuthorityCode = PostcodeData[PostcodeFields['AuthorityCode']]
    MsoaCode = PostcodeData[PostcodeFields['MsoaCode']]
    
    # Display progress message
    PostcodeCount +=1 
    if ( (PostcodeCount%100000) == 0 ) : 
        ErrorMessage = '%d postcodes processed' % PostcodeCount
        Utils.Logerror(ErrorFileObject,module,ErrorMessage,info)
       
    
    if not ( MsoaCode in Msoas.keys() ) : 
        #ErrorMessage = 'The Post code %s has an invalid MSOA code %s defined ' % (Postcode,MsoaCode)
        #Utils.Logerror(ErrorFileObject,module,ErrorMessage,warning)
        
        PostcodeErrorCount += 1
        
        if MsoaCode in InvalidMsoas.keys() :
            InvalidMsoas[MsoaCode].append(Postcode)
        else:
            InvalidData = [Postcode]
            InvalidMsoas[MsoaCode] = InvalidData
            InvalidData = []
            
    else :
        OutputRow = [Postcode,Msoas[MsoaCode]['Name'],Msoas[MsoaCode]['Code'],Msoas[MsoaCode]['Population'],AuthorityCodes[AuthorityCode]['Name'],AuthorityCodes[AuthorityCode]['Code'],AuthorityCodes[AuthorityCode]['Population']]
        PostCodeDataLine = Utils.GenerateCSVRow(OutputRow)
        
        ErrorMessage = 'Could not write line %s to %s' % (PostCodeDataLine,LookupFilename)
        if ( Utils.Writeline(LookupFileObject,PostCodeDataLine,failure) == failure ) : Utils.Logerror(ErrorFileObject,module,ErrorMessage,warning)
            
        
    PostcodeFileDataLine = Utils.Readline(PostcodeFileObject,empty)
    
# Output statistics.
ErrorMessage = 'A total of %d postcodes were processed ' % PostcodeCount
Utils.Logerror(ErrorFileObject,module,ErrorMessage,info)
ErrorMessage = 'A total of %d postcodes with non-existent MSOA\'s were found ' % PostcodeErrorCount
Utils.Logerror(ErrorFileObject,module,ErrorMessage,warning)

# Print invalid MSOA data
for MsoaCode in InvalidMsoas :

    # Pront MSOA code
    ErrorMessage = 'MSOA %s was invalid and associated with the following postcodes' % MsoaCode
    Utils.Logerror(ErrorFileObject,module,ErrorMessage,warning)
    
    # Print associated postcodes
    OutputRow = InvalidMsoas[MsoaCode]
    PostCodeDataLine = Utils.GenerateCSVRow(OutputRow)
    Utils.Logerror(ErrorFileObject,module,PostCodeDataLine,warning)

# Close postcode file
ErrorMessage = 'Could not close ' + PostcodeFilename
if ( Utils.Close(PostcodeFileObject,failure) == failure ) : Utils.Logerror(ErrorFileObject,module,ErrorMessage,warning)

# Close lookup file
ErrorMessage = 'Could not close ' + LookupFilename
if ( Utils.Close(LookupFileObject,failure) == failure ) : Utils.Logerror(ErrorFileObject,module,ErrorMessage,warning)

# Log end of script
Utils.Logerror(ErrorFileObject,module,'Completed',info)

# Close error log file
ErrorMessage = 'Could not close ' + ErrorFilename
if ( Utils.Close(ErrorFileObject,failure) == failure ) : Utils.Logerror(ErrorFileObject,module,ErrorMessage,warning)