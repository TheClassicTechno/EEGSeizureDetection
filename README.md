# # EEG Seizure Detection Pipeline (Stanford EEGML Lab)

work done as part of stanford eegml lab (aug 2022- sep 2023)

other files are to remain private.

End-to-end tooling for **loading, preprocessing, labeling, visualizing, and prototyping models** on multi-channel EEG time-series data (HDF5/`eeghdf` format).
Built to support seizure-related research workflows where **signal artifacts, noisy labels, and reproducibility** matter.

---

## Highlights

* **EEG ingestion + windowing** for `.eeg.h5` files (via `eeghdf`)
* **Signal preprocessing** aligned with common EEG practice:

  * FIR **high-pass / low-pass filtering** 
  * **Common Average Reference (CAR)** for reference stabilization
* **Multi-annotator label consolidation** (consensus voting across A/B/C CSV annotations)
* **Interactive visualization GUI** (QtPy + PyQtGraph):

  * Navigate EEG over time (seek left/right)
  * Compare filtered outputs and derived metrics
  * Inspect window-level statistics quickly
* **Baseline ML experiments** (Keras/PyTorch prototyping hooks) - one colab file with my pipeline to detect seizures using CNN model
* Optional: **compression/quantization analysis** for storage & throughput experiments


## Setup

### 1) Create environment

Recommended: Python 3.9+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Key dependencies

Core packages used:

* `numpy`, `scipy`, `pandas`
* `eeghdf`, `eegvis`, `eegml_signal`
* `qtpy`, `pyqtgraph`
* (optional) `tensorflow/keras`, `torch`, `xgboost`, `scikit-learn`

---

## Quick Start

### Load EEG and extract windows

* Load an EEG file using `eeghdf`
* Slice into fixed-length windows aligned to the sample rate

Typical workflow:

1. Load `.eeg.h5`
2. Select channels of interest (optionally exclude non-EEG channels)
3. Extract `N`-second windows for preprocessing + labeling + training

---

## Preprocessing

### Filters

This repo supports FIR filtering:

* **High-pass** (remove drift)
* **Low-pass** (remove high-frequency noise)

Example cutoff ranges commonly used:

* HPF: ~0.3–1 Hz (depends on dataset)
* LPF: ~40–50 Hz

### Common Average Reference (CAR)

CAR subtracts the mean across selected EEG electrodes at each time point, reducing reference bias and improving cross-channel comparability.

---

## Labeling (Multi-Annotator Consensus)

If multiple annotation files exist (e.g., A/B/C), we compute a consolidated label per time index / window using a consensus rule (e.g., majority vote or threshold on mean). This reduces noise from single-rater variability.

---

## Visualization GUI

The GUI (QtPy + PyQtGraph) supports:

* Plotting window-level EEG views
* Navigating forward/backward through time
* Displaying derived metrics and summaries

To run:

```bash
python -m src.viz.gui
```

(Adjust module path/name based on your repo structure.)

---

## Modeling

Baseline experiments include:

* Keras CNN prototype for window-level seizure detection
* Scikit-learn baselines for quick sanity checks
* Hooks for PyTorch architectures and collaboration experiments

---

## Notes on Reproducibility

* Prefer deterministic dataset splits and consistent windowing rules
* Keep preprocessing parameters (cutoffs, window length) versioned in config
* Track label consolidation rules explicitly (vote thresholds, exclusions)

---

## Disclaimer

This project is for research and engineering prototyping only and is **not a clinical diagnostic tool**.

---

## Acknowledgements

Built during research in the Stanford EEGML Lab, using open-source EEG tooling including `eeghdf` and `eegvis`.
