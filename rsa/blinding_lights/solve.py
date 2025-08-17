#!/usr/bin/env python3
import json
from pwn import remote
from Crypto.Util.number import bytes_to_long
from pkcs1 import emsa_pkcs1_v15

def main(host, port):
    # Connect to the challenge server
    io = remote(host, port)

    # 0) Receive and discard the initial banner
    io.recvline(timeout=2)
    target="admin=True"
    # 1) Request the provided signature
    io.sendline(json.dumps({"option": "get_pubkey"}).encode())
    data = json.loads(io.recvline().strip())
    N = int(data['N'], 16)
    e = int(data['e'],16)
    io.sendline(json.dumps({"option": "sign","msg":hex(bytes_to_long(target.encode())+N)[2:]}).encode())
    data = json.loads(io.recvline().strip())
    target_signature=data['signature']
    io.sendline(json.dumps({"option": "verify","msg":hex(bytes_to_long(target.encode()))[2:],"signature":target_signature}).encode())
    data = json.loads(io.recvline().strip())
    print(data)

if __name__ == '__main__':
    main('socket.cryptohack.org', 13376)
