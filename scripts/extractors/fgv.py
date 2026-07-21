"""
FGV Extractor: 2-column layout multiple-choice (A-E) & ranged reading passages.
"""

import re
from .base import BaseExamExtractor, split_options_ae, TRANSITION_PATTERNS, WORD_NUMS


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
