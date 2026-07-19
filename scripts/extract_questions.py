import os
import re
import json
import fitz

# Directory paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(SCRIPT_DIR, "..", "provas")
OUTPUT_JSON = os.path.join(SCRIPT_DIR, "..", "questions.json")
OUTPUT_JS = os.path.join(SCRIPT_DIR, "..", "questions.js")

# Regex patterns for splitting shared texts / reading passages
TRANSITION_PATTERNS = [
    # English patterns
    r"(?:(?:Língua\s+(?:Inglesa|Portuguesa|Espanhola))\s*\n\s*)?(?:READ\s+THE\s+TEXT\s+(?:AND\s+ANSWER|TO\s+ANSWER)\s+QUESTIONS\s+(\d+)\s+(?:TO|AND)\s+(\d+)\b:?)",
    r"(?:(?:Língua\s+(?:Inglesa|Portuguesa|Espanhola))\s*\n\s*)?(?:Use\s+the\s+following\s+TEXT\s+to\s+answer\s+the\s+next\s+(\w+|\d+)\s+questions\.?)",
    # Portuguese patterns
    r"(?:(?:Língua\s+(?:Inglesa|Portuguesa|Espanhola))\s*\n\s*)?(?:ATENÇÃO:\s*\n?\s*O texto a seguir deve ser usado para as próximas (\w+|\d+) questões\.?)",
    r"(?:Atenção\s*\n\s*Quando referidas, considere as tabelas.*)",
    r"(?:Texto para as questões de (\d+) a (\d+)\b:?)",
    r"(?:As questões de (\d+) a (\d+) referem-se ao (?:texto|caso|enunciado)\b.*)",
    r"(?:Texto comum para as questões de (\d+) a (\d+)\b:?)",
    r"(?:Considere o texto abaixo para responder às questões de (\d+) a (\d+)\b:?)",
    # Section headers and footers cleanup at end of option
    r"(?:---\s*PAGE\s*\d+\s*---\s*\n\s*)?(\bDISCURSIVA\b.*)",
    r"(?:---\s*PAGE\s*\d+\s*---\s*\n\s*)?(\bRASCUNHO\b.*)",
    r"(?:---\s*PAGE\s*\d+\s*---\s*\n\s*)?((?:Noções\s+de|Conhecimentos|Língua|Direito|Realização)\b.*)"
]

CEBRASPE_TRANSITION_PATTERN = r"((?:Julgue\s+os\s+itens|Julgue\s+os\s+próximos|Julgue\s+os\s+seguintes|Julgue\s+os\s+itens\s+a\s+seguir|A\s+respeito\s+de|No\s+que\s+se\s+refere\s+a|Acerca\s+de|Com\s+relação\s+a|Nos\s+termos\s+da)\b.*?(?:julgue\s+os\s+itens|julgue\s+os\s+seguintes|julgue\s+os\s+itens\s+subsequentes|julgue\s+os\s+itens\s+que\s+se\s+seguem|julgue\s+os\s+próximos\s+itens|julgue\s+os\s+seguintes\s+itens|julgue\s+os\s+itens\s+a\s+seguir)\.?\s*\n?)"


