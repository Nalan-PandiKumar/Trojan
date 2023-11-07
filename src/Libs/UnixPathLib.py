#!UnixPathLib <Dependency which contains functions to validate the paths in the change directory command for unix>


def isabsolute(path,user):
    #Check whether the path is absolute or not
    if(path[0]=="/" or remover(splitdirectory(path))[0]=="~" or remover(splitdirectory(path))[0].upper()=="$HOME"or (path[0]=="/" and remover(splitdirectory(path))[0]=="home" and remover(splitdirectory(path))[1]==user)):
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
    path=path.split("/")
    return path

def JoinrootPath(Directories):
    #Join the Directories with root directory

    return "/"+"/".join(Directories)


def JoinPath(Directories):
    #Join the Directories with slash
    path=""
    for directory in Directories:
        path+=directory+"/"
    return path

def CountDirectories(path):

    #Count the number of directories in the path
    count=0
    directories=remover(JoinrootPath(splitdirectory(path)))
    for directory in directories:
        count+=1
    return count


def BackDir(user,cwd,path):
    #Used to return to parent directories
    cwd=remover(splitdirectory(cwd))
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
    if (directories[0]=="home" and directories[1]==user):
        directories.pop(0);directories.pop(0);directories.insert(0,"~")
        return JoinPath(directories)
    else:
        return path
    
def ReverseReplacer(path,user):

    #Reverse the tidle sign with home path 
    directories=remover(splitdirectory(path))
    if (directories[0]=="~"):
        directories.pop(0);directories.insert(0,"home");directories.insert(1,user)
        return JoinrootPath(directories)
    else:
        return path

