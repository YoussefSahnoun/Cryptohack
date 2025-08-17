#!/usr/bin/env python3
from gmpy2 import iroot
from Crypto.PublicKey import RSA
from Crypto.Util.number import bytes_to_long,inverse,long_to_bytes

FLAG = b"crypto{test_flagaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa}"


def pad100(msg):
    return msg + b'\x00' * (100 - len(msg))


key = RSA.generate(1024, e=3)
n, e = key.n, key.e
print(bin(bytes_to_long(pad100(FLAG))))  
m = bytes_to_long(pad100(FLAG))
c = pow(m, e, n)

print(f"n = {n}")
print(f"e = {e}")
print(f"c = {c}")
m0=c*inverse(2**(8*3*(100-len(FLAG))),n) % n
print("m0:",m0)
print(iroot(m0+3*n,3))
