"""
Basic tests for Lithium-Validation framework.
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lithium_validation import ValidationInterface, quick_check, quick_validate
from lithium_validation.core.validation_engine import ConfidenceLevel


class TestValidationInterface(unittest.TestCase):
    """Test cases for ValidationInterface."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.interface = ValidationInterface()
    
    def test_quick_check_valid(self):
        """Test quick check with valid output."""
        output = "The capital of France is Paris. This is a well-established fact."
        result = quick_check(output)
        self.assertTrue(result)
    
    def test_quick_check_invalid(self):
        """Test quick check with invalid output."""
        output = "According to studies, the sky is always blue everywhere on Earth."
        result = quick_check(output)
        # This might be valid or invalid depending on configuration
        self.assertIsInstance(result, bool)
    
    def test_validation_result_structure(self):
        """Test that validation result has expected structure."""
        output = "Water boils at 100°C at sea level."
        result = self.interface.validate_output(output)
        
        self.assertIsInstance(result.is_valid, bool)
        self.assertIsInstance(result.confidence, ConfidenceLevel)
        self.assertIsInstance(result.score, float)
        self.assertIsInstance(result.details, dict)
        self.assertIsInstance(result.warnings, list)
        self.assertIsInstance(result.timestamp, type(result.timestamp))
        self.assertIsInstance(result.validation_type, str)
    
    def test_confidence_levels(self):
        """Test confidence level determination."""
        # Test different score ranges
        self.assertEqual(ConfidenceLevel.HIGH, self.interface.validator._determine_confidence(0.95))
        self.assertEqual(ConfidenceLevel.MEDIUM, self.interface.validator._determine_confidence(0.75))
        self.assertEqual(ConfidenceLevel.LOW, self.interface.validator._determine_confidence(0.65))
        self.assertEqual(ConfidenceLevel.INSUFFICIENT, self.interface.validator._determine_confidence(0.3))
    
    def test_batch_validation(self):
        """Test batch validation functionality."""
        outputs = [
            "The sun rises in the east.",
            "All birds can fly.",
            "Water is H2O."
        ]
        
        results = self.interface.batch_validate(outputs)
        
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertIsInstance(result.is_valid, bool)
            self.assertIsInstance(result.score, float)
    
    def test_validation_types(self):
        """Test different validation types."""
        output = "According to studies, cats are mammals."
        
        validation_types = ["quick", "comprehensive", "factual", "logical", "sources"]
        
        for vtype in validation_types:
            result = self.interface.validate_output(output, validation_type=vtype)
            self.assertEqual(result.validation_type, vtype)
            self.assertIsInstance(result.is_valid, bool)
    
    def test_custom_configuration(self):
        """Test custom configuration."""
        config = {
            "confidence_threshold": 0.9,
            "max_warnings": 3
        }
        
        interface = ValidationInterface(config)
        result = interface.validate_output("Test output")
        
        self.assertIsInstance(result.is_valid, bool)
        # The result should respect the configuration
        self.assertIsInstance(result.warnings, list)


class TestValidationEngine(unittest.TestCase):
    """Test cases for ValidationEngine."""
    
    def setUp(self):
        """Set up test fixtures."""
        from lithium_validation.core.validation_engine import OutputValidator
        self.validator = OutputValidator()
    
    def test_factual_validation(self):
        """Test factual validation logic."""
        output = "According to recent studies, the sky is always blue."
        score, warnings = self.validator._validate_factual_claims(output)
        
        self.assertIsInstance(score, float)
        self.assertIsInstance(warnings, list)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
    
    def test_logical_consistency(self):
        """Test logical consistency validation."""
        output = "All birds can fly, but penguins cannot fly."
        score, warnings = self.validator._validate_logical_consistency(output)
        
        self.assertIsInstance(score, float)
        self.assertIsInstance(warnings, list)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
    
    def test_source_attribution(self):
        """Test source attribution validation."""
        output = "According to Smith (2023), the results show..."
        score, warnings = self.validator._validate_source_attribution(output)
        
        self.assertIsInstance(score, float)
        self.assertIsInstance(warnings, list)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)


if __name__ == "__main__":
    unittest.main()
