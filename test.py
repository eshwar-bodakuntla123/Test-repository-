import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mtick
import math
import textwrap

def plot_overlap_heatmap(overlap_heatmap_df,
                         ALL_IOS_HEATMAP_SIZE='Medium',
                         COMPARISON_DIMENSION='Comparison',
                         mapping_dict=None,   # optional: {original_name: "IO1", ...} or { "IO1": original_name }
                         dpi=100):
    """
    overlap_heatmap_df : square DataFrame with values in 0..1 (fractions representing % overlap)
    ALL_IOS_HEATMAP_SIZE : 'Small'|'Medium'|'Large' controlling base figsize
    mapping_dict : optional dict to display mapping legend below the heatmap
    """
    try:
        # Assume overlap_heatmap_df is already cleaned by overlap_col_cleaner
        cleaned_df = overlap_heatmap_df.copy()

        # Choose figsize based on size selection (in inches)
        if ALL_IOS_HEATMAP_SIZE == 'Small':
            fig_w, fig_h = 10, 5
        elif ALL_IOS_HEATMAP_SIZE == 'Medium':
            fig_w, fig_h = 20, 10
        else:
            fig_w, fig_h = 30, 20

        # If there are many rows, increase height to avoid cramped labels (optional)
        n = cleaned_df.shape[0]
        # add a small per-row height bump so each row has at least ~0.25 inch
        extra_h = max(0, (n - 20) * 0.25)
        fig_h = fig_h + extra_h

        fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=dpi)

        # Plot heatmap. Assume values are fractions 0..1; annot shows percent with 0 decimals
        sns.heatmap(
            cleaned_df,
            cmap="Greens",
            annot=True,
            fmt=".0%",            # show annotations as percentages
            cbar=True,
            ax=ax,
            linewidths=0.5,
            linecolor="white",
            square=False
        )

        # Colorbar (legend) formatting: show ticks as percentages
        cbar = ax.collections[0].colorbar
        cbar.formatter = mtick.PercentFormatter(xmax=1.0, decimals=0)
        cbar.update_ticks()
        cbar.ax.tick_params(labelsize=10)

        # Titles and axis labels + font sizes
        ax.set_title("DV360 Reach Overlap Heatmap\n", fontsize=18, pad=14)
        ax.set_xlabel(COMPARISON_DIMENSION, fontsize=14)
        ax.set_ylabel(COMPARISON_DIMENSION, fontsize=14)

        # Ticks fontsize and rotation
        ax.tick_params(axis='y', labelsize=9)
        ax.tick_params(axis='x', labelsize=9)
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")  # rotate x labels for readability

        plt.tight_layout(rect=[0, 0.12, 1, 0.98])  # leave room at bottom for mapping legend

        # ---- Optional: mapping legend below the chart ----
        # mapping_dict expected either {original_name: "IO1"} or {"IO1": original_name}
        if mapping_dict:
            # Normalize mapping to IO -> original_name
            # detect which side looks like IOs (IO\d+). If keys look like IOs, flip.
            first_key = next(iter(mapping_dict))
            if str(first_key).upper().startswith("IO") or any(str(k).upper().startswith("IO") for k in mapping_dict.keys()):
                io_to_original = {k: v for k, v in mapping_dict.items()}
            else:
                io_to_original = {v: k for k, v in mapping_dict.items()}  # flip original->IO to IO->original

            # Build mapping lines
            mapping_lines = [f"{io} → {textwrap.shorten(orig, width=80)}" for io, orig in io_to_original.items()]

            # Auto-split into columns based on number of items
            def split_to_columns(lines, max_cols=6, approx_per_col=10):
                n = len(lines)
                # Choose cols so rows per column ~ approx_per_col
                ncols = min(max_cols, max(1, math.ceil(n / approx_per_col)))
                rows = math.ceil(n / ncols)
                cols = []
                for c in range(ncols):
                    start = c * rows
                    cols.append(lines[start:start + rows])
                # pad
                maxrows = max(len(c) for c in cols)
                for c in cols:
                    while len(c) < maxrows:
                        c.append("")
                rows_combined = []
                for r in range(maxrows):
                    row = "    ".join(col[r].ljust(60) for col in cols)
                    rows_combined.append(row)
                return "\n".join(rows_combined)

            # If many items, split into columns; otherwise single column
            if len(mapping_lines) > 12:
                mapping_text = split_to_columns(mapping_lines, max_cols=6, approx_per_col=12)
            else:
                mapping_text = "\n".join(mapping_lines)

            # Add as figure text centered below chart
            fig.text(0.5, 0.02, mapping_text, ha='center', va='bottom', fontsize=10, family='monospace')

        plt.show()

    except NameError as e:
        print('Could not find the Reach Overlap % data within your sheet')
        print(f"Invalid input. Details: {e}")
    except Exception as e:
        # generic catch so you get helpful feedback
        print("Failed to create heatmap. Details:", e)


# --------------------------
# Example usage:
# cleaned = overlap_col_cleaner(overlap_heatmap_df)  # as you had
# mapping_example = {"Very long campaign name A": "IO1", "Very long campaign name B": "IO2"}
# plot_overlap_heatmap(cleaned, ALL_IOS_HEATMAP_SIZE='Medium', COMPARISON_DIMENSION='Campaign', mapping_dict=mapping_example)