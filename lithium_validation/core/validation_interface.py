"""
High-level validation interface for Lithium-Validation framework.
Provides easy-to-use functions for common validation tasks.
"""

from typing import Optional, Dict, Any, Union
from .validation_engine import OutputValidator, ValidationResult, ConfidenceLevel


class ValidationInterface:
    """
    High-level interface for AI output validation.
    
    This class provides a simplified API for common validation tasks,
    making it easy to integrate validation into existing workflows.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the validation interface."""
        self.validator = OutputValidator(config)
        self._default_config = {
            "confidence_threshold": 0.7,
            "enable_factual_validation": True,
            "enable_logical_consistency": True,
            "enable_source_attribution": True,
            "max_warnings": 10
        }
    
    def validate_output(self, output: str, context: Optional[str] = None, 
                      validation_type: str = "comprehensive") -> ValidationResult:
        """
        Validate an AI-generated output.
        
        Args:
            output: The AI-generated content to validate
            context: Additional context for validation (optional)
            validation_type: Type of validation to perform
                - "quick": Fast validation with basic checks
                - "comprehensive": Full validation with all checks
                - "factual": Focus on factual accuracy
                - "logical": Focus on logical consistency
                - "sources": Focus on source attribution
        
        Returns:
            ValidationResult object with validation details
        """
        return self.validator.validate(output, context, validation_type)
    
    def quick_check(self, output: str) -> bool:
        """
        Quick validation check - returns True if output passes basic validation.
        
        Args:
            output: The AI-generated content to check
            
        Returns:
            True if output passes validation, False otherwise
        """
        result = self.validate_output(output, validation_type="quick")
        return result.is_valid
    
    def get_confidence_score(self, output: str) -> float:
        """
        Get confidence score for an output (0.0 to 1.0).
        
        Args:
            output: The AI-generated content to score
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        result = self.validate_output(output, validation_type="quick")
        return result.score
    
    def get_validation_summary(self, output: str) -> Dict[str, Any]:
        """
        Get a summary of validation results.
        
        Args:
            output: The AI-generated content to validate
            
        Returns:
            Dictionary with validation summary
        """
        result = self.validate_output(output)
        return {
            "is_valid": result.is_valid,
            "confidence": result.confidence.value,
            "score": result.score,
            "warning_count": len(result.warnings),
            "validation_type": result.validation_type,
            "timestamp": result.timestamp.isoformat()
        }
    
    def batch_validate(self, outputs: list[str], 
                      validation_type: str = "comprehensive") -> list[ValidationResult]:
        """
        Validate multiple outputs in batch.
        
        Args:
            outputs: List of AI-generated contents to validate
            validation_type: Type of validation to perform
            
        Returns:
            List of ValidationResult objects
        """
        results = []
        for output in outputs:
            result = self.validate_output(output, validation_type=validation_type)
            results.append(result)
        return results
    
    def configure(self, **kwargs) -> None:
        """
        Update validation configuration.
        
        Args:
            **kwargs: Configuration parameters to update
        """
        self._default_config.update(kwargs)
        self.validator = OutputValidator(self._default_config)


# Convenience functions for quick access
def quick_check(output: str) -> bool:
    """
    Quick validation check - returns True if output passes basic validation.
    
    Args:
        output: The AI-generated content to check
        
    Returns:
        True if output passes validation, False otherwise
    """
    interface = ValidationInterface()
    return interface.quick_check(output)


def quick_validate(output: str, context: Optional[str] = None) -> ValidationResult:
    """
    Quick validation with detailed results.
    
    Args:
        output: The AI-generated content to validate
        context: Additional context for validation (optional)
        
    Returns:
        ValidationResult object with validation details
    """
    interface = ValidationInterface()
    return interface.validate_output(output, context, "quick")


def comprehensive_validate(output: str, context: Optional[str] = None) -> ValidationResult:
    """
    Comprehensive validation with all checks.
    
    Args:
        output: The AI-generated content to validate
        context: Additional context for validation (optional)
        
    Returns:
        ValidationResult object with validation details
    """
    interface = ValidationInterface()
    return interface.validate_output(output, context, "comprehensive")


def get_confidence_level(score: float) -> str:
    """
    Get confidence level string from score.
    
    Args:
        score: Confidence score (0.0 to 1.0)
        
    Returns:
        Confidence level string
    """
    if score >= 0.9:
        return "HIGH"
    elif score >= 0.7:
        return "MEDIUM"
    elif score >= 0.5:
        return "LOW"
    else:
        return "INSUFFICIENT"


# Example usage and testing functions
def example_usage():
    """Example usage of the validation interface."""
    print("🔬 Lithium-Validation Example Usage")
    print("=" * 40)
    
    # Example outputs to validate
    outputs = [
        "The capital of France is Paris. This is a well-established fact.",
        "According to recent studies, the sky is always blue everywhere on Earth.",
        "The population of Tokyo is approximately 14 million people, but this number varies by source.",
        "I think the answer might be 42, but I'm not completely sure about this."
    ]
    
    interface = ValidationInterface()
    
    for i, output in enumerate(outputs, 1):
        print(f"\n📝 Example {i}: {output}")
        print("-" * 50)
        
        result = interface.validate_output(output)
        print(f"✅ Valid: {result.is_valid}")
        print(f"🎯 Confidence: {result.confidence.value.upper()}")
        print(f"📊 Score: {result.score:.2f}")
        
        if result.warnings:
            print(f"⚠️  Warnings ({len(result.warnings)}):")
            for warning in result.warnings[:3]:  # Show first 3 warnings
                print(f"   • {warning}")
        else:
            print("✅ No warnings")


if __name__ == "__main__":
    example_usage()
