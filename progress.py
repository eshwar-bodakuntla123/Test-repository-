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

# Example dataframe (remove when you have df)
# df = pd.DataFrame({
#     "your_category_col": ["Very Long Campaign A", "Very Long Campaign B", "Very Long Campaign C"],
#     "Unique Reach: Duplicate Total Reach": [123, 456, 78]
# })

# keep insertion order
unique_categories = list(pd.Series(df[COMPARISON_DIMENSION]).drop_duplicates())
mapping = {cat: f"IO{idx+1}" for idx, cat in enumerate(unique_categories)}

# add IO label
df["IO_label"] = df[COMPARISON_DIMENSION].map(mapping)

# aggregate values per category
aggregated = df.groupby(["IO_label", COMPARISON_DIMENSION], sort=False)[VALUE_COL].sum().reset_index()

# pixel → inch
fig_w = BAR_CHARTS_WIDTH_IN_PIXELS / dpi
fig_h = BAR_CHARTS_HEIGHT_IN_PIXELS / dpi

fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=dpi)

# horizontal barplot
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

# add value labels at bar end
for p in ax.patches:
    width = p.get_width()
    ax.annotate(f"{int(width):,}" if float(width).is_integer() else f"{width:.2f}",
                (width, p.get_y() + p.get_height() / 2),
                xytext=(5, 0),
                textcoords="offset points",
                va="center",
                fontsize=10)

# --------- CUSTOM LEGEND ---------
# create legend handles (IO → Original)
handles = []
for io_label, original in zip(aggregated["IO_label"], aggregated[COMPARISON_DIMENSION]):
    handles.append(Patch(color="#4285F4", label=f"{io_label} → {original}"))

# place legend outside
ax.legend(
    handles=handles,
    title="Mapping (IO → Original)",
    loc="center left",
    bbox_to_anchor=(1.02, 0.5),
    fontsize=9,
    title_fontsize=10,
    frameon=False
)

plt.tight_layout(rect=[0, 0, 0.75, 1])  # leave space for legend

buf = io.BytesIO()
plt.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
buf.seek(0)

print(f"bar chart ready with legend: {len(mapping)} IO mappings")