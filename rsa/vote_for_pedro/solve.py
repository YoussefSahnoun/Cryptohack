from Crypto.Util.number import bytes_to_long, long_to_bytes

# Inputs (replace N if different)
target = b'VOTE FOR PEDRO'
N = 22266616657574989868109324252160663470925207690694094953312891282341426880506924648525181014287214350136557941201445475540830225059514652125310445352175047408966028497316806142156338927162621004774769949534239479839334209147097793526879762417526445739552772039876568156469224491682030314994880247983332964121759307658270083947005466578077153185206199759569902810832114058818478518470715726064960617482910172035743003538122402440142861494899725720505181663738931151677884218457824676140190841393217857683627886497104915390385283364971133316672332846071665082777884028170668140862010444247560019193505999704028222347577
e = 3

def find_cube_with_suffix(target_bytes):
    L = len(target_bytes)
    tgt_int = bytes_to_long(target_bytes)

    # find solution modulo 256 (one byte)
    mod = 256
    tgt_mod = tgt_int % mod
    k = None
    for a in range(mod):
        if (a**3) % mod == tgt_mod:
            k = a
            break
    if k is None:
        return None

    # lift byte-by-byte: each step extends modulus to 256**r and tries 256 candidates
    for r in range(2, L+1):
        mod = 256**r
        tgt_mod = tgt_int % mod
        base = 256**(r-1)
        found = False
        for s in range(256):
            kcand = k + s * base
            if (kcand**3) % mod == tgt_mod:
                k = kcand
                found = True
                break
        if not found:
            return None

    m = k**3
    # verify suffix and that cube < N (so pow(k,3,N) == m)
    if m % (256**L) != tgt_int % (256**L):
        return None
    if m >= N:
        return None
    return k, m

res = find_cube_with_suffix(target)
if res:
    k, m = res
    print("Found k =", k)
    print("k^3 =", m)
    print("k hex (to submit):", hex(k)[2:])
    # show that bytes end with the target
    print("last bytes:", long_to_bytes(m)[-len(target):])
else:
    print("No solution found")
