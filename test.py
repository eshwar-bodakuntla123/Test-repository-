# Requires: reportlab, pillow
# Install if needed: pip install reportlab pillow

import os
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch, cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from textwrap import wrap
from PIL import Image

def create_report_with_image_and_text(
    image_path,
    out_pdf_report="final_report.pdf",
    title="DV360 Duplicate Reach Report",
    subtitle=None,
    paragraphs=None,
    mapping_dict=None,
    page_size=A4,
    image_max_width_ratio=0.9,   # fraction of page width
    image_max_height_ratio=0.5,  # fraction of page height for image area
    margin_cm=2
):
    """
    Create a PDF report that places the chart image on the first page and
    adds textual analysis and mapping on subsequent space (same page or next page)
    - image_path: path to the high-res PNG exported earlier
    - paragraphs: list of strings (analysis text) to include
    - mapping_dict: dictionary original->IO or IO->original (function will normalize)
    """

    # Prepare text
    if paragraphs is None:
        paragraphs = [
            "Analysis summarizes duplicate reach across several DV360 insertion orders.",
            "Key findings: Insertion orders differ substantially in duplicate reach; consider budget reallocation toward IOs with lower duplication to expand unique reach."
        ]

    # Normalize mapping: create IO -> original mapping
    io_to_original = {}
    if mapping_dict:
        # detect format
        first_key = next(iter(mapping_dict))
        if str(first_key).upper().startswith("IO") or any(str(k).upper().startswith("IO") for k in mapping_dict.keys()):
            # mapping given as IO->original
            io_to_original = {str(k): str(v) for k, v in mapping_dict.items()}
        else:
            # mapping given as original->IO, flip
            io_to_original = {v: k for k, v in mapping_dict.items()}

    # Create canvas
    c = canvas.Canvas(out_pdf_report, pagesize=page_size)
    page_w, page_h = page_size

    # Margins in points
    margin = margin_cm * cm

    # Draw title
    title_font = "Helvetica-Bold"
    c.setFont(title_font, 18)
    c.drawString(margin, page_h - margin - 10, title)
    if subtitle:
        c.setFont("Helvetica", 12)
        c.drawString(margin, page_h - margin - 30, subtitle)

    # Load image and compute size to fit
    img = Image.open(image_path)
    img_w_px, img_h_px = img.size

    # Determine image area
    max_img_w = page_w * image_max_width_ratio - 2 * margin
    max_img_h = page_h * image_max_height_ratio - 2 * margin

    # Convert image pixels to points assuming image DPI (if unknown, assume 300 DPI)
    img_dpi = img.info.get("dpi", (300, 300))[0]
    img_w_pts = img_w_px / img_dpi * inch
    img_h_pts = img_h_px / img_dpi * inch

    # Scale to fit inside max area while keeping aspect ratio
    scale = min(max_img_w / img_w_pts, max_img_h / img_h_pts, 1.0)
    draw_w = img_w_pts * scale
    draw_h = img_h_pts * scale

    # Place image centered horizontally below title
    img_x = (page_w - draw_w) / 2
    img_y = page_h - margin - 60 - draw_h  # leave space for title

    c.drawImage(ImageReader(img), img_x, img_y, width=draw_w, height=draw_h, preserveAspectRatio=True)

    # Text area below image
    text_x = margin
    text_y = img_y - 20  # start below image
    available_w = page_w - 2 * margin

    c.setFont("Helvetica-Bold", 12)
    c.drawString(text_x, text_y, "Summary & Recommendations")
    text_y -= 16

    # Draw paragraphs wrapped
    c.setFont("Helvetica", 10)
    for para in paragraphs:
        # wrap to available_w (approx chars per line)
        # compute approx chars per line: assume 6.5 pts per character at 10pt -> chars = available_w / 6.5
        approx_chars = max(40, int(available_w / 6.5))
        lines = wrap(para, approx_chars)
        for line in lines:
            if text_y < margin + 60:
                # new page if no space
                c.showPage()
                text_y = page_h - margin
                c.setFont("Helvetica", 10)
            c.drawString(text_x, text_y, line)
            text_y -= 14
        text_y -= 8  # paragraph gap

    # If mapping provided, add mapping section (may go to next page if not enough room)
    if io_to_original:
        if text_y < margin + 120:
            c.showPage()
            text_y = page_h - margin
        c.setFont("Helvetica-Bold", 12)
        c.drawString(text_x, text_y, "IO → Original Mapping (sample)")
        text_y -= 16
        c.setFont("Helvetica", 9)
        # Print mapping in columns for compactness: 3 columns
        items = list(io_to_original.items())
        cols = 3
        rows = math.ceil(len(items) / cols)
        col_w = available_w / cols
        for r in range(rows):
            for col in range(cols):
                idx = r + col * rows
                if idx >= len(items):
                    continue
                io, orig = items[idx]
                short_orig = orig if len(orig) <= 60 else orig[:57] + "..."
                x_pos = text_x + col * col_w
                if text_y < margin + 40:
                    c.showPage()
                    text_y = page_h - margin
                c.drawString(x_pos, text_y, f"{io} → {short_orig}")
            text_y -= 12

    # finalize
    c.save()
    return out_pdf_report

# ---------------- USAGE EXAMPLE ----------------
# 1) Create chart files using export_io_barplot_pdf (from previous code)
# mapping, chart_pdf, chart_png, png_b64 = export_io_barplot_pdf(df)

# 2) Provide analytical paragraphs and produce final PDF
# paragraphs = [
#     "Overall Reach and Frequency: The data reveals significant variations in duplicate reach across different insertion orders, indicating a mix of strategies focusing on reach versus frequency.",
#     "Recommendation: Reallocate budget away from insertion orders with high duplicate reach and invest in those showing lower duplication to expand the unique audience."
# ]
# final_pdf = create_report_with_image_and_text(chart_png, out_pdf_report="dv360_report.pdf",
#                                               title="DV360 Duplicate Reach Analysis",
#                                               subtitle="Generated on 2025-09-16",
#                                               paragraphs=paragraphs,
#                                               mapping_dict=mapping)
# print("Saved report:", final_pdf)