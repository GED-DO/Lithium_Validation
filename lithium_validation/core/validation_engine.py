"""
Core validation engine for Lithium-Validation framework.
Implements the main validation logic based on hallucination research.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import re
from datetime import datetime


class ConfidenceLevel(Enum):
    """Confidence levels for validation results."""
    HIGH = "high"          # 90-100% confidence
    MEDIUM = "medium"      # 70-89% confidence
    LOW = "low"            # 50-69% confidence
    INSUFFICIENT = "insufficient"  # <50% confidence


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    is_valid: bool
    confidence: ConfidenceLevel
    score: float  # 0.0 to 1.0
    details: Dict[str, Any]
    warnings: List[str]
    timestamp: datetime
    validation_type: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "is_valid": self.is_valid,
            "confidence": self.confidence.value,
            "score": self.score,
            "details": self.details,
            "warnings": self.warnings,
            "timestamp": self.timestamp.isoformat(),
            "validation_type": self.validation_type
        }


class OutputValidator:
    """
    Main validation engine for AI outputs.
    
    Based on research from "Why Language Models Hallucinate" by
    Kalai, Nachum, Vempala, & Zhang.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the validator with optional configuration."""
        self.config = config or self._default_config()
        self.validation_rules = self._load_validation_rules()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for the validator."""
        return {
            "confidence_threshold": 0.7,
            "enable_factual_validation": True,
            "enable_logical_consistency": True,
            "enable_source_attribution": True,
            "max_warnings": 10
        }
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules and patterns."""
        return {
            "factual_patterns": [
                r"according to [^,]+,",
                r"studies show",
                r"research indicates",
                r"data suggests",
                r"statistics show"
            ],
            "uncertainty_indicators": [
                r"might be",
                r"could be",
                r"possibly",
                r"perhaps",
                r"it seems",
                r"appears to"
            ],
            "citation_patterns": [
                r"\[[\d\w\s,]+\]",
                r"\([^)]*20\d{2}[^)]*\)",
                r"source:",
                r"reference:",
                r"according to"
            ]
        }
    
    def validate(self, output: str, context: Optional[str] = None, 
                validation_type: str = "comprehensive") -> ValidationResult:
        """
        Validate an AI output.
        
        Args:
            output: The AI-generated content to validate
            context: Additional context for validation
            validation_type: Type of validation to perform
            
        Returns:
            ValidationResult object with validation details
        """
        warnings = []
        details = {}
        score = 0.0
        
        # Factual validation
        if self.config.get("enable_factual_validation", True):
            factual_score, factual_warnings = self._validate_factual_claims(output)
            score += factual_score * 0.4
            warnings.extend(factual_warnings)
            details["factual_validation"] = {
                "score": factual_score,
                "warnings": len(factual_warnings)
            }
        
        # Logical consistency
        if self.config.get("enable_logical_consistency", True):
            logical_score, logical_warnings = self._validate_logical_consistency(output)
            score += logical_score * 0.3
            warnings.extend(logical_warnings)
            details["logical_consistency"] = {
                "score": logical_score,
                "warnings": len(logical_warnings)
            }
        
        # Source attribution
        if self.config.get("enable_source_attribution", True):
            source_score, source_warnings = self._validate_source_attribution(output)
            score += source_score * 0.3
            warnings.extend(source_warnings)
            details["source_attribution"] = {
                "score": source_score,
                "warnings": len(source_warnings)
            }
        
        # Determine confidence level
        confidence = self._determine_confidence(score)
        
        # Check if valid based on threshold
        is_valid = score >= self.config.get("confidence_threshold", 0.7)
        
        # Limit warnings
        max_warnings = self.config.get("max_warnings", 10)
        if len(warnings) > max_warnings:
            warnings = warnings[:max_warnings]
            warnings.append(f"... and {len(warnings) - max_warnings} more warnings")
        
        return ValidationResult(
            is_valid=is_valid,
            confidence=confidence,
            score=score,
            details=details,
            warnings=warnings,
            timestamp=datetime.now(),
            validation_type=validation_type
        )
    
    def _validate_factual_claims(self, output: str) -> tuple[float, List[str]]:
        """Validate factual claims in the output."""
        warnings = []
        score = 1.0
        
        # Check for unsupported factual claims
        factual_patterns = self.validation_rules["factual_patterns"]
        for pattern in factual_patterns:
            matches = re.findall(pattern, output, re.IGNORECASE)
            if matches:
                warnings.append(f"Unsupported factual claim detected: {matches[0]}")
                score -= 0.2
        
        # Check for uncertainty indicators (good sign)
        uncertainty_patterns = self.validation_rules["uncertainty_indicators"]
        uncertainty_count = 0
        for pattern in uncertainty_patterns:
            uncertainty_count += len(re.findall(pattern, output, re.IGNORECASE))
        
        if uncertainty_count > 0:
            score += min(uncertainty_count * 0.1, 0.3)
        
        return max(0.0, min(1.0, score)), warnings
    
    def _validate_logical_consistency(self, output: str) -> tuple[float, List[str]]:
        """Validate logical consistency of the output."""
        warnings = []
        score = 1.0
        
        # Check for contradictory statements
        contradictions = [
            ("always", "never"),
            ("all", "none"),
            ("every", "no"),
            ("completely", "partially")
        ]
        
        for pos, neg in contradictions:
            if re.search(rf"\b{pos}\b", output, re.IGNORECASE) and \
               re.search(rf"\b{neg}\b", output, re.IGNORECASE):
                warnings.append(f"Potential contradiction detected: {pos} vs {neg}")
                score -= 0.3
        
        # Check for logical flow
        sentences = re.split(r'[.!?]+', output)
        if len(sentences) > 1:
            # Simple coherence check
            transition_words = ["however", "therefore", "moreover", "furthermore", "additionally"]
            has_transitions = any(word in output.lower() for word in transition_words)
            if has_transitions:
                score += 0.1
        
        return max(0.0, min(1.0, score)), warnings
    
    def _validate_source_attribution(self, output: str) -> tuple[float, List[str]]:
        """Validate source attribution and citations."""
        warnings = []
        score = 1.0
        
        citation_patterns = self.validation_rules["citation_patterns"]
        has_citations = any(re.search(pattern, output, re.IGNORECASE) 
                           for pattern in citation_patterns)
        
        if not has_citations:
            warnings.append("No citations or source attributions found")
            score -= 0.4
        
        # Check for proper citation format
        if has_citations:
            # Look for incomplete citations
            incomplete_citations = re.findall(r"\[[^\]]*\]", output)
            for citation in incomplete_citations:
                if len(citation) < 5:  # Very short citations
                    warnings.append(f"Incomplete citation: {citation}")
                    score -= 0.1
        
        return max(0.0, min(1.0, score)), warnings
    
    def _determine_confidence(self, score: float) -> ConfidenceLevel:
        """Determine confidence level based on score."""
        if score >= 0.9:
            return ConfidenceLevel.HIGH
        elif score >= 0.7:
            return ConfidenceLevel.MEDIUM
        elif score >= 0.5:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.INSUFFICIENT
