"""
caiman_setup.py
Functions for interactive movie and output selection for CaImAn module.
"""
import os
import tkinter as tk
from tkinter import filedialog
import caiman as cm
import ipywidgets as widgets
from IPython.display import clear_output, display


def select_file(text_widget, title):
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    chosen_file = filedialog.askopenfilename(
        title=title, filetypes=[("TIFF Files", "*.tif *.tiff")]
    )
    root.destroy()
    if chosen_file:
        text_widget.value = os.path.normpath(chosen_file)


def select_folder(text_widget, title):
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    chosen_folder = filedialog.askdirectory(title=title)
    root.destroy()
    if chosen_folder:
        text_widget.value = os.path.normpath(chosen_folder)


def generate_caiman_panel(callback_on_load):
    """Creates the interactive UI panel for CaImAn and links it to the notebook."""
    txt_input = widgets.Text(
        description="Input Video:",
        placeholder="Select a file...",
        layout=widgets.Layout(width="70%"),
    )
    btn_browse_input = widgets.Button(
        description="Browse File...", layout=widgets.Layout(width="12%")
    )
    btn_browse_input.on_click(
        lambda b: select_file(txt_input, "Select Calcium Imaging TIF File")
    )

    txt_output = widgets.Text(
        description="Output Base:",
        placeholder="Select output path...",
        layout=widgets.Layout(width="70%"),
    )
    btn_browse_output = widgets.Button(
        description="Browse ...", layout=widgets.Layout(width="12%")
    )
    btn_browse_output.on_click(
        lambda b: select_folder(txt_output, "Select Output Folder")
    )

    btn_load = widgets.Button(
        description="Load Movie",
        button_style="success",
        layout=widgets.Layout(width="25%", margin="10px 0px 0px 150px"),
    )

    output_zone = widgets.Output()

    def run_init(b):
        with output_zone:
            clear_output()
            movie_path = txt_input.value.strip()
            output_base = txt_output.value.strip()

            if not movie_path or not os.path.exists(movie_path):
                print(
                    "Error: Please select a valid Input Video (.tif file)."
                )
                return

            if not output_base:
                output_path = os.path.join(
                    os.path.dirname(movie_path), "Caiman_Outputs"
                )
            else:
                output_path = os.path.join(output_base, "Caiman_Outputs")

            os.makedirs(output_path, exist_ok=True)

            print("==========================================================")
            print("PATHS CONFIGURED SUCCESSFULLY!")
            print(f"movie_path: {movie_path}")
            print(f"output_path: {output_path}")
            print("==========================================================")
            print("Loading movie into CaImAn...")

            movie = cm.load(movie_path)
            print(
                f"Loaded! Movie Shape: {movie.shape} (frames, height, width)"
            )

            # Returns the created variables back to the Notebook
            callback_on_load(movie, movie_path, output_path)

    btn_load.on_click(run_init)

    ui_input = widgets.HBox([txt_input, btn_browse_input])
    ui_output = widgets.HBox([txt_output, btn_browse_output])
    return widgets.VBox([ui_input, ui_output, btn_load, output_zone])