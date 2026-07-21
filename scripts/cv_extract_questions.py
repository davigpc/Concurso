"""
PrepConcursos - Main Orchestrator for Computer Vision PDF Question Extraction

Modular structure:
  - scripts/extractors/ : CebraspeExtractor, FGVExtractor, CesgranrioExtractor, ExtractorFactory
  - scripts/utils/      : PDF Bounding Box Parser & Image Extractor, Discipline Mapping
"""

import os
import re
import json
import sqlite3
import fitz  # PyMuPDF

from extractors import ExtractorFactory
from utils import extract_page_blocks, extract_images, map_discipline

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
PDF_DIR = os.path.join(PROJECT_DIR, "provas")
DB_PATH = os.path.join(PROJECT_DIR, "concurso.db")


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
