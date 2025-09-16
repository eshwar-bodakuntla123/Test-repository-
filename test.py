import os
import io
import base64
import math
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
from matplotlib.patches import Patch
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns

def export_io_barplot_pdf(
    df,
    COMPARISON_DIMENSION="Insertion Order",
    VALUE_COL="Unique Reach: Exclusive Total Reach",
    BAR_CHARTS_WIDTH_IN_PIXELS=1400,
    HEIGHT_PER_CATEGORY_PX=40,
    MIN_HEIGHT_PX=600,
    dpi_pdf=300,                # DPI used when saving raster (PNG) and for the PDF save
    out_pdf="bar_plot_vector.pdf",
    out_png="bar_plot_highres.png",
    annotation_fontsize=18,
    tick_label_fs=14,
    axis_label_fs=16,
    title_fs=20,
    legend_fs=12,
    legend_title_fs=14,
    font_family_list=None
):
    """
    Create high-quality barplot and export both a vector PDF (best when embedding in reports)
    and a high-res PNG fallback.

    Returns (mapping_dict, out_pdf, out_png, base64_png)
    """
    # ----------------- professional defaults -----------------
    if font_family_list is None:
        # list: first item will be used if installed; DejaVu Sans always available
        font_family_list = ["Arial", "DejaVu Sans"]

    # Make fonts embed-friendly for PDF
    mpl.rcParams['pdf.fonttype'] = 42   # TrueType (embed fonts)
    mpl.rcParams['ps.fonttype'] = 42
    mpl.rcParams['font.family'] = 'sans-serif'
    mpl.rcParams['font.sans-serif'] = font_family_list

    # Validate inputs
    if COMPARISON_DIMENSION not in df.columns:
        raise KeyError(f"Column '{COMPARISON_DIMENSION}' not found in DataFrame")
    if VALUE_COL not in df.columns:
        raise KeyError(f"Column '{VALUE_COL}' not found in DataFrame")

    # Work on a copy
    data = df.copy()

    # Ensure numeric
    data[VALUE_COL] = pd.to_numeric(data[VALUE_COL], errors="coerce")

    # Build mapping preserving insertion order
    unique_categories = list(pd.Series(data[COMPARISON_DIMENSION]).drop_duplicates())
    mapping = {orig: f"IO{idx+1}" for idx, orig in enumerate(unique_categories)}

    # Map and aggregate
    data["IO_label"] = data[COMPARISON_DIMENSION].map(mapping)
    aggregated = (
        data.groupby(["IO_label", COMPARISON_DIMENSION], sort=False)[VALUE_COL]
            .sum()
            .reset_index()
    )

    # Figure size in inches (fixed width; dynamic height per category)
    width_px = BAR_CHARTS_WIDTH_IN_PIXELS
    n_categories = max(1, aggregated.shape[0])
    height_px = max(MIN_HEIGHT_PX, n_categories * HEIGHT_PER_CATEGORY_PX)

    fig_w = width_px / dpi_pdf
    fig_h = height_px / dpi_pdf

    # Create figure
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=dpi_pdf)

    # Horizontal barplot so IO labels remain short
    sns.barplot(
        data=aggregated,
        x=VALUE_COL,
        y="IO_label",
        orient="h",
        ax=ax,
        color="#4285F4",
        linewidth=0
    )

    # Titles and axis labels
    ax.set_title(f"{COMPARISON_DIMENSION} — Exclusive Reach", fontsize=title_fs, family=font_family_list[0])
    ax.set_xlabel(VALUE_COL, fontsize=axis_label_fs, family=font_family_list[0])
    ax.set_ylabel("Insertion Orders (IO)", fontsize=axis_label_fs, family=font_family_list[0])

    # Ticks
    ax.tick_params(axis="x", labelsize=tick_label_fs)
    ax.tick_params(axis="y", labelsize=tick_label_fs)
    # avoid scientific notation, show integers with commas
    ax.xaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    ax.ticklabel_format(style="plain", axis="x")

    # Annotate bar-end values (big, bold, white background so they are always readable)
    for p in ax.patches:
        width = p.get_width()
        if pd.isna(width):
            label_text = ""
        else:
            # integer formatting if no fractional part
            label_text = f"{int(width):,}" if float(width).is_integer() else f"{width:,.2f}"
        ax.annotate(
            label_text,
            xy=(width, p.get_y() + p.get_height() / 2),
            xytext=(8, 0),
            textcoords="offset points",
            va="center",
            fontsize=annotation_fontsize,
            fontweight="bold",
            family=font_family_list[0],
            color="black",
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.9)
        )

    # Build IO -> original legend handles (preserve IO order from aggregated)
    # Use aggregated to preserve the insertion order of IOs
    seen = set()
    handles = []
    for io in aggregated["IO_label"]:
        if io in seen:
            continue
        seen.add(io)
        orig = aggregated.loc[aggregated["IO_label"] == io, COMPARISON_DIMENSION].iloc[0]
        short_orig = str(orig) if len(str(orig)) <= 90 else str(orig)[:87] + "..."
        handles.append(Patch(facecolor="#4285F4", label=f"{io} → {short_orig}"))

    # Auto ncol selection so legend doesn't become a single tall column
    n_items = len(handles)
    if n_items <= 10:
        ncol = 2
    elif n_items <= 20:
        ncol = 3
    elif n_items <= 40:
        ncol = 4
    else:
        ncol = 6

    # Place legend centered below the chart
    ax.legend(
        handles=handles,
        title="Mapping (IO → Original)",
        loc="upper center",
        bbox_to_anchor=(0.5, -0.12),
        fontsize=legend_fs,
        title_fontsize=legend_title_fs,
        ncol=ncol,
        frameon=False
    )

    # Leave space for legend
    plt.tight_layout(rect=[0, 0.06, 1, 1])

    # ---------------- Save: vector PDF (best) ----------------
    # Use PdfPages to ensure a single-page PDF at the exact figure size; fonts are embedded via rcParams
    with PdfPages(out_pdf) as pdf:
        pdf.savefig(fig, bbox_inches="tight", pad_inches=0.1, dpi=dpi_pdf)

    # ---------------- Save: very high-res PNG fallback ----------------
    # Many corporate tools rasterize on paste; provide a very-high-res PNG (600 DPI or more)
    fig.savefig(out_png, dpi=600, bbox_inches="tight", pad_inches=0.1)

    # Get PNG base64 if you need to embed programmatically
    with open(out_png, "rb") as f:
        img_bytes = f.read()
    img_b64 = base64.b64encode(img_bytes).decode("ascii")

    plt.close(fig)

    return mapping, out_pdf, out_png, img_b64

# ---------------- Example usage ----------------
# mapping, pdf_path, png_path, png_b64 = export_io_barplot_pdf(df)
# print("Saved:", pdf_path, png_path)