import numpy as np
from Crypto.Util.number import isPrime
import random
import string
from  pwn import *
p=remote('socket.cryptohack.org',13400)
allowed_chars = string.ascii_letters + string.digits + "_"

def generate_nonsense_password(length=10):
    return ''.join(random.choice(allowed_chars) for _ in range(length))

if __name__ == "__main__":
    password = ""
    array = np.array(list(map(ord, password)))
    while not (isPrime(int(array.prod())) and isPrime(int(array.sum()))):
    	password = generate_nonsense_password(11)
    	a=[ord(i) for i in password]
    	array = np.array(list(map(ord, password)))
    	print(f"Nonsense Password: {password}")
    print("Found password:", password)
    p.recv()
    p.sendline(b'{"password":"'+password.encode()+b'"}')
    print(p.recv())
