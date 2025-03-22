import socket
import os
import tkinter as tk
from tkinter import messagebox, ttk

# Server details (same as in your original code)
SERVER1_IP = "192.168.30.2"
SERVER2_IP = "192.168.30.2"
SERVER1_PORT = 8081
SERVER2_PORT = 8082

# Directory to save the merged file
MERGE_DIR = "merged_files"
os.makedirs(MERGE_DIR, exist_ok=True)

def merge_files():
    try:
        # Retrieve file parts from servers
        part1 = retrieve_file_from_server(SERVER1_IP, SERVER1_PORT, "client_part1.dat")
        part2 = retrieve_file_from_server(SERVER2_IP, SERVER2_PORT, "client_part2.dat")

        if not part1 or not part2:
            messagebox.showerror("Error", "Failed to retrieve one or more file parts.")
            return

        # Merge the file parts
        merged_data = part1 + part2

        # Save the merged file
        merged_file_path = os.path.join(MERGE_DIR, "merged_file.dat")
        with open(merged_file_path, "wb") as merged_file:
            merged_file.write(merged_data)

        messagebox.showinfo("Success", f"Files merged successfully and saved at {merged_file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to merge files: {e}")

def retrieve_file_from_server(server_ip, server_port, file_name):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, server_port))

        # Send the file name to the server
        client_socket.sendall(file_name.encode())

        # Receive the file data
        file_data = b""
        while True:
            chunk = client_socket.recv(4096)
            if not chunk:
                break
            file_data += chunk

        client_socket.close()
        return file_data
    except Exception as e:
        messagebox.showerror("Error", f"Failed to retrieve file from {server_ip}:{server_port} - {e}")
        return None

# Add a "Merge Files" button to the UI
def add_merge_button():
    merge_button = ttk.Button(frame, text="Merge Files", command=merge_files)
    merge_button.pack(pady=10)

# UI Setup (same as your original code)
root = tk.Tk()
root.title("Advanced File Splitter with Load Balancing")
root.geometry("550x450")
root.configure(bg="#1E1E1E")  # Dark mode background

style = ttk.Style()
style.configure("TButton", font=("Arial", 12), padding=10)
style.configure("TLabel", font=("Arial", 11, "bold"), background="#1E1E1E", foreground="white")
style.configure("TFrame", background="#1E1E1E")

frame = ttk.Frame(root, padding=20)
frame.pack(expand=True, fill="both")

title_label = ttk.Label(frame, text="Advanced File Splitter with Load Balancing", font=("Arial", 16, "bold"))
title_label.pack(pady=10)

# Add the "Merge Files" button
add_merge_button()

root.mainloop()