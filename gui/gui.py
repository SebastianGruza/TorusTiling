from PIL import Image, ImageTk
from tkinter import ttk, messagebox, filedialog

from PIL import ImageTk

from core.tiling import TilingConfig, solve_torus_tiling, draw_tiling
from functools import reduce
from math import gcd


import tkinter as tk
from tkinter import ttk

class TilingApp(tk.Tk):

    DEFAULT_TILE_TYPES = [
        (1, 20, 20, 2,  1, 100),
        (2, 40, 20, 3,  1, 100),
        (3, 40, 40, 5,  1, 100),
        (4, 60, 40, 7,  1, 100),
        (5, 60, 60, 9,  1, 100),
    ]
    def __init__(self):
        super().__init__()
        self.title("Torus Tiling Solver")
        self.last_image = None
        self._current_tkimg = None
        self._build_widgets()

    def _build_widgets(self):
        # ─── Tile types list ────────────────────────────────────────
        types_frame = ttk.LabelFrame(self, text="Tile Types")
        types_frame.pack(fill="x", padx=10, pady=5)

        cols = ("id", "width", "height", "weight", "min_count", "max_count")
        self.tree_types = ttk.Treeview(types_frame, columns=cols, show="headings", height=6)
        for col, heading in zip(cols, ("ID", "Width (cm)", "Height (cm)", "Cost", "Min", "Max")):
            self.tree_types.heading(col, text=heading)
            self.tree_types.column(col, width=80, anchor="center")
        self.tree_types.pack(side="left", fill="x", expand=True)

        # scrollbar
        scrollbar = ttk.Scrollbar(types_frame, orient="vertical", command=self.tree_types.yview)
        self.tree_types.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="left", fill="y")

        # buttons
        btn_frame = ttk.Frame(types_frame)
        btn_frame.pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Add type", command=self._add_type).pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="Remove type", command=self._remove_type).pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="Edit type", command=self._edit_type).pack(fill="x", pady=2)

        # ─── Default rows ───────────────────────────────────────────
        for tid, w, h, wt, mn, mx in self.DEFAULT_TILE_TYPES:
            self.tree_types.insert("", "end", values=(tid, w, h, wt, mn, mx))

        # ─── Solver parameters ───────────────────────────────────────
        params_frame = ttk.LabelFrame(self, text="Solver Parameters")
        params_frame.pack(fill="x", padx=10, pady=5)

        # floor dimensions
        ttk.Label(params_frame, text="Width (cm):").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.width_var = tk.IntVar(value=120)
        ttk.Entry(params_frame, textvariable=self.width_var).grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(params_frame, text="Height (cm):").grid(row=0, column=2, sticky="e", padx=5, pady=2)
        self.height_var = tk.IntVar(value=120)
        ttk.Entry(params_frame, textvariable=self.height_var).grid(row=0, column=3, padx=5, pady=2)

        # default grid_size 10
        ttk.Label(params_frame, text="Grid Size (cm):").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.grid_size_var = tk.IntVar(value=10)
        ttk.Entry(params_frame, textvariable=self.grid_size_var).grid(row=1, column=1, padx=5, pady=2)

        # max time
        ttk.Label(params_frame, text="Max Time (s):").grid(row=1, column=2, sticky="e", padx=5, pady=2)
        self.time_var = tk.DoubleVar(value=60.0)
        ttk.Entry(params_frame, textvariable=self.time_var).grid(row=1, column=3, padx=5, pady=2)

        # workers
        ttk.Label(params_frame, text="Workers:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.workers_var = tk.IntVar(value=8)
        ttk.Entry(params_frame, textvariable=self.workers_var).grid(row=2, column=1, padx=5, pady=2)

        # checkbuttons
        self.wrap_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(params_frame, text="Enforce wrap", variable=self.wrap_var)\
            .grid(row=2, column=2, padx=5, pady=2)
        self.no_lines_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(params_frame, text="No straight lines", variable=self.no_lines_var)\
            .grid(row=2, column=3, padx=5, pady=2)

        # four-corner penalty
        ttk.Label(params_frame, text="4-corner penalty:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        self.penalty_var = tk.StringVar(value="50")
        ttk.Entry(params_frame, textvariable=self.penalty_var).grid(row=3, column=1, padx=5, pady=2)

        # ─── Preview ────────────────────────────────────────────────
        self.preview_frame = ttk.LabelFrame(self, text="Preview")
        self.preview_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # This must be tk.Canvas, not ttk!
        self.preview_canvas = tk.Canvas(self.preview_frame, bg="white")
        self.preview_canvas.pack(fill="both", expand=True)

        # Bind resize event on the frame or the canvas:
        self.preview_canvas.bind("<Configure>", self._update_preview)

        # ─── Buttons ────────────────────────────────────────────────
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=5)
        self.solve_btn = ttk.Button(btn_frame, text="Solve", command=self._on_solve)
        self.solve_btn.pack(side="left")
        self.save_btn = ttk.Button(btn_frame, text="Save image", command=self._on_save_image)
        self.save_btn.pack(side="right")

    def _add_type(self):
        # Add a row with default values
        ids = [int(self.tree_types.set(i, "id")) for i in self.tree_types.get_children()]
        new_id = max(ids) + 1 if ids else 1
        self.tree_types.insert(
            "", "end",
            values=(new_id, 90, 60, 30, 1, 2)
        )

    def _update_preview(self, event=None):
        # Ensure preview_canvas exists and there's an image
        if not hasattr(self, "preview_canvas") or self.last_image is None:
            return

        w = self.preview_canvas.winfo_width()
        h = self.preview_canvas.winfo_height()
        if w < 10 or h < 10:
            return

        orig_w, orig_h = self.last_image.size
        scale = min(w/orig_w, h/orig_h, 1.0)
        new_size = (int(orig_w*scale), int(orig_h*scale))

        resized = self.last_image.resize(new_size, resample=Image.Resampling.LANCZOS)
        self._current_tkimg = ImageTk.PhotoImage(resized)

        # Remove previous image and draw new one centered
        self.preview_canvas.delete("IMG")
        self.preview_canvas.create_image(
            w//2, h//2,
            image=self._current_tkimg,
            anchor="center",
            tags="IMG"
        )

    def _remove_type(self):
        # Remove selected rows
        for item in self.tree_types.selection():
            self.tree_types.delete(item)

    def _on_solve(self):

        self.config(cursor="watch")
        self.preview_canvas.config(cursor="watch")
        self.solve_btn.config(state="disabled")
        self.save_btn.config(state="disabled")
        self.update_idletasks()
        try:
            try:
                # 1) Read tile types from Treeview
                items = self.tree_types.get_children()
                if not items:
                    raise ValueError("You must add at least one tile type.")
                formats = {}
                weights = {}
                min_counts = {}
                max_counts = {}
                for item in items:
                    vals = self.tree_types.item(item, "values")
                    tid = int(vals[0])
                    w_cm = int(vals[1])
                    h_cm = int(vals[2])
                    wt = float(vals[3])
                    mn = int(vals[4])
                    mx = int(vals[5])
                    formats[tid] = (w_cm, h_cm)
                    weights[tid] = wt
                    if mn > 0:
                        min_counts[tid] = mn
                    if mx > 0:
                        max_counts[tid] = mx

                # 2) Read floor dimensions
                width = int(self.width_var.get())
                height = int(self.height_var.get())

                # 3) Auto-calculate grid_size based on the GCD of all dimensions
                all_dims = [d for dims in formats.values() for d in dims]
                grid_size = reduce(gcd, all_dims)

                # 4) Build configuration
                cfg = TilingConfig(
                    formats=formats,
                    weights=weights,
                    grid_size=grid_size,
                    max_time_in_seconds=float(self.time_var.get()),
                    num_search_workers=int(self.workers_var.get()),
                    min_counts=min_counts,
                    max_counts=max_counts,
                    enforce_wrap=self.wrap_var.get(),
                    enforce_no_straight_lines=self.no_lines_var.get(),
                    four_corner_penalty_weight=int(self.penalty_var.get()) if self.penalty_var.get() else None
                )
            except Exception as e:
                messagebox.showerror("Data error", str(e))
                return

            # 5) Run solver
            result = solve_torus_tiling(width, height, cfg)
            if not result:
                messagebox.showinfo("No solution",
                                    f"No solution found for {width}×{height} cm.")
                return

            placements, w_out, h_out, G = result

            img = draw_tiling(placements, w_out, h_out, G, formats)
            self.last_image = img
            self._update_preview()

        finally:
            # Restore normal cursor and re-enable buttons
            self.config(cursor="")
            self.preview_canvas.config(cursor="")
            self.solve_btn.config(state="normal")
            self.save_btn.config(state="normal")
            self.update_idletasks()

    def _edit_type(self):
        sel = self.tree_types.selection()
        if not sel:
            messagebox.showwarning("No selection", "Select a type to edit.")
            return
        item = sel[0]
        vals = self.tree_types.item(item, "values")

        dialog = tk.Toplevel(self)
        dialog.title("Edit tile type")

        labels = ["ID", "Width (cm)", "Height (cm)", "Cost", "Min count", "Max count"]
        vars_   = [
            tk.StringVar(value=str(vals[0])),
            tk.StringVar(value=str(vals[1])),
            tk.StringVar(value=str(vals[2])),
            tk.StringVar(value=str(vals[3])),
            tk.StringVar(value=str(vals[4])),
            tk.StringVar(value=str(vals[5])),
        ]
        entries = {}
        for idx, label in enumerate(labels):
            ttk.Label(dialog, text=label+":").grid(row=idx, column=0, sticky="e", padx=5, pady=2)
            ent = ttk.Entry(dialog, textvariable=vars_[idx])
            ent.grid(row=idx, column=1, padx=5, pady=2)
            entries[label] = vars_[idx]

        def on_ok():
            try:
                new_vals = (
                    int(entries["ID"].get()),
                    int(entries["Width (cm)"].get()),
                    int(entries["Height (cm)"].get()),
                    float(entries["Cost"].get()),
                    int(entries["Min count"].get()),
                    int(entries["Max count"].get())
                )
            except ValueError:
                messagebox.showerror("Error", "Invalid values in fields.")
                return
            self.tree_types.item(item, values=new_vals)
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        btn_ok = ttk.Button(dialog, text="OK", command=on_ok)
        btn_ok.grid(row=len(labels), column=0, padx=5, pady=5)
        btn_cancel = ttk.Button(dialog, text="Cancel", command=on_cancel)
        btn_cancel.grid(row=len(labels), column=1, padx=5, pady=5)

        dialog.transient(self)
        dialog.grab_set()
        self.wait_window(dialog)

    def _on_save_image(self):
        if not self.last_image:
            messagebox.showwarning("No image", "Run the solver first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".png",
                                            filetypes=[("PNG", "*.png")])
        if path:
            try:
                self.last_image.save(path)
                messagebox.showinfo("Saved", f"Image saved to:\n{path}")
            except Exception as e:
                messagebox.showerror("Save error", str(e))


def main():
    app = TilingApp()
    app.mainloop()


if __name__ == "__main__":
    main()
