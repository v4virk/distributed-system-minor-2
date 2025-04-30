from tkinter import Tk, filedialog, messagebox, Text, Scrollbar, END, Frame, Canvas, Label
from tkinter import StringVar
from tkinter import ttk
import socket, os, subprocess, time, threading, json
from cryptography.fernet import Fernet
import random
import subprocess  # Used to run other Python files
import sys
# Ports and file setup
ports = [(8081, 8082), (8082, 8083), (8083, 8081)]
host = "127.0.0.1"
file_parts = ["client_part1.dat", "client_part2.dat", "client_part3.dat"]
output_file = "reconstructed_sample.txt"
metadata_file = "file_metadata.json"
transfer_log_file = "transfer_log.json"  # NEW: For transfer logging
selected_file = ""
fernet = None
stop_animation = False
load_balancer_counter = 0

def log(message):
    txt_log.config(state="normal")
    txt_log.insert(END, f"{message}\n")
    txt_log.see(END)
    txt_log.config(state="disabled")

def generate_key():
    global fernet
    key = Fernet.generate_key()
    with open("encryption.key", "wb") as kf:
        kf.write(key)
    fernet = Fernet(key)
    lbl_key.set("✨🔑 Key saved: encryption.key")
    sparkle_animation()
    log("🔐 Encryption key generated and saved.")

def select_file():
    global selected_file
    selected_file = filedialog.askopenfilename()
    if selected_file:
        lbl_file.set(f"📁 {os.path.basename(selected_file)}")
        log(f"📁 Selected file: {selected_file}")

def sparkle_animation():
    for _ in range(10):
        x = random.randint(100, 500)
        y = random.randint(50, 300)
        spark = canvas.create_text(x, y, text="✨", font=("Segoe UI", 16))
        root.after(300, lambda s=spark: canvas.delete(s))

def split_and_encrypt_file():
    if not selected_file:
        messagebox.showwarning("No file", "Please select a file.")
        return
    with open(selected_file, "rb") as f:
        data = f.read()
    part_size = len(data) // 3
    parts = [data[:part_size], data[part_size:part_size*2], data[part_size*2:]]
    for i in range(3):
        encrypted = fernet.encrypt(parts[i])
        with open(file_parts[i], "wb") as pf:
            pf.write(encrypted)
        fly_file_part(f"📦 Part {i+1}")
    log("🔐 File split and encrypted.")

def fly_file_part(label_text):
    label = Label(canvas, text=label_text, bg="#f0f4f7", font=("Segoe UI", 10, "bold"))
    label.place(x=20, y=500)
    def move():
        for i in range(30):
            label.place_configure(x=20 + i*10, y=500 - i*5)
            time.sleep(0.03)
        label.destroy()
    threading.Thread(target=move).start()

def choose_port(index):
    global load_balancer_counter
    main_port, replica_port = ports[index]
    chosen = main_port if load_balancer_counter % 2 == 0 else replica_port
    load_balancer_counter += 1
    return chosen

def send_file_to_server(port, filename):
    try:
        with open(filename, "rb") as f:
            data = f.read()
        s = socket.socket()
        s.connect((host, port))
        s.send(b"PUT")
        s.send(len(filename.encode()).to_bytes(4, 'big'))
        s.send(filename.encode())
        s.send(len(data).to_bytes(4, 'big'))
        s.sendall(data)
        s.close()
        log(f"✅ Sent {filename} to port {port}")

        store_metadata(filename, "client", port)
        store_transfer_log(filename, port)  # NEW

    except Exception as e:
        log(f"❌ Sending to port {port} failed: {e}")

def store_transfer_log(filename, port):
    transfer_log = []
    if os.path.exists(transfer_log_file):
        with open(transfer_log_file, "r") as f:
            transfer_log = json.load(f)

    transfer_log.append({
        "filename": filename,
        "port": port,
        "timestamp": time.ctime()
    })

    with open(transfer_log_file, "w") as f:
        json.dump(transfer_log, f, indent=4)

def retrieve_file_from_server(port, filename):
    try:
        s = socket.socket()
        s.connect((host, port))
        s.send(b"GET")
        s.send(len(filename.encode()).to_bytes(4, 'big'))
        s.send(filename.encode())
        size = int.from_bytes(s.recv(4), 'big')
        if size == 0:
            log(f"⚠️ {filename} not found at port {port}")
            return None
        data = b''
        while len(data) < size:
            chunk = s.recv(4096)
            if not chunk:
                break
            data += chunk
        s.close()
        log(f"📥 Retrieved {filename} from port {port}")
        store_metadata(filename, port, "client")
        return data
    except Exception as e:
        log(f"❌ Retrieval from port {port} failed: {e}")
        return None

def store_metadata(filename, src, dest):
    metadata = {}
    if os.path.exists(metadata_file):
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
    metadata[filename] = metadata.get(filename, [])
    metadata[filename].append({"from": src, "to": dest, "timestamp": time.ctime()})
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=4)

def merge_and_decrypt_files():
    merged = b''
    for filename in file_parts:
        index = file_parts.index(filename)
        main_port, replica_port = ports[index]
        port_to_use = choose_port(index)
        encrypted_data = retrieve_file_from_server(port_to_use, filename)
        if not encrypted_data:
            log(f"⚠️ Main server failed. Trying replica for {filename}...")
            encrypted_data = retrieve_file_from_server(replica_port, filename)
            if not encrypted_data:
                log(f"❌ Both main and replica failed for {filename}")
                return

        try:
            decrypted = fernet.decrypt(encrypted_data)
            merged += decrypted
        except Exception as e:
            log(f"❌ Decryption error for {filename}: {e}")
            return

    with open(output_file, "wb") as out:
        out.write(merged)
    log(f"✅ File reconstructed as {output_file}")
    messagebox.showinfo("Success", f"Reconstructed: {output_file}")

