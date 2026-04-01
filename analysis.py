import math

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


def calculate_covariance_matrix(matrix):
    # Calculeaza matricea de covarianta pe baza momentelor centrale de ordinul 2
    # Aplicata pe imaginea binarizata pentru a izola obiectul principal
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
