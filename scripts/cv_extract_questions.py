"""
PrepConcursos - Computer Vision & Geometric PDF Question Extractor (OOP Strategy Pattern)

Supported Bancas:
  - CebraspeExtractor: Right/Wrong (Certo/Errado) itemization & continuous support texts.
  - FGVExtractor: 2-column layout multiple-choice (A-E) & ranged reading passages.
  - CesgranrioExtractor: Multiple-choice (A-E) with isolated line numbers & tabbed option parsing.

Database Target: SQLite (concurso.db)
"""

import os
import re
import json
import sqlite3
from abc import ABC, abstractmethod
import fitz  # PyMuPDF

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
PDF_DIR = os.path.join(PROJECT_DIR, "provas")
DB_PATH = os.path.join(PROJECT_DIR, "concurso.db")
PUBLIC_IMAGES_DIR = os.path.join(PROJECT_DIR, "public", "images", "provas")

MIN_IMAGE_DIM = 60
HEADER_MARGIN = 40
FOOTER_MARGIN = 40

IMAGE_REF_PATTERN = re.compile(
    r"\b(?:figura|gr[áa]fico|tabela|diagrama|esquema|imagem|ilustra[çc][aã]o|quadro|fluxograma|c[óo]digo|algoritmo)\b",
    re.IGNORECASE,
)

CEBRASPE_SUPPORT_PATTERN = re.compile(
    r"((?:Texto\s+(?:I{1,3}|IV|V|VI|VII|VIII|IX|X|\d+)|"
    r"Leia\s+o\s+texto\s+.*?|Julgue\s+os?\s+(?:itens?|seguintes?|pr[oó]ximos?\s+itens?)|"
    r"Considerando\s+o\s+texto\s+.*?|Acerca\s+de|Com\s+rela[cç][aã]o\s+a|Nos\s+termos\s+da|Em\s+rela[cç][aã]o\s+a|"
    r"Quanto\s+a[os]?)\b.*?"
    r"(?:julgue\s+os?\s+(?:itens?|seguintes?|pr[oó]ximos?\s+itens?|"
    r"itens?\s+(?:subsequentes?|que\s+se\s+seguem|a\s+seguir)))\s*\.?\s*)",
    re.IGNORECASE | re.DOTALL
)

TRANSITION_PATTERNS = [
    re.compile(r"(?:READ\s+THE\s+TEXT\s+(?:AND\s+ANSWER|TO\s+ANSWER)\s+QUESTIONS\s+(\d+)\s+(?:TO|AND)\s+(\d+)\b:?)", re.IGNORECASE),
    re.compile(r"(?:Texto\s+para\s+as\s+quest[oõ]es\s+de\s+(\d+)\s+a\s+(\d+)\b:?)", re.IGNORECASE),
    re.compile(r"(?:Texto\s+comum\s+para\s+as\s+quest[oõ]es\s+de\s+(\d+)\s+a\s+(\d+)\b:?)", re.IGNORECASE),
    re.compile(r"(?:Considere\s+o\s+texto\s+abaixo\s+para\s+responder\s+[àa]s\s+quest[oõ]es\s+de\s+(\d+)\s+a\s+(\d+)\b:?)", re.IGNORECASE),
    re.compile(r"(?:As\s+quest[oõ]es\s+de\s+(\d+)\s+a\s+(\d+)\s+referem-se)", re.IGNORECASE),
    re.compile(r"(?:Use\s+the\s+following\s+TEXT\s+to\s+answer\s+the\s+next\s+(\w+|\d+)\s+questions\b\.?:?)", re.IGNORECASE),
    re.compile(r"(?:Texto\s+para\s+as\s+pr[óo]ximas\s+(\w+|\d+)\s+quest[oõ]es\b\.?:?)", re.IGNORECASE),
]

WORD_NUMS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "um": 1, "dois": 2, "três": 3, "tres": 3, "quatro": 4, "cinco": 5, "seis": 6, "sete": 7, "oito": 8, "nove": 9, "dez": 10
}


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


