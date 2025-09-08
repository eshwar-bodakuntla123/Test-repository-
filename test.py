print("this is sample python code")


Got it ✅ — we’ll extend the system so your AI output can include:

Title

Headings (main sections)

Subheadings (nested sections under a heading)

Paragraphs (intro or explanations)

Bullets (lists of insights)

Sub-bullets (nested under a bullet)

Images (optional, if you want charts in PDF later)


By using tags, everything stays clean, parseable, and PDF-friendly.


---

🔹 Updated sys_instruct (Tag-Based Formatting)

sys_instruct = f"""
You are a highly experienced DV360 Specialist. You specialize in crafting and optimizing programmatic advertising strategies that directly drive incremental sales. You have a deep understanding of the digital advertising landscape.

Expertise: Advanced knowledge of programmatic advertising, DV360 platform, audience targeting, campaign optimization, and data analysis. Proven ability to drive incremental sales and demonstrate ROI.

Keep in mind when preparing insights that reach cannot be summed. High Overlap (Duplicate Reach) is good for building frequency, whereas Low Overlap (Exclusive Reach) is good for building reach.

Tone: Be assertive and confident but approachable and conversational. Use clear, concise language. Avoid jargon and keep paragraphs short.

📄 PDF Formatting Rules with Tags:
- Wrap the **Title** in <title> ... </title>.
- Wrap the **Introduction** in <paragraph> ... </paragraph>.
- For each **Heading**, wrap in <heading> ... </heading>.
- For each **Subheading**, wrap in <subheading> ... </subheading>.
- For each **Bullet point**, wrap in <bullet> ... </bullet>.
- For **Nested bullet points**, wrap in <subbullet> ... </subbullet>.
- For body text, always use <paragraph> ... </paragraph>.
- For charts or images, use <image>path_or_url</image>.
- Keep output plain text with these tags only. No markdown, no extra symbols.

When prompt starts with "--", refine the text provided using the above rules and tags.
"""


---

🔹 Example AI Output

<title>DV360 Reach Overlap Analysis</title>

<paragraph>This report evaluates overlap and exclusive reach performance to guide smarter budget allocation. The goal is to maximize incremental audience growth while balancing frequency.</paragraph>

<heading>Key Findings and Recommendations:</heading>
<bullet>IO_1 and IO_3 show high overlap, supporting efficient frequency-building.</bullet>
<bullet>IO_5 demonstrates strong exclusive reach, ideal for incremental reach.</bullet>
<bullet>Reallocate budget to IO_5 while sustaining IO_1 + IO_3 for reinforcement.</bullet>

<subheading>Audience Insights:</subheading>
<bullet>Overlap is highest among younger demographics.</bullet>
<subbullet>IO_2 reaches 65% of the same audience as IO_3.</subbullet>
<subbullet>This reduces efficiency for incremental reach.</subbullet>

<heading>Budget Efficiency:</heading>
<bullet>CPM for IO_5 is 20% lower than average, improving cost per unique user.</bullet>
<bullet>IO_2 has high CPM and high overlap, reducing efficiency. Recommend budget pullback.</bullet>

<heading>Next Steps:</heading>
<bullet>Double down on IOs with high exclusive reach and strong CPM efficiency.</bullet>
<bullet>Maintain frequency-heavy IOs at reduced budget to balance reach and frequency.</bullet>
<image>filtered_ios_heatmap.png</image>


---

🔹 PDF Export Function (Handles All Tags)

import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

def export_tagged_to_pdf(text_output, filename="DV360_Full_Report.pdf"):
    """
    Converts tagged AI output (<title>, <heading>, <subheading>, <paragraph>, 
    <bullet>, <subbullet>, <image>) into a styled PDF.
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

    # Regex parsing
    for tag, content in re.findall(r"<(.*?)>(.*?)</\1>", text_output, re.DOTALL):
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
            bullet = ListItem(Paragraph(content, bullet_style))
            story.append(ListFlowable([bullet], bulletType="bullet", start="•"))

        elif tag == "subbullet":
            bullet = ListItem(Paragraph(content, subbullet_style))
            story.append(ListFlowable([bullet], bulletType="bullet", start="–"))

        elif tag == "image":
            try:
                story.append(Image(content, width=5*inch, height=3*inch))
                story.append(Spacer(1, 0.2 * inch))
            except Exception as e:
                story.append(Paragraph(f"[Image not found: {content}]", paragraph_style))

    doc.build(story)
    print(f"✅ PDF generated: {filename}")


---

✅ This setup gives you full control:

<title> → big centered title.

<heading> → bold section header.

<subheading> → smaller bold header.

<paragraph> → normal text.

<bullet> → bullet list.

<subbullet> → nested bullet list.

<image> → insert heatmap or chart automatically.



---

Would you like me to also add automatic page breaks (e.g., when a new <heading> starts) so long reports don’t look too crowded?






import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

def export_tagged_to_pdf(text_output, filename="DV360_Full_Report.pdf"):
    """
    Converts tagged AI output (<title>, <heading>, <subheading>, <paragraph>, 
    <bullet>, <subbullet>, <image>) into a styled PDF.
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

    # Regex parsing
    for tag, content in re.findall(r"<(.*?)>(.*?)</\1>", text_output, re.DOTALL):
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
            bullet = ListItem(Paragraph(content, bullet_style))
            story.append(ListFlowable([bullet], bulletType="bullet", start="•"))

        elif tag == "subbullet":
            bullet = ListItem(Paragraph(content, subbullet_style))
            story.append(ListFlowable([bullet], bulletType="bullet", start="–"))

        elif tag == "image":
            try:
                story.append(Image(content, width=5*inch, height=3*inch))
                story.append(Spacer(1, 0.2 * inch))
            except Exception as e:
                story.append(Paragraph(f"[Image not found: {content}]", paragraph_style))

    doc.build(story)
    print(f"✅ PDF generated: {filename}")