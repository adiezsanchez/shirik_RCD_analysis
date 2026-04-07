import os
import re
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def parse_well_row_col(well):
    """
    Parse a well identifier into row letter (A–H) and column (1–12).

    First tries plain plate IDs (entire string), e.g. ``B2``, ``H12``.
    If that fails, searches for ``Well<Row><Col>`` before a non-digit
    (e.g. ``...WellB2_after4h_...``), avoiding ``\\b`` after digits when
    the next character is ``_`` (underscore is a word char in Python regex).
    """
    s = str(well).strip()
    m = re.fullmatch(r"([A-H])(\d{1,2})", s)
    if m:
        return m.group(1), int(m.group(2))
    m = re.search(r"Well([A-H])(\d{1,2})(?=[^\d]|$)", s)
    if m:
        return m.group(1), int(m.group(2))
    return None, None


def plot_plate_view(df, column_name, title, label, save_dir, fmt=3, display=True, cmap="magma"):
    # --- Parse well_id into row (A–H) and column (1–12) ---
    df[["row", "col"]] = df["well_id"].apply(
        lambda x: pd.Series(parse_well_row_col(x))
    )
    df = df.dropna(subset=["row", "col"])

    # --- One matrix cell per well; mean if multiple rows share the same well (e.g. Pos013 + Pos014) ---
    plate_matrix = df.pivot_table(
        index="row", columns="col", values=column_name, aggfunc="mean"
    )

    # Reindex rows and columns to enforce full plate structure
    rows = list("ABCDEFGH")
    cols = list(range(1, 13))
    plate_matrix = plate_matrix.reindex(index=rows, columns=cols)

    # --- Plot heatmap ---
    plt.figure(figsize=(12, 6))
    ax = sns.heatmap(
        plate_matrix,
        cmap=cmap,  # or "coolwarm", "magma" etc.
        linewidths=0.5,
        linecolor="gray",
        cbar_kws={'label': label},
        annot=True, fmt=f".{fmt}f"
    )

    plt.title(title, fontsize=14)
    plt.xlabel("Column")
    plt.ylabel("Row")

    # Rotate row (y-axis) labels 90° to the right
    ax.set_yticklabels(ax.get_yticklabels(), rotation=-90, va="center")

    # --- Save plot ---
    save_dir_full = f"{save_dir}/plate_view"
    os.makedirs(save_dir_full, exist_ok=True)
    save_path = os.path.join(save_dir_full, f"{column_name}.png")
    plt.savefig(save_path, dpi=300, bbox_inches="tight")

    if display:
        plt.show()
    else:
        plt.close()

    print(f"Saved plate view to {save_path}")

def get_1st_99th_percentile(series):
    """
    Returns the 1st and 99th percentile values of a pandas Series as a tuple (min, max).
    """
    p1 = series.quantile(0.01)
    p99 = series.quantile(0.99)
    return (p1, p99)


