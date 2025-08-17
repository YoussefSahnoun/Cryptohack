from pwn import remote
import json
from sympy import symbols, Poly, gcd
from Crypto.Util.number import long_to_bytes

# Remote server details
HOST = 'socket.cryptohack.org'
PORT = 13386


def get_two_encryptions():

    io = remote(HOST, PORT)

    io.recvline()

    request = {"option": "get_flag"}


    io.sendline(json.dumps(request).encode())
    resp1 = json.loads(io.recvline().strip().decode())
    a1, b1 = resp1['padding']
    c1     = resp1['encrypted_flag']
    N      = resp1['modulus']

    io.sendline(json.dumps(request).encode())
    resp2 = json.loads(io.recvline().strip().decode())
    a2, b2 = resp2['padding']
    c2     = resp2['encrypted_flag']

    io.close()
    return (a1, b1, c1, a2, b2, c2, N)


if __name__ == '__main__':
  
    a1, b1, c1, a2, b2, c2, N = get_two_encryptions()

    x  = symbols('x')
    g1 = Poly((a1*x + b1)**11 - c1, x, modulus=N)
    g2 = Poly((a2*x + b2)**11 - c2, x, modulus=N)

    G = gcd(g1, g2)
    print(G)
    if G.degree() != 1:
        raise RuntimeError(f"Unexpected GCD degree {G.degree()}")

    coeffs = G.all_coeffs() 
    m = (-coeffs[1]) % N

    flag = long_to_bytes(m)
    print(flag.decode())
