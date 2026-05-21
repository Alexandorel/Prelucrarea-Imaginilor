import math
import numpy as np

def convert_to_grayscale(matrix):
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


def equalize_histogram(matrix):
    height = len(matrix)
    width = len(matrix[0])

    # Histograma
    histogram = [0] * 256
    for i in range(height):
        for j in range(width):
            r, g, b = matrix[i][j]
            level = (r + g + b) // 3
            histogram[level] += 1

    # Histograma cumulativa
    hc = [0] * 256
    hc[0] = histogram[0]
    for i in range(1, 256):
        hc[i] = hc[i - 1] + histogram[i]

    # Formula de egalizare
    total = width * height
    denominator = total - hc[0]
    result = []
    for i in range(height):
        row = []
        for j in range(width):
            r, g, b = matrix[i][j]
            level = (r + g + b) // 3
            if denominator > 0:
                new_level = int((hc[level] - hc[0]) * 255 / denominator)
            else:
                new_level = level
            new_level = max(0, min(255, new_level))
            row.append([new_level, new_level, new_level])
        result.append(row)
    return result


def dilate_image(binary_matrix):
    # Dilatarea unei imagini binare (0 = obiect negru, 255 = fundal alb)
    # Element structural: 3x3 plin (8-conectivitate)
    # Regula: un pixel devine 0 daca CEL PUTIN UN vecin (inclusiv el) este 0
    height = len(binary_matrix)
    width = len(binary_matrix[0])
    result = []
    for i in range(height):
        row = []
        for j in range(width):
            is_object = False
            for k in range(-1, 2):
                for m in range(-1, 2):
                    ni, nj = i + k, j + m
                    if 0 <= ni < height and 0 <= nj < width:
                        if binary_matrix[ni][nj][0] == 0:
                            is_object = True
                            break
                if is_object:
                    break
            val = 0 if is_object else 255
            row.append([val, val, val])
        result.append(row)
    return result


def erode_image(binary_matrix):
    # Eroziunea unei imagini binare (0 = obiect negru, 255 = fundal alb)
    # Element structural: 3x3 plin (8-conectivitate)
    # Regula: un pixel ramane 0 doar daca TOTI vecinii sunt 0, altfel devine 255
    height = len(binary_matrix)
    width = len(binary_matrix[0])
    result = []
    for i in range(height):
        row = []
        for j in range(width):
            all_object = True
            for k in range(-1, 2):
                for m in range(-1, 2):
                    ni, nj = i + k, j + m
                    if 0 <= ni < height and 0 <= nj < width:
                        if binary_matrix[ni][nj][0] != 0:
                            all_object = False
                            break
                    else:
                        # Pixelii din afara imaginii sunt considerati fundal
                        all_object = False
                        break
                if not all_object:
                    break
            val = 0 if all_object else 255
            row.append([val, val, val])
        result.append(row)
    return result


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

def Fourier_transform(matrix):
    # 1. Convertire imagine in tablou bidimensional în scala de gri
    height = len(matrix)
    width = len(matrix[0])
    gray_pixels = np.zeros((height, width), dtype=float)
    
    for y in range(height):
        for x in range(width):
            r, g, b = matrix[y][x]
            gray_pixels[y, x] = 0.299 * r + 0.587 * g + 0.114 * b
            
    # 2. Aplicarea transformatei fourier discrete
    # În Python numerele complexe sunt native (ex. 1 + 2j).
    dft = np.fft.fft2(gray_pixels)
    
    # Centrarea spectrului de frecvente
    dft_shift = np.fft.fftshift(dft)
    
    # 3. Salvarea spectrului de magnitudine într-o imagine
    magnitude = np.abs(dft_shift)
    # Aplicărea transformarii logaritmice pentru a face diferentele vizibile ochiului uman
    magnitude_log = np.log(1 + magnitude)
    
    # Normalizare pe 8 biți (0-255)
    mag_min = magnitude_log.min()
    mag_max = magnitude_log.max()
    normalized = 255 * (magnitude_log - mag_min) / (mag_max - mag_min) if mag_max != mag_min else magnitude_log
    
    # Conversie într-o matrice RGB standard pentru a fi afișată pe UI
    result = []
    for y in range(height):
        row = []
        for x in range(width):
            val = int(normalized[y, x])
            row.append([val, val, val])
        result.append(row)
        
    return result


