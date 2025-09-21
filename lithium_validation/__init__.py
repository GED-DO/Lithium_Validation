"""
Lithium-Validation: AI Output Validation Framework
Author: Guillermo Espinosa
Based on "Why Language Models Hallucinate" by Kalai, Nachum, Vempala, & Zhang
"""

__version__ = "1.0.0"
__author__ = "Guillermo Espinosa"
__email__ = "hola@ged.do"

from .core.validation_interface import ValidationInterface, quick_check, quick_validate
from .core.validation_engine import OutputValidator, ValidationResult, ConfidenceLevel

__all__ = [
    "ValidationInterface",
    "OutputValidator", 
    "ValidationResult",
    "ConfidenceLevel",
    "quick_check",
    "quick_validate"
]


