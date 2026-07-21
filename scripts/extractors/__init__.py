"""
Extractors package for banca-specific question parsing strategies.
"""

from .base import BaseExamExtractor
from .cebraspe import CebraspeExtractor
from .fgv import FGVExtractor
from .cesgranrio import CesgranrioExtractor
from .factory import ExtractorFactory

__all__ = [
    "BaseExamExtractor",
    "CebraspeExtractor",
    "FGVExtractor",
    "CesgranrioExtractor",
    "ExtractorFactory",
]
