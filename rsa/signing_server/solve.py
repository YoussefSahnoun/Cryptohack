from pwn import *
from Crypto.Util.number import bytes_to_long
r=remote('socket.cryptohack.org',13374)
print(r.recv())
r.sendline(b'{"option":"get_pubkey"}')
pub=r.recvline()
r.sendline(b'{"option":"get_secret"}')
sec=r.recvline()
r.sendline(b'{"option":"sign","msg":"'+sec[12:-3]+b'"}')
sign=r.recvline()
print(sign[17:-3])
print(bytes.fromhex(sign[17:-3].decode()))
