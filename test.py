# UI for DV360 Reach Overlap Analysis (ipywidgets)
# Paste this cell into your Jupyter / Colab notebook.
# Dependencies: ipywidgets, pandas, plotly
# Install in Colab if needed:
#   !pip install ipywidgets pandas plotly
# In classic Jupyter you may need:
#   !jupyter nbextension enable --py widgetsnbextension

import io
import re
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

import ipywidgets as widgets
from IPython.display import display, clear_output

# ------------------------
# Helper data-processing functions
# ------------------------

def read_csv_from_upload(file_upload_widget):
    """Return DataFrame from a single-file FileUpload widget (ipywidgets)."""
    if not file_upload_widget.value:
        return None
    # Take first uploaded file
    key = next(iter(file_upload_widget.value))
    content = file_upload_widget.value[key]['content']
    return pd.read_csv(io.BytesIO(content))

def read_csv_from_url(csv_url):
    """Read CSV from an exported Google Sheet CSV or any raw CSV URL."""
    # pandas can read many URLs directly in Colab / Notebook
    return pd.read_csv(csv_url)

def ensure_pivot_matrix(df, value_col='Overlap %', row_dim_col=None, col_dim_col=None, pivot_prefix=None):
    """
    Given the raw DV360 overlap export (expected with pivoted columns or as long format),
    try to produce a square matrix of overlap percentages where rows are entities and
    columns are entities being compared.

    The original repo produces a pivoted matrix; here we try to support:
     - Already pivoted data (wide): where df.index or first column contains row labels and
       columns are pivoted target entity columns.
     - Long format: columns like ['Source', 'Target', 'Overlap %']
    """
    # Heuristic: If the DF is already a square matrix (n x n) with numeric cells, return it.
    # Otherwise, try to detect long format.
    df_temp = df.copy()
    # Strip leading/trailing whitespace from column names
    df_temp.columns = [c.strip() if isinstance(c, str) else c for c in df_temp.columns]

    # Case 1: Already pivoted - detect if most non-index columns are numeric
    numeric_cols = [c for c in df_temp.columns if pd.api.types.is_numeric_dtype(df_temp[c])]
    # If more than half columns are numeric, interpret df as wide pivot
    if len(numeric_cols) >= max(1, len(df_temp.columns) // 2):
        # Try to set first column as index if it's non-numeric & unique
        first_col = df_temp.columns[0]
        if not pd.api.types.is_numeric_dtype(df_temp[first_col]) and df_temp[first_col].is_unique:
            mat = df_temp.set_index(first_col)
        else:
            # Otherwise try to infer index from index
            mat = df_temp.copy()
            mat.index = mat.index.astype(str)
        # ensure numeric
        mat = mat.apply(pd.to_numeric, errors='coerce')
        return mat.fillna(0).astype(float)

    # Case 2: long-format detection
    # Try to find likely column names
    cols = [c.lower() for c in df_temp.columns.astype(str)]
    # find candidate columns
    def _find(col_options):
        for opt in col_options:
            for i,c in enumerate(cols):
                if opt in c:
                    return df_temp.columns[i]
        return None

    src_col = _find(['source','row','insertion order','insertion_order','io','advertiser','from'])
    tgt_col = _find(['target','column','to','advertiser','insertion order','insertion_order','io'])
    val_col = _find(['overlap','unique reach','reach percent','percent','%'])

    if src_col and tgt_col and val_col:
        long_df = df_temp[[src_col, tgt_col, val_col]].copy()
        long_df.columns = ['source', 'target', 'value']
        # Remove percent signs and convert
        long_df['value'] = long_df['value'].astype(str).str.replace('%','').str.strip()
        long_df['value'] = pd.to_numeric(long_df['value'], errors='coerce').fillna(0)
        pivot = long_df.pivot_table(index='source', columns='target', values='value', aggfunc='first').fillna(0)
        return pivot.astype(float)

    # If nothing matched, attempt best-effort: treat first column as labels, others as numeric columns
    try:
        first_col = df_temp.columns[0]
        mat = df_temp.set_index(first_col).apply(pd.to_numeric, errors='coerce').fillna(0)
        return mat.astype(float)
    except Exception as e:
        raise ValueError("Could not auto-detect data format. Please provide a DV360-exported pivoted CSV or a long-format CSV with source/target/overlap columns.") from e

def filter_matrix(matrix, include_rows=None, exclude_rows=None, include_cols=None, exclude_cols=None):
    """
    Apply substring filters (case-sensitive per original repo) to select a filtered submatrix.
    include/exclude are substrings; if None or empty -> no change.
    """
    # Work on copies
    rows = matrix.index.astype(str)
    cols = matrix.columns.astype(str)

    def _apply_includes(items, substr):
        if not substr:
            return items
        return [i for i in items if substr in i]

    def _apply_excludes(items, substr):
        if not substr:
            return items
        return [i for i in items if substr not in i]

    rows_sel = _apply_includes(rows, include_rows)
    rows_sel = _apply_excludes(rows_sel, exclude_rows)
    cols_sel = _apply_includes(cols, include_cols)
    cols_sel = _apply_excludes(cols_sel, exclude_cols)

    filtered = matrix.loc[matrix.index.isin(rows_sel), matrix.columns.isin(cols_sel)]
    return filtered

def plot_heatmap(matrix, title="Heatmap", size='Large'):
    """
    Draw a heatmap using plotly. 'size' controls the figure width/height heuristically.
    """
    if matrix is None or matrix.size == 0:
        fig = go.Figure()
        fig.update_layout(title=title)
        return fig

    mapping = {'Small': (600, 450), 'Medium': (900, 700), 'Large': (1400, 900)}
    w, h = mapping.get(size, mapping['Large'])
    fig = px.imshow(matrix.values,
                    labels=dict(x="Target", y="Source", color="Overlap %"),
                    x=matrix.columns.astype(str),
                    y=matrix.index.astype(str),
                    aspect='auto',
                    origin='lower',
                    text_auto=True)
    fig.update_layout(title=title, width=w, height=h)
    return fig

def compute_exclusive_duplicate(matrix):
    """
    For each entity compute Exclusive reach and Duplicate reach with simple heuristics:
    - Exclusive = 100 - max(overlap of that entity with others)  (simple proxy)
    - Duplicate = max(overlap) (because duplicate reach indicates overlap with others)
    This is a lightweight proxy — adapt to the project’s canonical formulas as needed.
    """
    if matrix is None or matrix.size == 0:
        return pd.DataFrame(columns=['Entity','Exclusive','Duplicate'])

    max_overlap = pd.DataFrame({
        'Entity': matrix.index.astype(str),
        'Duplicate': matrix.max(axis=1).values
    })
    max_overlap['Exclusive'] = 100 - max_overlap['Duplicate']
    return max_overlap

# ------------------------
# Build Widgets (UI components)
# ------------------------
# File input / URL input
file_upload = widgets.FileUpload(accept='.csv', multiple=False, description='Upload CSV', button_style='primary')
csv_url_input = widgets.Text(placeholder='Or paste export CSV URL (Google Sheet "export?format=csv" link)', description='CSV URL:', layout=widgets.Layout(width='80%'))

# Filters & options
include_rows_text = widgets.Text(description='Include rows containing:', placeholder='case-sensitive substring')
exclude_rows_text = widgets.Text(description='Exclude rows containing:', placeholder='case-sensitive substring')
include_cols_text = widgets.Text(description='Include cols containing:', placeholder='case-sensitive substring')
exclude_cols_text = widgets.Text(description='Exclude cols containing:', placeholder='case-sensitive substring')

comparison_dropdown = widgets.Dropdown(options=['Insertion Order','Advertiser'], value='Insertion Order', description='Compare:')
all_chart_size = widgets.Dropdown(options=['Small','Medium','Large'], value='Large', description='All heatmap size:')
filtered_chart_size = widgets.Dropdown(options=['Small','Medium','Large'], value='Large', description='Filtered size:')

# Action buttons
load_button = widgets.Button(description='Load & Parse Data', button_style='success', icon='download')
run_button = widgets.Button(description='Run Analysis', button_style='primary', icon='play')
insights_button = widgets.Button(description='Regenerate AI Insights', button_style='info', icon='robot')
reset_button = widgets.Button(description='Reset Filters', button_style='warning')
sample_data_button = widgets.Button(description='Load Example (demo)', button_style='', icon='file')

# Output areas
out_logs = widgets.Output(layout={'border': '1px solid #ddd'})
out_heatmaps = widgets.Output()
out_charts = widgets.Output()
out_insights = widgets.Output(layout={'border': '1px solid #eee', 'padding': '8px'})

# Place widgets in a layout
left_col = widgets.VBox([
    widgets.HTML("<h3>Data Input</h3>"),
    widgets.HBox([file_upload, sample_data_button]),
    csv_url_input,
    widgets.HTML("<hr><h3>Filters</h3>"),
    include_rows_text,
    exclude_rows_text,
    include_cols_text,
    exclude_cols_text,
    comparison_dropdown,
    widgets.HTML("<hr>Display"),
    all_chart_size,
    filtered_chart_size,
    widgets.HBox([load_button, run_button, insights_button, reset_button]),
])

right_col = widgets.VBox([
    widgets.HTML("<h3>Logs / Info</h3>"),
    out_logs,
    widgets.HTML("<h3>AI Insights</h3>"),
    out_insights
], layout=widgets.Layout(width='48%'))

ui = widgets.HBox([left_col, right_col], layout=widgets.Layout(justify_content='space-between'))

# ------------------------
# Internal state
# ------------------------
_state = {
    'raw_df': None,
    'matrix': None,
    'filtered_matrix': None,
    'last_url': None,
}

# ------------------------
# Event Handlers
# ------------------------

def _log(msg, level='info'):
    with out_logs:
        if level == 'error':
            print("ERROR:", msg)
        else:
            print(msg)

def on_sample_clicked(b):
    # Load a small synthetic matrix for demo
    demo_entities = ['Netflix', 'Disney', 'YouTube', 'Amazon', 'Hotstar']
    rng = np.random.RandomState(42)
    m = rng.uniform(0, 80, size=(len(demo_entities), len(demo_entities)))
    np.fill_diagonal(m, 100)  # self overlap
    mat = pd.DataFrame(m, index=demo_entities, columns=demo_entities).round(1)
    _state['raw_df'] = None
    _state['matrix'] = mat
    with out_logs:
        clear_output()
        print("Loaded demo dataset.")
    _show_matrices_and_charts()

def on_load_clicked(b):
    with out_logs:
        clear_output()
        print("Loading data...")
    try:
        if file_upload.value:
            df = read_csv_from_upload(file_upload)
            _state['raw_df'] = df
            with out_logs:
                print("Loaded CSV from upload. Shape:", df.shape)
        elif csv_url_input.value.strip():
            url = csv_url_input.value.strip()
            df = read_csv_from_url(url)
            _state['raw_df'] = df
            _state['last_url'] = url
            with out_logs:
                print("Loaded CSV from URL. Shape:", df.shape)
        else:
            with out_logs:
                print("No file or URL provided. Use 'Load Example (demo)' for a quick test.")
            return

        # Attempt to convert to pivot matrix
        mat = ensure_pivot_matrix(_state['raw_df'])
        _state['matrix'] = mat
        with out_logs:
            print("Parsed pivot matrix with shape:", mat.shape)
        _show_matrices_and_charts()
    except Exception as e:
        with out_logs:
            print("Failed to load/parse data:", str(e))

def _show_matrices_and_charts():
    # Show "all" heatmap and filtered heatmap + exclusive/duplicate bars
    if _state['matrix'] is None:
        with out_logs:
            print("No matrix to display. Load data first.")
        return

    # Apply filters
    include_rows = include_rows_text.value.strip() or None
    exclude_rows = exclude_rows_text.value.strip() or None
    include_cols = include_cols_text.value.strip() or None
    exclude_cols = exclude_cols_text.value.strip() or None

    filtered = filter_matrix(_state['matrix'], include_rows, exclude_rows, include_cols, exclude_cols)
    _state['filtered_matrix'] = filtered

    # Plot
    with out_heatmaps:
        clear_output(wait=True)
        fig_all = plot_heatmap(_state['matrix'], title="All Entities Heatmap", size=all_chart_size.value)
        fig_filtered = plot_heatmap(filtered, title="Filtered Entities Heatmap", size=filtered_chart_size.value)
        display(widgets.HTML("<h4>Heatmaps</h4>"))
        display(fig_all)
        display(fig_filtered)

    # Exclusive / Duplicate charts for ALL
    ed_all = compute_exclusive_duplicate(_state['matrix'])
    ed_filtered = compute_exclusive_duplicate(filtered)

    with out_charts:
        clear_output(wait=True)
        display(widgets.HTML("<h4>Exclusive / Duplicate (All entities)</h4>"))
        if not ed_all.empty:
            fig1 = go.Figure()
            fig1.add_trace(go.Bar(x=ed_all['Entity'], y=ed_all['Exclusive'], name='Exclusive'))
            fig1.add_trace(go.Bar(x=ed_all['Entity'], y=ed_all['Duplicate'], name='Duplicate'))
            fig1.update_layout(barmode='group', title='Exclusive vs Duplicate (All)')
            display(fig1)
        else:
            print("No data for Exclusive/Duplicate (All).")

        display(widgets.HTML("<h4>Exclusive / Duplicate (Filtered)</h4>"))
        if not ed_filtered.empty:
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(x=ed_filtered['Entity'], y=ed_filtered['Exclusive'], name='Exclusive'))
            fig2.add_trace(go.Bar(x=ed_filtered['Entity'], y=ed_filtered['Duplicate'], name='Duplicate'))
            fig2.update_layout(barmode='group', title='Exclusive vs Duplicate (Filtered)')
            display(fig2)
        else:
            print("No data for Exclusive/Duplicate (Filtered).")

