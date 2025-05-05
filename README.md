# Torus Tiling

**A Python application for optimizing tile arrangements on a torus surface**

---

## Table of Contents

* [Overview](#overview)
* [Features](#features)
* [Requirements](#requirements)
* [Installation](#installation)
* [Building Executables](#building-executables)

  * [Windows (.exe)](#windows-exe)
  * [Linux (Ubuntu)](#linux-ubuntu)
* [GUI Settings](#gui-settings)
* [Usage](#usage)
* [Saving Results](#saving-results)
* [Project Structure](#project-structure)
* [License](#license)

---

## Overview

This project solves the **torus tiling** problem using Google OR-Tools’ CP-SAT solver. It provides a graphical interface built with Tkinter and visualizations via Matplotlib, allowing you to:

* Define a toroidal grid (width × height) of cells.
* Place rectangular tiles under periodic boundary conditions.
* Optimize packing (maximize number of tiles or cover specific patterns).

---

## Features

* **Automatic solver**: Uses CP-SAT to find optimal packings.
* **Flexible grid**: Configure torus dimensions.
* **Custom tile sizes**: Specify tile width and height.
* **GUI controls**: Easily adjust parameters and run the solver.
* **Visualization**: Display the resulting tiling and save as an image.

---

## Requirements

* Python 3.8 or higher
* [OR-Tools](https://developers.google.com/optimization) (`ortools`)
* [Matplotlib](https://matplotlib.org/) (`matplotlib`)
* [Pillow](https://python-pillow.org/) (`Pillow`)
* Tkinter (usually included with Python)

All external dependencies are listed in `requirements.txt`.

---

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/SebastianGruza/TorusTiling.git
   cd TorusTiling
   ```
2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv        # Windows/macOS/Linux
   source .venv/bin/activate   # macOS/Linux
   .\.venv\Scripts\activate  # Windows PowerShell
   ```
3. Install dependencies:

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## Building Executables

### Windows (.exe)

Use PyInstaller to bundle into a single executable:

```powershell
pip install pyinstaller
pyinstaller \
  --onefile \
  --windowed \
  --name TorusTiling \
  --add-data "core;core" \
  --collect-binaries ortools \
  gui\gui.py
```

The generated `TorusTiling.exe` will be in the `dist/` folder.

### Linux (Ubuntu)

Option 1: PyInstaller on Ubuntu

```bash
sudo apt install python3-tk
pip install pyinstaller
pyinstaller \
  --onefile \
  --name TorusTilingLinux \
  --add-data "core:core" \
  gui/gui.py
chmod +x dist/TorusTilingLinux
```

Option 2: Run from source (no bundling)

```bash
python -m gui.gui
```

---

## GUI Settings

When you launch the application, the GUI presents the following controls:

| Control            | Description                                       |
| ------------------ | ------------------------------------------------- |
| **Grid Width**     | Number of columns on the torus.                   |
| **Grid Height**    | Number of rows on the torus.                      |
| **Tile Width**     | Width of each rectangular tile (in cells).        |
| **Tile Height**    | Height of each rectangular tile (in cells).       |
| **Time Limit (s)** | Maximum solver runtime.                           |
| **Objective**      | Choose between maximizing tile count or coverage. |
| **Show Grid**      | Toggle drawing of grid lines on the canvas.       |
| **Buttons**        | \[Solve], \[Reset], \[Save Image]                 |

Adjust these parameters, then click **Solve** to compute the tiling.

---

## Usage

1. Run the application:

   ```bash
   python -m gui.gui
   ```
2. Enter your desired **Grid Width**, **Grid Height**, **Tile Width**, **Tile Height**, and **Time Limit**.
3. Select the **Objective** (e.g., maximize number of tiles).
4. (Optional) Toggle **Show Grid** for clearer visuals.
5. Click **Solve** and wait for the result.
6. View the tiling on the embedded Matplotlib canvas.

---

## Saving Results

* **Save Image** button: export the current tiling view as a PNG file.
* The file will be saved in the working directory with a timestamped name (e.g., `tiling_2025-05-05_15-30.png`).

---

## Project Structure

```
TorusTiling/
├── core/
│   ├── __init__.py   # Core solver and drawing logic
│   └── tiling.py     # Tiling model and helper functions
├── gui/
│   ├── __init__.py   # GUI package initializer
│   └── gui.py        # Tkinter interface and event loop
├── dist/             # Generated executables (gitignored)
├── requirements.txt  # Python dependencies
├── README.md         # This file
└── .gitignore        # Patterns to ignore
```

---

## License

This project is released under the [MIT License](LICENSE).