def inverse_fourier_transform(matrix):
    height = len(matrix)
    width = len(matrix[0])
    gray_pixels = np.zeros((height, width), dtype=float)
    r_pixels = np.zeros((height, width), dtype=float)
    g_pixels = np.zeros((height, width), dtype=float)
    b_pixels = np.zeros((height, width), dtype=float)
    
    for y in range(height):
        for x in range(width):
            r, g, b = matrix[y][x]
            gray_pixels[y, x] = 0.299 * r + 0.587 * g + 0.114 * b
            r_pixels[y, x] = r
            g_pixels[y, x] = g
            b_pixels[y, x] = b
            
    # 1. Trecem imaginea gri in domeniul frecventelor pentru a vizualiza spectrul
    dft = np.fft.fft2(gray_pixels)
    
    # --- Generare imagine spectru (ca in Fourier_transform) ---
    dft_shift = np.fft.fftshift(dft)
    magnitude = np.abs(dft_shift)
    magnitude_log = np.log(1 + magnitude)
    mag_min = magnitude_log.min()
    mag_max = magnitude_log.max()
    normalized_spectrum = 255 * (magnitude_log - mag_min) / (mag_max - mag_min) if mag_max != mag_min else magnitude_log
    
    spectrum_image = []
    for y in range(height):
        row = []
        for x in range(width):
            val = int(normalized_spectrum[y, x])
            row.append([val, val, val])
        spectrum_image.append(row)

    # 2. Reconstruim imaginea COLOR folosind Transformata Inversa pe fiecare canal
    dft_r = np.fft.fft2(r_pixels)
    dft_g = np.fft.fft2(g_pixels)
    dft_b = np.fft.fft2(b_pixels)
    
    rec_r = np.abs(np.fft.ifft2(dft_r))
    rec_g = np.abs(np.fft.ifft2(dft_g))
    rec_b = np.abs(np.fft.ifft2(dft_b))
    
    def normalize(channel):
        c_min = channel.min()
        c_max = channel.max()
        return 255 * (channel - c_min) / (c_max - c_min) if c_max != c_min else channel
        
    norm_r = normalize(rec_r)
    norm_g = normalize(rec_g)
    norm_b = normalize(rec_b)
    
    reconstructed_image = []
    for y in range(height):
        row = []
        for x in range(width):
            row.append([int(norm_r[y, x]), int(norm_g[y, x]), int(norm_b[y, x])])
        reconstructed_image.append(row)
        
    return spectrum_image, reconstructed_image


def mean_filter(matrix):
    height = len(matrix)
    width = len(matrix[0])
    
    # Initializam matricea destinatie facand o copie a originalului.
    # Acest lucru pastreaza marginile de 1 pixel intacte (nondistorsionate).
    dst = []
    for y in range(height):
        row = []
        for x in range(width):
            row.append(list(matrix[y][x]))
        dst.append(row)
        
    v = [
        [1.0/9.0, 1.0/9.0, 1.0/9.0],
        [1.0/9.0, 1.0/9.0, 1.0/9.0],
        [1.0/9.0, 1.0/9.0, 1.0/9.0]
    ]
    
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            sum_r = sum_g = sum_b = 0.0
            for k in range(-1, 2):
                for l in range(-1, 2):
                    r, g, b = matrix[y + k][x + l]
                    sum_r += v[k + 1][l + 1] * r
                    sum_g += v[k + 1][l + 1] * g
                    sum_b += v[k + 1][l + 1] * b
                    
            dst[y][x] = [int(sum_r), int(sum_g), int(sum_b)]
            
    return dst


