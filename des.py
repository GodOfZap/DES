import textwrap

# ==========================================
# UTILITY FUNCTIONS
# ==========================================

def int_to_bin(number: int, block_size=8) -> str:
    binary = bin(number)[2:]
    return '0' * (block_size - len(binary)) + binary

def bytes_to_bin(b: bytes) -> str:
    return ''.join(format(byte, '08b') for byte in b)

def bin_to_bytes(binary: str) -> bytes:
    return bytes(int(binary[i:i+8], 2) for i in range(0, len(binary), 8))

def pad(b: bytes) -> bytes:
    padding_len = 8 - (len(b) % 8)
    return b + bytes([padding_len] * padding_len)

def unpad(b: bytes) -> bytes:
    padding_len = b[-1]
    return b[:-padding_len]

def left_circ_shift(binary: str, shift: int) -> str:
    shift = shift % len(binary)
    return binary[shift:] + binary[0: shift]

def format_bin(binary: str, chunk_size=8) -> str:
    """Helper to print binary strings with spaces for readability."""
    return ' '.join(binary[i:i+chunk_size] for i in range(0, len(binary), chunk_size))


# ==========================================
# PERMUTATION BOX (P-BOX)
# ==========================================

class PBox:
    def __init__(self, key: dict):
        self.key = key
        self.in_degree = len(key)
        self.out_degree = sum(len(value) if isinstance(value, list) else 1 for value in key.values())

    def permutate(self, sequence: str) -> str:
        result = [0] * self.out_degree
        for index, value in enumerate(sequence):
            if (index + 1) in self.key:
                indices = self.key.get(index + 1, [])
                indices = indices if isinstance(indices, list) else [indices]
                for i in indices:
                    result[i - 1] = value
        return ''.join(map(str, result))

    @staticmethod
    def from_list(permutation: list):
        mapping = {}
        for index, value in enumerate(permutation):
            indices = mapping.get(value, [])
            indices.append(index + 1)
            mapping[value] = indices
        return PBox(mapping)

    @staticmethod
    def des_initial_permutation():
        return PBox.from_list(
            [58, 50, 42, 34, 26, 18, 10, 2, 60, 52, 44, 36, 28, 20, 12, 4,
             62, 54, 46, 38, 30, 22, 14, 6, 64, 56, 48, 40, 32, 24, 16, 8,
             57, 49, 41, 33, 25, 17, 9, 1, 59, 51, 43, 35, 27, 19, 11, 3,
             61, 53, 45, 37, 29, 21, 13, 5, 63, 55, 47, 39, 31, 23, 15, 7]
        )

    @staticmethod
    def des_final_permutation():
        return PBox.from_list(
            [40, 8, 48, 16, 56, 24, 64, 32, 39, 7, 47, 15, 55, 23, 63, 31,
             38, 6, 46, 14, 54, 22, 62, 30, 37, 5, 45, 13, 53, 21, 61, 29,
             36, 4, 44, 12, 52, 20, 60, 28, 35, 3, 43, 11, 51, 19, 59, 27,
             34, 2, 42, 10, 50, 18, 58, 26, 33, 1, 41, 9, 49, 17, 57, 25]
        )

    @staticmethod
    def des_single_round_expansion():
        return PBox.from_list(
            [32, 1, 2, 3, 4, 5, 4, 5, 6, 7, 8, 9,
             8, 9, 10, 11, 12, 13, 12, 13, 14, 15, 16, 17,
             16, 17, 18, 19, 20, 21, 20, 21, 22, 23, 24, 25,
             24, 25, 26, 27, 28, 29, 28, 29, 30, 31, 32, 1]
        )

    @staticmethod
    def des_single_round_final():
        return PBox.from_list(
            [16, 7, 20, 21, 29, 12, 28, 17, 1, 15, 23, 26, 5, 18, 31, 10,
             2, 8, 24, 14, 32, 27, 3, 9, 19, 13, 30, 6, 22, 11, 4, 25]
        )

    @staticmethod
    def des_key_initial_permutation():
        return PBox.from_list(
            [57, 49, 41, 33, 25, 17, 9, 1, 58, 50, 42, 34, 26, 18,
             10, 2, 59, 51, 43, 35, 27, 19, 11, 3, 60, 52, 44, 36,
             63, 55, 47, 39, 31, 23, 15, 7, 62, 54, 46, 38, 30, 22,
             14, 6, 61, 53, 45, 37, 29, 21, 13, 5, 28, 20, 12, 4]
        )

    @staticmethod
    def des_shifted_key_permutation():
        return PBox.from_list(
            [14, 17, 11, 24, 1, 5, 3, 28, 15, 6, 21, 10, 23, 19, 12, 4,
             26, 8, 16, 7, 27, 20, 13, 2, 41, 52, 31, 37, 47, 55, 30, 40,
             51, 45, 33, 48, 44, 49, 39, 56, 34, 53, 46, 42, 50, 36, 29, 32]
        )

