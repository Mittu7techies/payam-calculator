from __future__ import annotations

import math
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

try:
    import customtkinter as ctk
    from PIL import Image
except ImportError as error:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "Missing Package",
        "Install the required packages using:\n\npip install customtkinter pillow\n\n"
        f"Details: {error}",
    )
    root.destroy()
    sys.exit(1)


APP_TITLE = "Payam Calculator"
WINDOW_WIDTH = 980
WINDOW_HEIGHT = 700

BASE_DIR = Path(__file__).resolve().parent

COLORS = {
    "background": "#FFF7ED",
    "card": "#FFFFFF",
    "primary": "#C2410C",
    "primary_hover": "#9A3412",
    "secondary": "#EA580C",
    "text": "#431407",
    "muted": "#7C2D12",
    "border": "#FED7AA",
    "banana_card": "#FEF3C7",
    "sugar_card": "#E0F2FE",
    "pappadam_card": "#FFEDD5",
}

ATOMIC_DENSITIES = {
    "Banana": 9.51e22,
    "Sugar": 7.92e22,
    "Pappadam": 7.80e22,
}

SUPERSCRIPT_MAP = str.maketrans(
    "0123456789+-",
    "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻",
)


class FoodAsset:
    def __init__(self, filename: str, emoji: str, emoji_color: str):
        self.filename = filename
        self.emoji = emoji
        self.emoji_color = emoji_color
        self.image = None
        self.load_image()

    def load_image(self) -> None:
        image_path = BASE_DIR / self.filename

        try:
            if not image_path.exists():
                return

            image = Image.open(image_path).convert("RGBA")
            image.thumbnail((120, 120), Image.Resampling.LANCZOS)

            self.image = ctk.CTkImage(
                light_image=image,
                dark_image=image,
                size=(82, 82),
            )
        except Exception:
            self.image = None

    def widget(self, parent, width: int = 86, height: int = 86):
        if self.image:
            return ctk.CTkLabel(
                parent,
                text="",
                image=self.image,
                width=width,
                height=height,
            )

        return ctk.CTkLabel(
            parent,
            text=self.emoji,
            font=("Segoe UI Emoji", 46),
            text_color=self.emoji_color,
            width=width,
            height=height,
        )


ASSETS = {
    "Puttu": FoodAsset("puttu.png", "🍚", "#B45309"),
    "Banana": FoodAsset("banana.png", "🍌", "#CA8A04"),
    "Sugar": FoodAsset("sugar.png", "🧂", "#64748B"),
    "Pappadam": FoodAsset("pappadam.png", "🍘", "#D97706"),
}


def calculate_side_mass(puttu_grams: float, item: str) -> float:
    if item == "Banana":
        return (puttu_grams / 30.0) * 19.0

    if item == "Sugar":
        return (puttu_grams / 6.0) * 1.0

    if item == "Pappadam":
        return (puttu_grams / 3.0) * 1.0

    raise ValueError(f"Unknown side dish: {item}")


def calculate_atoms(puttu_grams: float, item: str) -> float:
    side_mass = calculate_side_mass(puttu_grams, item)
    return side_mass * ATOMIC_DENSITIES[item]


def format_scientific(value: float) -> str:
    if value == 0:
        return "0 atoms"

    coefficient, exponent = f"{value:.2e}".split("e")
    exponent = int(exponent)

    return f"{coefficient} × 10{str(exponent).translate(SUPERSCRIPT_MAP)} atoms"