def send_and_reconstruct():
    if not selected_file:
        messagebox.showwarning("No file", "Please select a file.")
        return

    def process():
        global stop_animation
        stop_animation = False
        threading.Thread(target=animate_status, args=("🔁 Working",)).start()
        progress["value"] = 0
        generate_key()
        update_progress(15)
        time.sleep(0.5)

        split_and_encrypt_file()
        update_progress(30)
        time.sleep(0.5)

        for i in range(3):
            main_port, replica_port = ports[i]
            send_file_to_server(main_port, file_parts[i])
            send_file_to_server(replica_port, file_parts[i])
            update_progress(50 + (i+1)*10)
            time.sleep(0.5)

        merge_and_decrypt_files()
        update_progress(100)
        stop_animation = True
        lbl_status.set("✅ Done!")
        log("🎉 All operations completed successfully.")

    threading.Thread(target=process).start()

def animate_status(msg):
    i = 0
    while not stop_animation:
        lbl_status.set(msg + "." * (i % 4))
        time.sleep(0.5)
        i += 1

def update_progress(value):
    progress["value"] = value
    root.update_idletasks()

def reset_ui():
    global selected_file, stop_animation
    selected_file = ""
    lbl_file.set("No file selected.")
    lbl_key.set("")
    lbl_status.set("")
    txt_log.config(state="normal")
    txt_log.delete(1.0, END)
    txt_log.config(state="disabled")
    progress["value"] = 0
    stop_animation = True
    log("🔄 Reset complete.")

def open_output_file():
    if os.path.exists(output_file):
        subprocess.Popen(["notepad", output_file])
    else:
        messagebox.showwarning("Missing", "No reconstructed file found.")

def logs_ui():
    

        # Now open adv2_ui.py
        subprocess.run([sys.executable, "logs_ui.py"])

# Function to handle console commands
def handle_console_input(event=None):
    command = console_input.get("1.0", END).strip().lower()
    console_input.delete("1.0", END)

    if command == "generate_key":
        generate_key()
    elif command == "select_file":
        select_file()
    elif command == "split_by_nodes":
        split_and_encrypt_file()
    elif command == "distribute_file":
        send_and_reconstruct()
    elif command == "reconstruct_file":
        open_output_file()
    elif command == "reset_ui":
        reset_ui()
    elif command == "exit":
        root.quit()
    elif command == "help":
        log("Commands:\n"
            "generate_key\nselect_file\nsplit_by_nodes\ndistribute_file\nreconstruct_file\nreset_ui\nexit\nhelp")
    else:
        log(f"Unknown command: {command}")
    

# GUI Setup
root = Tk()
root.title("🔐 Secure File Splitter & Rebuilder")
root.geometry("700x700")
root.configure(bg="#f0f4f7")

canvas = Canvas(root, width=700, height=100, bg="#f0f4f7", highlightthickness=0)
canvas.pack()

style = ttk.Style(root)
style.theme_use("clam")
style.configure("TButton", font=("Segoe UI", 10), padding=6)
style.configure("TLabel", font=("Segoe UI", 11))
style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"))

lbl_file = StringVar(value="No file selected.")
lbl_key = StringVar()
lbl_status = StringVar()

frame_top = Frame(root, bg="#f0f4f7")
frame_top.pack(pady=5)

ttk.Label(frame_top, text="📦 DISTRIBUTED SYSTEM", style="Header.TLabel").pack()

ttk.Label(root, textvariable=lbl_file, foreground="blue").pack(pady=5)
ttk.Label(root, textvariable=lbl_key, foreground="green").pack()
ttk.Label(root, textvariable=lbl_status, foreground="darkgreen", font=("Segoe UI", 10, "italic")).pack(pady=5)

ttk.Button(root, text="📁 Select File", command=select_file).pack(pady=5)
ttk.Button(root, text="📁 See index of transfers", command=logs_ui).pack(pady=5)
ttk.Button(root, text="🔄 Encrypt & Reconstruct", command=send_and_reconstruct).pack(pady=5)
ttk.Button(root, text="📂 Open Reconstructed File", command=open_output_file).pack(pady=5)

progress = ttk.Progressbar(root, length=500, mode='determinate')
progress.pack(pady=10)

frame_bottom = Frame(root, bg="#f0f4f7")
frame_bottom.pack(pady=10)
ttk.Button(frame_bottom, text="🔁 Reset", command=reset_ui).pack(side="left", padx=10)
ttk.Button(frame_bottom, text="❌ Exit", command=root.quit).pack(side="left", padx=10)

console_label = Label(root, text="🖥️ Command Console", font=("Segoe UI", 14), bg="#f0f4f7")
console_label.pack(pady=10)

console_input = Text(root, height=4, wrap="word", font=("Courier New", 12))
console_input.pack(fill="x", padx=10)
console_input.bind("<Return>", handle_console_input)

txt_log = Text(root, height=10, wrap="word", font=("Courier New", 12), state="disabled")
txt_log.pack(fill="x", padx=10, pady=5)

root.mainloop()
