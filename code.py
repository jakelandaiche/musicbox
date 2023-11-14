#!/usr/bin/env python3

seed = 68648

def code():
    global seed
    seed = 68648 + 36225 * seed
    g = [7, 5, 13, 19]
    d = []
    n = seed
    for _ in range(4):
        d.append(int(n % 26))
        n //= 26 
    return ''.join(chr(((g[i]*d[i]) % 26) + 65) for i in range(4))