def median_filter(matrix):
    height = len(matrix)
    width = len(matrix[0])
    
    # Initizare matrice -> copie
    dst = []
    for y in range(height):
        row = []
        for x in range(width):
            row.append(list(matrix[y][x]))
        dst.append(row)
        
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            r_vals, g_vals, b_vals = [], [], []
            for m in range(-1, 2):
                for n in range(-1, 2):
                    r, g, b = matrix[y + m][x + n]
                    r_vals.append(r)
                    g_vals.append(g)
                    b_vals.append(b)
            
            # Ordonarea crescatoare
            r_vals.sort()
            g_vals.sort()
            b_vals.sort()
            
            dst[y][x] = [r_vals[4], g_vals[4], b_vals[4]]
            
    return dst

# filtru de accentuare
def sharpen_filter(matrix):
    height = len(matrix)
    width = len(matrix[0])
    
    # Initializare matrice destinatie
    dst = []
    for y in range(height):
        row = []
        for x in range(width):
            row.append(list(matrix[y][x]))
        dst.append(row)
        
    v = [
        [0.0, -0.25, 0.0],
        [-0.25, 1.0, -0.25],
        [0.0, -0.25, 0.0]
    ]
    
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            sum_r = sum_g = sum_b = 0.0
            for k in range(-1, 2):
                for l in range(-1, 2):
                    r, g, b = matrix[y + k][x + l]
                    sum_r += v[k + 1][l + 1] * r
                    sum_g += v[k + 1][l + 1] * g
                    sum_b += v[k + 1][l + 1] * b
                    
            orig_r, orig_g, orig_b = matrix[y][x]
            
            # Aplicare accentuare cu factor de 0.6
            new_r = int(max(0, min(255, orig_r + 0.6 * sum_r)))
            new_g = int(max(0, min(255, orig_g + 0.6 * sum_g)))
            new_b = int(max(0, min(255, orig_b + 0.6 * sum_b)))
            
            dst[y][x] = [new_r, new_g, new_b]
            
    return dst


def minimum_filter(matrix):
    height = len(matrix)
    width = len(matrix[0])
    
    # Initializare matrice -> copie
    dst = []
    for y in range(height):
        row = []
        for x in range(width):
            row.append(list(matrix[y][x]))
        dst.append(row)
        
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            r_vals, g_vals, b_vals = [], [], []
            for m in range(-1, 2):
                for n in range(-1, 2):
                    r, g, b = matrix[y + m][x + n]
                    r_vals.append(r)
                    g_vals.append(g)
                    b_vals.append(b)
            
            dst[y][x] = [min(r_vals), min(g_vals), min(b_vals)]
            
    return dst


def maximum_filter(matrix):
    height = len(matrix)
    width = len(matrix[0])
    
    # initializare matrice -> copie
    dst = []
    for y in range(height):
        row = []
        for x in range(width):
            row.append(list(matrix[y][x]))
        dst.append(row)
        
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            r_vals, g_vals, b_vals = [], [], []
            for m in range(-1, 2):
                for n in range(-1, 2):
                    r, g, b = matrix[y + m][x + n]
                    r_vals.append(r)
                    g_vals.append(g)
                    b_vals.append(b)
            
            dst[y][x] = [max(r_vals), max(g_vals), max(b_vals)]
            
    return dst


def get_nearest_color(r, g, b, palette):
    # Afla culoarea cea mai apropiata din paleta folosind distanta euclidiana
    nearest_color = palette[0]
    min_dist = float('inf')
    for pr, pg, pb in palette:
        dist = (r - pr)**2 + (g - pg)**2 + (b - pb)**2
        if dist < min_dist:
            min_dist = dist
            nearest_color = (pr, pg, pb)
    return nearest_color


