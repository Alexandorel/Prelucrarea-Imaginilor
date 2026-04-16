import math
import tkinter as tk
from tkinter import filedialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from bmp_reader import read_bmp_24bit
from conversions import (
    get_grayscale_variations, convert_to_yuv, convert_to_ycbcr,
    convert_to_cmy, convert_to_hsv, get_inverse_matrix,
    get_binarized_matrix, get_red_channel, get_green_channel, get_blue_channel,
    equalize_histogram, dilate_image, erode_image
)
from analysis import (
    get_histogram_figure, calculate_moment_order1, calculate_moment_order2,
    get_projections_figure, calculate_covariance_matrix, label_objects, select_object_by_label,
    calculate_object_orientation, calculate_elongation_direction
)

current_photo = None
original_matrix = None
current_labels = None
dilate_frame = None
dilate_entry = None
erode_frame = None
erode_entry = None

# --- CONFIGURARE FEREASTRA ---
root = tk.Tk()
root.title("Photo Shop - Vint Alexandru")
root.geometry("1100x800")
root.configure(bg='white')
root.resizable(True, True)

# --- TOOLBAR ---
toolbar = tk.Frame(root, bg='#f0f0f0', bd=1, relief='raised')
toolbar.pack(side='top', fill='x')

# --- ZONA TEXT (momente, covarianta) ---
result_label = tk.Label(root, bg='white', font=("Courier", 11), justify='left')
result_label.pack(side='bottom', pady=8)

# --- ZONA DE AFISARE ---
display_frame = tk.Frame(root, bg='white')
display_frame.pack(side='top', fill='both', expand=True, pady=10)


# --- FUNCTII UI ---

def clear_display():
    for widget in display_frame.winfo_children():
        widget.destroy()
    result_label.config(text='')


def draw_matrix(matrix):
    global current_photo
    clear_display()
    height = len(matrix)
    width = len(matrix[0])
    photo = tk.PhotoImage(width=width, height=height)
    for y in range(height):
        for x in range(width):
            r, g, b = matrix[y][x]
            photo.put(f"#{r:02x}{g:02x}{b:02x}", (x, y))
    current_photo = photo
    lbl = tk.Label(display_frame, image=current_photo, bg='white')
    lbl.pack()


def show_figure_in_main(fig):
    clear_display()
    canvas = FigureCanvasTkAgg(fig, master=display_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)
    plt.close(fig)


def show_text_in_main(text):
    result_label.config(text=text)


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
    new_window.bind('<FocusIn>', lambda e: new_window.lift())


def matrix_to_np(matrix):
    return np.array(matrix, dtype=np.uint8)


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


def btn_action_grayscale():
    if original_matrix:
        v1, v2, v3 = get_grayscale_variations(original_matrix)
        fig, axes = plt.subplots(1, 3, figsize=(12, 4))
        for ax, m, title in zip(axes, [v1, v2, v3], ["Media Aritmetica", "Luminanta", "Desaturare"]):
            ax.imshow(matrix_to_np(m))
            ax.set_title(title)
            ax.axis('off')
        fig.tight_layout()
        show_figure_in_main(fig)
    else:
        print("Eroare: Incarca o imagine!")


def btn_action_cmy():
    if original_matrix:
        draw_matrix(convert_to_cmy(original_matrix))
    else:
        print("Eroare: Incarca o imagine!")


def btn_action_yuv():
    if original_matrix:
        draw_matrix(convert_to_yuv(original_matrix))
    else:
        print("Eroare: Incarca o imagine!")


def btn_action_ycbcr():
    if original_matrix:
        draw_matrix(convert_to_ycbcr(original_matrix))
    else:
        print("Eroare: Incarca o imagine!")


def btn_action_invers_si_canale():
    if original_matrix:
        inversa = get_inverse_matrix(original_matrix)
        imagini = [
            (inversa,                    "Inversa (Negativ)"),
            (get_red_channel(inversa),   "Canal Rosu"),
            (get_green_channel(inversa), "Canal Verde"),
            (get_blue_channel(inversa),  "Canal Albastru"),
        ]
        fig, axes = plt.subplots(1, 4, figsize=(16, 4))
        for ax, (m, title) in zip(axes, imagini):
            ax.imshow(matrix_to_np(m))
            ax.set_title(title)
            ax.axis('off')
        fig.tight_layout()
        show_figure_in_main(fig)
    else:
        print("Eroare: Incarca o imagine mai intai!")


def btn_action_binarizare():
    if original_matrix:
        draw_matrix(get_binarized_matrix(original_matrix, threshold=128))
    else:
        print("Eroare: Incarca o imagine mai intai!")


def btn_action_hsv():
    if original_matrix:
        draw_matrix(convert_to_hsv(original_matrix))
    else:
        print("Eroare: Incarca o imagine mai intai!")


def btn_action_histogram():
    if original_matrix:
        show_figure_in_main(get_histogram_figure(original_matrix))
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


def btn_action_equalize():
    if original_matrix:
        draw_matrix(equalize_histogram(original_matrix))
    else:
        print("Eroare: Incarca o imagine mai intai!")


def apply_dilation_n_times():
    if not original_matrix:
        print("Eroare: Incarca o imagine mai intai!")
        return
    try:
        n = int(dilate_entry.get())
    except ValueError:
        print("Introdu un numar valid (intreg)")
        return
    if n < 1:
        print("Numarul de iteratii trebuie sa fie >= 1")
        return
    result = get_binarized_matrix(original_matrix, threshold=128)
    for _ in range(n):
        result = dilate_image(result)
    draw_matrix(result)
    show_text_in_main(f"Dilatare aplicata de {n} ori")


