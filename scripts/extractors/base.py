"""
Base Abstract Extractor and shared text cleaning utilities.
"""

import re
from abc import ABC, abstractmethod

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
