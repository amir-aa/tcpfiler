import socket
import os
import argparse

def send_file(host, port, file_path):
    try:
        # Get file info
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        # Create TCP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        
        # Send file info
        file_info = f"{file_name}|{file_size}"
        client_socket.send(file_info.encode())
        
        # Send file data
        with open(file_path, 'rb') as file:
            while True:
                data = file.read(4096)  # Same buffer size as server
                if not data:
                    break
                client_socket.send(data)
                
        print(f"File {file_name} ({file_size} bytes) sent successfully")
        
    except Exception as e:
        print(f"Error sending file: {e}")
    finally:
        client_socket.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TCP File Sender')
    parser.add_argument('file', help='Path to the file to send')
    parser.add_argument('--host', default='localhost', help='Server host (default: localhost)')
    parser.add_argument('--port', type=int, default=5000, help='Server port (default: 5000)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"Error: File {args.file} does not exist")
        exit(1)
        
    send_file(args.host, args.port, args.file)
