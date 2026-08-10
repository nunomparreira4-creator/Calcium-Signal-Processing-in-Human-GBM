
# 2D 2P Calcium Imaging Analysis Pipeline

**Developed by:** Nuno Parreira (Aarhus Neuroscience Lab, Denmark, 2026)  
**Target:** Analysis of 2D 2-photon calcium imaging data in Glioblastoma (GBM) research using Python.

The pipeline was built to run using Jupyter Notebooks split into two sequential main steps:

1. 'Preprocessing.ipynb' (Exploratory Analysis + Motion Correction)
   * Powered by an adaptation of **[Suite2p](https://github.com/MouseLand/suite2p)**.
2. 'Signal_extraction.ipynb' (CNMF Segmentation)
   * Powered by an adaptation of **[CaImAn](https://github.com/flatironinstitute/CaImAn)** (Constrained Non-negative Matrix Factorization).
                                            **(https://caiman.readthedocs.io/en/latest/core_functions.html)**

To prevent software dependency conflicts between Suite2p and CaImAn, each module runs in its own isolated Conda environment.

**Prerequisite Software**

Before starting, make sure you have installed:
* **[Miniconda](https://docs.conda.io/en/latest/)**
* **[MiniForge](https://docs.conda.io/en/latest/)**

* **[VS Code](https://code.visualstudio.com/)** (Recommended editor, with the *Python* and *Jupyter* extensions installed)


#######################################################################

**Quick Start & Installation**

Open your **Anaconda Prompt** (Windows) and paste these line by line:

1. **Motion Correction**

conda create -n motion_correction python=3.9.25 -y
conda activate motion_correction
pip install suite2p==0.14.6


2. **Motion Correction Verification**
python -c "import suite2p; print('Suite2p ready!')"

3. **Source Extraction**

conda create -n source_extraction -c conda-forge caiman opencv ffmpeg -y
conda activate source_extraction


4. **Source Extraction Verification**
python -c "import caiman; print('CaImAn ready!')"

########

Note: Alter script Preprocessing.ipynb  in cell **# 6: SUITE2P NON-RIGID MOTION CORRECTION** to the motion correction python path already installed previously ( your path to miniconda3 + /envs/motion_correction/python.exe):

PYTHON_SUITE2P = r"C:/Users/35192/miniconda3/envs/motion_correction/python.exe"

########

################################################################

##  How to Execute? 

1. Open the project folder in VS Code pipeline (File >> Open Folder >> ... Signal_Extraction)

2. Set the global Kernel: In the top right corner of VS Code, select Python (source_extraction) as the default kernel for both notebooks.

3. Execute Preprocessing.ipynb cell by cell ( Ctrl + Enter)

4. Execute Signal_extraction.ipynb cell by cell ( Ctrl + Enter):

All the files are kept in the memmory folder, to be accessed when necessary


