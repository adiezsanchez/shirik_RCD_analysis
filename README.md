# shirik_RCD_analysis

[![DOI](https://img.shields.io/badge/DOI-10.5281/zenodo.XXXXXXX-blue.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)

CellposeSAM-mediated brightfield cell segmentation and intensity/morphology feature extraction for RCD (e.g. single-cell) analysis. The pipeline runs on ND2 images, outputs per-cell morphology and marker intensity tables, and supports batch processing and plate-level visualization.

An **infection pipeline** extends this workflow with Mycobacterium (Mtb) segmentation, per-cell infection status, bacterial load, and infection-specific summaries and plots.

---

## Notebooks

Notebooks are numbered by typical run order. Training notebooks (`0_*`) are optional setup steps.

### Model training (optional)

| Notebook | Description |
|----------|-------------|
| **`0_fine_tune_cpSAM.ipynb`** | Fine-tune Cellpose-SAM on brightfield training data; produces `./models/CPSAM_shirik_ft`. |
| **`0_Mtb_detection_training.ipynb`** | Train an APOC ObjectSegmenter for Mtb spot detection; produces `./models/Mtb_segmenter.cl`. |

### Standard RCD pipeline

| Notebook | Description |
|----------|-------------|
| **`1_SP_image_viz.ipynb`** | Single-image exploration: load one ND2, run CellposeSAM, extract morphology and marker intensity features, optional Napari visualization. |
| **`2_BP_batch_processing.ipynb`** | Batch run over all images in a data folder; writes one CSV per image under `results/<experiment_id>/`. |
| **`3_data_analysis.ipynb`** | Concatenates per-image CSVs, saves `processed_results/<experiment_id>/concatenated.csv`, computes mean features per well/timepoint, and generates plate-view heatmaps (e.g. area). |

### Infection pipeline

| Notebook | Description |
|----------|-------------|
| **`1_SP_infection_image_viz.ipynb`** | Single-image infection workflow: CellposeSAM cell segmentation, APOC Mtb segmentation, infected-cell detection, per-cell bacterial load, morphology/intensity features, Napari visualization. |
| **`2_BP_infection_batch_processing.ipynb`** | Batch infection processing over all images; writes one CSV per image plus `infection_summary.csv` under `results/<experiment_id>/`. |
| **`3_data_analysis_infection.ipynb`** | Aggregates infection batch outputs: concatenated per-cell table, mean features per well/timepoint, plate-view heatmaps for all features, and plate views of `%_inf_cells` from `infection_summary.csv`. |

---

## Infection-specific outputs

Per-cell CSVs from the infection pipeline include the standard morphology and marker intensity columns, plus:

- **`Mtb_infected_cell`** — `True` if the cell overlaps with segmented Mtb signal.
- **`mtb_area_sum`** — number of Mtb-foreground pixels inside the cell.
- **`%_bacterial_load`** — percentage of the cell area occupied by Mtb (`mtb_area_sum / area × 100`).

`infection_summary.csv` (one row per image) contains:

- **`total_nr_cells`**, **`infected_cells`**, **`non-infected_cells`**
- **`%_inf_cells`** — percentage of segmented cells that are Mtb-positive.

---

## Output layout

```
results/<experiment_id>/
  *.csv                    # one per-image per-cell table
  infection_summary.csv    # infection pipeline only

processed_results/<experiment_id>/
  concatenated.csv         # all per-cell rows combined
  mean_per_well.csv        # numeric features averaged by well_id and timepoint
  plate_view/              # heatmaps per feature and timepoint
```

Well ID and timepoint are parsed from filenames (e.g. `WellB2_after4h_`) via `utils_data_analysis.extract_well_id_and_timepoint`.

---

## Utility modules

| Module | Role |
|--------|------|
| **`utils.py`** | ND2 I/O, image listing, metadata checks. |
| **`utils_infection.py`** | Mtb detection (`detect_infected_cells`), bacterial load (`detect_infection_load`). |
| **`utils_data_analysis.py`** | Well/timepoint parsing, plate-view plotting (`plot_plate_view`). |
| **`data_viz.py`** | Map per-cell feature values onto label images in Napari. |

Pretrained models used by the infection pipeline: `./models/CPSAM_shirik_ft`, `./models/Mtb_segmenter.cl`.

---

## Running Jupyter with Pixi

[Pixi](https://pixi.sh/) manages the environment (Python, PyTorch/CUDA, Cellpose, Jupyter, Napari, APOC, etc.).

1. **Install Pixi** (if needed):  
   https://pixi.sh/latest/install/

2. **From the project root**, install the environment and start Jupyter Lab:

   ```bash
   pixi install
   pixi run lab
   ```

   This starts Jupyter Lab with the project kernel. Open any `.ipynb` notebook and run the cells.

To launch the Napari viewer only: `pixi run napari`.

---

## How to cite this pipeline

If you use this pipeline to analyze your bioimage data, you can include it in your references as follows:

- For APA and BibTeX, scroll to the top of this repository page, above the Release section, and under **About** click **Cite this repository**.

- For APA, Harvard, MLA, Vancouver, Chicago, and IEEE styles, visit the Zenodo record once available (link and DOI badge below are **placeholders until deposition**) and use the **Citation** section in the right panel.

  Placeholder DOI / badge (replace after Zenodo deposition):

  [![DOI](https://img.shields.io/badge/DOI-10.5281/zenodo.XXXXXXX-blue.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)

  Example APA citation (update author, title, version, year, and DOI after deposition):

  ```
  Díez-Sánchez, A. (2026). shirik_RCD_analysis: CellposeSAM RCD and Mtb infection analysis pipeline (v1.0.0). Zenodo. https://doi.org/10.5281/zenodo.XXXXXXX
  ```

---

## Related publications

Placeholder for publications citing this pipeline.