def on_run_clicked(b):
    with out_logs:
        print("Running analysis and rendering charts...")
    _show_matrices_and_charts()
    # Render heatmaps and charts outputs to the dedicated areas
    display(out_heatmaps)
    display(out_charts)

def on_reset_clicked(b):
    include_rows_text.value = ''
    exclude_rows_text.value = ''
    include_cols_text.value = ''
    exclude_cols_text.value = ''
    with out_logs:
        clear_output()
        print("Filters reset.")

def on_insights_clicked(b):
    """
    Placeholder for AI insights generation.
    If you want to integrate Gemini / OpenAI, accept an API key in a secure manner,
    then call the endpoint and display the generated insights here. The original
    notebook instructs to use Colab secrets to store the Gemini key.
    """
    with out_insights:
        clear_output()
        print("Generating AI insights (placeholder).")
        if _state.get('filtered_matrix') is None or _state['filtered_matrix'].size == 0:
            print("- No filtered data found. Run analysis and ensure filtered heatmap contains entities.")
            print()
        # Example lightweight 'insights' derived from the numbers (not an LLM):
        if _state.get('matrix') is not None:
            overall_mean = _state['matrix'].replace([np.inf, -np.inf], np.nan).stack().mean()
            highest_pair = _state['matrix'].stack().idxmax()
            mean_txt = f"Average overlap across all entity-pairs: {overall_mean:.1f}%"
            high_txt = f"Highest pairwise overlap: {highest_pair} -> {_state['matrix'].loc[highest_pair]:.1f}%"
            print(mean_txt)
            print(high_txt)
            print()
            print("To call Gemini/OpenAI for richer text insights, wire the 'Regenerate AI Insights' button to your API call and pass a short summary of the computed metrics and a small sample of the overlap matrix.")
        else:
            print("No matrix available to derive insights from. Load data first.")

# Wire events
sample_data_button.on_click(on_sample_clicked)
load_button.on_click(on_load_clicked)
run_button.on_click(on_run_clicked)
reset_button.on_click(on_reset_clicked)
insights_button.on_click(on_insights_clicked)

# Display the UI
display(ui)

# Display outputs placeholders underneath
display(widgets.HBox([out_heatmaps, out_charts], layout=widgets.Layout(justify_content='space-between')))