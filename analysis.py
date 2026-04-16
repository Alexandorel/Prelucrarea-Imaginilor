import math
from collections import deque

import matplotlib.pyplot as plt

from conversions import get_binarized_matrix


def calculate_histogram(matrix):
    # Calculeaza histograma imaginii in tonuri de gri
    # Returneaza o lista de 256 de valori: numarul de pixeli pentru fiecare intensitate
    height = len(matrix)
    width = len(matrix[0])
    histogram = [0] * 256
    for i in range(height):
        for j in range(width):
            r, g, b = matrix[i][j]
            gray = (r + g + b) // 3
            histogram[gray] += 1
    return histogram


def get_histogram_figure(matrix):
    # Construieste figura matplotlib cu histograma imaginii in tonuri de gri
    histogram = calculate_histogram(matrix)
    fig, ax = plt.subplots()
    ax.bar(range(256), histogram, color='gray', width=1)
    ax.set_title("Histograma imaginii gri")
    ax.set_xlabel("Intensitate (0-255)")
    ax.set_ylabel("Numar pixeli")
    ax.set_xlim([0, 255])
    fig.tight_layout()
    return fig


def calculate_moment_order1(matrix):
    # Calculeaza momentele geometrice de ordinul 1: M00, M10, M01
    # si coordonatele centroidului (cx, cy)
    height = len(matrix)
    width = len(matrix[0])
    M00 = M10 = M01 = 0
    for i in range(height):
        for j in range(width):
            r, g, b = matrix[i][j]
            gray = (r + g + b) // 3
            M00 += gray
            M10 += i * gray  # moment pe axa verticala
            M01 += j * gray  # moment pe axa orizontala
    if M00 == 0:
        return None, None, M00, M10, M01
    # Centroidul = momentul de ordinul 1 impartit la momentul de ordinul 0
    return M01 / M00, M10 / M00, M00, M10, M01


def calculate_moment_order2(matrix):
    # Calculeaza momentele centrale de ordinul 2 pe imaginea binarizata
    # si unghiul de rotatie al obiectului principal
    height = len(matrix)
    width = len(matrix[0])
    M00 = M10 = M01 = M20 = M02 = M11 = 0
    for i in range(height):
        for j in range(width):
            r, g, b = matrix[i][j]
            raw = (r + g + b) // 3
            # Binarizare locala: pixelii intunecati devin albi (obiect)
            gray = 255 if raw < 128 else 0
            M00 += gray
            M10 += i * gray
            M01 += j * gray
            M20 += i * i * gray
            M02 += j * j * gray
            M11 += i * j * gray
    if M00 == 0:
        return None
    cx = M01 / M00
    cy = M10 / M00
    # Momentele centrale (invariante la translatie)
    mu20 = M20 / M00 - cy ** 2
    mu02 = M02 / M00 - cx ** 2
    mu11 = M11 / M00 - cx * cy
    # Unghiul axei principale de inertie
    if mu20 - mu02 == 0:
        theta_rad = math.pi / 4
    else:
        theta_rad = 0.5 * math.atan2(2 * mu11, mu20 - mu02)
    theta_deg = abs(math.degrees(theta_rad))
    return cx, cy, mu20, mu02, mu11, theta_rad, theta_deg


def get_projections_figure(matrix):
    # Calculeaza si afiseaza proiectiile orizontala si verticala ale imaginii
    # Proiectia orizontala: suma intensitatilor pe fiecare linie
    # Proiectia verticala: suma intensitatilor pe fiecare coloana
    height = len(matrix)
    width = len(matrix[0])
    proj_H = [0] * height
    proj_V = [0] * width
    for i in range(height):
        for j in range(width):
            r, g, b = matrix[i][j]
            gray = (r + g + b) // 3
            proj_H[i] += gray
            proj_V[j] += gray

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    ax1.barh(range(len(proj_H)), proj_H, color='gray', height=1)
    ax1.set_title("Proiectie orizontala")
    ax1.set_xlabel("Suma pixeli pe linie")
    ax1.set_ylabel("Linie (i)")
    ax1.invert_yaxis()
    ax2.bar(range(len(proj_V)), proj_V, color='gray', width=1)
    ax2.set_title("Proiectie verticala")
    ax2.set_xlabel("Coloana (j)")
    ax2.set_ylabel("Suma pixeli pe coloana")
    fig.tight_layout()
    return fig


def calculate_object_orientation(matrix):
    # Calculeaza orientarea obiectului folosind operatorul Sobel
    # Returneaza unghiul (in radiani) al gradientului de maxima magnitudine
    height = len(matrix)
    width = len(matrix[0])

    def gray(row, col):
        r, g, b = matrix[row][col]
        return (r + g + b) // 3

    max_magnitude = 0
    orientation = 0.0

    for y in range(height):
        for x in range(width):
            if x == 0 or y == 0 or x == width - 1 or y == height - 1:
                continue

            gx = (gray(y - 1, x + 1) + 2 * gray(y, x + 1) + gray(y + 1, x + 1)
                  - gray(y - 1, x - 1) - 2 * gray(y, x - 1) - gray(y + 1, x - 1))

            gy = (gray(y + 1, x - 1) + 2 * gray(y + 1, x) + gray(y + 1, x + 1)
                  - gray(y - 1, x - 1) - 2 * gray(y - 1, x) - gray(y - 1, x + 1))

            magnitude = math.sqrt(gx * gx + gy * gy)

            if magnitude > max_magnitude:
                max_magnitude = magnitude
                orientation = math.atan2(gy, gx)

    return orientation


