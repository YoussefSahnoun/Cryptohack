

import sys, json, random, time
from pwn import remote
from fastecdsa.point import Point
from fastecdsa.curve import P256

Gx = int("6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296", 16)
Gy = int("4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5", 16)
G = Point(Gx, Gy, curve=P256)

MASK = (1 << (8 * 30)) - 1  # 240-bit mask
BASE = 37
class RNG:
    def __init__(self, seed, P, Q):
        self.seed = seed
        self.P = P
        self.Q = Q

    def next(self):
        t = self.seed
        s = (t * self.P).x
        self.seed = s
        r = (s * self.Q).x
        return r & (2**(8 * 30) - 1)


class Game:
    reds = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
    blacks = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}
    odds = {1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35}
    evens = {2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36}

    def __init__(self, P, Q):
        self.rng = RNG(random.getrandbits(60), P, Q)
        self.num_spins = None
        self.change_croupier()

    def rebase(self, n, b=37):
        if n < b:
            return [n]
        else:
            return [n % b] + self.rebase(n//b, b)

    def change_croupier(self):
        self.spins = self.rebase(self.rng.next())
        return len(self.spins)

    def spin_wheel(self):
        number = self.spins.pop()
        if self.spins == []:
            self.num_spins = self.change_croupier()

        return number

def unrebase(lst):
    n = 0
    print(lst[::-1])
    for i, digit in enumerate(lst[::-1]):
        n += digit * (37 ** i)
    return n
def send_json(rconn, obj):
    s = json.dumps(obj)
    print("-> sending:", s)
    rconn.sendline(s.encode())

def recv_json(rconn, timeout=20):
    start = time.time()
    while True:
        try:
            line = rconn.recvline(timeout=timeout)
        except EOFError:
            print("[!] EOF from remote")
            return None
        if not line:
            if time.time() - start > timeout:
                print("[!] recv timeout")
                return None
            continue
        s = line.decode(errors="replace").rstrip("\r\n")
        if not s:
            continue
        print("<- server:", s)
        if s and s[0] in "{[":
            try:
                obj = json.loads(s)
                return obj
            except Exception as e:
                print("[!] invalid JSON line:", e)
                continue




def find_full_seed_from_two_truncated_one_step(r1, r2, G_point, MASK, progress_step=0x1FFF):

    print("brute-forcing top 16 bits")
    for k in range(1 << 16):
        candidate = r1 + (k *(2 ** 240))
        p = candidate * G_point
        s3 = p.x
        if (s3 % (2**240)) == r2:
            print(f"found candidate k={k}")
            return candidate, k
    return None, None




def collect_two_consecutive_buffers(rconn, verbose=True):

    choices50 = ["EVEN", "ODD", "RED", "BLACK"]
    raw = []
    spins = []
    new_first = None
    if verbose: print("50/50 bets and collecting r1%(2**240) and r2%(2**240)")
    while True:
        send_json(rconn, {"choice": random.choice(choices50)})
        resp = recv_json(rconn)
        raw.append(resp)
        if "spin" in resp:
            spins.append(int(resp["spin"]))
        if "msg" in resp and "new croupier" in resp["msg"]:
            buf1 = spins[:]
            break
    spins2=[]
    if verbose: print("second r")
    while True:
        send_json(rconn, {"choice": random.choice(choices50)})
        resp = recv_json(rconn)

        raw.append(resp)
        if "spin" in resp:
            spins2.append(int(resp["spin"]))
        if "msg" in resp and "new croupier" in resp["msg"]:
        
            buf2 = spins2[:]
            break

    return buf1, buf2, raw

def main(host, port):
    print(f"connecting to {host}:{port}")
    r = remote(host, int(port))

    # register Q = G (as hex strings)
    send_json(r, {"x": "6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296", "y":"4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5"})
    reg = recv_json(r)
    if reg is None:
        print("[!] no registration response, exiting")
        return

    # collect buffers
    buf1, buf2, raw = collect_two_consecutive_buffers(r)
    print(buf1)
    print(len(buf1))
    print(buf2)
    print(len(buf2))
    # convert to integers to validate
    r1 = unrebase(buf1)
    r2 = unrebase(buf2)
    # printing number of bits to validate
    print(f"r1 = {r1}")
    print(len(bin(r1)[2:]))
    print(f"r2 = {r2}")
    print(len(bin(r2)[2:]))


    # brute force 16 unknown high bits
    s2_full, k = find_full_seed_from_two_truncated_one_step(r1, r2, G, MASK)
    if s2_full is None:
        print("Brute force failed — no candidate found")
        return

    print(f"Full s2 recovered: {s2_full}")
    print(f"k = {k}, s2_full hex = {s2_full:x}")

    recovered_rng = RNG(s2_full, G, G)
    predicted_game = Game(G, G)
    predicted_game.rng = recovered_rng
    predicted_game.spins = predicted_game.rebase(predicted_game.rng.next())
    predicted_game.num_spins = len(predicted_game.spins)

    print("Predicting and sending next spins to the server:")

    for i in range(len(predicted_game.spins)):
        spin = predicted_game.spin_wheel()
        print(f"Predicted spin {i+1}: {spin}")
        send_json(r, {"choice": spin})
        resp = recv_json(r)
        if "crypto" in resp:
            print("gg!")
            break

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 exploit_all_in_one.py HOST PORT")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
