"""
project_setup.py

Functions for managing folder creation and workspace initialization.
"""

import os
import ipywidgets as widgets
from IPython.display import display, clear_output
import tkinter as tk
from tkinter import filedialog

def select_folder(text_widget, title):
    """Opens the native dialog to choose a folder and updates the text widget."""
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    chosen_folder = filedialog.askdirectory(title=title)
    root.destroy()

    if chosen_folder:
        text_widget.value = os.path.normpath(chosen_folder)

def generate_setup_panel(paths_dict):
    """
    Creates all visual elements, binds events, and returns the unified UI panel.
    """
    # --- Elements Creation ---
    txt_input = widgets.Text(description='Input Folder:', layout=widgets.Layout(width='70%'))
    btn_browse_input = widgets.Button(description='Browse...', layout=widgets.Layout(width='10%'))
    btn_browse_input.on_click(lambda b: select_folder(txt_input, "Select Input Folder (TIFFs)"))

    txt_output = widgets.Text(value="", description='Output Base:', layout=widgets.Layout(width='70%'))
    btn_browse_output = widgets.Button(description='Browse...', layout=widgets.Layout(width='10%'))
    btn_browse_output.on_click(lambda b: select_folder(txt_output, "Select Output Base Folder"))

    txt_name = widgets.Text(value="", description='Name:', layout=widgets.Layout(width='40%'))

    btn_create = widgets.Button(
        description='Create Project Folders',
        button_style='success',
        layout=widgets.Layout(width='25%', margin='15px 0px 0px 150px')
    )

    output_zone = widgets.Output()

    # --- Button Logic ---
    def run_folder_creation(b):
        with output_zone:
            clear_output()

            INPUT_FOLDER = txt_input.value.strip()
            OUTPUT_BASE = txt_output.value.strip()
            PROJECT_NAME = txt_name.value.strip()

            if not INPUT_FOLDER or not PROJECT_NAME:
                print("Error: Please select the 'Input Folder' and set the 'Project Name'.")
                return

            base_folder = INPUT_FOLDER if OUTPUT_BASE in ["Same as input", "", "   "] else OUTPUT_BASE
            safe_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in PROJECT_NAME)
            project_folder = os.path.join(base_folder, f"Data_Analy_{safe_name}")

            paths_dict["input"] = INPUT_FOLDER
            paths_dict["project"] = project_folder
            paths_dict["calcium"] = os.path.join(project_folder, "Calcium_Channel")
            paths_dict["structural"] = os.path.join(project_folder, "Structural_Channel")
            paths_dict["std"] = os.path.join(project_folder, "STD_movie")

            try:
                for key in ("calcium", "structural", "std"):
                    os.makedirs(paths_dict[key], exist_ok=True)
                print("==========================================================")
                print("FOLDER STRUCTURE CREATED SUCCESSFULLY!")
                print(f"Main Folder: {paths_dict['project']}")
                print("You can now proceed and run the Metadata Cell bellow")
                print("==========================================================")
            except Exception as e:
                print(f"Error creating folders: {str(e)}")

    btn_create.on_click(run_folder_creation)

    # --- Layout Assembly ---
    ui_input = widgets.HBox([txt_input, btn_browse_input])
    ui_output = widgets.HBox([txt_output, btn_browse_output])
    
    # Retorna um VBox contendo toda a interface estruturada
    return widgets.VBox([ui_input, ui_output, txt_name, btn_create, output_zone])