def clean_option_text(text):
    """Remove trailing page markers, section headers, and draft text."""
    if not text:
        return ""
    text = re.sub(r"\n\s*--- PAGE \d+ ---.*$", "", text, flags=re.DOTALL)
    text = re.sub(r"\n\s*(?:<[^>]+>|\s)*RASCUNHO.*$", "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(
        r"\s*(?:<[^>]+>|\s)*(?:CONHECIMENTOS\s+ESPEC[ÍI]FICOS|CONHECIMENTOS\s+B[ÁA]SICOS|"
        r"MATEM[ÁA]TICA|L[ÍI]NGUA\s+INGLESA|L[ÍI]NGUA\s+PORTUGUESA|ATUALIDADES|"
        r"PROBABILIDADE|CONHECIMENTOS\s+BANC[ÁA]RIOS|TECNOLOGIA\s+DA\s+INFORMA|"
        r"Use\s+the\s+following|Texto\s+para\s+as\s+pr[óo]ximas|L[ÍI]NGUA\s+ESTRANGEIRA).*",
        "", text, flags=re.IGNORECASE | re.DOTALL
    )
    text = re.sub(r"(?:<[^>]+>|\s)+$", "", text)
    return text.strip()


def split_options_ae(body):
    """Split a question body into (statement, {A:..., B:..., C:..., D:..., E:...})."""
    markers = ["A", "B", "C", "D", "E"]
    pattern = r"(?:^|\n|\s+)(?:<[^>]+>|\s)*\(([A-E])\)\s*"
    matches = list(re.finditer(pattern, body))

    if len(matches) >= 5:
        seq = []
        expected = 0
        for m in matches:
            if m.group(1) == markers[expected]:
                seq.append(m)
                expected += 1
                if expected == 5:
                    break
        if len(seq) == 5:
            stmt = body[:seq[0].start()].strip()
            opts = {}
            for i in range(5):
                s = seq[i].end()
                e = seq[i + 1].start() if i + 1 < 5 else len(body)
                opts[markers[i]] = body[s:e].strip()
            return stmt, opts

    # Fallback: find each marker individually
    indices = []
    for m in markers:
        match = re.search(rf"(?:^|\n|\s+)(?:<[^>]+>|\s)*\({m}\)", body)
        if match:
            indices.append((m, match.start(), match.end()))
    if len(indices) == 5:
        indices.sort(key=lambda x: x[1])
        stmt = body[:indices[0][1]].strip()
        opts = {}
        for i in range(5):
            s = indices[i][2]
            e = indices[i + 1][1] if i + 1 < 5 else len(body)
            opts[indices[i][0]] = body[s:e].strip()
        return stmt, opts

    return body, {}


# ---------------------------------------------------------------------------
# OOP Strategy Pattern for Exam Extractors
# ---------------------------------------------------------------------------
class BaseExamExtractor(ABC):
    def __init__(self, exam_id, exam_name, doc, config, banca, total_questions, year):
        self.exam_id = exam_id
        self.exam_name = exam_name
        self.doc = doc
        self.config = config
        self.banca = banca
        self.total_questions = total_questions
        self.year = year

    @abstractmethod
    def extract_questions(self, full_text):
        pass

    @abstractmethod
    def attach_support_texts(self, questions):
        pass

    def clean_all_options(self, questions):
        for q in questions:
            if "options" in q:
                for k in q["options"]:
                    q["options"][k] = clean_option_text(q["options"][k])


class CebraspeExtractor(BaseExamExtractor):
    def extract_questions(self, full_text):
        item_pat = r'(?:^|\n|\b)\s*(?:<[^>]+>)*\s*(\d{1,3})\s*(?:</[^>]+>)*\s+(?=[A-Z\u00C0-\u00DC"\'$])'
        all_matches = list(re.finditer(item_pat, full_text))
        by_num = {}
        for i, m in enumerate(all_matches):
            try:
                q_num = int(m.group(1))
            except ValueError:
                continue
            if not (1 <= q_num <= 120):
                continue
            start = m.end()
            end = all_matches[i + 1].start() if i + 1 < len(all_matches) else len(full_text)
            body = full_text[start:end].strip()
            body = re.sub(r"\n\s*CEBRASPE.*$", "", body)
            body = re.sub(r"--- PAGE \d+ ---", "", body)
            if q_num not in by_num and len(body) > 10:
                by_num[q_num] = body

        questions = []
        for q_num in sorted(by_num.keys()):
            questions.append({
                "number": q_num,
                "statement": by_num[q_num],
                "options": {"C": "Certo", "E": "Errado"},
                "type": "right_wrong"
            })
        return questions

    def attach_support_texts(self, questions):
        active_support = None
        for q in questions:
            match = CEBRASPE_SUPPORT_PATTERN.search(q["statement"])
            if match:
                support = match.group(0).strip()
                remainder = (q["statement"][:match.start()] + " " + q["statement"][match.end():]).strip()
                active_support = support
                q["statement"] = remainder

            if active_support and "shared-text-block" not in q["statement"]:
                q["support_text"] = active_support