def _label_to_color(label):
    # Genereaza o culoare distincta pentru fiecare eticheta folosind unghiul de aur pe HSV
    if label == 0:
        return [255, 255, 255]  # fundal alb
    h = (label * 137) % 360  # distributie uniforma prin unghiul de aur
    h60 = h / 60.0
    i = int(h60)
    f = h60 - i
    # s=1, v=1 -> culori saturate
    p, q_val, t = 0, 1 - f, f
    if i == 0:   r, g, b = 1,     t,     p
    elif i == 1: r, g, b = q_val, 1,     p
    elif i == 2: r, g, b = p,     1,     t
    elif i == 3: r, g, b = p,     q_val, 1
    elif i == 4: r, g, b = t,     p,     1
    else:        r, g, b = 1,     p,     q_val
    return [int(r * 255), int(g * 255), int(b * 255)]


def label_objects(matrix):
    # Etichetare componente conexe prin BFS (8-conectivitate)
    # Pixelii inchisi (gray < 50) sunt considerati obiecte
    # Returneaza (colored_matrix, labels_matrix)
    height = len(matrix)
    width = len(matrix[0])

    # Binarizare cu prag 50: pixeli intunecati -> 0 (obiect), restul -> 255 (fundal)
    binary = []
    for i in range(height):
        row = []
        for j in range(width):
            r, g, b = matrix[i][j]
            gray = (r + g + b) // 3
            row.append(0 if gray < 50 else 255)
        binary.append(row)

    label = 0
    labels = [[0] * width for _ in range(height)]

    for i in range(height):
        for j in range(width):
            if binary[i][j] == 0 and labels[i][j] == 0:
                label += 1
                labels[i][j] = label
                queue = deque()
                queue.append((i, j))
                while queue:
                    q0, q1 = queue.popleft()
                    for k in range(-1, 2):
                        for m in range(-1, 2):
                            ni, nj = q0 + k, q1 + m
                            if 0 <= ni < height and 0 <= nj < width:
                                if binary[ni][nj] == 0 and labels[ni][nj] == 0:
                                    labels[ni][nj] = label
                                    queue.append((ni, nj))

    # Construieste imaginea colorata: fiecare eticheta primeste o culoare distincta
    dst = []
    for i in range(height):
        row = []
        for j in range(width):
            row.append(_label_to_color(labels[i][j]))
        dst.append(row)

    return dst, labels


def calculate_elongation_direction(matrix, labels, label_id):
    # Calculeaza directia de alungire a obiectului cu eticheta label_id
    # folosind operatorul Sobel aplicat doar pe pixelii obiectului
    # Returneaza unghiul dominant (medie ponderata cu magnitudinea gradientului)
    height = len(matrix)
    width = len(matrix[0])

    def gray(row, col):
        r, g, b = matrix[row][col]
        return (r + g + b) // 3

    sum_gx = 0.0
    sum_gy = 0.0
    total_magnitude = 0.0

    for y in range(1, height - 1):
        for x in range(1, width - 1):
            if labels[y][x] != label_id:
                continue

            gx = (gray(y-1, x+1) + 2*gray(y, x+1) + gray(y+1, x+1)
                  - gray(y-1, x-1) - 2*gray(y, x-1) - gray(y+1, x-1))

            gy = (gray(y+1, x-1) + 2*gray(y+1, x) + gray(y+1, x+1)
                  - gray(y-1, x-1) - 2*gray(y-1, x) - gray(y-1, x+1))

            magnitude = math.sqrt(gx * gx + gy * gy)
            sum_gx += gx * magnitude
            sum_gy += gy * magnitude
            total_magnitude += magnitude

    if total_magnitude == 0:
        return None

    return math.atan2(sum_gy, sum_gx)


def select_object_by_label(matrix, labels, label_id):
    # Returneaza imaginea originala cu obiectul selectat evidentiat
    # Pixelii cu eticheta label_id raman in culoarea originala, restul devin albi
    height = len(matrix)
    width = len(matrix[0])
    dst = []
    for i in range(height):
        row = []
        for j in range(width):
            if labels[i][j] == label_id:
                row.append(list(matrix[i][j]))
            else:
                row.append([255, 255, 255])
        dst.append(row)
    return dst


def calculate_covariance_matrix(matrix):
    # Calculeaza matricea de covarianta aplicata pe imaginea binarizata pentru a izola obiectul principal
    binary = get_binarized_matrix(matrix, threshold=128)
    height = len(matrix)
    width = len(matrix[0])
    M00 = M10 = M01 = M20 = M02 = M11 = 0
    for i in range(height):
        for j in range(width):
            gray = binary[i][j][0]
            M00 += gray
            M10 += i * gray
            M01 += j * gray
            M20 += i * i * gray
            M02 += j * j * gray
            M11 += i * j * gray
    if M00 == 0:
        return None
    cx = M01 / M00
    cy = M10 / M00
    # Momentele centrale de ordinul 2
    mu20 = M20 / M00 - cy ** 2  # varianta pe verticala
    mu02 = M02 / M00 - cx ** 2  # varianta pe orizontala
    mu11 = M11 / M00 - cx * cy  # covarianta
    return cx, cy, [[mu20, mu11], [mu11, mu02]]
