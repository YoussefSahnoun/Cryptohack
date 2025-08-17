def recover_flag(output_lines):
    bits = []
    
    # Parse output.txt lines
    i = 0
    while i < len(output_lines):
        # Parse the public_key and ciphertext pairs
        if output_lines[i].startswith('(public_key='):
            i += 1
            if i < len(output_lines) and output_lines[i].startswith('(c1='):
                # Extract c2 from the line
                line = output_lines[i]
                c2_start = line.find('c2=') + 3
                c2_end = line.find(')', c2_start)
                c2_hex = line[c2_start:c2_end]
                c2 = int(c2_hex, 16)
                
                # Check if c2 is odd or even
                bit = c2 % 2
                bits.append(bit)
            i += 1
        else:
            i += 1
    
    # Reconstruct the flag
    flag_int = 0
    for bit in reversed(bits):  # Reverse since we're reading from LSB to MSB
        flag_int = (flag_int << 1) | bit
    
    # Convert integer back to bytes
    from Crypto.Util.number import long_to_bytes
    flag = long_to_bytes(flag_int)
    
    return flag

def main():
    with open("output.txt", 'r') as f:
        output_lines = f.read().splitlines()
    flag = recover_flag(output_lines)
    print(flag)

if __name__ == '__main__':
    main()