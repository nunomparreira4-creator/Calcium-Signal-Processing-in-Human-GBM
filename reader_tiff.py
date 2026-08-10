"""
reader_tiff.py
──────────────
Utilities for discovering TIFF channels and loading image stacks.
"""

import glob
import os
import warnings
import logging
import numpy as np
import tifffile as tiff

warnings.filterwarnings("ignore")
logging.getLogger("tifffile").setLevel(logging.ERROR)


def scan_channels(folder: str, render_ui: bool = False):  # <- Adicionado render_ui=False
    """
    Scan *folder* and its subfolders for TIFF files and group them by channel tag.
    """
    all_files = sorted(
        glob.glob(os.path.join(folder, "*.tif")) +
        glob.glob(os.path.join(folder, "*.tiff"))
    )
    
    all_files = [f for f in all_files if "Data_Analy_" not in f]
    
    channels: dict[str, list] = {}
    for fn in all_files:
        basename = os.path.basename(fn)
        if "Ch" in basename:
            tag = "Ch" + basename.split("Ch")[-1].split("_")[0].split(".")[0]
            channels.setdefault(tag, []).append(fn)

    for tag in channels:
        channels[tag] = sorted(channels[tag])

    # --- BLOCO INTERATIVO JUPYTER (Apenas se render_ui for True) ---
    if render_ui:
        try:
            from IPython import get_ipython
            if get_ipython() is not None:
                import ipywidgets as widgets
                from IPython.display import display

                keys = sorted(list(channels.keys()))
                global dropdown_calcium, dropdown_structural
                
                dropdown_calcium = widgets.Dropdown(
                    options=keys if keys else ["Default"], 
                    description='Calcium:',
                    layout=widgets.Layout(width='35%')
                )
                dropdown_structural = widgets.Dropdown(
                    options=["None"] + keys, 
                    description='Structural:',
                    layout=widgets.Layout(width='35%')
                )

                print("Select the corresponding channels:")
                display(dropdown_calcium)
                display(dropdown_structural)
        except Exception:
            pass

    return channels, all_files


def load_stack(file_list: list) -> np.ndarray:
    """Load a list of TIFF files into a single (N, H, W) numpy array."""
    frames = []
    for path in file_list:
        with tiff.TiffFile(path) as tf:
            if len(tf.pages) > 1:
                for page in tf.pages:
                    frames.append(page.asarray())
            else:
                frames.append(tf.pages[0].asarray())
    return np.stack(frames)


def load_worker(folder: str, ch_cal: str, ch_struc: str):
    # Chama explicitamente com render_ui=False para não duplicar os dropdowns
    channels, all_files = scan_channels(folder, render_ui=False)

    if not all_files:
        raise ValueError(f"Não foi possível encontrar ficheiros válidos na pasta: {folder}")

    # 2. CASO SEJA UM FICHEIRO ÚNICO CONSOLIDADO
    if len(all_files) == 1:
        unique_file = all_files[0]
        print(f"[Universal Loader] Detetado ficheiro único consolidado: {os.path.basename(unique_file)}")
        stack_cal = tiff.imread(unique_file)
        if len(stack_cal.shape) == 2:
            stack_cal = stack_cal[np.newaxis, :, :]
        return stack_cal, None

    # 3. CASO SEJAM MÚLTIPLOS FICHEIROS SEPARADOS POR CANAL
    if ch_cal == "Default" or not channels:
        files_cal = all_files
        files_str = None
    else:
        files_cal = channels.get(ch_cal, all_files)
        files_str = (
            channels[ch_struc]
            if ch_struc not in ("None", "") and ch_struc in channels
            else None
        )

    stack_cal = load_stack(files_cal)
    stack_str = load_stack(files_str) if files_str else None

    return stack_cal, stack_str