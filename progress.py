import seaborn as sns
import matplotlib.pyplot as plt

try:
    # Desired pixel size
    width_px = 800   # same as BAR_CHARTS_WIDTH_IN_PIXELS
    height_px = 600  # same as BAR_CHARTS_HEIGHT_IN_PIXELS
    dpi = 100        # dots per inch (default in Matplotlib)

    # Convert pixels → inches
    fig_w = width_px / dpi
    fig_h = height_px / dpi

    # Create the figure with exact pixel size
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=dpi)

    # Bar chart
    sns.barplot(
        data=df,
        x="COMPARISON_DIMENSION",
        y="Unique Reach: Exclusive Total Reach",
        palette="crest",
        ax=ax
    )

    # Labels and title
    ax.set_title("COMPARISON_DIMENSION + Exclusive Reach", fontsize=14)
    ax.set_xlabel("COMPARISON_DIMENSION", fontsize=12)
    ax.set_ylabel("Unique Reach: Exclusive Total Reach", fontsize=12)
    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()
    plt.show()

except KeyError as e:
    print("⚠️ Could not find the Insertion Order and/or Advertiser values within those columns in your sheets")
    print(f"Invalid input. Details: {e}")