# ==========================================
# SUBSTITUTION BOX (S-BOX)
# ==========================================

class SBox:
    def __init__(self, table: dict, block_size=4, func=lambda binary: (binary[0] + binary[5], binary[1:5])):
        self.table = table
        self.block_size = block_size
        self.func = func

    def __call__(self, binary: str) -> str:
        a, b = self.func(binary)
        a, b = int(a, base=2), int(b, base=2)
        if (a, b) in self.table:
            return int_to_bin(self.table[(a, b)], block_size=self.block_size)
        return binary

    @staticmethod
    def from_list(sequence: list):
        mapping = {}
        for row in range(len(sequence)):
            for column in range(len(sequence[0])):
                mapping[(row, column)] = sequence[row][column]
        return SBox(table=mapping)

    @staticmethod
    def des_single_round_substitutions():
        return [
            SBox.des_s_box1(), SBox.des_s_box2(), SBox.des_s_box3(), SBox.des_s_box4(),
            SBox.des_s_box5(), SBox.des_s_box6(), SBox.des_s_box7(), SBox.des_s_box8()
        ]

    @staticmethod
    def des_s_box1():
        return SBox.from_list([
            [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
            [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
            [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
            [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]])

    @staticmethod
    def des_s_box2():
        return SBox.from_list([
            [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
            [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
            [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
            [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]])

    @staticmethod
    def des_s_box3():
        return SBox.from_list([
            [10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
            [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
            [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
            [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]])

    @staticmethod
    def des_s_box4():
        return SBox.from_list([
            [7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
            [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
            [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
            [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14]])

    @staticmethod
    def des_s_box5():
        return SBox.from_list([
            [2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
            [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
            [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
            [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]])

    @staticmethod
    def des_s_box6():
        return SBox.from_list([
            [12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
            [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
            [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
            [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]])

    @staticmethod
    def des_s_box7():
        return SBox.from_list([
            [4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
            [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
            [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
            [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12]])

    @staticmethod
    def des_s_box8():
        return SBox.from_list([
            [13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
            [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
            [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
            [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]])


# ==========================================
# THE CORE DES ALGORITHM WITH VISUALIZER
# ==========================================

class DES:
    def __init__(self, key: int):
        self.key = format(key, '064b')
        self.PC_1 = PBox.des_key_initial_permutation()
        self.PC_2 = PBox.des_shifted_key_permutation()
        self.IP = PBox.des_initial_permutation()
        self.FP = PBox.des_final_permutation()
        self.E_Box = PBox.des_single_round_expansion()
        self.P_Box_Round = PBox.des_single_round_final()
        self.single_shift = {1, 2, 9, 16}
        self.subkeys = self.generate_subkeys()

    def print_system_tables(self):
        """Displays the physical wiring tables used by DES."""
        print("\n" + "="*50)
        print("          DES SYSTEM WIRING TABLES")
        print("="*50)
        
        print("\n[Initial Permutation (IP)] - Scrambles 64-bit plaintext")
        print(textwrap.fill("58 50 42 34 26 18 10 2 60 52 44 36 28 20 12 4 62 54 46 38 30 22 14 6 64 56 48 40 32 24 16 8 57 49 41 33 25 17 9 1 59 51 43 35 27 19 11 3 61 53 45 37 29 21 13 5 63 55 47 39 31 23 15 7", width=60))

        print("\n[Expansion Box (E-Box)] - Duplicates edges to stretch 32->48 bits")
        print(textwrap.fill("32 1 2 3 4 5 4 5 6 7 8 9 8 9 10 11 12 13 12 13 14 15 16 17 16 17 18 19 20 21 20 21 22 23 24 25 24 25 26 27 28 29 28 29 30 31 32 1", width=60))
        
        print("\n[Substitution Box 1 (S-Box 1)] - Non-linear compression 6->4 bits")
        print("  14  4 13  1  2 15 11  8  3 10  6 12  5  9  0  7")
        print("   0 15  7  4 14  2 13  1 10  6 12 11  9  5  3  8")
        print("   4  1 14  8 13  6  2 11 15 12  9  7  3 10  5  0")
        print("  15 12  8  2  4  9  1  7  5 11  3 14 10  0  6 13")
        print("  *(8 unique S-Boxes are used in total)*")

        print("\n[Straight P-Box] - Shuffles 32 bits after S-Boxes")
        print(textwrap.fill("16 7 20 21 29 12 28 17 1 15 23 26 5 18 31 10 2 8 24 14 32 27 3 9 19 13 30 6 22 11 4 25", width=60))
        print("="*50 + "\n")

    def generate_subkeys(self) -> list:
        subkeys = []
        k = self.PC_1.permutate(self.key)
        l, r = k[0:28], k[28:]
        for i in range(1, 17):
            shift = 1 if i in self.single_shift else 2
            l = left_circ_shift(l, shift)
            r = left_circ_shift(r, shift)
            subkeys.append(self.PC_2.permutate(l + r))
        return subkeys

    def feistel_function(self, right_half: str, subkey: str, round_num: int, verbose=False) -> str:
        # 1. Expand
        expanded = self.E_Box.permutate(right_half)
        if verbose:
            print(f"      -> [E-Box] Expanded R to 48-bit: {format_bin(expanded, 6)}")
        
        # 2. XOR with Key
        xored = format(int(expanded, 2) ^ int(subkey, 2), '048b')
        if verbose:
            print(f"      -> [Key]   XOR with Subkey K{round_num}: {format_bin(xored, 6)}")
        
        # 3. Substitute
        s_boxes = SBox.des_single_round_substitutions()
        substituted = ""
        for i in range(8):
            substituted += s_boxes[i](xored[i * 6 : (i + 1) * 6])
        if verbose:
            print(f"      -> [S-Box] Compressed to 32-bit: {format_bin(substituted, 4)}")
            
        # 4. Permutate
        pboxed = self.P_Box_Round.permutate(substituted)
        if verbose:
            print(f"      -> [P-Box] Shuffled 32-bit     : {format_bin(pboxed, 4)}")
            
        return pboxed

    def process_block(self, block: str, encrypt=True, verbose=False) -> str:
        # Initial Permutation
        block = self.IP.permutate(block)
        l, r = block[:32], block[32:]
        
        if verbose:
            print(f"\n[!] Initial Permutation (IP) applied to block.")
            print(f"    L0: {format_bin(l, 8)}")
            print(f"    R0: {format_bin(r, 8)}\n")

        keys = self.subkeys if encrypt else self.subkeys[::-1]
        
        # 16 Rounds
        for i in range(16):
            if verbose: print(f"--- ROUND {i+1} START ---")
            
            # f-function
            f_result = self.feistel_function(r, keys[i], i+1, verbose)
            
            # XOR with Left Half
            new_r = format(int(l, 2) ^ int(f_result, 2), '032b')
            if verbose:
                print(f"      -> [XOR]   L{i} XOR f-result    : {format_bin(new_r, 4)}")
                print(f"      -> [SWAP]  L becomes R, R becomes L")
            
            l = r
            r = new_r
            
            if verbose:
                print(f"    L{i+1}: {format_bin(l, 8)}")
                print(f"    R{i+1}: {format_bin(r, 8)}\n")
            
        # Final Swap & Final Permutation
        if verbose: print(f"[!] Reversing final swap and applying Final Permutation (FP)...")
        pre_output = r + l
        return self.FP.permutate(pre_output)

    def encrypt_message(self, plaintext: str) -> str:
        byte_text = plaintext.encode('utf-8')
        padded_bytes = pad(byte_text)
        binary_text = bytes_to_bin(padded_bytes)
        ciphertext = ""
        
        total_blocks = len(binary_text) // 64
        print(f"\n>> Message split into {total_blocks} block(s) of 64 bits.")
        print(f">> (PKCS#7 Padding added to fill missing bytes)")
        
        for idx in range(0, len(binary_text), 64):
            block = binary_text[idx:idx+64]
            # ONLY trace the first block so we don't spam the console infinitely
            is_verbose = (idx == 0)
            
            if is_verbose:
                print(f"\n{'='*40}\nTRACING BLOCK 1 ENCRYPTION\n{'='*40}")
                print(f"Original 64-bit block: {format_bin(block, 8)}")
                
            ciphertext += self.process_block(block, encrypt=True, verbose=is_verbose)
            
        return hex(int(ciphertext, 2))[2:]

    def decrypt_message(self, hex_ciphertext: str) -> str:
        binary_cipher = format(int(hex_ciphertext, 16), f'0{len(hex_ciphertext)*4}b')
        decrypted_binary = ""
        
        for i in range(0, len(binary_cipher), 64):
            block = binary_cipher[i:i+64]
            # Turn verbose OFF for decryption to keep console clean
            decrypted_binary += self.process_block(block, encrypt=False, verbose=False)
            
        decrypted_bytes = bin_to_bytes(decrypted_binary)
        unpadded_bytes = unpad(decrypted_bytes)
        return unpadded_bytes.decode('utf-8')


# ==========================================
# USER INPUT & EXECUTION
# ==========================================

if __name__ == "__main__":
    print("========================================")
    print("      DATA ENCRYPTION STANDARD (DES)")
    print("========================================")
    
    # 1. Get Text Input
    msg = input("\nEnter message to encrypt (e.g., 'hello world'):\n> ")
    if not msg: msg = "hello world"
    
    # 2. Get Key Input
    key_input = input("\nEnter a 16-digit integer key (Press Enter for default: 1234567890123456):\n> ")
    try:
        my_secret_key = int(key_input)
    except ValueError:
        print("Using default key: 1234567890123456")
        my_secret_key = 1234567890123456 

    # 3. Initialize DES and Print Setup
    des_cipher = DES(key=my_secret_key)
    des_cipher.print_system_tables()

    print("\n" + "▼"*40)
    print("           DES ENCRYPTION START")
    print("▼"*40)
    print(f"\nOriginal String: {msg}")
    
    # 4. Encrypt and show steps
    encrypted_hex = des_cipher.encrypt_message(msg)
    
    print("\n" + "="*50)
    print(f"FINAL Encrypted Ciphertext (Hex Format):\n{encrypted_hex}")
    print("="*50 + "\n")
    
    # 5. Decrypt to verify
    print("Attempting to decrypt the Hex string back to text...")
    decrypted_str = des_cipher.decrypt_message(encrypted_hex)
    print(f"\nDecrypted String: {decrypted_str}")
    
    print("\n--- PROCESS COMPLETE ---")