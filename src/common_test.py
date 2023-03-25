def reflect(v, bitwidth):
    nv = 0
    for i in range(bitwidth):
        if v & (1 << i):
            nv |= 1 << (bitwidth - i - 1)

    return nv
