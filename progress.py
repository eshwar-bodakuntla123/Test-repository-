import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

def export_tagged_to_pdf(text_output, filename="DV360_Full_Report.pdf"):
    """
    Converts tagged AI output (<title>, <heading>, <subheading>, <paragraph>, 
    <bullet>, <subbullet>, <image>) into a styled PDF with proper nested bullets.
    """

    doc = SimpleDocTemplate(filename, pagesize=letter,
                            rightMargin=40, leftMargin=40,
                            topMargin=60, bottomMargin=40)

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], fontSize=18, spaceAfter=12)
    heading_style = ParagraphStyle("HeadingStyle", parent=styles["Heading2"], fontSize=14,
                                   spaceBefore=14, spaceAfter=6, leading=16)
    subheading_style = ParagraphStyle("SubheadingStyle", parent=styles["Heading3"], fontSize=12,
                                      spaceBefore=10, spaceAfter=4, leading=14)
    paragraph_style = ParagraphStyle("ParagraphStyle", parent=styles["Normal"], fontSize=11,
                                     leading=14, spaceAfter=8)
    bullet_style = ParagraphStyle("BulletStyle", parent=styles["Normal"], fontSize=11,
                                  leftIndent=20, bulletIndent=10, spaceAfter=4)
    subbullet_style = ParagraphStyle("SubBulletStyle", parent=styles["Normal"], fontSize=11,
                                     leftIndent=40, bulletIndent=30, spaceAfter=3)

    story = []

    # Parse tags
    tokens = re.findall(r"<(.*?)>(.*?)</\1>", text_output, re.DOTALL)

    i = 0
    while i < len(tokens):
        tag, content = tokens[i]
        content = content.strip()

        if tag == "title":
            story.append(Paragraph(content, title_style))
            story.append(Spacer(1, 0.2 * inch))

        elif tag == "heading":
            story.append(Paragraph(f"<b>{content}</b>", heading_style))
            story.append(Spacer(1, 0.1 * inch))

        elif tag == "subheading":
            story.append(Paragraph(f"<b>{content}</b>", subheading_style))
            story.append(Spacer(1, 0.05 * inch))

        elif tag == "paragraph":
            story.append(Paragraph(content, paragraph_style))

        elif tag == "bullet":
            # Collect all consecutive bullets & subbullets
            bullet_items = []
            while i < len(tokens) and tokens[i][0] in ["bullet", "subbullet"]:
                btag, bcontent = tokens[i]
                bcontent = bcontent.strip()

                if btag == "bullet":
                    bullet_items.append(ListItem(Paragraph(bcontent, bullet_style)))
                elif btag == "subbullet":
                    # Nest subbullet inside its own ListFlowable for indentation
                    sub_list = ListFlowable(
                        [ListItem(Paragraph(bcontent, subbullet_style))],
                        bulletType="bullet",
                        start="–",
                        leftIndent=20
                    )
                    bullet_items.append(sub_list)
                i += 1

            # Create one grouped bullet list
            story.append(ListFlowable(bullet_items, bulletType="bullet", start="•", leftIndent=0))
            story.append(Spacer(1, 0.1 * inch))
            continue  # skip extra increment (already moved i)

        elif tag == "image":
            try:
                story.append(Image(content, width=5*inch, height=3*inch))
                story.append(Spacer(1, 0.2 * inch))
            except Exception:
                story.append(Paragraph(f"[Image not found: {content}]", paragraph_style))

        i += 1

    doc.build(story)
    print(f"✅ PDF generated: {filename}")