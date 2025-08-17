#!/usr/bin/env python3
import json
from pwn import remote
from Crypto.Util.number import bytes_to_long
from pkcs1 import emsa_pkcs1_v15

def main(host, port):

    io = remote(host, port)


    io.recvline(timeout=2)

    io.sendline(json.dumps({"option": "get_signature"}).encode())
    data = json.loads(io.recvline().strip())
    S = int(data['signature'], 16)


    msg = "I am Mallory and I own CryptoHack.org"
    padded = emsa_pkcs1_v15.encode(msg.encode(), 256)
    D = bytes_to_long(padded)

    e2 = 1
    n2 = S - D

    assert pow(S, e2, n2) == D, "Failed sanity check for e=1, n = S - D"

    assert n2 > D, "n must be greater than D"


    payload = {
        "option": "verify",
        "msg": msg,
        "N": hex(n2),
        "e": hex(e2)
    }
    io.sendline(json.dumps(payload).encode())

    print(io.recvline().decode().strip())
    io.close()

if __name__ == '__main__':
    main('socket.cryptohack.org', 13391)
