"""
PDF Parser module: Bounding box geometric text extraction & image processing.
"""

import os
import fitz  # PyMuPDF

MIN_IMAGE_DIM = 60
HEADER_MARGIN = 40
FOOTER_MARGIN = 40

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PUBLIC_IMAGES_DIR = os.path.join(PROJECT_DIR, "public", "images", "provas")


def escape_html(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def extract_page_blocks(page, is_two_column=None):
    """Returns text extracted from a single PDF page with geometric layout awareness."""
    page_rect = page.rect
    header_y = page_rect.y0 + HEADER_MARGIN
    footer_y = page_rect.y1 - FOOTER_MARGIN

    drawings = page.get_drawings()
    underlines = []
    for d in drawings:
        r = fitz.Rect(d["rect"])
        w, h = r.x1 - r.x0, r.y1 - r.y0
        if h <= 2.0 and w > 2.0:
            underlines.append(r)

    raw = page.get_text("rawdict")
    text_blocks = [b for b in raw["blocks"] if b["type"] == 0]

    if is_two_column is None:
        mid = page_rect.width / 2.0
        left_count = sum(1 for b in text_blocks if (b["bbox"][0] + b["bbox"][2]) / 2.0 < mid)
        right_count = sum(1 for b in text_blocks if (b["bbox"][0] + b["bbox"][2]) / 2.0 >= mid)
        is_two_column = left_count >= 2 and right_count >= 2

    if is_two_column:
        mid = page_rect.width / 2.0
        full_width = [b for b in text_blocks 
                      if b["bbox"][0] < mid - 20 and b["bbox"][2] > mid + 20 
                      and b["bbox"][1] < page_rect.height * 0.25]
        left = [b for b in text_blocks 
                if b not in full_width and (b["bbox"][0] + b["bbox"][2]) / 2.0 < mid]
        right = [b for b in text_blocks 
                 if b not in full_width and (b["bbox"][0] + b["bbox"][2]) / 2.0 >= mid]
        full_width.sort(key=lambda b: b["bbox"][1])
        left.sort(key=lambda b: b["bbox"][1])
        right.sort(key=lambda b: b["bbox"][1])
        sorted_blocks = full_width + left + right
    else:
        sorted_blocks = sorted(text_blocks, key=lambda b: b["bbox"][1])

    html_parts = []
    for b in sorted_blocks:
        b_rect = fitz.Rect(b["bbox"])
        if b_rect.y1 <= header_y or b_rect.y0 >= footer_y:
            continue

        for line in b["lines"]:
            line_html = []
            for span in line["spans"]:
                chars = span.get("chars", [])
                span_text = "".join(c["c"] for c in chars)
                if not span_text.strip():
                    line_html.append(span_text)
                    continue

                font = span["font"]
                flags = span["flags"]
                is_bold = bool(flags & 16) or "bold" in font.lower()
                is_italic = bool(flags & 2) or "italic" in font.lower()

                current_text = ""
                current_underlined = None
                segments = []

                for c in chars:
                    c_bbox = fitz.Rect(c["bbox"])
                    char_underlined = False
                    for u in underlines:
                        if abs(u.y0 - c_bbox.y1) <= 3.0:
                            x_center = (c_bbox.x0 + c_bbox.x1) / 2.0
                            if u.x0 - 0.5 <= x_center <= u.x1 + 0.5:
                                char_underlined = True
                                break
                    if current_underlined is None:
                        current_underlined = char_underlined
                        current_text = c["c"]
                    elif char_underlined == current_underlined:
                        current_text += c["c"]
                    else:
                        segments.append((current_text, current_underlined))
                        current_text = c["c"]
                        current_underlined = char_underlined

                if current_text:
                    segments.append((current_text, current_underlined))

                for seg_text, seg_underlined in segments:
                    part = escape_html(seg_text)
                    if is_bold:
                        part = f"<strong>{part}</strong>"
                    if is_italic:
                        part = f"<em>{part}</em>"
                    if seg_underlined:
                        part = f"<u>{part}</u>"
                    line_html.append(part)

            html_parts.append("".join(line_html))
        html_parts.append("\n")

    return "".join(html_parts)


def extract_images(doc, exam_id):
    """Extract images from all pages with geometric bounding box coordinates."""
    exam_img_dir = os.path.join(PUBLIC_IMAGES_DIR, exam_id)
    page_images = {}

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        page_rect = page.rect
        images = page.get_images(full=True)
        if not images:
            continue
        page_num = page_idx + 1
        img_list = []
        for img_idx, img in enumerate(images):
            xref = img[0]
            try:
                base = doc.extract_image(xref)
                w, h = base.get("width", 0), base.get("height", 0)
                if w < MIN_IMAGE_DIM or h < MIN_IMAGE_DIM:
                    continue
                if w >= page_rect.width * 0.9 and h >= page_rect.height * 0.9:
                    continue

                rects = page.get_image_rects(xref)
                y0 = rects[0].y0 if rects else 0
                y1 = rects[0].y1 if rects else 0

                os.makedirs(exam_img_dir, exist_ok=True)
                fname = f"img_p{page_num}_{img_idx+1}.{base['ext']}"
                fpath = os.path.join(exam_img_dir, fname)
                with open(fpath, "wb") as f:
                    f.write(base["image"])
                url = f"/images/provas/{exam_id}/{fname}"
                img_list.append({"url": url, "y0": y0, "y1": y1})
            except Exception as e:
                print(f"  Image error p{page_num} xref {xref}: {e}")
        if img_list:
            page_images[page_num] = img_list
    return page_images