def floyd_steinberg_dithering(matrix):
    height = len(matrix)
    width = len(matrix[0])
    
    # Definim o paleta standard (ex: 8 culori de baza)
    palette = [
        (0, 0, 0),       # Negru
        (255, 0, 0),     # Rosu
        (0, 255, 0),     # Verde
        (0, 0, 255),     # Albastru
        (0, 255, 255),   # Cyan
        (255, 0, 255),   # Magenta
        (255, 255, 0),   # Galben
        (255, 255, 255)  # Alb
    ]

    # Cream o copie de lucru cu valori float pentru a nu pierde din precizie la rotunjirea erorii
    work = [[[float(r), float(g), float(b)] for r, g, b in row] for row in matrix]
    
    dst = [[[0, 0, 0] for _ in range(width)] for _ in range(height)]

    for y in range(height):
        for x in range(width):
            old_r, old_g, old_b = work[y][x]
            
            # Gasim culoarea cea mai apropiata din paleta
            new_r, new_g, new_b = get_nearest_color(old_r, old_g, old_b, palette)
            dst[y][x] = [new_r, new_g, new_b]
            
            # Calculam eroarea per canal
            err_r, err_g, err_b = old_r - new_r, old_g - new_g, old_b - new_b
            
            # Propagam eroarea la vecini conform matricei Floyd-Steinberg
            if x + 1 < width:
                work[y][x + 1][0] += err_r * 7 / 16
                work[y][x + 1][1] += err_g * 7 / 16
                work[y][x + 1][2] += err_b * 7 / 16
            if x - 1 >= 0 and y + 1 < height:
                work[y + 1][x - 1][0] += err_r * 3 / 16
                work[y + 1][x - 1][1] += err_g * 3 / 16
                work[y + 1][x - 1][2] += err_b * 3 / 16
            if y + 1 < height:
                work[y + 1][x][0] += err_r * 5 / 16
                work[y + 1][x][1] += err_g * 5 / 16
                work[y + 1][x][2] += err_b * 5 / 16
            if x + 1 < width and y + 1 < height:
                work[y + 1][x + 1][0] += err_r * 1 / 16
                work[y + 1][x + 1][1] += err_g * 1 / 16
                work[y + 1][x + 1][2] += err_b * 1 / 16
                
def laplacian_filter(matrix):
    height = len(matrix)
    width = len(matrix[0])

    dst = []
    for y in range(height):
        row = []
        for x in range(width):
            dst_row_pixel = list(matrix[y][x])
            row.append(dst_row_pixel)
        dst.append(row)

    v = [
        [-1, -1, -1],
        [-1,  8, -1],
        [-1, -1, -1]
    ]

    for y in range(1, height - 1):
        for x in range(1, width - 1):
            sum_val = 0
            for m in range(-1, 2):
                for n in range(-1, 2):
                    r, g, b = matrix[y + n][x + m]
                    gray = (r + g + b) // 3
                    sum_val += v[m + 1][n + 1] * gray

            sum_val = max(0, min(255, sum_val))
            dst[y][x] = [sum_val, sum_val, sum_val]

def remove_gaussian_noise(matrix):
    height = len(matrix)
    width = len(matrix[0])

    dst = []
    for y in range(height):
        row = []
        for x in range(width):
            row.append([0, 0, 0])
        dst.append(row)

    kernel_size = 3
    half_kernel = kernel_size // 2

    for y in range(height):
        for x in range(width):
            sum_r = sum_g = sum_b = 0
            # Calcularea mediei intensitatilor pixelilor din jur
            for i in range(-half_kernel, half_kernel + 1):
                for j in range(-half_kernel, half_kernel + 1):
                    offset_x = min(max(x + i, 0), width - 1)
                    offset_y = min(max(y + j, 0), height - 1)
                    r, g, b = matrix[offset_y][offset_x]
                    sum_r += r
                    sum_g += g
                    sum_b += b

            avg_r = sum_r // (kernel_size * kernel_size)
            avg_g = sum_g // (kernel_size * kernel_size)
            avg_b = sum_b // (kernel_size * kernel_size)

            dst[y][x] = [avg_r, avg_g, avg_b]

    return dst


    return dst


