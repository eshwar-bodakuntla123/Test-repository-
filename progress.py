import io
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from matplotlib.patches import Patch

# ---------- USER CONFIG ----------
COMPARISON_DIMENSION = "your_category_col"   # categorical col
VALUE_COL = "Unique Reach: Duplicate Total Reach"
BAR_CHARTS_WIDTH_IN_PIXELS = 1200
BAR_CHARTS_HEIGHT_IN_PIXELS = 800
dpi = 100
# ----------------------------------

# Example df (remove when you already have it)
# df = pd.DataFrame({
#     "your_category_col": ["Campaign A", "Campaign B", "Campaign A", "Campaign C"],
#     "Unique Reach: Duplicate Total Reach": [100, 200, 50, 300]
# })

# create IO mapping
unique_categories = list(pd.Series(df[COMPARISON_DIMENSION]).drop_duplicates())
mapping = {cat: f"IO{idx+1}" for idx, cat in enumerate(unique_categories)}
df["IO_label"] = df[COMPARISON_DIMENSION].map(mapping)

# aggregate per IO
aggregated = df.groupby(["IO_label", COMPARISON_DIMENSION], sort=False)[VALUE_COL].sum().reset_index()

# pixel → inch
fig_w = BAR_CHARTS_WIDTH_IN_PIXELS / dpi
fig_h = BAR_CHARTS_HEIGHT_IN_PIXELS / dpi

fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=dpi)

# barplot
sns.barplot(
    data=aggregated,
    x=VALUE_COL,
    y="IO_label",
    orient="h",
    ax=ax,
    color="#4285F4"
)

ax.set_title(f"{COMPARISON_DIMENSION} — Duplicate Reach", fontsize=16)
ax.set_xlabel("Unique Reach: Duplicate Total Reach", fontsize=12)
ax.set_ylabel("Insertion Orders", fontsize=12)

# add bar value labels
for p in ax.patches:
    width = p.get_width()
    ax.annotate(f"{int(width):,}" if float(width).is_integer() else f"{width:.2f}",
                (width, p.get_y() + p.get_height() / 2),
                xytext=(5, 0),
                textcoords="offset points",
                va="center",
                fontsize=10)

# --------- LEGEND BELOW ---------
handles = []
for io_label, original in zip(aggregated["IO_label"], aggregated[COMPARISON_DIMENSION]):
    handles.append(Patch(color="#4285F4", label=f"{io_label} → {original}"))

# Place legend below the chart
ax.legend(
    handles=handles,
    title="Mapping (IO → Original)",
    loc="upper center",
    bbox_to_anchor=(0.5, -0.15),  # center below
    fontsize=9,
    title_fontsize=10,
    ncol=3,   # <-- adjust number of columns for compactness
    frameon=False
)

plt.tight_layout(rect=[0, 0.1, 1, 1])  # leave extra space at bottom

buf = io.BytesIO()
plt.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
buf.seek(0)

print(f"Chart ready with legend BELOW (total {len(mapping)} IOs)")