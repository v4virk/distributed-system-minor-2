import socket
import os

# Server 1 code (same for Server 2 with appropriate changes)
SERVER1_IP = "192.168.30.2"
SERVER1_PORT = 8081
SAVE_DIR = "server1_storage"

os.makedirs(SAVE_DIR, exist_ok=True)

def start_server1():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER1_IP, SERVER1_PORT))
    server_socket.listen(5)
    print(f"Server 1 listening on {SERVER1_IP}:{SERVER1_PORT}")

    while True:
        conn, addr = server_socket.accept()
        file_name = conn.recv(1024).decode()

        if file_name:
            file_path = os.path.join(SAVE_DIR, file_name)
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    file_data = f.read()
                conn.sendall(file_data)
            else:
                conn.sendall(b"File not found")

        conn.close()

if __name__ == "__main__":
    start_server1()