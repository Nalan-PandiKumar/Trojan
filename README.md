---

# 🚀 remotemal - Remote Access Tool (RAT)

Welcome to **remotemal**, a powerful and flexible Remote Access Tool that allows you to control systems remotely, transfer files, and execute commands seamlessly. Whether you're managing a fleet of machines or conducting security assessments, `remotemal` has you covered!

## 🌟 Features

- **Remote File Upload and Download**: Easily transfer files between your local machine and the target system.
- **Command Execution**: Execute commands on the remote machine and retrieve output.
- **Support for Text and Binary Files**: Upload and download both text and binary files effortlessly.
- **Real-time Progress Feedback**: Enjoy a smooth user experience with progress bars during file transfers.
- **Terminal-like Functionality**: Navigate directories as you would in a normal command prompt/terminal, supporting all types of directory navigations.
- **Cross-Platform Support**: Compatible with Windows, Linux, and macOS.

## ⚙️ Installation

To get started with `remotemal`, clone the repository and install the required dependencies:

```bash
git clone https://github.com/Nalan-PandiKumar/Trojan.git
cd Trojan/src
pip install -r requirements.txt
```

## 📜 Usage

### Starting the Server

Run the server script to listen for incoming connections. You can specify a socket data transfer buffer using the `-b` option:

```bash
python server.py -b <buffer_size>
```

**Command-Line Argument:**
- `-b <socket-data-transfer-buffer>`: This command will ask you for the buffer value for data transmission as input.
  - **Minimum Value:** 1024 Bytes
  - **Maximum Value:** 999999999 Bytes

### Connecting the Client

On the target machine, run the client script to connect back to the server:

```bash
python client.py
```

## 📥 File Transfer Commands

### Download Commands

- **Download Text Files**
  ```bash
  remotemal-dld -t <file_path>
  ```

- **Download Binary Files** (Images, Videos, Music, etc.)
  ```bash
  remotemal-dld -b <file_path>
  ```

### Upload Commands

- **Upload Text Files**
  ```bash
  remotemal-upld -t <file_path>
  ```

- **Upload Binary Files** (Images, Videos, Music, etc.)
  ```bash
  remotemal-upld -b <file_path>
  ```

### Example Usage

- To download a text file:
  ```bash
  remotemal-dld -t /path/to/your/file.txt
  ```

- To upload a binary file:
  ```bash
  remotemal-upld -b /path/to/your/image.png
  ```

## 🛠️ Command Execution

Execute commands on the remote machine and retrieve the output:

```bash
<your_command_here>
```

## 🚧 Note

Ensure that the target system is connected and has the `remotemal` client running to accept connections.

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/Nalan-PandiKumar/Trojan/blob/main/LICENSE.txt) file for more information.

---