class FGVExtractor(BaseExamExtractor):
    def extract_questions(self, full_text):
        by_num = {}
        all_matches = []
        for q_num in range(1, self.total_questions + 1):
            num_str = f"(?:0?{q_num}|{q_num:02d})"
            pat = rf"\n\s*(?:<[^>]+>)*\s*{num_str}\s*(?:</[^>]+>)*\s+(?=[A-Z\u00C0-\u00DC\"\'$\d<\(])"
            for m in re.finditer(pat, full_text):
                all_matches.append((q_num, m.start(), m.end()))

        all_matches.sort(key=lambda x: x[1])
        unique_matches = []
        seen = set()
        for q_num, s, e in all_matches:
            if q_num not in seen:
                seen.add(q_num)
                unique_matches.append((q_num, s, e))
        unique_matches.sort(key=lambda x: x[1])

        for i, (q_num, s, e) in enumerate(unique_matches):
            end = unique_matches[i + 1][1] if i + 1 < len(unique_matches) else len(full_text)
            body = full_text[e:end].strip()
            by_num[q_num] = body

        questions = []
        for q_num in sorted(by_num.keys()):
            body = by_num[q_num]
            stmt, opts = split_options_ae(body)
            questions.append({
                "number": q_num,
                "statement": stmt,
                "options": opts,
                "type": "multiple_choice"
            })
        return questions

    def attach_support_texts(self, questions):
        for q in questions:
            opts = q.get("options", {})
            if "E" not in opts:
                continue
            plain_e = re.sub(r"<[^>]*>", "", opts["E"])
            for tp in TRANSITION_PATTERNS:
                m = tp.search(plain_e)
                if m:
                    groups = [g for g in m.groups() if g]
                    start_q, end_q = None, None
                    if len(groups) >= 2 and groups[0].isdigit() and groups[1].isdigit():
                        start_q, end_q = int(groups[0]), int(groups[1])
                    elif len(groups) == 1:
                        val = groups[0].lower()
                        count = int(val) if val.isdigit() else WORD_NUMS.get(val, 5)
                        start_q = q["number"] + 1
                        end_q = q["number"] + count

                    if start_q and end_q:
                        m_raw = tp.search(opts["E"])
                        raw_start = m_raw.start() if m_raw else m.start()
                        support = opts["E"][raw_start:].strip()
                        opts["E"] = opts["E"][:raw_start].strip()
                        for tgt in questions:
                            if start_q <= tgt["number"] <= end_q:
                                tgt["support_text"] = support
                    break
        self.clean_all_options(questions)


