#!UnixPathLib <Dependency which contains functions to validate the paths in the change directory command for unix>

def isabsolute(path):
    #Check whether the path is absolute or not
    if(path[0]=="/" or path[0]=="~" or remover(splitdirectory(path))[0].upper()=="$HOME" ):
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
    path=path.replace("\\","/")
    return path.split("/")

