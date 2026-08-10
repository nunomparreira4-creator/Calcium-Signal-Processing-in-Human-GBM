"""
video_viewer.py
───────────────
Interactive video viewer for calcium and structural stacks, including
on-the-fly standard deviation calculation and visualization.
"""

import io
import os
import threading
import numpy as np
import tifffile as tiff
import ipywidgets as widgets
import matplotlib.pyplot as plt
from IPython.display import display


def compute_running_std(stack: np.ndarray, window_size: int = 21) -> np.ndarray:
    """Calculates the running standard deviation across frames using a sliding window."""
    half = window_size // 2
    n_frames = stack.shape[0]
    output = np.zeros_like(stack, dtype=np.float32)
    for i in range(n_frames):
        s = max(0, i - half)
        e = min(n_frames, i + half + 1)
        output[i] = np.std(stack[s:e].astype(np.float32), axis=0)
    return output


def save_std_tiff(std_stack: np.ndarray, out_path: str) -> None:
    """Normalizes and saves the standard deviation map as a 16-bit TIFF."""
    mn, mx = std_stack.min(), std_stack.max()
    if mx > mn:
        out16 = ((std_stack - mn) / (mx - mn) * 65535).astype(np.uint16)
    else:
        out16 = np.zeros_like(std_stack, dtype=np.uint16)
    tiff.imwrite(out_path, out16)


def frame_to_bytes(frame_data: np.ndarray, cmap_name: str, vmin: float, vmax: float) -> bytes:
    """Converts a single frame to compressed JPEG bytes for fluid browser playback."""
    norm_data = np.clip((frame_data - vmin) / (vmax - vmin + 1e-8), 0, 1)
    cmap = plt.get_cmap(cmap_name)
    rgba_image = cmap(norm_data)
    rgb_image = (rgba_image[:, :, :3] * 255).astype(np.uint8)
    
    buffer = io.BytesIO()
    plt.imsave(buffer, rgb_image, format='jpeg')
    return buffer.getvalue()


def launch_interactive_viewer(paths: dict):
    """Assembles and displays the video player inside Jupyter."""
    stack_calcium = paths.get("stack_calcium")
    stack_structural = paths.get("stack_structural")

    if stack_calcium is None:
        print("ERROR: The calcium stack was not found in 'paths'. Run Cell 4 first!")
        return

    num_frames = stack_calcium.shape[0]

    # Dynamic dictionaries to manage layers
    stacks_view = {"Original": stack_calcium}
    limits_cache = {"Original": (float(stack_calcium.min()), float(stack_calcium.max()))}
    
    if stack_structural is not None:
        stacks_view["Structural"] = stack_structural
        limits_cache["Structural"] = (float(stack_structural.min()), float(stack_structural.max()))

    FILTERS = ["gray", "viridis", "hot", "inferno", "Greens_r"]

    # --- UI Components Elements ---
    ui_frame = widgets.IntSlider(value=0, min=0, max=num_frames - 1, step=1, description="Frame:", layout=widgets.Layout(width='50%'))
    ui_play = widgets.Play(value=0, min=0, max=num_frames - 1, step=1, interval=50) # ~20 FPS
    ui_mode = widgets.Dropdown(options=list(stacks_view.keys()), value="Original", description="View:")
    ui_cmap = widgets.Dropdown(options=FILTERS, value="gray", description="Colormap:")

    btn_std = widgets.Button(description="Compute STD", button_style="warning", icon="calculator")
    btn_save = widgets.Button(description="Save TIFFs", button_style="success", icon="save")
    lbl_status = widgets.Label(value="Status: Ready")
    
    image_widget = widgets.Image(format='jpeg', width=500, height=400)

    widgets.jslink((ui_play, "value"), (ui_frame, "value"))

    # --- Central Dynamic Update Trigger ---
    def update_viewer(change):
        frame = ui_frame.value
        view_mode = ui_mode.value
        colormap = ui_cmap.value
        
        current_stack = stacks_view.get(view_mode)
        if current_stack is None:
            return

        f_idx = min(frame, current_stack.shape[0] - 1)
        vmin, vmax = limits_cache.get(view_mode, (0, 1))
        
        try:
            img_bytes = frame_to_bytes(current_stack[f_idx], colormap, vmin, vmax)
            image_widget.value = img_bytes
        except Exception:
            pass

    ui_frame.observe(update_viewer, names='value')
    ui_mode.observe(update_viewer, names='value')
    ui_cmap.observe(update_viewer, names='value')

    # --- Actions: Compute Running STD ---
    def _bg_compute_std(b):
        btn_std.disabled = True
        btn_std.description = "Computing..."
        lbl_status.value = "Status: Computing running STD (Window = 21)..."

        def worker():
            try:
                std_stack = compute_running_std(stack_calcium, window_size=21)

                std_dir = paths.get("std", os.getcwd())
                out_path = os.path.join(std_dir, "running_std.tif")
                os.makedirs(std_dir, exist_ok=True)
                
                save_std_tiff(std_stack, out_path)

                stacks_view["STD"] = std_stack
                limits_cache["STD"] = (float(std_stack.min()), float(std_stack.max()))
                paths["stack_std"] = std_stack

                btn_std.description = "STD Done"
                btn_std.button_style = "info"
                lbl_status.value = f"STD saved at: {out_path}"
                ui_mode.options = list(stacks_view.keys())

            except Exception as e:
                btn_std.disabled = False
                btn_std.description = "Error STD"
                lbl_status.value = f"Error: {str(e)}"

        threading.Thread(target=worker, daemon=True).start()

    # --- Actions: Save Consolidated Stacks ---
    def _save_current_stacks(b):
        lbl_status.value = "Status: Exporting TIFF files to disk..."
        try:
            cal_path = os.path.join(paths.get("calcium", "."), "calcium.tif")
            tiff.imwrite(cal_path, stack_calcium)
            if stack_structural is not None:
                str_path = os.path.join(paths.get("structural", "."), "structural.tif")
                tiff.imwrite(str_path, stack_structural)
            lbl_status.value = "Save completed successfully!"
        except Exception as e:
            lbl_status.value = f"Error while saving: {str(e)}"

    btn_std.on_click(_bg_compute_std)
    btn_save.on_click(_save_current_stacks)

    # Boot frame zero
    update_viewer(None)

    # --- UI Layout Assembly ---
    controls = widgets.VBox([
        widgets.HBox([ui_play, ui_frame]),
        widgets.HBox([ui_mode, ui_cmap]),
        widgets.HBox([btn_std, btn_save, lbl_status]),
        widgets.Box([image_widget], layout=widgets.Layout(margin='10px 0px', display='flex', justify_content='center'))
    ])

    display(controls)