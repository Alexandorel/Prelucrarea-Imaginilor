
# Prelucrare Imaginilor
Repository destinat materiei "Prelucrarea Imaginilor"


## Cerinte
Limbaj de programare:
```http
  Python 3.14.3
```

Bilioteci necesare:
```http
  pip install matplotlib numpy
```

## Rulare

```http
  python app.py
```

## Descriere
Aplicatie desktop pentru prelucrarea imaginilor BMP pe 24 de biti.
Permite incarcarea, vizualizarea si aplicarea de transformari asupra imaginilor.

## Structura proiectului
- `app.py` — punctul de intrare al aplicatiei
- `ui.py` — interfata grafica (fereastra, toolbar, butoane)
- `bmp_reader.py` — citirea fisierelor BMP pe 24 de biti
- `conversions.py` — conversii de spatiu de culoare
- `analysis.py` — histograma, momente, proiectii, covarianta

## Functionalitati
- Incarcare imagini BMP pe 24 de biti
- Conversii: Grayscale (3 variante), CMY, YUV, YCbCr, HSV
- Invertire imagine si extragere canale RGB
- Binarizare
- Histograma imaginii in tonuri de gri
- Calcul momente de ordinul 1 si 2 cu afisarea centroidului
- Calcul matrice de covarianta
- Proiectii orizontale si verticale

## Capturi de Ecran

Imagine originala:
![Imagine originală](screenshots/s2.png)
Imagine CMY:
![Imagine CMY](screenshots/s3.png)
Histograma:
![Histogramă](screenshots/s1.png)