class CesgranrioExtractor(BaseExamExtractor):
    def extract_questions(self, full_text):
        by_num = {}
        all_matches = []

        # Cesgranrio question numbers appear on line boundaries or preceded by QUESTÃO
        for q_num in range(1, self.total_questions + 1):
            num_str = f"(?:0?{q_num}|{q_num:02d})"
            pat = rf"(?:^|\n|\b)\s*(?:<[^>]+>|\s)*(?:QUEST[AÃO]+\s+)?{num_str}\s*(?:</[^>]+>)*\s*(?=[A-Z\u00C0-\u00DC\"\'$])"
            for m in re.finditer(pat, full_text):
                all_matches.append((q_num, m.start(), m.end()))

        all_matches.sort(key=lambda x: x[1])
        unique_matches = []
        seen = set()
        for q_num, s, e in all_matches:
            if q_num not in seen:
                seen.add(q_num)
                unique_matches.append((q_num, s, e))
        unique_matches.sort(key=lambda x: x[1])

        for i, (q_num, s, e) in enumerate(unique_matches):
            end = unique_matches[i + 1][1] if i + 1 < len(unique_matches) else len(full_text)
            body = full_text[e:end].strip()
            by_num[q_num] = body

        questions = []
        for q_num in sorted(by_num.keys()):
            body = by_num[q_num]
            stmt, opts = split_options_ae(body)
            questions.append({
                "number": q_num,
                "statement": stmt,
                "options": opts,
                "type": "multiple_choice"
            })
        return questions

    def attach_support_texts(self, questions):
        for q in questions:
            opts = q.get("options", {})
            if "E" not in opts:
                continue
            plain_e = re.sub(r"<[^>]*>", "", opts["E"])
            for tp in TRANSITION_PATTERNS:
                m = tp.search(plain_e)
                if m:
                    groups = [g for g in m.groups() if g]
                    start_q, end_q = None, None
                    if len(groups) >= 2 and groups[0].isdigit() and groups[1].isdigit():
                        start_q, end_q = int(groups[0]), int(groups[1])
                    elif len(groups) == 1:
                        val = groups[0].lower()
                        count = int(val) if val.isdigit() else WORD_NUMS.get(val, 5)
                        start_q = q["number"] + 1
                        end_q = q["number"] + count

                    if start_q and end_q:
                        m_raw = tp.search(opts["E"])
                        raw_start = m_raw.start() if m_raw else m.start()
                        support = opts["E"][raw_start:].strip()
                        opts["E"] = opts["E"][:raw_start].strip()
                        for tgt in questions:
                            if start_q <= tgt["number"] <= end_q:
                                tgt["support_text"] = support
                    break
        self.clean_all_options(questions)


class ExtractorFactory:
    @staticmethod
    def get_extractor(banca, exam_id, exam_name, doc, config, total_questions, year) -> BaseExamExtractor:
        banca_upper = banca.upper()
        name_lower = exam_name.lower()

        if banca_upper == "CESGRANRIO" or "banco do brasil" in name_lower:
            return CesgranrioExtractor(exam_id, exam_name, doc, config, banca, total_questions, year)
        elif banca_upper == "FGV":
            return FGVExtractor(exam_id, exam_name, doc, config, banca, total_questions, year)
        else:
            return CebraspeExtractor(exam_id, exam_name, doc, config, banca, total_questions, year)


# ---------------------------------------------------------------------------
# Discipline mapping
# ---------------------------------------------------------------------------
def map_discipline(banca, exam_name, q_num, total_questions):
    """Map question number to a discipline category."""
    name_lower = exam_name.lower()
    if "banco do brasil" in name_lower or "escriturario" in name_lower or "escriturário" in name_lower:
        if q_num <= 10: return "Língua Portuguesa"
        if q_num <= 15: return "Língua Inglesa"
        if q_num <= 20: return "Matemática"
        if q_num <= 25: return "Atualidades do Mercado Financeiro"
        if q_num <= 30: return "Probabilidade e Estatística"
        if q_num <= 35: return "Conhecimentos Bancários"
        return "Tecnologia da Informação"

    if banca == "FGV":
        if total_questions == 80:
            if q_num <= 20: return "Língua Portuguesa"
            if q_num <= 40: return "Legislação / Raciocínio Lógico"
            return "Tecnologia da Informação"
        elif total_questions == 70:
            if q_num <= 12: return "Língua Portuguesa"
            if q_num <= 18: return "Língua Inglesa"
            return "Conhecimentos Específicos (TI)"
        elif total_questions == 60:
            if q_num <= 20: return "Língua Portuguesa / Legislação"
            return "Conhecimentos Específicos (TI)"

    if banca == "CEBRASPE":
        if "segurança" in name_lower: return "Segurança da Informação"
        if "engenharia de dados" in name_lower: return "Banco de Dados & Big Data"

    return "Conhecimentos Específicos"


