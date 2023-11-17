#!PathLib <Dependency which contains functions to validate the paths in the change directory command for windows>

__all__=['isabsolute','isrelative','remover','splitdirectory','isdirectories','isdirectory','CountDirectories','DriveAPath','BackDir','isBack','replacer','RemoveDot','BackDotRemover']

def isabsolute(path):

    #Used to check the path is absolute or not
    if (len(remover(splitdirectory(path)))!=0 ):
        if(remover(splitdirectory(path))[0][-1]==":"):
        	return True
        else:
        	return False
    else:
        return False

def isrelative(path):

    #Used to check the path is relative or not
    if (isdirectories(remover(splitdirectory(path)))):
        return True
    else:
        raise False


def JoinPath(Directories):
    #Join the Directories with slash
    path=""
    for directory in Directories:
        path+=directory+"\\"
    return path



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


def DriveAPath(path):
    # separate and return drive and path as tuple
    if (isabsolute(path)):
        drive,path=path.split(":")
        drive+=":"
        return drive,path
    else:
        return '',path


def BackDir(drive,cwd,path):
    #Used to return to parent directories
    if (not isabsolute(path)):
        cwd=remover(splitdirectory(cwd))
        path=remover(splitdirectory(path))
    else:
        cwd=remover(splitdirectory(cwd));cwd.clear()
        path=remover(splitdirectory(path))
        drive=path[0];path.pop(0)
    
    for directory in path:
        if (directory==".." and len(cwd)!=0):
            cwd.pop()
        elif(isdirectory(directory)and directory!=".."):
            cwd.append(directory)
            
    cwd=RemoveDot(cwd)
    cwd.insert(0,drive)
    return replacer(JoinPath(cwd))


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

def isBack(path):

    #Return true the path contains back navigation
    path=remover(splitdirectory(path))
    if ".." in path:
        return True
    else:
        return False


def BackDotRemover(cmd):

    #Return the List of Corrected Command
    NewDirectories=list()
    for directory in cmd:
        if (directory.count('.')==len(directory) and directory.count('.')!=2):
            pass
        else:
            NewDirectories.append(directory)
    return NewDirectories

