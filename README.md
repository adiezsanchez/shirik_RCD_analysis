# shirik_RCD_analysis

CellposeSAM-mediated brightfield cell segmentation and intensity/morphology feature extraction for RCD (e.g. single-cell) analysis. The pipeline runs on ND2 images, outputs per-cell morphology and marker intensity tables, and supports batch processing and plate-level visualization.

**Notebooks:**

- **SP_image_viz** — Single-image exploration: load one ND2, run CellposeSAM, extract features, optional sanity-check filtering and Napari visualization.
- **BP_batch_processing** — Batch run over all images in a data folder; writes one CSV per image under `results/<experiment_id>/` (no filtering).
- **data_analysis** — Concatenates those CSVs, saves under `processed_results/<experiment_id>/`, computes mean features per well, and plots plate views (e.g. area) via `utils_data_analysis.plot_plate_view`.

---

## Running Jupyter with Pixi

[Pixi](https://pixi.sh/) is used to manage the environment (Python, PyTorch/CUDA, Cellpose, Jupyter, Napari, etc.).

1. **Install Pixi** (if needed):  
   https://pixi.sh/latest/install/

2. **From the project root**, install the environment and start Jupyter Lab:

   ```bash
   pixi install
   pixi run lab
   ```

   This starts Jupyter Lab with the project kernel. Open any `.ipynb` notebook and run the cells.

To launch the Napari viewer only: `pixi run napari`.
