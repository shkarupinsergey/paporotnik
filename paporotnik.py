"""Лабораторная работа: интерактивный фрактал «Папоротник Барнсли».

Для запуска: python paporotnik.py
Используются только стандартные библиотеки Python (tkinter и random).
"""

import random
import tkinter as tk
from tkinter import ttk


# Наборы коэффициентов, дающие разные формы фрактального растения.
# (изгиб основного стебля, ширина боковых ветвей, вертикальный коэффициент)
PRESETS = {
    "Классический папоротник": (0.04, 1.00, 0.85),
    "Узкий папоротник": (0.02, 0.60, 0.88),
    "Широкий папоротник": (0.04, 1.45, 0.80),
    "Изогнутый папоротник": (-0.12, 1.10, 0.85),
    "Высокий папоротник": (0.03, 0.85, 0.91),
}

CANVAS_WIDTH = 660
CANVAS_HEIGHT = 650
POINT_COLOR = "#68ef8c"
BACKGROUND_COLOR = "#060b09"


class BarnsleyFern:
    """Создаёт точки фрактала с помощью четырёх аффинных преобразований."""

    def __init__(self, bend=0.04, spread=1.0, vertical=0.85):
        self.bend = bend
        self.spread = spread
        self.vertical = vertical
        self.x = 0.0
        self.y = 0.0

    def transform(self, random_number):
        """Выбирает одно из четырёх преобразований по вероятностям 1/85/7/7 %."""
        x, y = self.x, self.y

        if random_number < 0.01:
            # Формирование основания стебля.
            self.x = 0.0
            self.y = 0.16 * y
        elif random_number < 0.86:
            # Главный стебель: изменяем b (изгиб) и d (вытянутость).
            self.x = 0.85 * x + self.bend * y
            self.y = -self.bend * x + self.vertical * y + 1.6
        elif random_number < 0.93:
            # Левая ветвь: изменяем коэффициент ширины w.
            self.x = 0.20 * x - 0.26 * self.spread * y
            self.y = 0.23 * x + 0.22 * y + 1.6
        else:
            # Правая ветвь: тот же коэффициент w.
            self.x = -0.15 * x + 0.28 * self.spread * y
            self.y = 0.26 * x + 0.24 * y + 0.44

    def generate_points(self, iterations, seed=42):
        """Возвращает координаты точек; seed делает сравнение форм наглядным."""
        rng = random.Random(seed)
        self.x, self.y = 0.0, 0.0

        # Первые точки пропускаем, пока система выходит на аттрактор.
        for _ in range(20):
            self.transform(rng.random())

        points = []
        for _ in range(iterations):
            self.transform(rng.random())
            points.append((self.x, self.y))
        return points


class FernApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Папоротник Барнсли — интерактивный фрактал")
        self.root.configure(bg="#edf2ef")
        self.root.resizable(False, False)
        self.pending_update = None

        self.bend = tk.DoubleVar(value=0.04)
        self.spread = tk.DoubleVar(value=1.0)
        self.vertical = tk.DoubleVar(value=0.85)
        self.iterations = tk.IntVar(value=20000)

        self._create_interface()
        self.root.after(100, self.draw_fern)

    def _create_interface(self):
        main = tk.Frame(self.root, bg="#edf2ef", padx=12, pady=12)
        main.pack()

        self.canvas = tk.Canvas(
            main,
            width=CANVAS_WIDTH,
            height=CANVAS_HEIGHT,
            bg=BACKGROUND_COLOR,
            highlightthickness=0,
        )
        self.canvas.pack(side=tk.LEFT)

        controls = tk.Frame(main, bg="#edf2ef", width=310, padx=16)
        controls.pack(side=tk.LEFT, fill=tk.Y, anchor="n")

        tk.Label(
            controls,
            text="Папоротник Барнсли",
            font=("Arial", 16, "bold"),
            bg="#edf2ef",
            fg="#174b30",
        ).pack(anchor="w", pady=(2, 8))

        tk.Label(
            controls,
            text=("Меняйте коэффициенты уравнений — "
                  "форма фрактального растения будет изменяться."),
            font=("Arial", 10),
            bg="#edf2ef",
            fg="#394c41",
            wraplength=285,
            justify=tk.LEFT,
        ).pack(anchor="w", pady=(0, 14))

        self._add_slider(
            controls, "Изгиб стебля (b)", self.bend,
            -0.17, 0.17, 0.01,
        )
        self._add_slider(
            controls, "Ширина боковых ветвей (w)", self.spread,
            0.50, 1.55, 0.05,
        )
        self._add_slider(
            controls, "Вытянутость растения (d)", self.vertical,
            0.75, 0.92, 0.01,
        )
        self._add_slider(
            controls, "Количество точек", self.iterations,
            2000, 50000, 1000,
        )

        ttk.Separator(controls, orient="horizontal").pack(fill=tk.X, pady=12)
        tk.Label(
            controls,
            text="Готовые варианты растения",
            font=("Arial", 11, "bold"),
            bg="#edf2ef", fg="#174b30",
        ).pack(anchor="w", pady=(0, 6))

        self.preset_selector = ttk.Combobox(
            controls,
            values=list(PRESETS),
            state="readonly",
            width=30,
            font=("Arial", 10),
        )
        self.preset_selector.set("Классический папоротник")
        self.preset_selector.pack(fill=tk.X, pady=(0, 5))
        self.preset_selector.bind("<<ComboboxSelected>>", self.select_preset)

        tk.Button(
            controls,
            text="Сбросить к стандартному виду",
            command=lambda: self.apply_preset(PRESETS["Классический папоротник"]),
            font=("Arial", 10, "bold"),
            bg="#176a3f",
            fg="white",
            activebackground="#238454",
            activeforeground="white",
            pady=6,
        ).pack(fill=tk.X, pady=(12, 8))

        tk.Label(
            controls,
            text="Изменяемые уравнения:",
            font=("Arial", 10, "bold"),
            bg="#edf2ef", fg="#174b30",
        ).pack(anchor="w", pady=(6, 4))
        tk.Label(
            controls,
            text=("Основное преобразование:\n"
                  "x′ = 0.85·x + b·y\n"
                  "y′ = −b·x + d·y + 1.6\n"
                  "В боковых ветвях коэффициент w\n"
                  "изменяет ширину листьев."),
            font=("Arial", 9),
            bg="#edf2ef",
            fg="#394c41",
            justify=tk.LEFT,
        ).pack(anchor="w")

        self.status = tk.Label(
            self.root,
            text="Построение...",
            bg="#edf2ef", fg="#425d4a",
            anchor="w", padx=13, pady=4,
        )
        self.status.pack(fill=tk.X)

    def _add_slider(self, parent, title, variable, minimum, maximum, resolution):
        tk.Label(
            parent,
            text=title,
            bg="#edf2ef",
            fg="#253a2c",
            font=("Arial", 10),
        ).pack(anchor="w")

        tk.Scale(
            parent,
            variable=variable,
            from_=minimum,
            to=maximum,
            resolution=resolution,
            orient=tk.HORIZONTAL,
            length=280,
            showvalue=True,
            bg="#edf2ef",
            fg="#253a2c",
            highlightthickness=0,
            troughcolor="#bed6c7",
            command=self.schedule_redraw,
        ).pack(anchor="w", pady=(0, 9))

    def select_preset(self, _event=None):
        self.apply_preset(PRESETS[self.preset_selector.get()])

    def apply_preset(self, settings):
        bend, spread, vertical = settings
        self.bend.set(bend)
        self.spread.set(spread)
        self.vertical.set(vertical)
        for title, values in PRESETS.items():
            if values == settings:
                self.preset_selector.set(title)
                break
        self.schedule_redraw()

    def schedule_redraw(self, _value=None):
        # Обновляем с небольшой задержкой, чтобы ползунки не тормозили.
        if self.pending_update is not None:
            self.root.after_cancel(self.pending_update)
        self.pending_update = self.root.after(180, self.draw_fern)

    def draw_fern(self):
        self.pending_update = None
        fern = BarnsleyFern(
            bend=self.bend.get(),
            spread=self.spread.get(),
            vertical=self.vertical.get(),
        )
        count = self.iterations.get()
        points = fern.generate_points(count)

        # Подгоняем масштаб под текущую форму, чтобы фрактал помещался на экране.
        min_x = min(x for x, _ in points)
        max_x = max(x for x, _ in points)
        min_y = min(y for _, y in points)
        max_y = max(y for _, y in points)
        padding = 25
        width = CANVAS_WIDTH
        height = CANVAS_HEIGHT
        scale = min(
            (width - 2 * padding) / max(max_x - min_x, 0.001),
            (height - 2 * padding) / max(max_y - min_y, 0.001),
        )
        left = (width - (max_x - min_x) * scale) / 2
        top = (height - (max_y - min_y) * scale) / 2

        self.canvas.delete("all")
        for x, y in points:
            pixel_x = round(left + (x - min_x) * scale)
            pixel_y = round(top + (max_y - y) * scale)
            # Рисуем точку размером 1×1 пиксель.
            self.canvas.create_rectangle(
                pixel_x, pixel_y, pixel_x + 1, pixel_y + 1,
                outline=POINT_COLOR,
                fill=POINT_COLOR,
                width=0,
            )

        self.status.config(
            text=(f"Построено точек: {count:,}    "
                  f"b = {self.bend.get():.2f}    "
                  f"w = {self.spread.get():.2f}    "
                  f"d = {self.vertical.get():.2f}").replace(",", " ")
        )


def main():
    root = tk.Tk()
    FernApplication(root)
    root.mainloop()


if __name__ == "__main__":
    main()
