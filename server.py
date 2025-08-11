import socket
import threading
import configparser
import os
from concurrent.futures import ThreadPoolExecutor

class TCPServer:
    def __init__(self, config_file='server.conf'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        
        # Server configuration
        self.host = self.config.get('Server', 'host', fallback='0.0.0.0')
        self.port = self.config.getint('Server', 'port', fallback=5000)
        self.backlog = self.config.getint('Server', 'backlog', fallback=5)
        self.buffer_size = self.config.getint('Server', 'buffer_size', fallback=4096)
        self.max_threads = self.config.getint('Server', 'max_threads', fallback=10)
        self.save_dir = self.config.get('Server', 'save_dir', fallback='received_files')
        
        # Create save directory if it doesn't exist
        os.makedirs(self.save_dir, exist_ok=True)
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.backlog)
        
        self.thread_pool = ThreadPoolExecutor(max_workers=self.max_threads)
        
        print(f"Server started on {self.host}:{self.port}")
        print(f"Backlog: {self.backlog}, Max threads: {self.max_threads}")
        print(f"Saving files to: {self.save_dir}")

    def handle_client(self, client_socket, client_address):
        try:
            print(f"Connection from {client_address}")
            
            # Receive file info (name and size)
            file_info = client_socket.recv(self.buffer_size).decode()
            if not file_info:
                raise Exception("No file info received")
                
            file_name, file_size = file_info.split('|')
            file_size = int(file_size)
            file_path = os.path.join(self.save_dir, file_name)
            
            # Check if file exists and add suffix if needed
            counter = 1
            while os.path.exists(file_path):
                base, ext = os.path.splitext(file_name)
                file_path = os.path.join(self.save_dir, f"{base}_{counter}{ext}")
                counter += 1
            
            # Receive file data
            received = 0
            with open(file_path, 'wb') as file:
                while received < file_size:
                    data = client_socket.recv(min(self.buffer_size, file_size - received))
                    if not data:
                        break
                    file.write(data)
                    received += len(data)
                    
            print(f"File received: {file_path} ({received} bytes)")
            
        except Exception as e:
            print(f"Error handling client {client_address}: {e}")
        finally:
            client_socket.close()

    def start(self):
        try:
            while True:
                client_socket, client_address = self.server_socket.accept()
                self.thread_pool.submit(self.handle_client, client_socket, client_address)
        except KeyboardInterrupt:
            print("\nServer shutting down...")
        finally:
            self.thread_pool.shutdown(wait=True)
            self.server_socket.close()

if __name__ == '__main__':
    server = TCPServer()
    server.start()
