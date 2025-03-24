import heapq
from collections import defaultdict
import os
import PyPDF2
import zlib
import pickle
from cryptography.fernet import Fernet

def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    return open("secret.key", "rb").read()

def encrypt_data(data, key):
    cipher = Fernet(key)
    return cipher.encrypt(data)

def decrypt_data(encrypted_data, key):
    cipher = Fernet(key)
    return cipher.decrypt(encrypted_data)

def read_file(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == ".txt":
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    elif file_extension == ".pdf":
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = "".join(page.extract_text() or "" for page in reader.pages)
            return text
    else:
        raise ValueError("Unsupported file format. Only .txt and .pdf are supported.")

def write_binary_file(file_path, content):
    with open(file_path, 'wb') as file:
        file.write(content)

def read_binary_file(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{file_path}' not found.")
    with open(file_path, 'rb') as file:
        return file.read()

def write_text_file(file_path, content):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def compress_data(data):
    return zlib.compress(data.encode())

def decompress_data(compressed_data):
    return zlib.decompress(compressed_data).decode()

class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None
    
    def __lt__(self, other):
        return self.freq < other.freq

def build_huffman_tree(text):
    frequency = defaultdict(int)
    for char in text:
        frequency[char] += 1
    
    priority_queue = [HuffmanNode(char, freq) for char, freq in frequency.items()]
    heapq.heapify(priority_queue)
    
    while len(priority_queue) > 1:
        left = heapq.heappop(priority_queue)
        right = heapq.heappop(priority_queue)
        
        merged = HuffmanNode(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        
        heapq.heappush(priority_queue, merged)
    
    return priority_queue[0]

def generate_huffman_codes(root, current_code="", code_map={}):
    if root is None:
        return
    
    if root.char is not None:
        code_map[root.char] = current_code
    
    generate_huffman_codes(root.left, current_code + "0", code_map)
    generate_huffman_codes(root.right, current_code + "1", code_map)
    
    return code_map

def huffman_encoding(text):
    root = build_huffman_tree(text)
    huffman_codes = generate_huffman_codes(root)
    
    encoded_text = "".join(huffman_codes[char] for char in text)
    return encoded_text, root

def huffman_decoding(encoded_text, root):
    decoded_text = ""
    current_node = root
    
    for bit in encoded_text:
        current_node = current_node.left if bit == "0" else current_node.right
        if current_node.char is not None:
            decoded_text += current_node.char
            current_node = root
    
    return decoded_text

# Menu-driven approach
if __name__ == "__main__":
    generate_key()  # Ensure encryption key exists
    key = load_key()
    
    while True:
        print("\nMenu:")
        print("1. Encode and Encrypt a file")
        print("2. Decrypt and Decode a file")
        print("3. Exit")
        choice = input("Enter your choice: ")
        
        if choice == "1":
            input_file = input("Enter the input file path: ").strip()
            encrypted_file = "encoded_encrypted.bin"
            tree_file = "huffman_tree.pkl"
            try:
                text = read_file(input_file)
                encoded_text, tree = huffman_encoding(text)
                encrypted_text = encrypt_data(encoded_text.encode(), key)
                write_binary_file(encrypted_file, encrypted_text)
                with open(tree_file, 'wb') as f:
                    pickle.dump(tree, f)
                print(f"Encrypted Huffman encoded file saved to {encrypted_file}")
            except Exception as e:
                print(f"An error occurred: {e}")
        
        elif choice == "2":
            encrypted_file = input("Enter the encrypted file path: ").strip()
            tree_file = "huffman_tree.pkl"
            output_file = "decrypted_output.txt"
            try:
                encrypted_text = read_binary_file(encrypted_file)
                decoded_text = decrypt_data(encrypted_text, key).decode()
                with open(tree_file, 'rb') as f:
                    tree = pickle.load(f)
                original_text = huffman_decoding(decoded_text, tree)
                write_text_file(output_file, original_text)
                print(f"Decrypted and decoded text saved to {output_file}")
            except FileNotFoundError as e:
                print(f"Error: {e}")
            except Exception as e:
                print(f"An error occurred: {e}")
        
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")