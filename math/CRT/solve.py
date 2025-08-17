def chinese_remainder(n, a):
    """Solve x ≡ a[i] (mod n[i]) using the Chinese Remainder Theorem."""
    from functools import reduce

    def mul_inv(a, m):
        """Modular inverse using Extended Euclidean Algorithm."""
        m0, x0, x1 = m, 0, 1
        while a > 1:
            q = a // m
            a, m = m, a % m
            x0, x1 = x1 - q * x0, x0
        return x1 + m0 if x1 < 0 else x1

    N = reduce(lambda x, y: x * y, n)  # product of all moduli
    result = 0
    for ni, ai in zip(n, a):
        Ni = N // ni
        yi = mul_inv(Ni, ni)
        result += ai * Ni * yi
    return result % N


n = [5, 11, 17]   # moduli
a = [2, 3, 5]     # remainders

solution = chinese_remainder(n, a)
print("x ≡", solution, "(mod", 5*11*17, ")")
