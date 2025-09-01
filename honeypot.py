#LIBRARIES

import logging
from logging.handlers import RotatingFileHandler
import paramiko
import socket
import threading
import time
from pathlib import Path

#CONSTANTS
logging_format = logging.Formatter('%(message)s')
SSH_BANNER = "SSH-2.0-OpenSSH_7.6"
# generate_key.pyclear
if not Path("server_key").exists():
    key = paramiko.RSAKey.generate(2048)
    key.write_private_key_file("server_key")
    print("server_key generated successfully.")
host_key = paramiko.RSAKey(filename="server_key")

print("server_key generated successfully.")
host_key = paramiko.RSAKey(filename="server_key")



#LOGGERS
logging_format = logging.Formatter('%(message)s')

funnel_logger =logging.getLogger('FunnelLogger')
funnel_logger.setLevel(logging.INFO)
funnel_handler = RotatingFileHandler('audits.log' , maxBytes=2000 , backupCount=5)
funnel_handler.setFormatter(logging_format)
funnel_logger.addHandler(funnel_handler)

funnel_logger.info("audits log is online")

creds_logger =logging.getLogger('credsLogger')
creds_logger.setLevel(logging.INFO)
creds_handler = RotatingFileHandler('cmd_audits.log' , maxBytes=2000 , backupCount=5)
creds_handler.setFormatter(logging_format)
creds_logger.addHandler(creds_handler)
creds_logger.info("cmd_audits log is online")
#EMULATED SHELL
def emulated_shell(channel, client_ip):
    channel.send(b'admin$ ')
    command = b''
    while True:
        char = channel.recv(1)
        if not char:
            break
        command += char
        channel.send(char)  # echo back once

        if char in [b'\r', b'\n']:
            cmd = command.strip().decode()
            if cmd == "exit":
                channel.send(b"\nConnection terminated...\r\n")
                break
            elif cmd == "pwd":
                channel.send(b"\n/User/local\r\n")
                creds_logger.info(f'Command{command.strip()}'+'executed by '+f'{client_ip}')
            elif cmd == "whoami":
                channel.send(b"\ncorpuser1\r\n")
                creds_logger.info(f'Command{command.strip()}'+'executed by '+f'{client_ip}')
            elif cmd == "ls":
                channel.send(b"\njumpbox1.conf\r\n")
                creds_logger.info(f'Command{command.strip()}'+'executed by '+f'{client_ip}')
            elif cmd == "cat jumpbox1.conf":
                channel.send(b"\nGo to homepage\r\n")
                creds_logger.info(f'Command{command.strip()}'+'executed by '+f'{client_ip}')
            else:
                channel.send(b"\n" + command.strip() + b"\r\n")
            channel.send(b"admin$ ")
            command = b""
    channel.close()
#SERVER+SOCKET
class Server(paramiko.ServerInterface):

    def __init__(self, client_ip, input_username=None, input_password=None):
        self.event =threading.Event()
        self.client_ip = client_ip
        self.input_username = input_username
        self.input_password = input_password
    
    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        else:
            return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

        
    def get_allowed_auths(self , username):
        return "password"
# Dynamically checks credentials against input values set at runtime.
# Logs all attempted connections for monitoring and analysis.
    def check_auth_password(self, username, password):
        funnel_logger.info(f'Client {self.client_ip} attempted connection with ' + f'username: {username}, ' + f'password: {password}')
        creds_logger.info(f'{self.client_ip}, {username}, {password}')
        if self.input_username is not None and self.input_password is not None:
            if username == self.input_username and password == self.input_password:
                return paramiko.AUTH_SUCCESSFUL
            else:
                return paramiko.AUTH_FAILED
        else:
            return paramiko.AUTH_SUCCESSFUL
    
    def check_channel_shell_request(self, channel):
        self.event.set()
        return True
    
    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    def check_channel_exec_request(self, channel, command):
        command = str(command)
        return True
def client_handle(client, addr, username, password):
    client_ip = addr[0]
    print(f"{client_ip} connected to server.")
    try:
        transport = paramiko.Transport(client)
        transport.local_version = SSH_BANNER 
        server = Server(client_ip=client_ip, input_username=username, input_password=password)
        transport.add_server_key(host_key)
        transport.start_server(server=server)
        channel =transport.accept(100)
        if channel is None:
            print("[!] No channel was opened!")
        else:
            print("[*] Channel opened successfully")
        if channel is None:
            print("No channel was opened.")

        standard_banner = "ssh sucessfully established with stable channel"
        channel.send(standard_banner)
        emulated_shell(channel, client_ip=client_ip)       
    except Exception as error:
        print(error)
        print("!!! Exception !!!")
    finally:
        try:
            transport.close()
        except Exception:
            pass
        
        client.close()
host_key = paramiko.RSAKey(filename="server_key")
#PROVISION SSH BASED HONEYPOT
def honeypot(address, port ,username ,password):
    skt = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
    skt.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    skt.bind((address, port))

    skt.listen(20)
    print(f"SSH server is listening on port {port}.")

    while True: 
        try:
            client, addr = skt.accept()
            ssh_honeypot_thread = threading.Thread(target=client_handle, args=(client, addr, username, password))
            ssh_honeypot_thread.daemon = True
            ssh_honeypot_thread.start()


        except Exception as error:
            print("!!! Exception - Could not open new client connection !!!")
            print(error)


honeypot('127.0.0.1', 2220 ,'username' ,'1234')





