def edge_detect(matrix, filter_type, iteratii=1):
    # Detectie de contur prin convolutie
    FILTER_VERTICAL   = [[ 1, 0, -1], [ 1, 0, -1], [ 1, 0, -1]]
    FILTER_HORIZONTAL = [[ 1, 1,  1], [ 0, 0,  0], [-1,-1, -1]]
    FILTER_SOBEL_V    = [[ 1, 0, -1], [ 2, 0, -2], [ 1, 0, -1]]
    FILTER_SOBEL_H    = [[ 1, 2,  1], [ 0, 0,  0], [-1,-2, -1]]
    FILTER_SCHARR_V   = [[ 3, 0, -3], [10, 0,-10], [ 3, 0, -3]]
    FILTER_SCHARR_H   = [[ 3,10,  3], [ 0, 0,  0], [-3,-10,-3]]

    filters = {
        1: FILTER_VERTICAL,   2: FILTER_HORIZONTAL,
        3: FILTER_SOBEL_V,    4: FILTER_SOBEL_H,
        5: FILTER_SCHARR_V,   6: FILTER_SCHARR_H,
    }
    kernel = filters[filter_type]

    height = len(matrix)
    width = len(matrix[0])

    src = matrix
    for _ in range(iteratii):
        dst = [[[0, 0, 0] for _ in range(width)] for _ in range(height)]
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                sum_r = sum_g = sum_b = 0.0
                for ky in range(-1, 2):
                    for kx in range(-1, 2):
                        r, g, b = src[y + ky][x + kx]
                        coef = kernel[ky + 1][kx + 1]
                        sum_r += coef * r
                        sum_g += coef * g
                        sum_b += coef * b

                total = sum_r + sum_g + sum_b
                val = min(255, abs(int(total)))
                dst[y][x] = [val, val, val]
        src = dst

    return src


def edge_enhance(matrix, filter_type):
    FILTER_SLAB     = [[ 0, -1,  0], [-1,  5, -1], [ 0, -1,  0]]
    FILTER_PUTERNIC = [[-1, -1, -1], [-1,  9, -1], [-1, -1, -1]]
    FILTER_EXCESIV  = [[ 1, -2,  1], [-2,  5, -2], [ 1, -2,  1]]

    filters = {
        1: FILTER_SLAB,
        2: FILTER_PUTERNIC,
        3: FILTER_EXCESIV,
    }
    kernel = filters[filter_type]

    height = len(matrix)
    width = len(matrix[0])

    dst = [[list(matrix[y][x]) for x in range(width)] for y in range(height)]

    for y in range(1, height - 1):
        for x in range(1, width - 1):
            sum_r = sum_g = sum_b = 0.0
            for ky in range(-1, 2):
                for kx in range(-1, 2):
                    r, g, b = matrix[y + ky][x + kx]
                    coef = kernel[ky + 1][kx + 1]
                    sum_r += coef * r
                    sum_g += coef * g
                    sum_b += coef * b

            new_r = max(0, min(255, int(sum_r)))
            new_g = max(0, min(255, int(sum_g)))
            new_b = max(0, min(255, int(sum_b)))
            dst[y][x] = [new_r, new_g, new_b]

    return dst


def _canny_grayscale(matrix):
    # Conversia la grayscale, usurand munca
    height = len(matrix)
    width = len(matrix[0])
    gray = [[0] * width for _ in range(height)]
    for y in range(height):
        for x in range(width):
            r, g, b = matrix[y][x]
            gray[y][x] = (r + g + b) // 3
    return gray


def _canny_gaussian_blur(gray):
    # Aplicarea blur-ului
    kernel = [
        [1,  4,  7,  4, 1],
        [4, 16, 26, 16, 4],
        [7, 26, 41, 26, 7],
        [4, 16, 26, 16, 4],
        [1,  4,  7,  4, 1]
    ]
    kernel_sum = 273.0
    height = len(gray)
    width = len(gray[0])
    blurred = [[0] * width for _ in range(height)]
    for y in range(2, height - 2):
        for x in range(2, width - 2):
            s = 0
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    s += gray[y + dy][x + dx] * kernel[dy + 2][dx + 2]
            blurred[y][x] = int(s / kernel_sum)
    return blurred


def _canny_gradient(blurred):
    # Calculul gradientului : magnitudine si directie folosind Sobel
    SOBEL_X = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
    SOBEL_Y = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
    height = len(blurred)
    width = len(blurred[0])
    magnitude = [[0.0] * width for _ in range(height)]
    direction = [[0.0] * width for _ in range(height)]
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            gx = 0
            gy = 0
            for ky in range(-1, 2):
                for kx in range(-1, 2):
                    pixel = blurred[y + ky][x + kx]
                    gx += pixel * SOBEL_X[ky + 1][kx + 1]
                    gy += pixel * SOBEL_Y[ky + 1][kx + 1]
            magnitude[y][x] = math.sqrt(gx * gx + gy * gy)
            direction[y][x] = math.atan2(gy, gx)
    return magnitude, direction


