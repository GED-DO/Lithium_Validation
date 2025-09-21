"""
MCP (Model Context Protocol) server for Lithium-Validation framework.
Provides validation services through MCP for Claude Desktop integration.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from datetime import datetime

try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        CallToolRequest,
        CallToolResult,
        ListToolsRequest,
        ListToolsResult,
        Tool,
        TextContent,
        ImageContent
    )
except ImportError:
    print("MCP not installed. Install with: pip install mcp")
    raise

from ..core.validation_interface import ValidationInterface, ValidationResult


class LithiumMCPServer:
    """MCP server for Lithium-Validation framework."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the MCP server."""
        self.server = Server("lithium-validation")
        self.validator = ValidationInterface(config)
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up MCP request handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available validation tools."""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="validate_output",
                        description="Validate AI-generated output for accuracy and reliability",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "output": {
                                    "type": "string",
                                    "description": "The AI-generated content to validate"
                                },
                                "context": {
                                    "type": "string",
                                    "description": "Additional context for validation (optional)"
                                },
                                "validation_type": {
                                    "type": "string",
                                    "enum": ["quick", "comprehensive", "factual", "logical", "sources"],
                                    "default": "comprehensive",
                                    "description": "Type of validation to perform"
                                }
                            },
                            "required": ["output"]
                        }
                    ),
                    Tool(
                        name="quick_check",
                        description="Quick validation check - returns true/false",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "output": {
                                    "type": "string",
                                    "description": "The AI-generated content to check"
                                }
                            },
                            "required": ["output"]
                        }
                    ),
                    Tool(
                        name="get_confidence_score",
                        description="Get confidence score for an output (0.0 to 1.0)",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "output": {
                                    "type": "string",
                                    "description": "The AI-generated content to score"
                                }
                            },
                            "required": ["output"]
                        }
                    ),
                    Tool(
                        name="batch_validate",
                        description="Validate multiple outputs in batch",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "outputs": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of AI-generated contents to validate"
                                },
                                "validation_type": {
                                    "type": "string",
                                    "enum": ["quick", "comprehensive", "factual", "logical", "sources"],
                                    "default": "comprehensive",
                                    "description": "Type of validation to perform"
                                }
                            },
                            "required": ["outputs"]
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls."""
            try:
                if name == "validate_output":
                    return await self._handle_validate_output(arguments)
                elif name == "quick_check":
                    return await self._handle_quick_check(arguments)
                elif name == "get_confidence_score":
                    return await self._handle_get_confidence_score(arguments)
                elif name == "batch_validate":
                    return await self._handle_batch_validate(arguments)
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Unknown tool: {name}")],
                        isError=True
                    )
            except Exception as e:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")],
                    isError=True
                )
    
    async def _handle_validate_output(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle validate_output tool call."""
        output = arguments.get("output", "")
        context = arguments.get("context")
        validation_type = arguments.get("validation_type", "comprehensive")
        
        if not output:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: No output provided")],
                isError=True
            )
        
        result = self.validator.validate_output(output, context, validation_type)
        
        # Format result for display
        result_text = self._format_validation_result(result)
        
        return CallToolResult(
            content=[TextContent(type="text", text=result_text)]
        )
    
    async def _handle_quick_check(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle quick_check tool call."""
        output = arguments.get("output", "")
        
        if not output:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: No output provided")],
                isError=True
            )
        
        is_valid = self.validator.quick_check(output)
        result_text = f"Quick validation result: {'✅ Valid' if is_valid else '❌ Invalid'}"
        
        return CallToolResult(
            content=[TextContent(type="text", text=result_text)]
        )
    
    async def _handle_get_confidence_score(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle get_confidence_score tool call."""
        output = arguments.get("output", "")
        
        if not output:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: No output provided")],
                isError=True
            )
        
        score = self.validator.get_confidence_score(output)
        result_text = f"Confidence score: {score:.2f} ({self._get_confidence_level(score)})"
        
        return CallToolResult(
            content=[TextContent(type="text", text=result_text)]
        )
    
    async def _handle_batch_validate(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle batch_validate tool call."""
        outputs = arguments.get("outputs", [])
        validation_type = arguments.get("validation_type", "comprehensive")
        
        if not outputs:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: No outputs provided")],
                isError=True
            )
        
        results = self.validator.batch_validate(outputs, validation_type)
        
        # Format batch results
        result_text = "🔬 Batch Validation Results\n"
        result_text += "=" * 40 + "\n\n"
        
        for i, result in enumerate(results, 1):
            result_text += f"📝 Output {i}:\n"
            result_text += f"  ✅ Valid: {'Yes' if result.is_valid else 'No'}\n"
            result_text += f"  🎯 Confidence: {result.confidence.value.upper()}\n"
            result_text += f"  📊 Score: {result.score:.2f}\n"
            if result.warnings:
                result_text += f"  ⚠️  Warnings: {len(result.warnings)}\n"
            result_text += "\n"
        
        return CallToolResult(
            content=[TextContent(type="text", text=result_text)]
        )
    
    def _format_validation_result(self, result: ValidationResult) -> str:
        """Format validation result for display."""
        text = "🔬 Lithium-Validation Results\n"
        text += "=" * 40 + "\n"
        text += f"✅ Valid: {'Yes' if result.is_valid else 'No'}\n"
        text += f"🎯 Confidence: {result.confidence.value.upper()}\n"
        text += f"📊 Score: {result.score:.2f}\n"
        text += f"⏰ Timestamp: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        if result.details:
            text += "\n📈 Detailed Analysis:\n"
            for category, details in result.details.items():
                text += f"  • {category.replace('_', ' ').title()}: {details['score']:.2f}\n"
        
        if result.warnings:
            text += f"\n⚠️  Warnings ({len(result.warnings)}):\n"
            for i, warning in enumerate(result.warnings, 1):
                text += f"  {i}. {warning}\n"
        else:
            text += "\n✅ No warnings found\n"
        
        return text
    
    def _get_confidence_level(self, score: float) -> str:
        """Get confidence level string from score."""
        if score >= 0.9:
            return "HIGH"
        elif score >= 0.7:
            return "MEDIUM"
        elif score >= 0.5:
            return "LOW"
        else:
            return "INSUFFICIENT"
    
    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="lithium-validation",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities={}
                    )
                )
            )


def main():
    """Main entry point for MCP server."""
    server = LithiumMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
