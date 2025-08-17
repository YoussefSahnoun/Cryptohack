# find_px.py
nums = [588, 665, 216, 113, 642, 4, 836, 114, 851, 492, 819, 237]

def is_prime(n):
    if n < 2: return False
    if n % 2 == 0: return n == 2
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True

def egcd(a, b):
    """Extended gcd: returns (g, x, y) with g = gcd(a,b) and ax + by = g."""
    if b == 0:
        return (a, 1, 0)
    g, x1, y1 = egcd(b, a % b)
    return (g, y1, x1 - (a // b) * y1)

def modinv(a, m):
    """Return inverse of a mod m, or None if not invertible."""
    a %= m
    g, x, _ = egcd(a, m)
    if g != 1:
        return None
    return x % m

def find_px(nums, p_min=100, p_max=999):
    results = []
    lower_p = max(max(nums) + 1, p_min)  # residues must be < p
    for p in range(lower_p, p_max + 1):
        if not is_prime(p):
            continue

        # find first index i where nums[i] is invertible mod p
        inv_index = None
        for i, v in enumerate(nums[:-1]):
            if egcd(v, p)[0] == 1:
                inv_index = i
                break
        if inv_index is None:
            continue

        # candidate x from that invertible consecutive pair
        inv_v = modinv(nums[inv_index], p)
        x_cand = (nums[inv_index + 1] * inv_v) % p

        # verify all successive relations hold: nums[i]*x ≡ nums[i+1] (mod p)
        ok = True
        for i in range(len(nums) - 1):
            if (nums[i] * x_cand) % p != nums[i + 1]:
                ok = False
                break
        if not ok:
            continue

        # find smallest t >= 0 with x^t ≡ nums[0] (mod p) by brute force
        powv = 1
        t = None
        for e in range(0, p):   # at most p-1 needed
            if powv == nums[0] % p:
                t = e
                break
            powv = (powv * x_cand) % p

        results.append((p, x_cand, t))
    return results

if __name__ == "__main__":
    sol = find_px(nums)
    if sol:
        for p, x, t in sol:
            print("Found p =", p, "x =", x, "t =", t)
    else:
        print("No solution found in the given prime range.")
