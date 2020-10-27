# msoa_lookup

This repository delivers utility scripts 'msoa_lookup.bat', 'generate_lookup.py' and 'retrieve_files.py' which 
together support the creation of file 'lookup_data.csv' containing information  relating to the MSOA 
( Middles Super Output Area ) and LTLA (Lower Tier Local Authority ) in which each UK  postcode resides. 
Each row of this file consists of the following fields:

\<Post code\>,\<MSOA name\>\<MSOA code\>,\<MSOA population\>,\<LTLA name\>\<LTLA code\>,\<LTLA population\>

File 'lookup_data.csv' can be searched using 'findstr' to determine the  LTLA in which a postocode 
resides which is required when looking up data provided at an LTLA level on the government's COVID-19 
portal.

e.g.

findstr /C:"BN14 0BH" lookup_data.csv

Gives the following output.

BN14 0BH,High Salvington & Findon Valley,E02006621,7648,Worthing,E07000229,110570

A compressed version of this data file 'lookup_data.zip' is also generated to
make distribution of this large file easier. 

Deliverables
------------
To implement the functionality discussed above the following scripts and configuration files are delivered:

File | File Contents
------------- | -------------
msoa_lookup.bat | Runs all utiltity scripts and commands necessary to create file ..\data\lookup_data.csv
generate_lookup.csv | Configuration file for generation_lookup.py
generate_lookup.py | Generates file ..\data\lookup_data.csv from input files retrieved by retrieve_file.py
retrieve_files.csv | Configuration file for retrieve_files.py
retrieve_files.py | Retrieves input files from web required to create file ..\data\lookup_data.csv
extract_populations.vbs | Converts excel spreadsheet covering NHS trust deaths to interim csv file 
ExtractPopulationData.txt | Source for Excel macro ExtractPopulationDat used by extract_populations.vbs. 
utils.py | Python module containing functions used by both generate_lookup.py and retrieve_file.py. 

As well as the above scripts and data files the following supporting documentation is also provided:

Document File | File Contents
------------- | -------------
msoa_lookup_installation.txt | Installation instructions