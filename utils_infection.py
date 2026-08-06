import numpy as np
import pandas as pd
from skimage.measure import regionprops_table
import pyclesperanto_prototype as cle

def detect_infected_cells(img, mtb_segmenter, cell_labels, mtb_channel, filename, infection_stats):
        """Detect infected cells"""
        print("\nDetecting infected cells...")

        # Detect Mtb spots
        mtb_labels = mtb_segmenter.predict(img[mtb_channel])
        mtb_labels = cle.pull(mtb_labels)

        # Convert mtb_labels to boolean mask
        mtb_boolean = mtb_labels.astype(bool)

        # Use NumPy's indexing to identify cell labels that intersect with mtb_boolean (bacterial mask)
        infected_cell_labels = np.unique(cell_labels[mtb_boolean])
        infected_cell_labels = infected_cell_labels[infected_cell_labels != 0]

        # Extract stats for each cell
        infected_cell_mask = np.isin(cell_labels, infected_cell_labels)
        non_infected_cell_mask = np.isin(cell_labels, infected_cell_labels, invert=True)
        infected_cells_array = np.where(infected_cell_mask, cell_labels, 0).astype(cell_labels.dtype)
        non_infected_cells_array = np.where(non_infected_cell_mask, cell_labels, 0).astype(cell_labels.dtype)

        infected_cells = len(np.unique(infected_cells_array)) - (0 in infected_cells_array)
        non_infected_cells = len(np.unique(non_infected_cells_array)) - (0 in non_infected_cells_array)
        total_cells = cell_labels.max()

        # Calculate percentage of infected cells 
        perc_inf_cells = round(infected_cells / total_cells * 100, 2) if total_cells > 0 else 0

        print(f"Total cells: {total_cells}")
        print(f"Percentage infected:{perc_inf_cells}")

        # Create a dictionary containing all extracted info per image
        stats_dict = {
                    "filename": filename,
                    "total_nr_cells": total_cells,
                    "infected_cells": infected_cells,
                    "non-infected_cells": non_infected_cells,
                    "%_inf_cells": perc_inf_cells,
        }

        # Append the current data point to the stats_list
        infection_stats.append(stats_dict)

        return mtb_labels, infected_cell_labels

def extract_mtb_regionprops(mtb_labels, plate_nr, well_id, image):

    print("Extracting Mtb properties...")

    # Single list of regionprops to request (modify based on needs)
    regionprops_properties = [
        "label",
        "area",                          # number of voxels (volume in voxel units)
        "axis_major_length",             # length of major axis from inertia tensor (elongation)
        "axis_minor_length",             # length of minor axis (second principal axis in 3D)
        "equivalent_diameter_area",      # diameter of sphere with same volume as region
        "euler_number",                  # topology: objects + holes − tunnels (connectivity)
        "extent",                        # volume / bounding-box volume (fill of the box)
        "feret_diameter_max",            # maximum Feret (caliper) diameter
        "solidity"                      # volume / convex-hull volume (compact vs lobed)
    ]

    # Create a dictionary containing all image metadata
    descriptor_dict = {
        "plate": plate_nr,
        "well_id": well_id,
        "filepath": image
        }

    # Extract morphological features from bacterial labels (mtb_labels)
    props = regionprops_table(label_image=mtb_labels,
                        properties=regionprops_properties)

    # Convert to dataframe
    props_df = pd.DataFrame(props)

    # Add each key-value pair from descriptor_dict to props_df at the specified position
    insertion_position = 0
    for key, value in descriptor_dict.items():
        props_df.insert(insertion_position, key, value)
        insertion_position += 1  # Increment position to maintain the order of keys in descriptor_dict

    return props_df


def detect_infection_load(mtb_labels, cell_labels, props_df):
    """Sum of Mtb (foreground) pixels per cell, left-join onto props_df, plus %_bacterial_load vs cell area."""

    # Non-zero Mtb voxels become True so we count bacterial footprint regardless of label id
    mtb_mask = np.asarray(mtb_labels).astype(bool)
    cell_labels = np.asarray(cell_labels)

    # Per-pixel overlap only makes sense when both arrays align spatially
    if mtb_mask.shape != cell_labels.shape:
        raise ValueError(
            f"mtb_labels shape {mtb_mask.shape} does not match cell_labels shape {cell_labels.shape}"
        )

    max_label = int(cell_labels.max())
    if max_label <= 0:
        # No segmented cells: nothing to aggregate, merge will only add an empty column
        load_df = pd.DataFrame(columns=["label", "mtb_area_sum"])
    else:
        # Cell id at each Mtb pixel; bincount gives Mtb pixel count per cell label index
        masked_cells = cell_labels[mtb_mask].ravel().astype(np.int64)
        counts = np.bincount(masked_cells, minlength=max_label + 1)
        cell_label_ids = np.unique(cell_labels)
        cell_label_ids = cell_label_ids[cell_label_ids != 0]
        load_df = pd.DataFrame(
            {
                "label": cell_label_ids.astype(int),
                "mtb_area_sum": counts[cell_label_ids].astype(np.int64),
            }
        )

    # Keep every props_df row; add mtb_area_sum where labels match
    out = props_df.merge(load_df, on="label", how="left")
    # Cells with no overlapping Mtb get NaN from the left merge — treat as zero load
    out["mtb_area_sum"] = out["mtb_area_sum"].fillna(0).astype(np.int64)

    # Share of cell region area (regionprops "area") covered by Mtb foreground pixels
    out["%_bacterial_load"] = np.where(
        out["area"] > 0,
        np.round(out["mtb_area_sum"] / out["area"] * 100, 2),
        0.0,
    )

    return out