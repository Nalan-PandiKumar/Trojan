#!UnixPathLib <Dependency which contains functions to validate the paths in the change directory command for unix>


def isabsolute(path,user):
    #Check whether the path is absolute or not
    if(path[0]=="/" or remover(splitdirectory(path))[0]=="~" or remover(splitdirectory(path))[0].upper()=="$HOME"or (remover(splitdirectory(path))[0]=="/" and remover(splitdirectory(path))[1]=="home" and remover(splitdirectory(path))[2]==user)):
        return True
    else:
        return False

def remover(directories):

    #Remove the empty quotes
    while ('' in directories):
        directories.remove('')
    return directories

def splitdirectory(path):
    #spearate each and every directories from path
    directories=path.split("/")
    if path[0]=="/":
        directories.insert(0,"/")
    return directories



def JoinrootPath(Directories):
    #Join the Directories with slash
    path=""
    for directory in Directories:
        if directory=="/":
            path+='/'
        else:
            path+=directory+"/"
    return path

def CountDirectories(path):

    #Count the number of directories in the path <Count from the root directory> 
    count=0
    directories=remover(splitdirectory(path))

    for directory in directories:
        count+=1
    return count


def BackDir(user,cwd,path):
    #Used to return to parent directories
    root="/"
    cwd=remover(splitdirectory(cwd));cwd.pop()
    path=BackDotRemover(remover(splitdirectory(path)))
    try:
        for directory in path:
            if directory=="..":
                cwd.pop()
            else:
                cwd.append(directory)
    except IndexError:
        pass
    finally:
        cwd.insert(0,root)
        return replacer(JoinrootPath(cwd),user)


def BackDotRemover(cmd):

    #Return the List of Corrected Command
    NewDirectories=list()
    for directory in cmd:
        if (directory.count('.')==len(directory) and directory.count('.')!=2):
            pass
        else:
            NewDirectories.append(directory)
    return NewDirectories

def replacer(path,user):
    #Reverse the home path with tidle sign
    directories=remover(splitdirectory(path))

    if (isabsolute(path,user) and CountDirectories(path)>=3):
        if (directories[0]=="/" and directories[1]=="home" and directories[2]==user):
            directories.pop(0);directories.pop(0);directories.pop(0);directories.insert(0,"~")

        elif (directories[0].upper()=="$HOME"):
            directories.pop(0);directories.insert(0,"~")
    return JoinrootPath(directories)
            
    
def ReverseReplacer(path,user):
    #Reverse the tidle sign with home path 
    directories=remover(splitdirectory(path))

    if isabsolute(path,user):
        if (directories[0]=="~"):
            directories.pop(0);directories.insert(0,"/");directories.insert(1,"home");directories.insert(2,user)

    return JoinrootPath(directories)
    
