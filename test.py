def plot_overlap_heatmap(overlap_heatmap_df,
                         ALL_IOS_HEATMAP_SIZE='Medium',
                         COMPARISON_DIMENSION='Comparison',
                         dpi=100):
    """
    overlap_heatmap_df : square DataFrame with overlap fractions (0..1).
    The index/columns are the original IO names (may be long).
    """
    import matplotlib.pyplot as plt
    import seaborn as sns
    import matplotlib.ticker as mtick
    from matplotlib.patches import Patch
    import math, textwrap

    try:
        cleaned_df = overlap_heatmap_df.copy()

        # ---- AUTO BUILD IO MAPPING ----
        categories = list(cleaned_df.index)   # or .columns (same in square heatmap)
        mapping_dict = {cat: f"IO{idx+1}" for idx, cat in enumerate(categories)}

        # Rename both index & columns to IO codes
        cleaned_df = cleaned_df.rename(index=mapping_dict, columns=mapping_dict)

        # ---- FIGURE SIZE ----
        if ALL_IOS_HEATMAP_SIZE == 'Small':
            fig_w, fig_h = 10, 5
        elif ALL_IOS_HEATMAP_SIZE == 'Medium':
            fig_w, fig_h = 20, 10
        else:
            fig_w, fig_h = 30, 20

        n = cleaned_df.shape[0]
        fig_h += max(0, (n - 20) * 0.25)  # grow height with rows

        fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=dpi)

        # ---- HEATMAP ----
        sns.heatmap(
            cleaned_df,
            cmap="Greens",
            annot=True,
            fmt=".0%",
            cbar=True,
            ax=ax,
            linewidths=0.5,
            linecolor="white"
        )

        # format colorbar as %
        cbar = ax.collections[0].colorbar
        cbar.formatter = mtick.PercentFormatter(xmax=1.0, decimals=0)
        cbar.update_ticks()

        # labels
        ax.set_title("DV360 Reach Overlap Heatmap\n", fontsize=18, pad=14)
        ax.set_xlabel(COMPARISON_DIMENSION, fontsize=14)
        ax.set_ylabel(COMPARISON_DIMENSION, fontsize=14)

        ax.tick_params(axis='x', labelsize=9)
        ax.tick_params(axis='y', labelsize=9)
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

        plt.tight_layout(rect=[0, 0.12, 1, 0.98])  # leave space for legend

        # ---- LEGEND (Mapping IO → Original) ----
        handles = [Patch(color="green", label=f"{v} → {k}")
                   for k, v in mapping_dict.items()]

        # auto decide number of columns
        n_items = len(handles)
        if n_items <= 10:
            ncol = 2
        elif n_items <= 20:
            ncol = 3
        elif n_items <= 40:
            ncol = 4
        else:
            ncol = 5

        ax.legend(
            handles=handles,
            title="Mapping (IO → Original)",
            loc="upper center",
            bbox_to_anchor=(0.5, -0.12),
            fontsize=9,
            title_fontsize=10,
            ncol=ncol,
            frameon=False
        )

        plt.show()

    except Exception as e:
        print("Failed to create heatmap:", e)