# ---------------------------------------------------------------------------
# Main extraction pipeline -> SQLite
# ---------------------------------------------------------------------------
def extract_all():
    """Main entry point: extract all PDFs and populate concurso.db."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    cur = conn.cursor()

    pdf_files = [f for f in os.listdir(PDF_DIR) if f.endswith(".pdf")]
    total_extracted_global = 0

    for f in pdf_files:
        base_name = f.replace(".pdf", "")
        cfg_path = os.path.join(PDF_DIR, f"{base_name}.json")
        if not os.path.exists(cfg_path):
            continue

        with open(cfg_path, "r", encoding="utf-8") as json_f:
            config = json.load(json_f)

        exam_name = config.get("nome_prova", base_name)
        banca = config.get("banca", "CEBRASPE")
        total_q = config.get("total_questoes", 120)
        answers = config.get("gabarito", {})

        year_match = re.search(r"20\d{2}", exam_name)
        year = int(year_match.group()) if year_match else None

        exam_id = base_name
        pdf_path = os.path.join(PDF_DIR, f)
        print(f"Extracting [{banca}]: {exam_name}...")

        doc = fitz.open(pdf_path)
        page_images = extract_images(doc, exam_id)

        full_text = ""
        for i in range(len(doc)):
            full_text += f"\n--- PAGE {i + 1} ---\n"
            full_text += extract_page_blocks(doc[i], is_two_column=None)
        doc.close()

        # Factory Strategy Pattern Extraction
        extractor = ExtractorFactory.get_extractor(banca, exam_id, exam_name, doc, config, total_q, year)
        questions = extractor.extract_questions(full_text)
        extractor.attach_support_texts(questions)
        questions.sort(key=lambda q: q["number"])

        # Insert exam
        cur.execute(
            "INSERT OR REPLACE INTO exams (id, name, banca, year, total_questions, config_json) VALUES (?, ?, ?, ?, ?, ?)",
            (exam_id, exam_name, banca, year, total_q, json.dumps(config, ensure_ascii=False))
        )

        # Insert questions and options
        for q in questions:
            q_num = q["number"]
            q_id = f"{exam_id}_q{q_num}"
            discipline = map_discipline(banca, exam_name, q_num, total_q)
            ans = answers.get(q_num, "")

            q_images = []
            stmt_snippet = re.sub(r"<[^>]*>", "", q["statement"])[:40].strip()
            if stmt_snippet:
                escaped = re.escape(stmt_snippet)
                m = re.search(r"--- PAGE (\d+) ---.*?" + escaped, full_text, re.DOTALL)
                if m:
                    p_num = int(m.group(1))
                    p_imgs = page_images.get(p_num, [])
                    full_q_text = (q["statement"] + " " + (q.get("support_text") or "")).lower()
                    image_ref_match = re.search(r"\b(?:figura|gr[áa]fico|tabela|diagrama|esquema|imagem|ilustra[çc][aã]o|quadro|fluxograma|c[óo]digo|algoritmo)\b", full_q_text)
                    if image_ref_match or "<img" in full_q_text:
                        q_images = [img["url"] if isinstance(img, dict) else img for img in p_imgs]

            statement = q["statement"]
            support_text = q.get("support_text")
            if support_text:
                statement = (
                    f'<div class="shared-text-block">'
                    f'<strong>Texto de apoio:</strong><br>'
                    f'{support_text}'
                    f'</div><hr>'
                    f'{statement}'
                )

            cur.execute(
                """INSERT OR REPLACE INTO questions 
                   (id, exam_id, number, discipline, type, statement, support_text, correct_answer, explanation, images_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    q_id,
                    exam_id,
                    q_num,
                    discipline,
                    q.get("type", "multiple_choice"),
                    statement,
                    support_text,
                    ans,
                    "",
                    json.dumps(q_images, ensure_ascii=False)
                )
            )

            opts = q.get("options", {})
            for key, opt_text in opts.items():
                cur.execute(
                    "INSERT OR REPLACE INTO options (question_id, option_key, option_text) VALUES (?, ?, ?)",
                    (q_id, key, opt_text)
                )

        conn.commit()
        total_extracted_global += len(questions)
        print(f"  -> {len(questions)} questions inserted into concurso.db")

    conn.close()
    print("\n" + "=" * 50)
    print(f"Total: {total_extracted_global} questions extracted into {DB_PATH}")
    print("=" * 50)


if __name__ == "__main__":
    extract_all()
