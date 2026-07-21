"""
Extractor Factory for instantiating banca-specific exam extractors.
"""

from .base import BaseExamExtractor
from .cebraspe import CebraspeExtractor
from .fgv import FGVExtractor
from .cesgranrio import CesgranrioExtractor


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