def btn_action_dilate():
    global dilate_frame, dilate_entry
    if not original_matrix:
        print("Eroare: Incarca o imagine mai intai!")
        return
    if dilate_frame is None:
        dilate_frame = tk.Frame(toolbar, bg='#f0f0f0')
        dilate_frame.pack(side="left", padx=4, pady=4)
        tk.Label(dilate_frame, text="Iteratii:", bg='#f0f0f0',
                 font=("Arial", 10)).pack(side="left", padx=(4, 2))
        dilate_entry = tk.Entry(dilate_frame, width=4, font=("Arial", 10))
        dilate_entry.insert(0, "1")
        dilate_entry.pack(side="left", padx=2)
        tk.Button(dilate_frame, text="Aplica Dilatare",
                  command=apply_dilation_n_times, **btn_style).pack(side="left", padx=2)
    apply_dilation_n_times()


def apply_erosion_n_times():
    if not original_matrix:
        print("Eroare: Incarca o imagine mai intai!")
        return
    try:
        n = int(erode_entry.get())
    except ValueError:
        print("Introdu un numar valid (intreg)")
        return
    if n < 1:
        print("Numarul de iteratii trebuie sa fie >= 1")
        return
    result = get_binarized_matrix(original_matrix, threshold=128)
    for _ in range(n):
        result = erode_image(result)
    draw_matrix(result)
    show_text_in_main(f"Eroziune aplicata de {n} ori")


def btn_action_erode():
    global erode_frame, erode_entry
    if not original_matrix:
        print("Eroare: Incarca o imagine mai intai!")
        return
    if erode_frame is None:
        erode_frame = tk.Frame(toolbar, bg='#f0f0f0')
        erode_frame.pack(side="left", padx=4, pady=4)
        tk.Label(erode_frame, text="Iteratii:", bg='#f0f0f0',
                 font=("Arial", 10)).pack(side="left", padx=(4, 2))
        erode_entry = tk.Entry(erode_frame, width=4, font=("Arial", 10))
        erode_entry.insert(0, "1")
        erode_entry.pack(side="left", padx=2)
        tk.Button(erode_frame, text="Aplica Eroziune",
                  command=apply_erosion_n_times, **btn_style).pack(side="left", padx=2)
    apply_erosion_n_times()


def btn_action_orientation():
    if original_matrix:
        angle_rad = calculate_object_orientation(original_matrix)
        angle_deg = math.degrees(angle_rad)
        print(f"Orientare obiect: {angle_rad:.4f} rad = {angle_deg:.2f} grade")
    else:
        print("Eroare: Incarca o imagine mai intai!")


def btn_action_projections():
    if original_matrix:
        show_figure_in_main(get_projections_figure(original_matrix))
    else:
        print("Eroare: Incarca o imagine mai intai!")


def on_label_click(event):
    global current_labels
    if current_labels is None or original_matrix is None:
        return
    x, y = event.x, event.y
    height = len(current_labels)
    width = len(current_labels[0])
    if 0 <= y < height and 0 <= x < width:
        label_id = current_labels[y][x]
        if label_id == 0:
            show_text_in_main("Ai selectat fundalul (eticheta 0)")
            return
        result = select_object_by_label(original_matrix, current_labels, label_id)
        show_in_new_window(result, f"Obiect cu eticheta {label_id}")

        angle_rad = calculate_elongation_direction(original_matrix, current_labels, label_id)
        if angle_rad is not None:
            angle_deg = math.degrees(angle_rad)
            print(f"Eticheta {label_id} | Directie alungire: {angle_rad:.4f} rad = {angle_deg:.2f} grade")
            show_text_in_main(f"Eticheta {label_id} | Directie alungire: {angle_rad:.4f} rad = {angle_deg:.2f} grade")
        else:
            print(f"Eticheta {label_id} | Nu s-a putut calcula directia de alungire")
            show_text_in_main(f"Obiect selectat: eticheta {label_id}")


def btn_action_etichetare():
    global current_labels
    if original_matrix:
        colored, labels = label_objects(original_matrix)
        current_labels = labels
        clear_display()
        height = len(colored)
        width = len(colored[0])
        photo = tk.PhotoImage(width=width, height=height)
        for y in range(height):
            for x in range(width):
                r, g, b = colored[y][x]
                photo.put(f"#{r:02x}{g:02x}{b:02x}", (x, y))
        current_photo_ref = photo
        lbl = tk.Label(display_frame, image=photo, bg='white', cursor='crosshair')
        lbl.image = photo
        lbl.pack()
        lbl.bind("<Button-1>", on_label_click)
        show_text_in_main("Click pe un obiect din imagine pentru a-l selecta")
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

btn_reset = tk.Button(toolbar, text="Resetare",
                      command=lambda: draw_matrix(original_matrix) if original_matrix else None,
                      **btn_style)
btn_reset.pack(side="left", padx=(2, 2), pady=4)

tk.Frame(toolbar, width=1, bg="#cccccc").pack(side="left", fill="y", padx=4, pady=4)

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
dropdown.add_command(label="Egalizare Histograma",    command=btn_action_equalize)
dropdown.add_command(label="Dilatare",                command=btn_action_dilate)
dropdown.add_command(label="Eroziune",                command=btn_action_erode)
dropdown.add_separator()
dropdown.add_command(label="Moment Ordin 1",          command=btn_action_moment)
dropdown.add_command(label="Moment Ordin 2",          command=btn_action_moment2)
dropdown.add_command(label="Matrice Covarianta",      command=btn_action_covariance)
dropdown.add_command(label="Proiectii",               command=btn_action_projections)
dropdown.add_command(label="Orientare obiect",        command=btn_action_orientation)
dropdown.add_command(label="Etichetare",              command=btn_action_etichetare)
dropdown.add_separator()
dropdown.add_command(label="Inchide aplicatia",       command=root.destroy)
