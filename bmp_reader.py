import struct


def read_bmp_24bit(file_path):
    with open(file_path, 'rb') as f:
        # Citire file header (14 bytes): semnatura, dimensiune, offset date pixeli
        file_header = f.read(14)
        if len(file_header) < 14:
            raise ValueError("Fisierul este prea mic pentru a fi un BMP")
        if file_header[0:2] != b'BM':
            raise ValueError("Nu este un fisier BMP (semnatura invalida)")

        # Offset-ul indica unde incep datele efective ale pixelilor in fisier
        data_offset = struct.unpack('<I', file_header[10:14])[0]

        # Citire info header (40 bytes): dimensiuni, biti/pixel, compresie
        info_header = f.read(40)
        if len(info_header) < 40:
            raise ValueError("Header-ul info BMP este incomplet")

        width      = struct.unpack('<i', info_header[4:8])[0]
        height     = struct.unpack('<i', info_header[8:12])[0]
        bit_count  = struct.unpack('<H', info_header[14:16])[0]
        compression = struct.unpack('<I', info_header[16:20])[0]

        if bit_count != 24:
            raise ValueError("Sunt suportate doar BMP-uri pe 24 de biti")
        if compression != 0:
            raise ValueError("Sunt suportate doar BMP-uri fara compresie")

        # Height pozitiv => imaginea e stocata de jos in sus (bottom-up)
        bottom_up = height > 0
        abs_height = abs(height)

        # Fiecare rand este aliniat la multiplu de 4 bytes
        row_size = ((width * 3 + 3) // 4) * 4

        f.seek(data_offset)

        pixels = []
        for _ in range(abs_height):
            row_data = f.read(row_size)
            if len(row_data) < row_size:
                raise ValueError("Sfarsit de fisier neasteptat")
            row_pixels = []
            for x in range(width):
                # BMP stocheaza canalele in ordinea BGR, nu RGB
                b = row_data[x * 3]
                g = row_data[x * 3 + 1]
                r = row_data[x * 3 + 2]
                row_pixels.append([r, g, b])
            pixels.append(row_pixels)

        # Inversam randurile pentru a obtine ordinea top-down
        if bottom_up:
            pixels.reverse()

        return pixels
