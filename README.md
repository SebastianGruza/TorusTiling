# Torus Tiling

**A Python application for generating non-trivial tile arrangements with toroidal continuity**

---

## Table of Contents

* [Overview](#overview)
* [Core Principles](#core-principles)
* [GUI Features](#gui-features)
* [Requirements](#requirements)
* [Installation](#installation)
* [Running the Application](#running-the-application)
* [Building Executables](#building-executables)
* [Saving Results](#saving-results)
* [Project Structure](#project-structure)
* [License](#license)

---

## Overview

This project solves the **torus tiling** problem using [Google OR-Tools](https://developers.google.com/optimization) and provides a visual, user-friendly interface via Tkinter.

It allows the user to design a tiling layout using multiple tile formats and automatically finds a non-trivial periodic layout that satisfies a strict set of geometric constraints. The resulting pattern is displayed in a **3×3 toroidal tiling preview**, demonstrating seamless periodicity.

---

![Screenshot TorusTiling](images/Screenshot.jpg)

---

## Core Principles

The solver must place tiles according to these rules:

1. **No overlaps** – tiles must not cover the same area.
2. **No gaps** – the entire surface must be perfectly filled.
3. **Toroidal continuity** – top edge must match the bottom, and left edge must match the right.
4. **Non-trivial boundaries** – straight uninterrupted edges are disallowed.
5. **Tile diversity** – every tile format listed must appear at least once.
6. **Labeling** – each tile is marked with its ID.
7. **Visual output** – shows a 3×3 tiling grid (central tile plus its eight toroidal neighbors).
8. **Optimization** – tile usage is weighted by user-defined cost, and solutions are optimized accordingly.

---

## GUI Features

The graphical interface offers the following:

### **Tile Types Table**
Define tile formats with parameters:
- **ID** – unique integer label
- **Width / Height (cm)** – real-world dimensions
- **Cost** – optimization weight
- **Min / Max Count** – constraints on usage count

Buttons:
- `Add type` – insert a new tile row with default values
- `Edit type` – modify selected row values
- `Remove type` – delete selected tile entry

### **Solver Parameters**
- **Width / Height (cm)** – dimensions of the tiling surface
- **Grid Size (cm)** – unit of discretization (auto-computed from tile GCD)
- **Max Time (s)** – time budget for the solver
- **Workers** – number of threads
- **Enforce wrap** – require top/bottom and left/right continuity
- **No straight lines** – prohibit uninterrupted straight seams
- **4-corner penalty** – weight to discourage perfect 2×2 tile alignment

### **Preview**
- Dynamically updated image showing the tiling pattern
- Central layout plus eight neighbors for visual verification of toroidal constraints

### **Buttons**
- `Solve` – launch the OR-Tools solver
- `Save image` – export preview to PNG

---

## Requirements

* Python 3.8+
* [OR-Tools](https://developers.google.com/optimization)
* [Matplotlib](https://matplotlib.org/)
* [Pillow](https://python-pillow.org/)
* Tkinter (usually bundled with Python)

---

## Installation

```bash
git clone https://github.com/SebastianGruza/TorusTiling.git
cd TorusTiling

python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.\.venv\Scripts\activate    # Windows

pip install -r requirements.txt
```

---

## Running the Application

```bash
python -m gui.gui
```

Fill in the tile types, adjust constraints, and click **Solve** to view the result.

---

## Building Executables

### Windows (.exe)

```powershell
pip install pyinstaller
pyinstaller ^
  --onefile ^
  --windowed ^
  --name TorusTiling ^
  --add-data "core;core" ^
  --collect-binaries ortools ^
  gui\gui.py
```

### Linux (Ubuntu)

```bash
sudo apt install python3-tk
pip install pyinstaller
pyinstaller   --onefile   --name TorusTilingLinux   --add-data "core:core"   gui/gui.py
```

Or run directly:

```bash
python -m gui.gui
```

---

## Saving Results

Click **Save image** to export the current preview as PNG. You will be prompted to choose the file location.

---

## Project Structure

```
TorusTiling/
├── core/
│   └── tiling.py      # Solver and visualization logic
├── gui/
│   └── gui.py         # Tkinter interface
├── requirements.txt
├── README.md
└── ...
```

---

## License

Released under the [MIT License](LICENSE).



---

# Torus Tiling (wersja polska)

**Aplikacja w Pythonie do generowania nietrywialnych układów płytek z ciągłością toroidalną**

---

## Spis treści

* [Opis](#opis)
* [Zasady działania](#zasady-działania)
* [Funkcje GUI](#funkcje-gui)
* [Wymagania](#wymagania)
* [Instalacja](#instalacja)
* [Uruchamianie aplikacji](#uruchamianie-aplikacji)
* [Budowanie pliku wykonywalnego](#budowanie-pliku-wykonywalnego)
* [Zapisywanie wyników](#zapisywanie-wyników)
* [Struktura projektu](#struktura-projektu)
* [Licencja](#licencja)

---

## Opis

Projekt rozwiązuje problem **układania płytek na torusie** przy użyciu [Google OR-Tools](https://developers.google.com/optimization) i udostępnia przyjazny graficzny interfejs zbudowany w Tkinterze.

Pozwala użytkownikowi zdefiniować różne formaty płytek i automatycznie znaleźć nietrywialny periodyczny układ, który spełnia zestaw rygorystycznych ograniczeń geometrycznych. Wynikowy wzór wyświetlany jest w formie **podglądu układu 3×3**, pokazującego ciągłość toroidalną.

---

## Zasady działania

Układanie płytek musi spełniać następujące reguły:

1. **Brak nakładania** – płytki nie mogą się pokrywać.
2. **Brak dziur** – cała powierzchnia musi być dokładnie pokryta.
3. **Ciągłość toroidalna** – górna krawędź musi pasować do dolnej, a lewa do prawej.
4. **Nietrywialne krawędzie** – niedozwolone są proste nieprzerwane linie na brzegach.
5. **Różnorodność płytek** – każda zdefiniowana płytka musi wystąpić co najmniej raz.
6. **Etykiety** – każda płytka oznaczona jest swoim ID.
7. **Wizualizacja** – rysunek zawiera centralny układ oraz jego sąsiadów (3×3).
8. **Optymalizacja** – użycie płytek uwzględnia zadane koszty, a rozwiązanie jest optymalne względem tych wag.

---

## Funkcje GUI

Interfejs graficzny zawiera:

### **Tabela płytek**
Możliwość zdefiniowania płytek z parametrami:
- **ID** – unikalny numer
- **Szerokość / Wysokość (cm)** – rozmiar fizyczny płytki
- **Koszt** – waga w funkcji celu, solver minimalizuje łączny koszt
- **Min / Max liczba** – minimalna i maksymalna liczba użyć

Przyciski:
- `Add type` – dodaje nowy wiersz z domyślnymi wartościami
- `Edit type` – edytuje zaznaczony wiersz
- `Remove type` – usuwa zaznaczony wiersz

### **Parametry solwera**
- **Szerokość / Wysokość (cm)** – wymiary powierzchni
- **Rozmiar siatki (cm)** – jednostka dyskretyzacji
- **Max czas (s)** – limit czasu działania solvera
- **Liczba wątków** – równoległość przeszukiwania
- **Enforce wrap** – wymuszanie ciągłości brzegów
- **No straight lines** – zakaz długich linii przebiegających w całości przez krawędzie płytek
- **4-corner penalty** – kara za punkty, w których łączą się 4 krawędzie płytek (solver unika sytuacji, że w jednym punkcie zbiegają się 4 krawędzie płytek)

### **Podgląd**
- Dynamicznie aktualizowany rysunek z układem
- Pokazuje centralny blok i ośmiu sąsiadów toroidalnych

### **Przyciski**
- `Solve` – uruchamia solver
- `Save image` – zapisuje podgląd jako PNG

---

## Wymagania

* Python 3.8 lub nowszy
* [OR-Tools](https://developers.google.com/optimization)
* [Matplotlib](https://matplotlib.org/)
* [Pillow](https://python-pillow.org/)
* Tkinter (zwykle dołączony do Pythona)

---

## Instalacja

```bash
git clone https://github.com/SebastianGruza/TorusTiling.git
cd TorusTiling

python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.\.venv\Scripts\activate    # Windows

pip install -r requirements.txt
```

---

## Uruchamianie aplikacji

```bash
python -m gui.gui
```

Wypełnij dane o płytkach, dostosuj ograniczenia i kliknij **Solve**, by zobaczyć wynik.

---

## Budowanie pliku wykonywalnego

### Windows (.exe)

```powershell
pip install pyinstaller
pyinstaller ^
  --onefile ^
  --windowed ^
  --name TorusTiling ^
  --add-data "core;core" ^
  --collect-binaries ortools ^
  gui\gui.py
```

### Linux (Ubuntu)

```bash
sudo apt install python3-tk
pip install pyinstaller
pyinstaller   --onefile   --name TorusTilingLinux   --add-data "core:core"   gui/gui.py
```

Lub uruchomienie bezpośrednio:

```bash
python -m gui.gui
```

---

## Zapisywanie wyników

Kliknij **Save image**, by zapisać podgląd jako PNG. Wybierz miejsce zapisania pliku.

---

## Struktura projektu

```
TorusTiling/
├── core/
│   └── tiling.py      # Logika solvera i rysowania
├── gui/
│   └── gui.py         # Interfejs użytkownika w Tkinterze
├── requirements.txt
├── README.md
└── ...
```

---

## Licencja

Projekt jest udostępniony na licencji [MIT](LICENSE).
