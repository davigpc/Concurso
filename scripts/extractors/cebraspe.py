"""
Cebraspe Extractor: Right/Wrong (Certo/Errado) itemization & continuous support texts.
"""

import re
from .base import BaseExamExtractor, CEBRASPE_SUPPORT_PATTERN


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