class PayamCalculator(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_TITLE)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(850, 620)
        self.configure(fg_color=COLORS["background"])

        self.selected_items = []
        self.selection_frame = None
        self.calculation_frame = None
        self.weight_entry = None
        self.result_container = None

        self.checkbox_variables = {
            item: tk.BooleanVar(value=False)
            for item in ("Banana", "Sugar", "Pappadam")
        }

        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.show_selection_screen()

    def create_header(self, parent, subtitle: str) -> None:
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", padx=42, pady=(28, 0))

        ctk.CTkLabel(
            header,
            text="Payam Calculator",
            font=("Segoe UI", 31, "bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text=subtitle,
            font=("Segoe UI", 15),
            text_color=COLORS["muted"],
        ).pack(anchor="w", pady=(4, 0))

        ctk.CTkFrame(
            header,
            height=2,
            fg_color=COLORS["border"],
        ).pack(fill="x", pady=(18, 0))

    def clear_frames(self) -> None:
        if self.selection_frame is not None:
            self.selection_frame.destroy()
            self.selection_frame = None

        if self.calculation_frame is not None:
            self.calculation_frame.destroy()
            self.calculation_frame = None

    def show_selection_screen(self) -> None:
        self.clear_frames()

        self.selection_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["background"],
            corner_radius=0,
        )
        self.selection_frame.pack(fill="both", expand=True)

        self.create_header(
            self.selection_frame,
            "Choose the side dishes you want to measure atomically.",
        )

        content = ctk.CTkFrame(
            self.selection_frame,
            fg_color="transparent",
        )
        content.pack(fill="both", expand=True, padx=42, pady=28)

        intro_card = ctk.CTkFrame(
            content,
            fg_color=COLORS["card"],
            corner_radius=22,
            border_width=1,
            border_color=COLORS["border"],
        )
        intro_card.pack(fill="x", pady=(0, 20))

        puttu_image = ASSETS["Puttu"].widget(intro_card, 104, 104)
        puttu_image.grid(row=0, column=0, rowspan=2, padx=(24, 18), pady=22)

        ctk.CTkLabel(
            intro_card,
            text="Start with your puttu quantity",
            font=("Segoe UI", 21, "bold"),
            text_color=COLORS["text"],
            anchor="w",
        ).grid(row=0, column=1, sticky="w", padx=(0, 24), pady=(24, 2))

        ctk.CTkLabel(
            intro_card,
            text="Select one or more side dishes below, then continue.",
            font=("Segoe UI", 14),
            text_color=COLORS["muted"],
            anchor="w",
        ).grid(row=1, column=1, sticky="w", padx=(0, 24), pady=(0, 24))

        intro_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            content,
            text="Select side dishes",
            font=("Segoe UI", 22, "bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", pady=(0, 12))

        choices_frame = ctk.CTkFrame(
            content,
            fg_color="transparent",
        )
        choices_frame.pack(fill="both", expand=True)

        for column in range(3):
            choices_frame.grid_columnconfigure(column, weight=1)

        card_colors = {
            "Banana": COLORS["banana_card"],
            "Sugar": COLORS["sugar_card"],
            "Pappadam": COLORS["pappadam_card"],
        }

        for column, item in enumerate(("Banana", "Sugar", "Pappadam")):
            card = ctk.CTkFrame(
                choices_frame,
                fg_color=card_colors[item],
                corner_radius=20,
                border_width=1,
                border_color=COLORS["border"],
            )
            card.grid(
                row=0,
                column=column,
                sticky="nsew",
                padx=(0 if column == 0 else 8, 8 if column < 2 else 0),
            )

            ASSETS[item].widget(card, 110, 110).pack(pady=(25, 12))

            ctk.CTkLabel(
                card,
                text=item,
                font=("Segoe UI", 19, "bold"),
                text_color=COLORS["text"],
            ).pack(pady=(0, 12))

            ctk.CTkCheckBox(
                card,
                text="Include",
                variable=self.checkbox_variables[item],
                font=("Segoe UI", 15),
                text_color=COLORS["text"],
                fg_color=COLORS["primary"],
                hover_color=COLORS["primary_hover"],
                border_color=COLORS["primary"],
                checkmark_color="#FFFFFF",
                corner_radius=5,
            ).pack(pady=(0, 25))

        button_row = ctk.CTkFrame(
            content,
            fg_color="transparent",
        )
        button_row.pack(fill="x", pady=(22, 0))

        ctk.CTkButton(
            button_row,
            text="Next  →",
            command=self.go_to_calculation_screen,
            width=190,
            height=52,
            corner_radius=16,
            font=("Segoe UI", 17, "bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
        ).pack(side="right")

    def go_to_calculation_screen(self) -> None:
        self.selected_items = [
            item
            for item, variable in self.checkbox_variables.items()
            if variable.get()
        ]

        if not self.selected_items:
            messagebox.showwarning(
                "Select a side dish",
                "Please select at least one side dish before continuing.",
            )
            return

        self.show_calculation_screen()

    def show_calculation_screen(self) -> None:
        self.clear_frames()

        self.calculation_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["background"],
            corner_radius=0,
        )
        self.calculation_frame.pack(fill="both", expand=True)

        self.create_header(
            self.calculation_frame,
            "Enter the puttu weight to calculate the atomic scale.",
        )

        content = ctk.CTkFrame(
            self.calculation_frame,
            fg_color="transparent",
        )
        content.pack(fill="both", expand=True, padx=42, pady=26)

        input_card = ctk.CTkFrame(
            content,
            fg_color=COLORS["card"],
            corner_radius=22,
            border_width=1,
            border_color=COLORS["border"],
        )
        input_card.pack(fill="x", pady=(0, 22))

        ASSETS["Puttu"].widget(input_card, 96, 96).grid(
            row=0,
            column=0,
            rowspan=2,
            padx=(24, 18),
            pady=22,
        )

        ctk.CTkLabel(
            input_card,
            text="Puttu weight",
            font=("Segoe UI", 21, "bold"),
            text_color=COLORS["text"],
            anchor="w",
        ).grid(row=0, column=1, sticky="w", padx=(0, 20), pady=(22, 3))

        ctk.CTkLabel(
            input_card,
            text="Enter the quantity in grams.",
            font=("Segoe UI", 14),
            text_color=COLORS["muted"],
            anchor="w",
        ).grid(row=1, column=1, sticky="w", padx=(0, 20), pady=(0, 22))

        self.weight_entry = ctk.CTkEntry(
            input_card,
            placeholder_text="Example: 250",
            width=190,
            height=46,
            corner_radius=12,
            font=("Segoe UI", 16),
            border_color=COLORS["primary"],
            text_color=COLORS["text"],
        )
        self.weight_entry.grid(
            row=0,
            column=2,
            rowspan=2,
            padx=(10, 24),
        )

        ctk.CTkButton(
            input_card,
            text="Calculate Atoms",
            command=self.calculate_and_display,
            width=180,
            height=46,
            corner_radius=13,
            font=("Segoe UI", 15, "bold"),
            fg_color=COLORS["secondary"],
            hover_color=COLORS["primary_hover"],
        ).grid(
            row=0,
            column=3,
            rowspan=2,
            padx=(0, 24),
        )

        input_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            content,
            text="Atomic results",
            font=("Segoe UI", 22, "bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", pady=(0, 12))

        self.result_container = ctk.CTkScrollableFrame(
            content,
            fg_color="transparent",
            corner_radius=0,
        )
        self.result_container.pack(fill="both", expand=True)

        footer = ctk.CTkFrame(
            content,
            fg_color="transparent",
        )
        footer.pack(fill="x", pady=(18, 0))

        ctk.CTkButton(
            footer,
            text="← Back",
            command=self.show_selection_screen,
            width=130,
            height=42,
            corner_radius=12,
            font=("Segoe UI", 14, "bold"),
            fg_color="#9A3412",
            hover_color="#7C2D12",
        ).pack(side="left")

        self.after(100, self.focus_weight_entry)

    def focus_weight_entry(self) -> None:
        if self.weight_entry:
            self.weight_entry.focus_set()

    def calculate_and_display(self) -> None:
        if not self.weight_entry or not self.result_container:
            return

        raw_value = self.weight_entry.get().strip()

        try:
            if not raw_value:
                raise ValueError

            puttu_grams = float(raw_value)

            if not math.isfinite(puttu_grams) or puttu_grams <= 0:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Invalid Weight",
                "Please enter a valid positive number of grams.\n\n"
                "Examples: 100, 250, 500.5",
            )
            self.weight_entry.focus_set()
            return

        for child in self.result_container.winfo_children():
            child.destroy()

        for item in self.selected_items:
            self.create_result_card(item, puttu_grams)

    def create_result_card(self, item: str, puttu_grams: float) -> None:
        if not self.result_container:
            return

        atom_value = calculate_atoms(puttu_grams, item)

        card_colors = {
            "Banana": COLORS["banana_card"],
            "Sugar": COLORS["sugar_card"],
            "Pappadam": COLORS["pappadam_card"],
        }

        card = ctk.CTkFrame(
            self.result_container,
            fg_color=card_colors[item],
            corner_radius=20,
            border_width=1,
            border_color=COLORS["border"],
            height=120,
        )
        card.pack(fill="x", pady=(0, 12))
        card.pack_propagate(False)

        ASSETS[item].widget(card, 82, 82).pack(
            side="left",
            padx=(22, 18),
            pady=19,
        )

        text_area = ctk.CTkFrame(card, fg_color="transparent")
        text_area.pack(side="left", fill="both", expand=True, pady=17)

        ctk.CTkLabel(
            text_area,
            text=item,
            font=("Segoe UI", 20, "bold"),
            text_color=COLORS["text"],
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            text_area,
            text=format_scientific(atom_value),
            font=("Segoe UI", 21, "bold"),
            text_color=COLORS["primary"],
            anchor="w",
        ).pack(anchor="w", pady=(7, 0))


def main() -> None:
    try:
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        app = PayamCalculator()
        app.mainloop()

    except Exception as error:
        try:
            messagebox.showerror(
                "Application Error",
                f"Payam Calculator could not start.\n\nDetails: {error}",
            )
        except Exception:
            print(f"Application Error: {error}", file=sys.stderr)


if __name__ == "__main__":
    main()