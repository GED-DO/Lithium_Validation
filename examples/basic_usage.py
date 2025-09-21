#!/usr/bin/env python3
"""
Basic usage examples for Lithium-Validation framework.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lithium_validation import ValidationInterface, quick_check, quick_validate, comprehensive_validate


def main():
    """Demonstrate basic usage of Lithium-Validation."""
    print("🔬 Lithium-Validation Basic Usage Examples")
    print("=" * 50)
    
    # Example 1: Quick validation
    print("\n1️⃣ Quick Validation")
    print("-" * 30)
    
    outputs = [
        "The capital of France is Paris. This is a well-established fact.",
        "According to recent studies, the sky is always blue everywhere on Earth.",
        "The population of Tokyo is approximately 14 million people, but this number varies by source.",
        "I think the answer might be 42, but I'm not completely sure about this."
    ]
    
    for i, output in enumerate(outputs, 1):
        print(f"\nExample {i}: {output}")
        is_valid = quick_check(output)
        print(f"Quick check: {'✅ Valid' if is_valid else '❌ Invalid'}")
    
    # Example 2: Detailed validation
    print("\n\n2️⃣ Detailed Validation")
    print("-" * 30)
    
    interface = ValidationInterface()
    result = interface.validate_output(
        "According to recent studies, the Earth is flat. This has been proven by multiple researchers.",
        context="This is about Earth's shape",
        validation_type="comprehensive"
    )
    
    print(f"Valid: {result.is_valid}")
    print(f"Confidence: {result.confidence.value.upper()}")
    print(f"Score: {result.score:.2f}")
    print(f"Warnings: {len(result.warnings)}")
    
    if result.warnings:
        print("Warning details:")
        for warning in result.warnings:
            print(f"  • {warning}")
    
    # Example 3: Batch validation
    print("\n\n3️⃣ Batch Validation")
    print("-" * 30)
    
    test_outputs = [
        "The sun rises in the east and sets in the west.",
        "All birds can fly, according to my research.",
        "Water boils at 100°C at sea level, though this may vary with altitude.",
        "The answer is definitely 42, no question about it."
    ]
    
    results = interface.batch_validate(test_outputs, "comprehensive")
    
    for i, result in enumerate(results, 1):
        print(f"Output {i}: {'✅' if result.is_valid else '❌'} "
              f"({result.confidence.value.upper()}, {result.score:.2f})")
    
    # Example 4: Different validation types
    print("\n\n4️⃣ Different Validation Types")
    print("-" * 30)
    
    test_text = "According to studies, all cats are mammals. This is a scientific fact."
    
    validation_types = ["quick", "comprehensive", "factual", "logical", "sources"]
    
    for vtype in validation_types:
        result = interface.validate_output(test_text, validation_type=vtype)
        print(f"{vtype.title()}: {'✅' if result.is_valid else '❌'} "
              f"({result.confidence.value.upper()}, {result.score:.2f})")
    
    # Example 5: Configuration
    print("\n\n5️⃣ Custom Configuration")
    print("-" * 30)
    
    # Create validator with custom config
    custom_config = {
        "confidence_threshold": 0.8,  # Higher threshold
        "max_warnings": 5  # Fewer warnings
    }
    
    custom_interface = ValidationInterface(custom_config)
    result = custom_interface.validate_output(
        "The sky is blue because of Rayleigh scattering, though this explanation might be oversimplified."
    )
    
    print(f"Custom config result: {'✅' if result.is_valid else '❌'} "
          f"({result.confidence.value.upper()}, {result.score:.2f})")
    print(f"Threshold: {custom_config['confidence_threshold']}")
    print(f"Max warnings: {custom_config['max_warnings']}")


if __name__ == "__main__":
    main()