def escape_html(text):
    """Escapes special characters to their corresponding HTML entities."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def find_html_index(html_text, plain_idx):
    """Maps a plain-text index back to its index in the original HTML string containing tags."""
    html_idx = 0
    plain_count = 0
    in_tag = False
    
    while html_idx < len(html_text):
        if plain_count == plain_idx:
            return html_idx
            
        char = html_text[html_idx]
        if char == "<":
            in_tag = True
            html_idx += 1
        elif char == ">":
            in_tag = False
            html_idx += 1
        elif in_tag:
            html_idx += 1
        else:
            entity_match = re.match(r"&(amp|lt|gt|quot|apos|#\d+);", html_text[html_idx:])
            if entity_match:
                html_idx += len(entity_match.group(0))
                plain_count += 1
            else:
                html_idx += 1
                plain_count += 1
                
    return len(html_text)


def split_transition(option_text, q_num):
    """Checks if an option text contains a transition pattern and splits it out."""
    plain_text = re.sub(r"<[^>]*>", "", option_text)
    
    for pattern in TRANSITION_PATTERNS:
        match = re.search(pattern, plain_text, re.IGNORECASE | re.DOTALL)
        if match:
            html_start = find_html_index(option_text, match.start())
            clean_option = option_text[:html_start].strip()
            transition_content = option_text[html_start:].strip()
            
            targets = []
            num_word_map = {
                "um": 1, "dois": 2, "três": 3, "quatro": 4, "cinco": 5, "seis": 6, "sete": 7, "oito": 8, "nove": 9, "dez": 10,
                "uma": 1, "duas": 2,
                "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
            }
            
            matched_text = match.group(0)
            range_match = re.search(r"(?:questões|questions)\s+(?:de\s+)?(\d+)\s+(?:a|and|to)\s+(\d+)", matched_text, re.IGNORECASE)
            if range_match:
                start_q = int(range_match.group(1))
                end_q = int(range_match.group(2))
                targets = list(range(start_q, end_q + 1))
            else:
                next_match = re.search(r"(?:next|próximas)\s+(\w+|\d+)\s+(?:questões|questions)", matched_text, re.IGNORECASE)
                if next_match:
                    num_val = next_match.group(1).lower()
                    if num_val.isdigit():
                        count = int(num_val)
                    else:
                        count = num_word_map.get(num_val, 1)
                    targets = list(range(q_num + 1, q_num + 1 + count))
                    
            return clean_option, transition_content, targets
    return option_text, None, []


def extract_html_text_from_page(page, is_two_column=False):
    """Extracts text from a fitz.Page, converting formatting to HTML tags and filtering headers/footers."""
    page_rect = page.rect
    header_threshold = page_rect.y0 + 65.0
    footer_threshold = page_rect.y1 - 65.0
    
    drawings = page.get_drawings()
    underlines = []
    for d in drawings:
        r = fitz.Rect(d["rect"])
        w = r.x1 - r.x0
        h = r.y1 - r.y0
        if h <= 2.0 and w > 2.0:
            underlines.append(r)
            
    raw = page.get_text("rawdict")
    text_parts = []
    
    blocks_text = [b for b in raw["blocks"] if b["type"] == 0]
    
    if is_two_column:
        mid = page_rect.width / 2.0
        full_width_top = [b for b in blocks_text if b["bbox"][0] < mid - 20 and b["bbox"][2] > mid + 20 and b["bbox"][1] < page_rect.height * 0.25]
        left_blocks = [b for b in blocks_text if b not in full_width_top and (b["bbox"][0] + b["bbox"][2])/2.0 < mid]
        right_blocks = [b for b in blocks_text if b not in full_width_top and (b["bbox"][0] + b["bbox"][2])/2.0 >= mid]
        
        full_width_top.sort(key=lambda b: b["bbox"][1])
        left_blocks.sort(key=lambda b: b["bbox"][1])
        right_blocks.sort(key=lambda b: b["bbox"][1])
        
        sorted_blocks = full_width_top + left_blocks + right_blocks
    else:
        sorted_blocks = sorted(blocks_text, key=lambda b: b["bbox"][1])

    for b in sorted_blocks:
            b_rect = fitz.Rect(b["bbox"])
            if b_rect.y1 <= header_threshold:
                continue
            if b_rect.y0 >= footer_threshold:
                continue
                
            for line in b["lines"]:
                line_html = []
                for span in line["spans"]:
                    chars = span.get("chars", [])
                    span_text = "".join(c["c"] for c in chars)
                    
                    if not span_text.strip():
                        line_html.append(span_text)
                        continue
                        
                    current_text = ""
                    current_bold = None
                    current_italic = None
                    current_underline = None
                    
                    font = span["font"]
                    flags = span["flags"]
                    is_bold_span = bool(flags & 16) or "bold" in font.lower() or "negrito" in font.lower()
                    is_italic_span = bool(flags & 2) or "italic" in font.lower() or "oblique" in font.lower()

                    for c in chars:
                        char_text = c["c"]
                        c_bbox = fitz.Rect(c["bbox"])
                        
                        char_underlined = False
                        for u in underlines:
                            y_dist = abs(u.y0 - c_bbox.y1)
                            if y_dist <= 3.0:
                                x_center = (c_bbox.x0 + c_bbox.x1) / 2.0
                                if u.x0 - 0.5 <= x_center <= u.x1 + 0.5:
                                    char_underlined = True
                                    break
                                    
                        if current_bold is None:
                            current_bold = is_bold_span
                            current_italic = is_italic_span
                            current_underline = char_underlined
                            current_text = char_text
                        elif (is_bold_span == current_bold and 
                              is_italic_span == current_italic and 
                              char_underlined == current_underline):
                            current_text += char_text
                        else:
                            part = escape_html(current_text)
                            if current_bold: part = f"<strong>{part}</strong>"
                            if current_italic: part = f"<em>{part}</em>"
                            if current_underline: part = f"<u>{part}</u>"
                            line_html.append(part)
                            
                            current_bold = is_bold_span
                            current_italic = is_italic_span
                            current_underline = char_underlined
                            current_text = char_text
                            
                    if current_text:
                        part = escape_html(current_text)
                        if current_bold: part = f"<strong>{part}</strong>"
                        if current_italic: part = f"<em>{part}</em>"
                        if current_underline: part = f"<u>{part}</u>"
                        line_html.append(part)
                text_parts.append("".join(line_html))
            text_parts.append("\n")
    return "".join(text_parts)


def split_fgv_options(q_body, q_num):
    """Splits a question body into statement and multiple choice options (A-E)."""
    markers = ["A", "B", "C", "D", "E"]
    indices = []
    matches = []
    for m in markers:
        match = re.search(rf"\({m}\)", q_body)
        if match:
            indices.append(match.start())
            matches.append(match)
        else:
            indices.append(-1)
            matches.append(None)
    
    # Try positional splitting first
    if all(idx != -1 for idx in indices) and all(indices[i] < indices[i+1] for i in range(len(indices)-1)):
        statement = q_body[:indices[0]].strip()
        options = {}
        for i in range(len(markers)):
            start = matches[i].end()
            end = indices[i+1] if i+1 < len(markers) else len(q_body)
            option_char = markers[i]
            options[option_char] = q_body[start:end].strip()
        return statement, options
    
    # Fallback to lookahead regex splitter
    option_matches = re.findall(
        r"\(([A-E])\)(.*?)(?=\([A-E]\)|$)",
        q_body,
        re.DOTALL
    )
    if len(option_matches) >= 5:
        first_marker_match = re.search(r"\(A\)", q_body)
        if first_marker_match:
            statement = q_body[:first_marker_match.start()].strip()
        else:
            statement = q_body.split("(A)")[0].strip()
        options = {item[0]: item[1].strip() for item in option_matches[:5]}
        return statement, options
        
    return q_body, {}


def parse_fgv_questions(text, total_questions):
    """Parses FGV questions from raw text using regex bounds matching."""
    questions_raw = []
    current_pos = 0
    
    for q_num in range(1, total_questions + 1):
        pattern = rf"\n\s*(?:<strong>|<em>|<u>|\s)*{q_num}(?:</strong>|</em>|</u>|\s)*\n"
        match = re.search(pattern, text[current_pos:])
        if not match:
            pattern_loose = rf"\n\s*(?:<strong>|<em>|<u>|\s)*{q_num}(?:</strong>|</em>|</u>|\s)+"
            match = re.search(pattern_loose, text[current_pos:])
            if not match:
                print(f"Warning: Could not find Q{q_num}!")
                continue
                
        start_idx = current_pos + match.end()
        
        next_q_num = q_num + 1
        if next_q_num <= total_questions:
            next_pattern = rf"\n\s*(?:<strong>|<em>|<u>|\s)*{next_q_num}(?:</strong>|</em>|</u>|\s)*\n"
            next_match = re.search(next_pattern, text[start_idx:])
            if not next_match:
                next_pattern_loose = rf"\n\s*(?:<strong>|<em>|<u>|\s)*{next_q_num}(?:</strong>|</em>|</u>|\s)+"
                next_match = re.search(next_pattern_loose, text[start_idx:])
                
            if next_match:
                end_idx = start_idx + next_match.start()
            else:
                end_idx = len(text)
        else:
            end_idx = len(text)
            
        q_body = text[start_idx:end_idx].strip()
        questions_raw.append((q_num, q_body))
        current_pos = start_idx
        
    parsed_questions = []
    for q_num, q_body in questions_raw:
        statement, options = split_fgv_options(q_body, q_num)
        
        q_item = {
            "number": q_num,
            "statement": statement,
            "options": options,
            "type": "multiple_choice"
        }
        if not options:
            q_item["error"] = "Failed to split options"
            
        parsed_questions.append(q_item)
                
    return parsed_questions


def parse_cesgranrio_questions(text, total_questions):
    """Parses Cesgranrio questions from raw text using dedicated 2-column regex matching."""
    cb_pos = re.search(r"CONHECIMENTOS\s+B[ÁA]SICOS", text, re.IGNORECASE)
    if cb_pos:
        text = text[cb_pos.end():]

    questions_raw = []
    current_pos = 0
    
    for q_num in range(1, total_questions + 1):
        pattern = rf"\n\s*(?:<[^>]+>|\s)*{q_num}(?:<[^>]+>|\s)*(?=[A-Z\u00C0-\u00DC\"“'‘\$\d<])"
        candidates = list(re.finditer(pattern, text[current_pos:]))
        
        selected_match = None
        for cand in candidates:
            cand_start = current_pos + cand.start()
            sample_chunk = text[cand_start:cand_start + 1200]
            if re.search(r"\(A\)", sample_chunk):
                selected_match = cand
                break
                
        if not selected_match:
            if candidates:
                selected_match = candidates[0]
            else:
                print(f"Warning: Could not find Q{q_num}!")
                continue
                
        start_idx = current_pos + selected_match.end()
        
        next_q_num = q_num + 1
        if next_q_num <= total_questions:
            next_pattern = rf"\n\s*(?:<[^>]+>|\s)*{next_q_num}(?:<[^>]+>|\s)*(?=[A-Z\u00C0-\u00DC\"“'‘\$\d<])"
            next_candidates = list(re.finditer(next_pattern, text[start_idx:]))
            next_selected = None
            for n_cand in next_candidates:
                n_start = start_idx + n_cand.start()
                n_sample = text[n_start:n_start + 1200]
                if re.search(r"\(A\)", n_sample):
                    next_selected = n_cand
                    break
                    
            if next_selected:
                end_idx = start_idx + next_selected.start()
            else:
                end_idx = len(text)
        else:
            end_idx = len(text)
            
        q_body = text[start_idx:end_idx].strip()
        statement, options = split_fgv_options(q_body, q_num)
        
        if not options or len(options) < 5:
            extended_chunk = text[start_idx:start_idx + 3500]
            opt_matches = re.findall(r"\(([A-E])\)(.*?)(?=\([A-E]\)|$)", extended_chunk, re.DOTALL)
            if len(opt_matches) >= 5:
                first_a = re.search(r"\(A\)", extended_chunk)
                if first_a:
                    statement = extended_chunk[:first_a.start()].strip()
                    options = {m[0]: m[1].strip() for m in opt_matches[:5]}

        questions_raw.append((q_num, statement, options))
        current_pos = start_idx
        
    parsed_questions = []
    for q_num, statement, options in questions_raw:
        q_item = {
            "number": q_num,
            "statement": statement,
            "options": options,
            "type": "multiple_choice"
        }
        if not options:
            q_item["error"] = "Failed to split options"
            
        parsed_questions.append(q_item)
                
    return parsed_questions


def parse_cebraspe_questions(text):
    """Parses CEBRASPE right/wrong items from raw text."""
    pattern = r"\n\s*(?:<strong>|<em>|<u>|\s)*(\d+)(?:</strong>|</em>|</u>|\s)+"
    splits = list(re.finditer(pattern, text))
    
    parsed_questions = []
    for i in range(len(splits)):
        start_idx = splits[i].end()
        end_idx = splits[i+1].start() if i+1 < len(splits) else len(text)
        
        q_num = int(splits[i].group(1))
        if q_num < 51 or q_num > 120:
            continue
            
        statement = text[start_idx:end_idx].strip()
        statement = re.sub(r"\n\s*CEBRASPE.*$", "", statement)
        statement = re.sub(r"--- PAGE \d+ ---", "", statement)
        statement = statement.strip()
        
        parsed_questions.append({
            "number": q_num,
            "statement": statement,
            "options": {
                "C": "Certo",
                "E": "Errado"
            },
            "type": "right_wrong"
        })
        
    return parsed_questions


def map_discipline(exam_type, exam_name, q_num, total_questions):
    """Maps a question to its discipline category based on type, name, and index."""
    discipline = "Conhecimentos Específicos"
    if exam_type == "fgv":
        if total_questions == 80:  # TCESP or TCE-ES
            if q_num <= 20:
                discipline = "Língua Portuguesa"
            elif q_num <= 30 and "TCESP" in exam_name:
                discipline = "Direito e Legislação"
            elif q_num <= 40 and "TCESP" in exam_name:
                discipline = "Língua Inglesa / Raciocínio Lógico"
            else:
                discipline = "Tecnologia da Informação"
        elif total_questions == 70:  # DATAPREV
            if q_num <= 12:
                discipline = "Língua Portuguesa"
            elif q_num <= 18:
                discipline = "Língua Inglesa"
            else:
                discipline = "Conhecimentos Específicos (TI)"
    else:  # CEBRASPE
        if "Segurança" in exam_name:
            discipline = "Segurança da Informação"
        elif "Engenharia de Dados" in exam_name:
            discipline = "Banco de Dados & Big Data"
    return discipline


def save_databases(all_exams_data):
    """Persists parsed exams data to both questions.json and questions.js databases."""
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(all_exams_data, f, ensure_ascii=False, indent=2)
    print(f"Saved all questions database to {OUTPUT_JSON}")

    with open(OUTPUT_JS, "w", encoding="utf-8") as f:
        f.write("const EXAMS_DATA = ")
        json.dump(all_exams_data, f, ensure_ascii=False, indent=2)
        f.write(";\n")
    print(f"Saved all questions database to {OUTPUT_JS}")


def extract_all():
    """Main dynamic loader and compiler loop for exam PDFs."""
    all_exams_data = []
    
    # Dynamic discovery of exams in the provas/ directory
    exams_to_process = []
    for f in os.listdir(PDF_DIR):
        if f.endswith(".pdf"):
            base_name = f.rsplit(".", 1)[0]
            config_path = os.path.join(PDF_DIR, base_name + ".json")
            if os.path.exists(config_path):
                try:
                    with open(config_path, "r", encoding="utf-8") as cfg_file:
                        config_data = json.load(cfg_file)
                    
                    answers_config = config_data.get("answers", {})
                    if isinstance(answers_config, str):
                        answers = {i+1: char for i, char in enumerate(answers_config)}
                    else:
                        answers = {int(k): v for k, v in answers_config.items()}
                        
                    exam_item = {
                        "filename": f,
                        "name": config_data.get("name", base_name),
                        "banca": config_data.get("banca", "FGV").upper(),
                        "type": config_data.get("banca", "FGV").lower(),
                        "total_questions": config_data.get("total_questions", 0),
                        "answers": answers
                    }
                    exams_to_process.append(exam_item)
                except Exception as e:
                    print(f"Error reading configuration for {f}: {e}")
            else:
                print(f"Warning: Configuration file {base_name + '.json'} not found for {f}. Skipping.")
                
    for exam in exams_to_process:
        path = os.path.join(PDF_DIR, exam["filename"])
        if not os.path.exists(path):
            print(f"Warning: File {path} not found.")
            continue
            
        print(f"Extracting {exam['name']}...")
        doc = fitz.open(path)
        
        is_two_col = (exam["type"] == "cesgranrio" or "cesgranrio" in exam["banca"].lower() or "banco do brasil" in exam["name"].lower())
        full_text = ""
        for i in range(len(doc)):
            full_text += f"\n--- PAGE {i+1} ---\n"
            full_text += extract_html_text_from_page(doc[i], is_two_column=is_two_col)
            
        if exam["type"] == "cesgranrio" or "cesgranrio" in exam["banca"].lower() or "banco do brasil" in exam["name"].lower():
            questions = parse_cesgranrio_questions(full_text, exam["total_questions"])
        elif exam["type"] == "fgv":
            questions = parse_fgv_questions(full_text, exam["total_questions"])
        else:  # cebraspe
            questions = parse_cebraspe_questions(full_text)
            
        final_questions = []
        for q in questions:
            num = q["number"]
            ans = exam["answers"].get(num, "")
            discipline = map_discipline(exam["type"], exam["name"], num, exam["total_questions"])
            
            q_data = {
                "id": f"{exam['filename'].split('.')[0]}_q{num}",
                "number": num,
                "discipline": discipline,
                "statement": q["statement"],
                "options": q["options"],
                "type": q["type"],
                "correct_answer": ans,
                "explanation": ""
            }
            final_questions.append(q_data)
            
        # Post-process to handle transitions and shared text blocks
        if exam["type"] == "fgv":
            for q in final_questions:
                options = q["options"]
                if "E" in options:
                    clean_opt, trans_content, targets = split_transition(options["E"], q["number"])
                    if trans_content:
                        options["E"] = clean_opt
                        for target_num in targets:
                            target_q = next((item for item in final_questions if item["number"] == target_num), None)
                            if target_q:
                                target_q["statement"] = (
                                    f'<div class="shared-text-block">'
                                    f'<strong>Texto de apoio:</strong><br>'
                                    f'{trans_content}'
                                    f'</div><hr>'
                                    f'{target_q["statement"]}'
                                )
        elif exam["type"] == "cebraspe":
            active_transition = None
            for q in final_questions:
                match = re.search(CEBRASPE_TRANSITION_PATTERN, q["statement"], re.IGNORECASE | re.DOTALL)
                if match:
                    clean_statement = q["statement"][:match.start()].strip()
                    trans_content = q["statement"][match.start():].strip()
                    q["statement"] = clean_statement
                    active_transition = trans_content
                    
                if active_transition and not match:
                    q["statement"] = (
                        f'<div class="shared-text-block">'
                        f'<strong>Texto de apoio:</strong><br>'
                        f'{active_transition}'
                        f'</div><hr>'
                        f'{q["statement"]}'
                    )
                    
        all_exams_data.append({
            "exam_id": exam["filename"].split(".")[0],
            "exam_name": exam["name"],
            "banca": exam["banca"],
            "questions": final_questions
        })
        
        print(f"Successfully parsed {len(final_questions)} questions from {exam['name']}.")
        
    save_databases(all_exams_data)


if __name__ == "__main__":
    extract_all()
