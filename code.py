seed = 68648
i = 0

def generate_code():
    """Basic linear congruential generator"""
    global i 
    n = seed + 41055 * i 
    i += 1 
    g = [7, 5, 15, 19]
    d = []
    for _ in range(4):
        d.append(int(n % 26))
        n //= 26 
    return ''.join(chr(((g[i]*d[i]) % 26) + 65) for i in range(4))
