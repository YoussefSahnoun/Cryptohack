
def inv_mod(x: int, p: int) -> int:
    """
    Modular inverse of x mod p. Raises ValueError if x is 0 mod p.
    """
    if x % p == 0:
        raise ValueError("No inverse exists for 0")
    # Python 3.8+: pow(x, -1, p) also works
    return pow(x, p-2, p)

def ec_add(P, Q, a, p):
    """
    Add two points P and Q on the elliptic curve y^2 = x^3 + a x + b over F_p.
    - P, Q: either a tuple (x, y) or None representing the point at infinity.
    - a: the curve parameter 'a'.
    - p: the prime modulus.
    Returns: P + Q as either (x3, y3) or None.
    """
    # (a) identity cases
    if P is None:
        return Q
    if Q is None:
        return P

    x1, y1 = P
    x2, y2 = Q

    # (d) P = -Q ⇒ result is O
    if x1 == x2 and (y1 + y2) % p == 0:
        return None

    # (e) choose slope λ
    if P != Q:
        # (e1) distinct points
        num   = (y2 - y1) % p
        denom = (x2 - x1) % p
    else:
        # (e2) doubling
        num   = (3 * x1 * x1 + a) % p
        denom = (2 * y1) % p

    # λ = num * denom^{-1} mod p
    try:
        lam = (num * inv_mod(denom, p)) % p
    except ValueError:
        # denominator = 0 mod p ⇒ vertical tangent ⇒ point at infinity
        return None

    # (f) x3 = λ^2 − x1 − x2  mod p
    x3 = (lam * lam - x1 - x2) % p
    # (h) y3 = λ (x1 − x3) − y1 mod p
    y3 = (lam * (x1 - x3) - y1) % p

    return (x3, y3)


# Example usage:
if __name__ == "__main__":
    # Curve: y^2 = x^3 + 497 x + 1768 over F_9739
    a = 497
    p_mod = 9739

    P = (493,5564)
    Q = (1539,4742)
    R =(4403,5202)  

    print(ec_add(ec_add(ec_add(P,P,a,p_mod),Q,a,p_mod),R,a,p_mod),a,p_mod)