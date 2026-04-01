import tkinter as tk
from tkinter import filedialog
import struct
import os
import matplotlib.pyplot as plt
import numpy as np

current_photo = None
original_matrix = None

# --- CONFIGURARE FEREASTRA ---
root = tk.Tk()
root.title("Photo Shop - Vint Alexandru")
root.geometry("1100x800")
root.configure(bg='white')
root.resizable(True, True)

# --- TOOLBAR ---
toolbar = tk.Frame(root, bg='#f0f0f0', bd=1, relief='raised')
toolbar.pack(side='top', fill='x')

# --- LABEL IMAGINE ---
img_label = tk.Label(root, bg='white')
img_label.pack(side='top', pady=10)

# --- FUNCTII ---

def read_bmp_24bit(file_path):
    with open(file_path, 'rb') as f:
        file_header = f.read(14)
        if len(file_header) < 14:
            raise ValueError("Fisierul este prea mic pentru a fi un BMP")
        signature = file_header[0:2]
        if signature != b'BM':
            raise ValueError("Nu este un fisier BMP (semnatura invalida)")

        file_size = struct.unpack('<I', file_header[2:6])[0]
        data_offset = struct.unpack('<I', file_header[10:14])[0]

        info_header = f.read(40)
        if len(info_header) < 40:
            raise ValueError("Header-ul info BMP este incomplet")

        header_size = struct.unpack('<I', info_header[0:4])[0]
        width = struct.unpack('<i', info_header[4:8])[0]
        height = struct.unpack('<i', info_header[8:12])[0]
        planes = struct.unpack('<H', info_header[12:14])[0]
        bit_count = struct.unpack('<H', info_header[14:16])[0]
        compression = struct.unpack('<I', info_header[16:20])[0]
        image_size = struct.unpack('<I', info_header[20:24])[0]

        if bit_count != 24:
            raise ValueError(f"Sunt suportate doar BMP-uri pe 24 de biti")
        if compression != 0:
            raise ValueError("Sunt suportate doar BMP-uri fara compresie")

        bottom_up = height > 0
        abs_height = abs(height)
        row_size = ((width * 3 + 3) // 4) * 4

        f.seek(data_offset)

        pixels = []
        for _ in range(abs_height):
            row_data = f.read(row_size)
            if len(row_data) < row_size:
                raise ValueError("Sfarsit de fisier neasteptat")

            row_pixels = []
            for x in range(width):
                b = row_data[x*3]
                g = row_data[x*3 + 1]
                r = row_data[x*3 + 2]
                row_pixels.append([r, g, b])
            pixels.append(row_pixels)

        if bottom_up:
            pixels.reverse()

        return pixels

def draw_matrix(matrix):
    global current_photo
    height = len(matrix)
    width = len(matrix[0])

    photo = tk.PhotoImage(width=width, height=height)

    for y in range(height):
        for x in range(width):
            r, g, b = matrix[y][x]
            photo.put(f"#{r:02x}{g:02x}{b:02x}", (x, y))

    current_photo = photo
    img_label.config(image=current_photo)

def open_image_and_create_matrix():
    global original_matrix
    file_path = filedialog.askopenfilename(
        title="Deschide Imagine BMP",
        filetypes=[("Fisiere BMP", "*.bmp"), ("Toate fisierele", "*.*")]
    )

    if not file_path:
        return

    try:
        original_matrix = read_bmp_24bit(file_path)
        draw_matrix(original_matrix)
    except Exception as e:
        print(f"Eroare la citirea BMP: {e}")

def convert_to_grayscale(matrix):
    height = len(matrix)
    width = len(matrix[0])
    grayscale_matrix = []
    for y in range(height):
        row = []
        for x in range(width):
            r, g, b = matrix[y][x]
            gray_value = int((r + g + b) / 3)
            row.append([gray_value, gray_value, gray_value])
        grayscale_matrix.append(row)
    return grayscale_matrix

def calculate_histogram(matrix):
    width = len(matrix[0])
    height = len(matrix)

    histogram = [0] * 256

    for i in range(height):
        for j in range(width):
            r, g, b = matrix[i][j]
            gray = (r + g + b) // 3
            histogram[gray] += 1

    return histogram

def show_histogram(matrix):
    histogram = calculate_histogram(matrix)
    plt.figure("Histograma Imagine Gri")
    plt.bar(range(256), histogram, color='gray', width=1)
    plt.title("Histograma imaginii gri")
    plt.xlabel("Intensitate (0-255)")
    plt.ylabel("Numar pixeli")
    plt.xlim([0, 255])
    plt.tight_layout()
    plt.show()

def btn_action_histogram():
    if original_matrix:
        show_histogram(original_matrix)
    else:
        print("Eroare: Incarca o imagine mai intai!")

def calculate_moment_order1(matrix):
    height = len(matrix)
    width = len(matrix[0])

    M00 = 0
    M10 = 0
    M01 = 0

    for i in range(height):
        for j in range(width):
            r, g, b = matrix[i][j]
            gray = (r + g + b) // 3
            M00 += gray
            M10 += i * gray
            M01 += j * gray

    if M00 == 0:
        return None, None, M00, M10, M01

    centroid_x = M01 / M00
    centroid_y = M10 / M00

    return centroid_x, centroid_y, M00, M10, M01

def calculate_moment_order2(matrix):
    height = len(matrix)
    width = len(matrix[0])

    M00 = 0
    M10 = 0
    M01 = 0
    M20 = 0
    M02 = 0
    M11 = 0

    for i in range(height):
        for j in range(width):
            r, g, b = matrix[i][j]
            raw = (r + g + b) // 3
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

    mu20 = M20 / M00 - cy ** 2
    mu02 = M02 / M00 - cx ** 2
    mu11 = M11 / M00 - cx * cy

    import math
    if mu20 - mu02 == 0:
        theta_rad = math.pi / 4
    else:
        theta_rad = 0.5 * math.atan2(2 * mu11, mu20 - mu02)

    theta_deg = abs(math.degrees(theta_rad))

    return cx, cy, mu20, mu02, mu11, theta_rad, theta_deg

def btn_action_moment2():
    if original_matrix:
        result = calculate_moment_order2(original_matrix)
        if result is None:
            print("Imaginea este neagra, M00 = 0")
            return

        cx, cy, mu20, mu02, mu11, theta_rad, theta_deg = result

        print(f"Centroid: cx = {cx:.2f}, cy = {cy:.2f}")
        print(f"mu(2,0) = {mu20:.2f}  <- varianta pe verticala")
        print(f"mu(0,2) = {mu02:.2f}  <- varianta pe orizontala")
        print(f"mu(1,1) = {mu11:.2f}  <- covarianta")
        print(f"Unghi de rotatie: {theta_rad:.4f} rad = {theta_deg:.2f} grade")

        height = len(original_matrix)
        width = len(original_matrix[0])
        result_img = [row[:] for row in original_matrix]

        for di in range(-5, 6):
            for dj in range(-5, 6):
                ni, nj = int(cy) + di, int(cx) + dj
                if 0 <= ni < height and 0 <= nj < width:
                    result_img[ni][nj] = [255, 0, 0]

        show_in_new_window(result_img, f"Moment ordin 2 | Unghi: {theta_rad:.4f} rad = {theta_deg:.1f} grade")
    else:
        print("Eroare: Incarca o imagine mai intai!")

def calculate_projections(matrix):
    height = len(matrix)
    width = len(matrix[0])

    proj_H = [0] * height
    for i in range(height):
        for j in range(width):
            r, g, b = matrix[i][j]
            gray = (r + g + b) // 3
            proj_H[i] += gray

    proj_V = [0] * width
    for i in range(height):
        for j in range(width):
            r, g, b = matrix[i][j]
            gray = (r + g + b) // 3
            proj_V[j] += gray

    return proj_H, proj_V

def btn_action_projections():
    if original_matrix:
        proj_H, proj_V = calculate_projections(original_matrix)

        _, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        ax1.barh(range(len(proj_H)), proj_H, color='gray', height=1)
        ax1.set_title("Proiectie orizontala")
        ax1.set_xlabel("Suma pixeli pe linie")
        ax1.set_ylabel("Linie (i)")
        ax1.invert_yaxis()

        ax2.bar(range(len(proj_V)), proj_V, color='gray', width=1)
        ax2.set_title("Proiectie verticala")
        ax2.set_xlabel("Coloana (j)")
        ax2.set_ylabel("Suma pixeli pe coloana")

        plt.tight_layout()
        plt.show()
    else:
        print("Eroare: Incarca o imagine mai intai!")

def calculate_covariance_matrix(matrix):
    import math
    height = len(matrix)
    width = len(matrix[0])

    binary = get_binarized_matrix(matrix, threshold=128)

    M00 = 0
    M10 = 0
    M01 = 0
    M20 = 0
    M02 = 0
    M11 = 0

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

    mu20 = M20 / M00 - cy ** 2
    mu02 = M02 / M00 - cx ** 2
    mu11 = M11 / M00 - cx * cy

    cov_matrix = [
        [mu20, mu11],
        [mu11, mu02]
    ]

    return cx, cy, cov_matrix


def convert_to_yuv(matrix):
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
            y_f = int(max(0, min(255, y_val)))
            u_f = int(max(0, min(255, u_val + 128)))
            v_f = int(max(0, min(255, v_val + 128)))
            row.append([y_f, u_f, v_f])
        yuv_matrix.append(row)
    return yuv_matrix

def convert_to_ycbcr(matrix):
    height = len(matrix)
    width = len(matrix[0])
    ycbcr_matrix = []

    for y in range(height):
        row = []
        for x in range(width):
            r, g, b = matrix[y][x]

            y_val = 0.299 * r + 0.587 * g + 0.114 * b
            cb_val = 128 - 0.168736 * r - 0.331264 * g + 0.5 * b
            cr_val = 128 + 0.5 * r - 0.418688 * g - 0.081312 * b

            y_f = int(max(0, min(255, y_val)))
            cb_f = int(max(0, min(255, cb_val)))
            cr_f = int(max(0, min(255, cr_val)))

            row.append([y_f, cb_f, cr_f])
        ycbcr_matrix.append(row)
    return ycbcr_matrix

def get_binarized_matrix(matrix, threshold=128):
    height = len(matrix)
    width = len(matrix[0])
    binary_matrix = []

    for y in range(height):
        row = []
        for x in range(width):
            r, g, b = matrix[y][x]
            gray = (r + g + b) // 3
            if gray < threshold:
                val = 0
            else:
                val = 255
            row.append([val, val, val])
        binary_matrix.append(row)

    return binary_matrix

def apply_grayscale_filter():
    global original_matrix
    if original_matrix is not None:
        gray_matrix = convert_to_grayscale(original_matrix)
        draw_matrix(gray_matrix)
    else:
        print("Eroare: Incarca o imagine mai intai!")

def show_in_new_window(matrix, title):
    new_window = tk.Toplevel(root)
    new_window.title(title)
    height = len(matrix)
    width = len(matrix[0])
    photo = tk.PhotoImage(width=width, height=height)
    for y in range(height):
        for x in range(width):
            r, g, b = matrix[y][x]
            photo.put(f"#{r:02x}{g:02x}{b:02x}", (x, y))
    lbl = tk.Label(new_window, image=photo)
    lbl.image = photo
    lbl.pack()
    new_window.lift()
    new_window.focus_force()

def get_grayscale_variations(matrix):
    h, w = len(matrix), len(matrix[0])
    v1, v2, v3 = [], [], []
    for y in range(h):
        r1, r2, r3 = [], [], []
        for x in range(w):
            r, g, b = matrix[y][x]
            avg = int((r + g + b) / 3)
            lum = int(0.299*r + 0.587*g + 0.114*b)
            light = int((max(r, g, b) + min(r, g, b)) / 2)
            r1.append([avg, avg, avg])
            r2.append([lum, lum, lum])
            r3.append([light, light, light])
        v1.append(r1); v2.append(r2); v3.append(r3)
    return v1, v2, v3

def convert_to_hsv(matrix):
    height = len(matrix)
    width = len(matrix[0])
    hsv_matrix = []
    for y in range(height):
        row = []
        for x in range(width):
            R, G, B = matrix[y][x]
            r = R / 255
            g = G / 255
            b = B / 255

            M = max(r, g, b)
            m = min(r, g, b)
            C = M - m

            V = M

            if V != 0:
                S = C / V
            else:
                S = 0

            if C != 0:
                if M == r:
                    H = 60 * (g - b) / C
                elif M == g:
                    H = 120 + 60 * (b - r) / C
                else:
                    H = 240 + 60 * (r - g) / C
            else:
                H = 0

            if H < 0:
                H = H + 360

            H_norm = int(H * 255 / 360)
            S_norm = int(S * 255)
            V_norm = int(V * 255)

            row.append([H_norm, S_norm, V_norm])
        hsv_matrix.append(row)
    return hsv_matrix

def convert_to_cmy(matrix):
    cmy_matrix = []
    for row in matrix:
        new_row = [[255-r, 255-g, 255-b] for r, g, b in row]
        cmy_matrix.append(new_row)
    return cmy_matrix

def get_inverse_matrix(matrix):
    return [[[255-r, 255-g, 255-b] for r, g, b in row] for row in matrix]

def get_red_channel(matrix):
    return [[[pixel[0], 0, 0] for pixel in row] for row in matrix]

def get_green_channel(matrix):
    return [[[0, pixel[1], 0] for pixel in row] for row in matrix]

def get_blue_channel(matrix):
    return [[[0, 0, pixel[2]] for pixel in row] for row in matrix]

def btn_action_grayscale():
    if original_matrix:
        v1, v2, v3 = get_grayscale_variations(original_matrix)
        show_in_new_window(v1, "Media Aritmetica")
        show_in_new_window(v2, "Luminanta")
        show_in_new_window(v3, "Desaturare")
    else:
        print("Eroare: Incarca o imagine!")

def btn_action_cmy():
    if original_matrix:
        cmy = convert_to_cmy(original_matrix)
        show_in_new_window(cmy, "Imagine CMY")
    else:
        print("Eroare: Incarca o imagine!")

def btn_action_yuv():
    if original_matrix:
        yuv = convert_to_yuv(original_matrix)
        show_in_new_window(yuv, "Imagine YUV")
    else:
        print("Eroare: Incarca o imagine!")

def btn_action_ycbcr():
    if original_matrix:
        ycbcr_data = convert_to_ycbcr(original_matrix)
        show_in_new_window(ycbcr_data, "Imagine YCbCr")
    else:
        print("Eroare: Incarca o imagine!")

def btn_action_invers_si_canale():
    if original_matrix:
        inversa = get_inverse_matrix(original_matrix)
        show_in_new_window(inversa, "Imagine Inversa (Negativ)")

        rosu = get_red_channel(inversa)
        verde = get_green_channel(inversa)
        albastru = get_blue_channel(inversa)

        show_in_new_window(rosu, "Canal Rosu Inversat")
        show_in_new_window(verde, "Canal Verde Inversat")
        show_in_new_window(albastru, "Canal Albastru Inversat")
    else:
        print("Eroare: Incarca o imagine mai intai!")

def btn_action_binarizare():
    if original_matrix:
        binara = get_binarized_matrix(original_matrix, threshold=128)
        show_in_new_window(binara, "Imagine Binarizata (Alb-Negru)")
    else:
        print("Eroare: Incarca o imagine mai intai!")

def btn_action_hsv():
    if original_matrix:
        hsv = convert_to_hsv(original_matrix)
        show_in_new_window(hsv, "Imagine HSV")
    else:
        print("Eroare: Incarca o imagine mai intai!")

def btn_action_moment():
    if original_matrix:
        cx, cy, M00, M10, M01 = calculate_moment_order1(original_matrix)
        if cx is None:
            print("Imaginea este neagra, M00 = 0")
            return

        print(f"M(0,0) = {M00}")
        print(f"M(1,0) = {M10}")
        print(f"M(0,1) = {M01}")
        print(f"Centroid: cx = {cx:.2f}, cy = {cy:.2f}")

        height = len(original_matrix)
        width = len(original_matrix[0])
        result = [row[:] for row in original_matrix]

        for di in range(-5, 6):
            for dj in range(-5, 6):
                ni, nj = int(cy) + di, int(cx) + dj
                if 0 <= ni < height and 0 <= nj < width:
                    result[ni][nj] = [255, 0, 0]

        show_in_new_window(result, f"Centroid: ({cx:.1f}, {cy:.1f})")
    else:
        print("Eroare: Incarca o imagine mai intai!")

def btn_action_covariance():
    if original_matrix:
        result = calculate_covariance_matrix(original_matrix)
        if result is None:
            print("Imaginea este neagra, M00 = 0")
            return

        cx, cy, cov = result

        print(f"Centroid: cx = {cx:.2f}, cy = {cy:.2f}")
        print(f"Matricea de covarianta:")
        print(f"  | {cov[0][0]:12.2f}  {cov[0][1]:12.2f} |")
        print(f"  | {cov[1][0]:12.2f}  {cov[1][1]:12.2f} |")
    else:
        print("Eroare: Incarca o imagine mai intai!")

# --- BUTOANE TOOLBAR ---

btn_style = {
    "font": ("Arial", 10),
    "bg": "white",
    "fg": "black",
    "relief": "flat",
    "padx": 10,
    "pady": 4,
    "cursor": "",
}

btn_start = tk.Button(toolbar, text="Incarcare Imagine",
                      command=open_image_and_create_matrix, **btn_style)
btn_start.pack(side="left", padx=(6, 2), pady=4)

tk.Frame(toolbar, width=1, bg="#cccccc").pack(side="left", fill="y", padx=4, pady=4)

# Dropdown "Menu"
menu_btn = tk.Menubutton(toolbar, text="Menu \u25be", **btn_style)
menu_btn.pack(side="left", padx=2, pady=4)

dropdown = tk.Menu(menu_btn, tearoff=0)
menu_btn.config(menu=dropdown)

dropdown.add_command(label="Cele 3 Variante Gray",   command=btn_action_grayscale)
dropdown.add_command(label="Conversie CMY",           command=btn_action_cmy)
dropdown.add_command(label="Conversie YUV",           command=btn_action_yuv)
dropdown.add_command(label="Conversie YCbCr",         command=btn_action_ycbcr)
dropdown.add_separator()
dropdown.add_command(label="Invertire + Canale",      command=btn_action_invers_si_canale)
dropdown.add_command(label="Binarizare",              command=btn_action_binarizare)
dropdown.add_command(label="Conversie HSV",           command=btn_action_hsv)
dropdown.add_command(label="Histograma",              command=btn_action_histogram)
dropdown.add_separator()
dropdown.add_command(label="Moment Ordin 1",          command=btn_action_moment)
dropdown.add_command(label="Moment Ordin 2",          command=btn_action_moment2)
dropdown.add_command(label="Matrice Covarianta",      command=btn_action_covariance)
dropdown.add_command(label="Proiectii",               command=btn_action_projections)
dropdown.add_separator()
dropdown.add_command(label="Inchide aplicatia",       command=root.destroy)

root.mainloop()
