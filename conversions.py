def convert_to_grayscale(matrix):
    # Conversie la tonuri de gri prin media aritmetica a canalelor R, G, B
    height = len(matrix)
    width = len(matrix[0])
    grayscale_matrix = []
    for y in range(height):
        row = []
        for x in range(width):
            r, g, b = matrix[y][x]
            gray = int((r + g + b) / 3)
            row.append([gray, gray, gray])
        grayscale_matrix.append(row)
    return grayscale_matrix


def get_grayscale_variations(matrix):
    # Returneaza 3 variante de grayscale:
    # v1 - media aritmetica: (R+G+B)/3
    # v2 - luminanta: formula ITU-R BT.601 (perceptuala)
    # v3 - desaturare: (max(R,G,B) + min(R,G,B)) / 2
    h, w = len(matrix), len(matrix[0])
    v1, v2, v3 = [], [], []
    for y in range(h):
        r1, r2, r3 = [], [], []
        for x in range(w):
            r, g, b = matrix[y][x]
            avg   = int((r + g + b) / 3)
            lum   = int(0.299 * r + 0.587 * g + 0.114 * b)
            light = int((max(r, g, b) + min(r, g, b)) / 2)
            r1.append([avg, avg, avg])
            r2.append([lum, lum, lum])
            r3.append([light, light, light])
        v1.append(r1)
        v2.append(r2)
        v3.append(r3)
    return v1, v2, v3


def convert_to_yuv(matrix):
    # Conversie RGB -> YUV
    # Y = luminanta, U si V = crominanta (offset cu 128 pentru a fi in [0, 255])
    height = len(matrix)
    width = len(matrix[0])
    yuv_matrix = []
    for y in range(height):
        row = []
        for x in range(width):
            r, g, b = matrix[y][x]
            y_val = 0.3 * r + 0.6 * g + 0.1 * b
            u_val = 0.74 * (r - y_val) + 0.27 * (b - y_val)
            v_val = 0.48 * (r - y_val) + 0.41 * (b - y_val)
            row.append([
                int(max(0, min(255, y_val))),
                int(max(0, min(255, u_val + 128))),
                int(max(0, min(255, v_val + 128)))
            ])
        yuv_matrix.append(row)
    return yuv_matrix


def convert_to_ycbcr(matrix):
    # Conversie RGB -> YCbCr (standard JPEG)
    # Y = luminanta, Cb/Cr = diferenta de culoare fata de albastru/rosu
    height = len(matrix)
    width = len(matrix[0])
    ycbcr_matrix = []
    for y in range(height):
        row = []
        for x in range(width):
            r, g, b = matrix[y][x]
            y_val  = 0.299 * r + 0.587 * g + 0.114 * b
            cb_val = 128 - 0.168736 * r - 0.331264 * g + 0.5 * b
            cr_val = 128 + 0.5 * r - 0.418688 * g - 0.081312 * b
            row.append([
                int(max(0, min(255, y_val))),
                int(max(0, min(255, cb_val))),
                int(max(0, min(255, cr_val)))
            ])
        ycbcr_matrix.append(row)
    return ycbcr_matrix


def get_binarized_matrix(matrix, threshold=128):
    # Binarizare: pixelii sub prag devin negri (0), restul albi (255)
    height = len(matrix)
    width = len(matrix[0])
    binary_matrix = []
    for y in range(height):
        row = []
        for x in range(width):
            r, g, b = matrix[y][x]
            gray = (r + g + b) // 3
            val = 0 if gray < threshold else 255
            row.append([val, val, val])
        binary_matrix.append(row)
    return binary_matrix


def convert_to_hsv(matrix):
    # Conversie RGB -> HSV (Hue, Saturation, Value)
    # H normalizat in [0, 255] din [0, 360 grade]
    height = len(matrix)
    width = len(matrix[0])
    hsv_matrix = []
    for y in range(height):
        row = []
        for x in range(width):
            R, G, B = matrix[y][x]
            r, g, b = R / 255, G / 255, B / 255
            M, m = max(r, g, b), min(r, g, b)
            C = M - m  # chroma

            V = M
            S = C / V if V != 0 else 0

            # Calculul nuantei H in functie de canalul dominant
            if C != 0:
                if M == r:
                    H = 60 * (g - b) / C
                elif M == g:
                    H = 120 + 60 * (b - r) / C
                else:
                    H = 240 + 60 * (r - g) / C
            else:
                H = 0  # gri, nuanta nedefinita

            if H < 0:
                H += 360

            row.append([int(H * 255 / 360), int(S * 255), int(V * 255)])
        hsv_matrix.append(row)
    return hsv_matrix


def convert_to_cmy(matrix):
    # Conversie RGB -> CMY: C=255-R, M=255-G, Y=255-B
    return [[[255 - r, 255 - g, 255 - b] for r, g, b in row] for row in matrix]


def get_inverse_matrix(matrix):
    # Negativul imaginii: fiecare canal este inversat (255 - valoare)
    return [[[255 - r, 255 - g, 255 - b] for r, g, b in row] for row in matrix]


def get_red_channel(matrix):
    # Pastreaza doar canalul rosu, G si B devin 0
    return [[[pixel[0], 0, 0] for pixel in row] for row in matrix]


def get_green_channel(matrix):
    # Pastreaza doar canalul verde, R si B devin 0
    return [[[0, pixel[1], 0] for pixel in row] for row in matrix]


def get_blue_channel(matrix):
    # Pastreaza doar canalul albastru, R si G devin 0
    return [[[0, 0, pixel[2]] for pixel in row] for row in matrix]
