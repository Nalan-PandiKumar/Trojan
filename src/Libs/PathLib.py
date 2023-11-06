#!PathLib <Dependency which contains functions to validate the paths in the change directory command for windows>

__all__=['isabsolute','isrelative','remover','splitdirectory','isdirectories','isdirectory','CountDirectories','DriveAPath','BackDir','replacer','RemoveDot','isValidPath','BackDotRemover']

def isabsolute(path,partitions):

    #Used to check the path is absolute or not
    if (remover(splitdirectory(path))[0][-1]==":" ):
        if (remover(splitdirectory(path))[0] in partitions.split("\\")):
            return True
        else:
            raise ValueError("Invalid path")
    else:
        return False

def isrelative(path):

        #Used to check the path is relative or not
        if (isdirectories(remover(splitdirectory(path)))):
            return True
        else:
            raise ValueError("Invalid Directory Name")

def remover(directories):

    #Remove the empty quotes
    while ('' in directories):
        directories.remove('')
    return directories

def splitdirectory(path):

    #spearate each and every directories from path
    path=path.replace("/","\\")
    return path.split("\\")
   
        

def isdirectories(directories):
    #This function not check "?" and "*" because they are used in cd command in replacement of space character 
    #Check  all directories are valid directories
    NotValidChars=[":","\\","/",'"',"<",">","|"]
    for directory in directories:
        for char in NotValidChars:
            if (char in directory):
                return False
    return True

def isdirectory(directory):
    #This function not check "?" and "*" because they are used in cd command in replacement of space character 
    #check it is a valid directory
    NotValidChars=[":","\\","/",'"',"<",">","|"]
    for char in NotValidChars:
        if (char in directory):
            return False
    return True


def CountDirectories(path):

    #Count the number of directories in the path
    count=0
    directories=remover(splitdirectory(path))
    for directory in directories:
        if (isdirectory(directory)):
            count+=1
    return count


def DriveAPath(path,partitions):
    # separate and return drive and path as tuple
    if (isabsolute(path,partitions)):
        drive,path=path.split(":")
        drive+=":"
        return drive,path
    else:
        return '',path


def BackDir(drive,cwd,path):
    #Used to return to parent directories
    cwd=remover(splitdirectory(cwd))
    path=remover(splitdirectory(path))
    for directory in path:
        if directory=="..":
            cwd.pop()
        elif isdirectory(directory):
            cwd.append(directory)
        elif not isdirectory(directory):
            raise ValueError("Invalid Path")
    cwd=RemoveDot(cwd)
    cwd.insert(0,drive)
    return replacer("\\".join(cwd))


def replacer(path):
    #Function replaces the special characters used between directories ,used instead of space
    path=path.replace("*"," ")
    path=path.replace("?"," ")
    return path

def RemoveDot(directories):
    #Remove the unnecessary dot in the directories
    NewDirectories=list()
    for directory in directories:
        try:
            while(directory[-1]=="."):
                directory=directory[0:len(directory)-1]
        except IndexError:
            pass
        else:
            NewDirectories.append(directory)
    return NewDirectories

def isValidPath(stdout):
    #validate the path os client's path
    
    if stdout in ["The system cannot find the path specified.\n","The system cannot find the drive specified.\n","The filename, directory name, or volume label syntax is incorrect.\n","The system cannot find the path specified.","The system cannot find the drive specified.","The filename, directory name, or volume label syntax is incorrect."]:
        return False
    else:
        return True

def BackDotRemover(cmd):

    #Return the List of Corrected Command
    NewDirectories=list()
    for directory in cmd:
        if (directory.count('.')==len(directory) and directory.count('.')!=2):
            pass
        else:
            NewDirectories.append(directory)
    return NewDirectories

