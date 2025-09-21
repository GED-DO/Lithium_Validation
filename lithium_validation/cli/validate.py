#!/usr/bin/env python3
"""
Command-line interface for Lithium-Validation framework.
"""

import argparse
import sys
import json
from typing import Optional
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lithium_validation.core.validation_interface import ValidationInterface, quick_check, quick_validate


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Lithium-Validation: AI Output Validation Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  lithium-validate "The capital of France is Paris"
  lithium-validate --file output.txt
  lithium-validate --comprehensive "According to studies..."
  lithium-validate --json "Some AI output"
        """
    )
    
    # Input options
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("text", nargs="?", help="Text to validate")
    group.add_argument("--file", "-f", help="File containing text to validate")
    
    # Validation options
    parser.add_argument("--type", "-t", 
                       choices=["quick", "comprehensive", "factual", "logical", "sources"],
                       default="comprehensive",
                       help="Type of validation to perform")
    
    parser.add_argument("--context", "-c", help="Additional context for validation")
    parser.add_argument("--json", "-j", action="store_true", 
                       help="Output results in JSON format")
    parser.add_argument("--quiet", "-q", action="store_true",
                       help="Only output validation result (true/false)")
    parser.add_argument("--threshold", type=float, default=0.7,
                       help="Confidence threshold for validation (0.0-1.0)")
    
    args = parser.parse_args()
    
    # Get text to validate
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read().strip()
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        text = args.text
    
    if not text:
        print("Error: No text provided for validation", file=sys.stderr)
        sys.exit(1)
    
    # Configure validator
    config = {"confidence_threshold": args.threshold}
    interface = ValidationInterface(config)
    
    # Perform validation
    try:
        result = interface.validate_output(text, args.context, args.type)
        
        if args.quiet:
            print("true" if result.is_valid else "false")
            sys.exit(0 if result.is_valid else 1)
        
        if args.json:
            print(json.dumps(result.to_dict(), indent=2))
        else:
            print_validation_result(result, args.type)
            
    except Exception as e:
        print(f"Error during validation: {e}", file=sys.stderr)
        sys.exit(1)


def print_validation_result(result, validation_type: str):
    """Print validation result in human-readable format."""
    print("🔬 Lithium-Validation Results")
    print("=" * 40)
    print(f"📋 Validation Type: {validation_type.title()}")
    print(f"✅ Valid: {'Yes' if result.is_valid else 'No'}")
    print(f"🎯 Confidence: {result.confidence.value.upper()}")
    print(f"📊 Score: {result.score:.2f}")
    print(f"⏰ Timestamp: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if result.details:
        print("\n📈 Detailed Analysis:")
        for category, details in result.details.items():
            print(f"  • {category.replace('_', ' ').title()}: {details['score']:.2f}")
    
    if result.warnings:
        print(f"\n⚠️  Warnings ({len(result.warnings)}):")
        for i, warning in enumerate(result.warnings, 1):
            print(f"  {i}. {warning}")
    else:
        print("\n✅ No warnings found")
    
    # Recommendations
    print("\n💡 Recommendations:")
    if result.confidence == result.confidence.INSUFFICIENT:
        print("  • Consider adding more supporting evidence")
        print("  • Review factual claims for accuracy")
        print("  • Add proper citations and sources")
    elif result.confidence == result.confidence.LOW:
        print("  • Add more context or supporting information")
        print("  • Consider adding uncertainty indicators")
    elif result.confidence == result.confidence.MEDIUM:
        print("  • Good validation score")
        print("  • Consider minor improvements for higher confidence")
    else:
        print("  • Excellent validation score!")
        print("  • Output meets high quality standards")


if __name__ == "__main__":
    main()
