import socket
import threading
import os

def handle_client(conn, addr, storage_dir):
    try:
        request_type = conn.recv(3).decode()  # Either PUT or GET

        name_len = int.from_bytes(conn.recv(4), byteorder='big')
        file_name = conn.recv(name_len).decode()

        if request_type == "PUT":
            file_size = int.from_bytes(conn.recv(4), byteorder='big')
            file_data = b''
            while len(file_data) < file_size:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                file_data += chunk
            with open(os.path.join(storage_dir, file_name), 'wb') as f:
                f.write(file_data)
            print(f"✅ Received: {file_name} from {addr}")

        elif request_type == "GET":
            file_path = os.path.join(storage_dir, file_name)
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    data = f.read()
                conn.send(len(data).to_bytes(4, byteorder='big'))
                conn.sendall(data)
                print(f"📤 Sent: {file_name} to {addr}")
            else:
                conn.send((0).to_bytes(4, byteorder='big'))
                print(f"❌ Not found: {file_name} on server {addr}")
    except Exception as e:
        print(f"❌ Error with {addr}: {e}")
    finally:
        conn.close()

def start_server(port):
    storage_dir = f"storage_{port}"
    os.makedirs(storage_dir, exist_ok=True)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", port))
    server.listen()
    print(f"🚀 Server listening on port {port}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr, storage_dir), daemon=True).start()

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8081
    start_server(port)
