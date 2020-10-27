import subprocess
import sys
import time

# Opens a file
def Open (filename,mode,failure):
    
    "Opens a file"

    try:
        fo = open(filename,mode)
    except:
        return failure
    else:
        return fo
      

# Closes a file      
def Close (Fileobject,failure):
    
    "Closes a file"

    try:
        Fileobject.close()
    except:
        return failure

# Read contents of a file      
def Read (Fileobject,failure):
    
    "Closes a file"

    try:
        contents = Fileobject.read()
    except:
        return failure
    else:
        return contents
        
        # Reads a line from a file      
def Readline (Fileobject,failure):
    
    "Reads a line from a file"

    try:
        line = Fileobject.readline()      
    except:
        return failure
    else:
        return line
        
# Writes buffer to a file      
def Write (Fileobject,buffer,failure):
    
    "Writes line to a file"

    try:
        Fileobject.write(buffer)      
    except:
        return failure
    else:
        return True
        
# Writes a line to a file      
def Writeline (Fileobject,line,failure):
    
    "Writes line to a file"

    try:
        Fileobject.writelines(line)      
    except:
        return failure
    else:
        return line
        
# Write error log entry. The program will exit if the error level
# is 'error'
def Logerror (Fileobject,module,text,level):

    "Write an entry in the error log"
    
    timestamp = time.asctime( time.localtime(time.time()) )
    message = timestamp + ' ' + level + ': ' +  module + ': ' + text
    
    try:
        Fileobject.writelines('%s%s' % ( message,'\n') )
    except:
        print ('Unable to log %s%s%s' % ('\"',message,'\"') )
        sys.exit()
    else:
        if ( level != 'LOG' ) : print ('%s' % message )
        if ( level == 'ERROR' ) : sys.exit()


# Launches spreadsheet program with file argument
def ViewSpeadsheet (spreadsheet,file) :
 
    "Launches spreadsheet program with file argument"
    
    launch = 'start' + ' ' + spreadsheet + ' ' + file
    subprocess.run(['cmd.exe','/C',launch])
    
# Runs script 'script' and waits 'delay' seconds before returning
def RunScript (script,delay) :
 
    "Runs script 'script' and waits 'delay' seconds before returning"
    
    launch = 'start' + ' ' + script
    subprocess.run(['cmd.exe','/C',launch])
    
    time.sleep(delay)  
    
# This procedure will return a string containing the
# elements of list separated by a comma. All elements are
# cast to strings.
def GenerateCSVRow(list) :
 
    "This procedure will generate a string containing the elements of 'list' separated by a comma"
 
    string = ''
    for item in list : string = string + str(item) + ',' 
    string = string.rstrip(',')
    
    return string + '\n'
    
# This procedure will return a lists of data values
# from a line of data. The data values are separated 
# by comma's and may be included in 
# double quotation marks.
def ReturnData(line) :

    "This procedure will return a lists of data values returned from a line of data"
    
    data = []
    
    # Remove line termination
    dataline = line.rstrip('\n')
    
    if ( dataline.count('"') > 0 ) :
    
        tempdata = dataline.split('"')
        for part in tempdata :
            if ( part.startswith(',') or part.endswith(',') ) : 
                part = part.strip(',') 
                if ( len(part) != 0 ) : 
                    for item in (part.split(',')) :
                        data.append(item)
            else:  
                data.append(part)
    else :
        data = dataline.split(',')
        
    return data

# This procedure will return a dictionary of field positions
# created from the contents of 'string'. 
def ReturnPositions(string) :

    "This procedure will return a dictionary of field positions created from the contents of 'string'"
    
    positions = {}
    
    for field in string.split(',') :
        combined = field.split(':')
        key = combined[0]
        value = int(combined[1])
        positions[key] = value

    return positions
