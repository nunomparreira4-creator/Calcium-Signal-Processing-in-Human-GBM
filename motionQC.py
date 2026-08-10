"""
motionQC.py
──────────────
Utility module for registration quality control (QC).
Renders plots inline directly in the Jupyter Notebook.
"""

import os
import numpy as np
import tifffile
import matplotlib.pyplot as plt

def load_suite2p_data(plane_dir):
    """Loads the raw and registered binaries via memory-mapping."""
    ops = np.load(os.path.join(plane_dir, "ops.npy"), allow_pickle=True).item()
    Ly, Lx = ops["Ly"], ops["Lx"]
    nframes = ops["nframes"]

    raw = np.memmap(os.path.join(plane_dir, "data_raw.bin"), dtype="int16", mode="r").reshape(nframes, Ly, Lx)
    reg = np.memmap(os.path.join(plane_dir, "data.bin"), dtype="int16", mode="r").reshape(nframes, Ly, Lx)
    return ops, raw, reg

def load_registered_tiffs(reg_folder):
    """Recursively reads the TIFF blocks saved by Suite2P."""
    reg_files = sorted([
        os.path.join(reg_folder, f)
        for f in os.listdir(reg_folder)
        if f.lower().endswith((".tif", ".tiff"))
    ])

    if not reg_files:
        raise FileNotFoundError(f"No TIFF file found in:\n{reg_folder}")

    stacks = []
    for file in reg_files:
        stack = tifffile.imread(file)
        if stack.ndim == 2:
            stack = stack[np.newaxis]
        stacks.append(stack)
    return np.concatenate(stacks, axis=0)

def compute_crispness(img, border=0):
    """Sharpness metric based on gradient magnitude (Frobenius norm)."""
    img = img.astype(np.float32)
    if border > 0:
        img = img[border:-border, border:-border]
    gx, gy = np.gradient(img)
    gradient_mag = np.sqrt(gx**2 + gy**2)
    return np.linalg.norm(gradient_mag, ord="fro")

def registration_qc(raw, reg, ops):
    print("Computing mean projections and crispness...")
    mean_raw = raw.astype(np.float32).mean(axis=0)
    mean_reg = reg.astype(np.float32).mean(axis=0)

    crisp_before = compute_crispness(mean_raw, border=10)
    crisp_after  = compute_crispness(mean_reg, border=10)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), dpi=100)
    images = [mean_raw, mean_reg]
    titles = [
        f"Mean Projection Original\nCrispness: {crisp_before:.0f}",
        f"Mean Projection Registered\nCrispness: {crisp_after:.0f}",
    ]
    
    for ax, img, t in zip(axes, images, titles):
        ax.imshow(img, cmap="gray")
        ax.set_title(t, fontsize=10, fontweight="bold")
        ax.axis("off")
    plt.tight_layout()
    plt.show()

def intensity_qc(orig_tiff, reg_folder):
    print("Extracting frame-by-frame intensity profiles...")
    orig_video = tifffile.imread(orig_tiff)
    if orig_video.ndim == 2:
        orig_video = orig_video[np.newaxis]

    reg_video = load_registered_tiffs(reg_folder)
    orig_mean = orig_video.astype(np.float32).mean(axis=(1, 2))
    reg_mean  = reg_video.astype(np.float32).mean(axis=(1, 2))

    plt.figure(figsize=(12, 4), dpi=100)
    plt.plot(orig_mean, label="Original (Temporary File)", alpha=0.8)
    plt.plot(reg_mean,  label="Registered (Suite2P Output)", alpha=0.8)
    plt.xlabel("Frame")
    plt.ylabel("Mean Intensity")
    plt.title("Mean Intensity Profile (Pre vs Post Registration)", fontweight="bold")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()

def offsets_qc(paths_dict):
    print("Processing vector offsets (shifts)...")
    plane_dir = paths_dict["plane_dir"]
    rigid_offsets = np.load(os.path.join(plane_dir, "rigid_offsets.npy"), allow_pickle=True)
    nonrigid_offsets = np.load(os.path.join(plane_dir, "nonrigid_offsets.npy"), allow_pickle=True)

    fig, axes = plt.subplots(1, 2, figsize=(14, 4.5), dpi=100)

    # Rigid
    axes[0].plot(rigid_offsets[0], label="X shift", alpha=0.8)
    axes[0].plot(rigid_offsets[1], label="Y shift", alpha=0.8)
    axes[0].set_title("Rigid Offsets per Frame", fontweight="bold")
    axes[0].set_xlabel("Frame")
    axes[0].set_ylabel("Pixels")
    axes[0].legend()
    axes[0].grid(True, linestyle="--", alpha=0.5)

    # Non-Rigid (central/initial block as a sample)
    axes[1].plot(nonrigid_offsets[0, :, 0], label="X shift (Block 1)", alpha=0.8)
    axes[1].plot(nonrigid_offsets[1, :, 0], label="Y shift (Block 1)", alpha=0.8)
    axes[1].set_title("Non-Rigid Offsets (Block 1 Example)", fontweight="bold")
    axes[1].set_xlabel("Frame")
    axes[1].set_ylabel("Pixels")
    axes[1].legend()
    axes[1].grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.show()

def run_pipeline_qc(paths_dict):
    """Master function called from Jupyter, passing the global 'paths' dictionary."""
    if "plane_dir" not in paths_dict:
        print("ERROR: 'plane_dir' missing from memory. Did you run Cell 6 successfully?")
        return
        
    plane_dir = paths_dict["plane_dir"]
    ops, raw, reg = load_suite2p_data(plane_dir)
    
    # Sequentially triggers the inline plots
    registration_qc(raw, reg, ops)
    intensity_qc(paths_dict["orig_tiff"], paths_dict["reg_folder"])
    offsets_qc(paths_dict)