def _canny_non_max_suppression(magnitude, direction):
    # Non-Maximum Suppresion: subtierea conturului
    height = len(magnitude)
    width = len(magnitude[0])
    thinned = [[0.0] * width for _ in range(height)]
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            mag = magnitude[y][x]
            angle = math.degrees(direction[y][x]) % 180

            if (0 <= angle < 22.5) or (157.5 <= angle < 180):
                # Orizontal: vecinii din stanga si dreapta
                n1 = magnitude[y][x - 1]
                n2 = magnitude[y][x + 1]
            elif 22.5 <= angle < 67.5:
                # Diagonala /: vecinii sus-dreapta si jos-stanga
                n1 = magnitude[y - 1][x + 1]
                n2 = magnitude[y + 1][x - 1]
            elif 67.5 <= angle < 112.5:
                # Vertical: vecinii de sus si de jos
                n1 = magnitude[y - 1][x]
                n2 = magnitude[y + 1][x]
            else:
                # Diagonala \: vecinii sus-stanga si jos-dreapta
                n1 = magnitude[y - 1][x - 1]
                n2 = magnitude[y + 1][x + 1]

            # Pastram pixel daca e maxim local
            if mag >= n1 and mag >= n2:
                thinned[y][x] = mag
            else:
                thinned[y][x] = 0
    return thinned


def _canny_hysteresis(thinned, low_threshold, high_threshold):
    # Clasifica pixelii folosind 2 praguri
    height = len(thinned)
    width = len(thinned[0])
    edges = [[[0, 0, 0] for _ in range(width)] for _ in range(height)]

    stack = []
    for y in range(height):
        for x in range(width):
            if thinned[y][x] >= high_threshold:
                edges[y][x] = [255, 255, 255]
                stack.append((y, x))

    while stack:
        y, x = stack.pop()
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if dy == 0 and dx == 0:
                    continue
                ny, nx = y + dy, x + dx
                if 0 <= ny < height and 0 <= nx < width:
                    if edges[ny][nx][0] == 0 and thinned[ny][nx] >= low_threshold:
                        edges[ny][nx] = [255, 255, 255]
                        stack.append((ny, nx))

    return edges


def _build_gaussian_kernel(kernel_size, sigma):
    half = kernel_size // 2
    kernel = [[0.0] * kernel_size for _ in range(kernel_size)]
    kernel_sum = 0.0
    for i in range(-half, half + 1):
        for j in range(-half, half + 1):
            value = math.exp(-(i * i + j * j) / (2.0 * sigma * sigma))
            kernel[i + half][j + half] = value
            kernel_sum += value
    for i in range(kernel_size):
        for j in range(kernel_size):
            kernel[i][j] /= kernel_sum
    return kernel


def canny_edge_detection(matrix, low_threshold=50, high_threshold=150):
    gray = _canny_grayscale(matrix)
    blurred = _canny_gaussian_blur(gray)
    magnitude, direction = _canny_gradient(blurred)
    thinned = _canny_non_max_suppression(magnitude, direction)
    edges = _canny_hysteresis(thinned, low_threshold, high_threshold)
    return edges


def canny_edge_detection_adaptive(matrix, sigma=0.33):

    gray = _canny_grayscale(matrix)
    blurred = _canny_gaussian_blur(gray)
    magnitude, direction = _canny_gradient(blurred)

    flat = []
    height = len(magnitude)
    width = len(magnitude[0])
    for y in range(height):
        for x in range(width):
            if magnitude[y][x] > 0:
                flat.append(magnitude[y][x])

    if flat:
        flat.sort()
        median = flat[len(flat) // 2]
    else:
        median = 0.0

    low_threshold = max(0.0, (1.0 - sigma) * median)
    high_threshold = (1.0 + sigma) * median

    thinned = _canny_non_max_suppression(magnitude, direction)
    edges = _canny_hysteresis(thinned, low_threshold, high_threshold)
    return edges
