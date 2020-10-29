@echo off
rem
rem msoa_lookup.bat
rem
rem This batch file will create file 'lookup_data.csv' containing information 
rem relating to the MSOA ( Middles Super Output Area ) and LTLA (Lower Tier
rem Local Authority ) in which each UK  postcode resides. Each row of this 
rem file consists of the following fields:
rem 
rem <Post code>,<MSOA name><MSOA code>,<MSOA population>,<LTLA name><LTLA code>,<LTLA population>
rem
rem This script invokes Python utilities 'retrieve_files.py' and 
rem 'generate_lookup.py' and assumes that the 7-Zip utility is installed 
rem in directory C:\Program Files\7-Zip
rem
rem File 'lookup_data.csv' can be searched using 'findstr' to determine the 
rem LTLA in which a postocode resides which is required when looking up data
rem provided at an LTLA level on the government's COVID-19 portal.
rem
rem e.g.
rem
rem findstr /C:"BN14 0BH" lookup_data.csv
rem 
rem Gives the following output.
rem
rem BN14 0BH,High Salvington & Findon Valley,E02006621,7648,Worthing,E07000229,110570
rem
rem A compressed version of this data file 'lookup_data.zip' is also generated to
rem make distribution of this large file easier. 
 
rem Create variables
rem
rem Files and directories
set ScriptDir=%cd%
set LogDir=%ScriptDir%\log
set LogFile=%LogDir%\log.txt
set DataDir=%ScriptDir%\data
set NamesFile=msoa_names
set PopulationsFile=msoa_populations
set AuthorityFile=authority_data
set PostcodesFile=postcode_data
set LookupFile=lookup_data
set TempDir=c:\temp
rem
rem Executables
set Zip="C:\Program Files\7-Zip\7z.exe"
set RetrieveFiles=%ScriptDir%\retrieve_files.py
set GenerateLookup=%ScriptDir%\generate_lookup.py
set ExtractPopulations=%ScriptDir%\extract_populations.vbs

rem Move to script directory
cd %ScriptDir%

rem Remove old log file
erase %LogFile%

rem Retrieve source data files from web locations to temporary storage
%RetrieveFiles%

rem Generate input data files from temporary data files by extracting data for England
rem and ordering data records 

rem Generate msoa_names.csv
type %TempDir%\%NamesFile%.csv | findstr "^E" | findstr /V "^W" | sort > %DataDir%\%NamesFile%.csv

rem Generate msoa_populations.csv
%Zip% rn %TempDir%\%PopulationsFile%.zip SAPE22DT4-mid-2019-msoa-syoa-estimates-unformatted.xlsx %PopulationsFile%.xlsx 
%Zip% e %TempDir%\%PopulationsFile%.zip -o%TempDir% %PopulationsFile%.xlsx -y -r 
%ExtractPopulations%
type %TempDir%\%PopulationsFile%.csv | findstr "^E" | findstr /V "^W" | sort > %DataDir%\%PopulationsFile%.csv

rem Generate authority_data.csv
%Zip% e %TempDir%\%AuthorityFile%.zip -so "LA_UA names and codes UK as at 04_20.csv" | findstr "^E" | findstr /V "^W" | sort > %DataDir%\%AuthorityFile%.csv

rem Generate postcode_data.csv
%Zip% e %TempDir%\%PostcodesFile%.zip -so "gridall.csv" | findstr /C:"E0200" | findstr /V /C:"W0200" | findstr /V /C:"N99999999" > %DataDir%\%PostcodesFile%.csv

rem Remove temporary files
erase /f /s %TempDir%\%AuthorityFile%.zip
erase /f /s %TempDir%\%NamesFile%.csv
erase /f /s %TempDir%\%PostcodesFile%.zip
erase /f /s %TempDir%\%PopulationsFile%.*

rem Generate lookup_data.csv 
%GenerateLookup%
cd %DataDir%

rem Create compressed lookup data file lookup_data.zip.
%Zip% a %LookupFile%.zip %LookupFile%.csv

rem Remove all csv files.
rem
rem NOTE: This line should be removed once software is installed
erase  /f /s *.csv