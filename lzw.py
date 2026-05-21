MAX_DICT_SIZE = 4096


def lzw_compress(data):
    if not data:
        return []

    dictionary = {bytes([i]): i for i in range(256)}
    next_code = 256

    codes = []
    p = bytes([data[0]])
    for i in range(1, len(data)):
        c = bytes([data[i]])
        pc = p + c
        if pc in dictionary:
            p = pc
        else:
            codes.append(dictionary[p])
            if next_code < MAX_DICT_SIZE:
                dictionary[pc] = next_code
                next_code += 1
            p = c

    codes.append(dictionary[p])
    return codes
