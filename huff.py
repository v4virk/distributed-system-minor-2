import heapq
from collections import defaultdict
import os
import PyPDF2
import zlib

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

def write_file(file_path, content):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def compress_file(file_path):
    with open(file_path, 'rb') as file:
        data = file.read()
    compressed_data = zlib.compress(data)
    compressed_file = file_path + ".gz"
    with open(compressed_file, 'wb') as file:
        file.write(compressed_data)
    print(f"Compressed file saved to {compressed_file}")

def decompress_file(compressed_file):
    with open(compressed_file, 'rb') as file:
        compressed_data = file.read()
    decompressed_data = zlib.decompress(compressed_data)
    decompressed_file = compressed_file.replace(".gz", "")
    with open(decompressed_file, 'wb') as file:
        file.write(decompressed_data)
    print(f"Decompressed file saved to {decompressed_file}")
    return decompressed_file

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
    while True:
        print("\nMenu:")
        print("1. Encode a file")
        print("2. Decode a file")
        print("3. Compress a file")
        print("4. Decompress a file")
        print("5. Exit")
        choice = input("Enter your choice: ")
        
        if choice == "1":
            input_file = input("Enter the input file path: ")
            encoded_file = "encoded.txt"
            try:
                text = read_file(input_file)
                encoded_text, tree = huffman_encoding(text)
                write_file(encoded_file, encoded_text)
                print(f"Encoded text saved to {encoded_file}")
            except Exception as e:
                print(f"An error occurred: {e}")
        
        elif choice == "2":
            encoded_file = input("Enter the encoded file path: ")
            decoded_file = "decoded.txt"
            try:
                encoded_text = read_file(encoded_file)
                decoded_text = huffman_decoding(encoded_text, tree)
                write_file(decoded_file, decoded_text)
                print(f"Decoded text saved to {decoded_file}")
            except Exception as e:
                print(f"An error occurred: {e}")
        
        elif choice == "3":
            file_to_compress = input("Enter the file path to compress: ")
            compress_file(file_to_compress)
        
        elif choice == "4":
            compressed_file = input("Enter the compressed file path: ")
            decompress_file(compressed_file)
        
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")
