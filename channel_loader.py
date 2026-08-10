"""
channel_loader.py
Módulo para processar o carregamento de canais TIFF e geração do ficheiro de configuração.
"""

import json
import os
from reader_tiff import load_worker


def load_channels_and_configure(paths_dict, ch_cal_val, ch_struc_val):
    """Executa a validação, carregamento dos TIFFs e salvamento do config.json."""
    INPUT_FOLDER = paths_dict.get("input", "")
    project_folder = paths_dict.get("project", "")
    meta_data = paths_dict.get("metadata", {})

    # --- CRITICAL SAFETY VALIDATION ---
    if not ch_cal_val:
        print("ERROR: The Calcium channel is not selected!")
        print(
            "Make sure you chose a valid option in the dropdown from Cell 3 before running this cell."
        )
        return

    if not INPUT_FOLDER or not os.path.exists(INPUT_FOLDER):
        print(
            f"ERROR: The input folder does not exist or is empty: '{INPUT_FOLDER}'"
        )
        return

    print(f"Loading channels...")
    print(f" -> Calcium selected: '{ch_cal_val}'")
    print(f" -> Structural selected: '{ch_struc_val}'\n")
    print("Please wait, this may take a while depending on the file size...\n")

    # Criar as pastas físicas no disco
    for key in ("calcium", "structural", "std"):
        if key in paths_dict:
            os.makedirs(paths_dict[key], exist_ok=True)

    try:
        # Executa o carregamento dos dados
        stack_calcium, stack_structural = load_worker(
            INPUT_FOLDER, ch_cal_val, ch_struc_val
        )

        # Configuração do dicionário para salvar em JSON
        config = {
            "project_folder": project_folder,
            "input_folder": INPUT_FOLDER,
            "calcium_channel": ch_cal_val,
            "structural_channel": ch_struc_val,
            "project_name": os.path.basename(project_folder).replace(
                "Data_Analy_", ""
            ),
            "metadata": meta_data,
        }

        config_path = os.path.join(project_folder, "config.json")
        with open(config_path, "w") as fh:
            json.dump(config, fh, indent=4)

        # Guarda os resultados no dicionário global do notebook
        paths_dict["stack_calcium"] = stack_calcium
        paths_dict["stack_structural"] = stack_structural

        print("=" * 50)
        print(f"SUCCESS: {stack_calcium.shape[0]} frames loaded successfully!")
        print(f"Calcium array shape: {stack_calcium.shape}")
        if stack_structural is not None:
            print(f"Structural array shape: {stack_structural.shape}")
        print(f"Memory file saved at: {config_path}")
        print("=" * 50)

    except ValueError as e:
        print("=" * 50)
        print("READ ERROR (ValueError):")
        print(
            f"The reader tried to stack images for channel '{ch_cal_val}', but the corresponding file list is empty."
        )
        print(
            f"Check whether the files in folder '{INPUT_FOLDER}' actually contain the chosen channel identifier."
        )
        print("=" * 50)