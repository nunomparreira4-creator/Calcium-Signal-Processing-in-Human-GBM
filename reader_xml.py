"""
reader_xml.py
─────────────
Reads Bruker/PrairieView XML files and returns a metadata dict.
"""

import glob
import os
import xml.etree.ElementTree as ET
import ipywidgets as widgets

#to Scan Metadata File

def scan_xml(folder: str) -> dict:
    """
    Parse the first .xml file found in *folder*.
    """
    xml_files = glob.glob(os.path.join(folder, "*.xml")) + glob.glob(os.path.join(folder, "*.XML"))
    if not xml_files:
        return {}

    try:
        tree = ET.parse(xml_files[0])
    except ET.ParseError:
        return {}

    root = tree.getroot()
    meta = {}

    for elem in root.iter("PVStateValue"):
        key = elem.attrib.get("key", "")

        if key == "framePeriod":
            val = float(elem.attrib["value"])
            meta["frame_period"] = round(val, 4)
            meta["fps"] = round(1.0 / val, 3)

        elif key == "pixelsPerLine":
            meta["pixels_x"] = int(elem.attrib["value"])

        elif key == "linesPerFrame":
            meta["pixels_y"] = int(elem.attrib["value"])

        elif key == "micronsPerPixel":
            for sub in elem:
                if sub.attrib.get("index") == "XAxis":
                    meta["um_per_pixel_x"] = round(float(sub.attrib["value"]), 3)
                if sub.attrib.get("index") == "YAxis":
                    meta["um_per_pixel_y"] = round(float(sub.attrib["value"]), 3)

        elif key == "pmtGain":
            active = []
            for sub in elem:
                try:
                    if float(sub.attrib["value"]) > 0:
                        active.append(sub.attrib.get("description", sub.attrib.get("index", "?")))
                except (ValueError, KeyError):
                    pass
            meta["PMTs"] = active

    # derived fields
    if "pixels_x" in meta and "um_per_pixel_x" in meta:
        meta["fov_x_um"] = round(meta["pixels_x"] * meta["um_per_pixel_x"], 3)
    if "pixels_y" in meta and "um_per_pixel_y" in meta:
        meta["fov_y_um"] = round(meta["pixels_y"] * meta["um_per_pixel_y"], 3)

    return meta




#if there is no Metadata File
def extract_metadata_panel(paths_dict):
    """
    Scans the folder, extracts metadata using scan_xml, PRINTS the 
    results to Jupyter, and opens a manual FPS fallback ONLY if NO metadata was found.
    """
    raw_folder = paths_dict.get("input", "")
    if not raw_folder:
        print("ERROR: The 'input' path is empty. Run Cell 1 first.")
        return None

    folder_to_scan = os.path.normpath(raw_folder)

    patterns = [
        os.path.join(folder_to_scan, "*.xml"),
        os.path.join(folder_to_scan, "*.XML"),
        os.path.join(folder_to_scan, "*", "*.xml"),
        os.path.join(folder_to_scan, "*", "*.XML")
    ]

    xml_found = []
    for pattern in patterns:
        xml_found.extend(glob.glob(pattern))

    if not xml_found:
        print(f"ERROR: No XML file found in: {folder_to_scan}")
        meta = {}
        paths_dict["metadata"] = meta
    else:
        target_dir = os.path.dirname(xml_found[0])
        meta = scan_xml(target_dir)
        paths_dict["metadata"] = meta
        
        print("===== METADATA EXTRACTED =====")
        for key, val in meta.items():
            print(f"{key}: {val}")

    if not meta:
        print("\n[NO METADATA FOUND - MANUAL CONFIGURATION REQUIRED]")
        
        txt_fps = widgets.FloatText(value=1.0, description='Manual FPS:', layout=widgets.Layout(width='30%'))
        btn_confirm = widgets.Button(description='Confirm FPS', button_style='info')
        
        def confirm_fps(b):
            meta["fps"] = round(txt_fps.value, 2)
            meta["frame_period"] = round(1.0 / txt_fps.value, 4)
            print(f"Manual frequency set to: {meta['fps']} Hz")
            txt_fps.disabled = True
            btn_confirm.disabled = True

        btn_confirm.on_click(confirm_fps)
        return widgets.HBox([txt_fps, btn_confirm])
        
    return None