import io
import math
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.patches import Patch
import seaborn as sns
import pandas as pd

# ----- Optional: ensure good PDF font embedding -----
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['font.sans-serif'] = ['Arial']  # or ["Google Sans","Arial"] if available

# ------------------- Inputs (example) -------------------
# aggregated should be a DataFrame with columns: "IO_label", COMPARISON_DIMENSION, VALUE_COL
# for example:
# aggregated = pd.DataFrame({
#     "IO_label": ["IO1","IO2","IO3"],
#     "Insertion Order": ["Long name A","Long name B","Long name C"],
#     "Unique Reach: Exclusive Total Reach": [1234, 5678, 9012]
# })

COMPARISON_DIMENSION = "Insertion Order"
VALUE_COL = "Unique Reach: Exclusive Total Reach"

# --------------- Figure & plotting params ----------------
BAR_CHARTS_WIDTH_IN_PIXELS = 1400
# choose dynamic height or fixed:
HEIGHT_PER_CATEGORY_PX = 40
MIN_HEIGHT_PX = 600
dpi = 100

TITLE_FS = 20
AXIS_LABEL_FS = 16
TICK_LABEL_FS = 15
ANNOT_FONT_FS = 20    # large annotation font
LEGEND_FS = 14
LEGEND_TITLE_FS = 16

# ----------------- compute figure size -------------------
n_categories = aggregated.shape[0]
width_px = BAR_CHARTS_WIDTH_IN_PIXELS
height_px = max(MIN_HEIGHT_PX, n_categories * HEIGHT_PER_CATEGORY_PX)

fig_w = width_px / dpi
fig_h = height_px / dpi

fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=dpi)

# ------------------ plot (horizontal bars) ----------------
sns.barplot(
    data=aggregated,
    x=VALUE_COL,
    y="IO_label",
    orient="h",
    ax=ax,
    color="#4285F4"
)

# -------------- format axes, title, ticks -----------------
ax.set_title(f"{COMPARISON_DIMENSION} — Duplicate Reach", fontsize=TITLE_FS, family="Arial")
ax.set_xlabel(VALUE_COL, fontsize=AXIS_LABEL_FS, family="Arial")
ax.set_ylabel("Insertion Orders (IO)", fontsize=AXIS_LABEL_FS, family="Arial")

# tick sizes and rotation
ax.tick_params(axis="x", labelsize=TICK_LABEL_FS)
ax.tick_params(axis="y", labelsize=TICK_LABEL_FS)
plt.setp(ax.get_xticklabels(), rotation=0, ha="center", fontsize=TICK_LABEL_FS)
plt.setp(ax.get_yticklabels(), fontsize=TICK_LABEL_FS, family="Arial")

# format x axis to avoid small decimals or scientific notation
ax.xaxis.set_major_formatter(mtick.StrMethodFormatter("{x:,.0f}"))
ax.ticklabel_format(style="plain", axis="x")

# ---------------- annotate values at bar end ----------------
for p in ax.patches:
    width = p.get_width()
    # safety for NaN
    if pd.isna(width):
        label_text = ""
    else:
        # integer if whole number else show 2 decimals
        label_text = f"{int(width):,}" if float(width).is_integer() else f"{width:.2f}"

    ax.annotate(
        label_text,
        xy=(width, p.get_y() + p.get_height() / 2),
        xytext=(10, 0),                  # offset to the right
        textcoords="offset points",
        va="center",
        fontsize=ANNOT_FONT_FS,
        fontweight="bold",
        family="Arial",
        color="black"
    )

# ---------------- build legend handles (IO -> original) ----------------
# aggregated contains IO_label and original long name in COMPARISON_DIMENSION
handles = []
for io_label, original in zip(aggregated["IO_label"], aggregated[COMPARISON_DIMENSION]):
    # shorten long original names so legend isn't huge, but keep full if short
    short_orig = original if len(str(original)) <= 80 else str(original)[:77] + "..."
    handles.append(Patch(color="#4285F4", label=f"{io_label} → {short_orig}"))

# auto ncol selection
n_items = len(handles)
if n_items <= 10:
    ncol = 2
elif n_items <= 20:
    ncol = 3
elif n_items <= 40:
    ncol = 4
else:
    ncol = 6

# -------------- place legend below and style it ----------------
ax.legend(
    handles=handles,
    title="Mapping (IO → Original)",
    loc="upper center",
    bbox_to_anchor=(0.5, -0.12),   # centered below
    fontsize=LEGEND_FS,
    title_fontsize=LEGEND_TITLE_FS,
    ncol=ncol,
    frameon=False
)

# leave room for legend
plt.tight_layout(rect=[0, 0.05, 1, 0.98])

# -------------- increase xticks/yticks fontsize explicitly --------------
plt.yticks(fontsize=TICK_LABEL_FS)
plt.xticks(rotation=0, ha="center", fontsize=TICK_LABEL_FS)

# ------------------ Save to buffer and files ------------------
buf = io.BytesIO()
# PNG (high res)
plt.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", pad_inches=0.1)
buf.seek(0)

# also save to disk PNG
plt.savefig("bar_plot.png", dpi=300, bbox_inches="tight", pad_inches=0.1)

# Save high-quality PDF (vector text; fonts embedded via rcParams above)
plt.savefig("bar_plot.pdf", format="pdf", bbox_inches="tight", pad_inches=0.1)

plt.show()
plt.close(fig)