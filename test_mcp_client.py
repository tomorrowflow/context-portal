"""
MCP client test script for KV cache optimization system.
Demonstrates how to call KV cache tools via MCP and integrate with Ollama.
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from context_portal_mcp.handlers import mcp_handlers
from context_portal_mcp.db import models


class MCPKVCacheClient:
    """MCP client for testing KV cache optimization workflows"""
    
    def __init__(self, workspace_id: str):
        self.workspace_id = workspace_id
        self.session_id = None
        self.stable_context_hash = None
        
    async def initialize_session(self) -> Dict[str, Any]:
        """Initialize Ollama-optimized session"""
        
        print("🚀 Initializing Ollama session...")
        
        args = models.InitializeOllamaSessionArgs(workspace_id=self.workspace_id)
        result = mcp_handlers.handle_initialize_ollama_session(args)
        
        self.session_id = result["session_id"]
        self.stable_context_hash = result["stable_context_hash"]
        
        print(f"✓ Session initialized: {self.session_id}")
        print(f"✓ Stable context ready: {result['stable_context_tokens']} tokens")
        print(f"✓ Cache optimization enabled: {result['cache_optimization_enabled']}")
        
        return result
    
    async def get_cacheable_content(self, threshold: int = 1500) -> List[Dict[str, Any]]:
        """Get content suitable for caching"""
        
        print(f"📋 Getting cacheable content (threshold: {threshold} chars)...")
        
        args = models.GetCacheableContentArgs(
            workspace_id=self.workspace_id,
            content_threshold=threshold
        )
        result = mcp_handlers.handle_get_cacheable_content(args)
        
        print(f"✓ Found {len(result)} cacheable items")
        
        # Display summary
        for item in result[:3]:  # Show first 3 items
            print(f"  - {item['source']}: {item['priority']} priority, ~{item['token_estimate']} tokens")
        
        if len(result) > 3:
            print(f"  ... and {len(result) - 3} more items")
        
        return result
    
    async def build_stable_context(self, format_type: str = "ollama_optimized") -> Dict[str, Any]:
        """Build stable context prefix for caching"""
        
        print(f"🏗️  Building stable context prefix ({format_type})...")
        
        args = models.BuildStableContextPrefixArgs(
            workspace_id=self.workspace_id,
            format_type=format_type
        )
        result = mcp_handlers.handle_build_stable_context_prefix(args)
        
        self.stable_context_hash = result["prefix_hash"]
        
        print(f"✓ Stable context built: {result['total_tokens']} tokens")
        print(f"✓ Context hash: {result['prefix_hash'][:16]}...")
        print(f"✓ Sections included: {len(result['sections'])}")
        
        return result
    
    async def check_cache_state(self) -> Dict[str, Any]:
        """Check if cache needs refresh"""
        
        print("🔍 Checking cache state...")
        
        args = models.GetCacheStateArgs(
            workspace_id=self.workspace_id,
            current_prefix_hash=self.stable_context_hash
        )
        result = mcp_handlers.handle_get_cache_state(args)
        
        status = "✓ VALID" if result["cache_valid"] else "⚠️  INVALID"
        print(f"{status} Cache state: {result['recommendation']}")
        
        if result["changes_detected"]:
            print("  Changes detected:")
            for change in result["changes_detected"]:
                print(f"    - {change['type']}: {change.get('last_modified', 'unknown')}")
        
        return result
    
    async def get_dynamic_context(self, query_intent: str, budget: int = 2000) -> Dict[str, Any]:
        """Get query-specific dynamic context"""
        
        print(f"🎯 Getting dynamic context for: '{query_intent}' (budget: {budget} tokens)...")
        
        args = models.GetDynamicContextArgs(
            workspace_id=self.workspace_id,
            query_intent=query_intent,
            context_budget=budget
        )
        result = mcp_handlers.handle_get_dynamic_context(args)
        
        print(f"✓ Dynamic context assembled: {result['total_tokens']} tokens used")
        print(f"✓ Budget remaining: {result['budget_remaining']} tokens")
        print(f"✓ Sections included: {len(result['sections'])}")
        
        return result
    
    async def monitor_performance(self) -> Dict[str, Any]:
        """Monitor cache performance metrics"""
        
        print("📊 Monitoring cache performance...")
        
        args = models.GetCachePerformanceArgs(
            workspace_id=self.workspace_id,
            session_id=self.session_id
        )
        result = mcp_handlers.handle_get_cache_performance(args)
        
        print(f"✓ Cache hit rate: {result['hit_rate']:.1%}")
        print(f"✓ Average stable tokens: {result['average_stable_tokens']}")
        print(f"✓ Assembly time: {result['context_assembly_time_ms']}ms")
        
        if result["recommendations"]:
            print("💡 Recommendations:")
            for rec in result["recommendations"]:
                print(f"  - {rec}")
        
        return result
    
    async def simulate_ollama_workflow(self, query: str) -> Dict[str, Any]:
        """Simulate complete Ollama integration workflow"""
        
        print(f"\n🤖 Simulating Ollama workflow for query: '{query}'")
        print("=" * 60)
        
        # Step 1: Check cache state
        cache_state = await self.check_cache_state()
        
        # Step 2: Build or reuse stable context
        if not cache_state["cache_valid"]:
            print("🔄 Cache invalid, rebuilding stable context...")
            stable_context = await self.build_stable_context()
        else:
            print("✅ Using cached stable context")
            stable_context = {"prefix_hash": self.stable_context_hash}
        
        # Step 3: Get dynamic context for the query
        dynamic_context = await self.get_dynamic_context(query)
        
        # Step 4: Assemble final context for Ollama
        final_context = self.assemble_ollama_context(stable_context, dynamic_context)
        
        # Step 5: Monitor performance
        performance = await self.monitor_performance()
        
        return {
            "cache_state": cache_state,
            "stable_context": stable_context,
            "dynamic_context": dynamic_context,
            "final_context": final_context,
            "performance": performance
        }
    
    def assemble_ollama_context(self, stable_context: Dict[str, Any], 
                              dynamic_context: Dict[str, Any]) -> Dict[str, Any]:
        """Assemble final context for Ollama"""
        
        print("🔧 Assembling final context for Ollama...")
        
        # In a real implementation, this would format the context
        # according to Ollama's requirements
        final_context = {
            "stable_prefix": stable_context.get("stable_prefix", ""),
            "dynamic_content": dynamic_context.get("dynamic_context", ""),
            "total_tokens": (
                stable_context.get("total_tokens", 0) + 
                dynamic_context.get("total_tokens", 0)
            ),
            "cache_optimized": True,
            "assembly_metadata": {
                "stable_hash": stable_context.get("prefix_hash"),
                "dynamic_sections": len(dynamic_context.get("sections", [])),
                "timestamp": "2025-01-16T19:04:00Z"
            }
        }
        
        print(f"✓ Final context assembled: {final_context['total_tokens']} total tokens")
        
        return final_context


async def demonstrate_kv_cache_workflow():
    """Demonstrate complete KV cache workflow"""
    
    print("🎯 KV Cache Optimization System - MCP Client Demo")
    print("=" * 60)
    
    # Setup workspace (you can change this path)
    workspace_id = "/tmp/kv_cache_demo_workspace"
    workspace_path = Path(workspace_id)
    workspace_path.mkdir(exist_ok=True)
    
    # Initialize client
    client = MCPKVCacheClient(workspace_id)
    
    try:
        # Step 1: Initialize session
        session_result = await client.initialize_session()
        
        print("\n" + "=" * 60)
        
        # Step 2: Analyze cacheable content
        cacheable_content = await client.get_cacheable_content()
        
        print("\n" + "=" * 60)
        
        # Step 3: Build stable context
        stable_context = await client.build_stable_context()
        
        print("\n" + "=" * 60)
        
        # Step 4: Simulate different query scenarios
        query_scenarios = [
            "Help me optimize database performance",
            "What are the current architectural decisions?",
            "Show me the progress on current tasks",
            "Explain the security requirements"
        ]
        
        for i, query in enumerate(query_scenarios, 1):
            print(f"\n📝 Scenario {i}: {query}")
            print("-" * 40)
            
            workflow_result = await client.simulate_ollama_workflow(query)
            
            # Show key metrics
            print(f"Cache efficiency: {workflow_result['performance']['hit_rate']:.1%}")
            print(f"Total context tokens: {workflow_result['final_context']['total_tokens']}")
            
        print("\n" + "=" * 60)
        print("✅ Demo completed successfully!")
        
        # Summary
        print("\n📊 Summary:")
        print(f"  - Session ID: {client.session_id}")
        print(f"  - Stable context hash: {client.stable_context_hash[:16] if client.stable_context_hash else 'None'}...")
        print(f"  - Cacheable items found: {len(cacheable_content)}")
        print(f"  - Query scenarios tested: {len(query_scenarios)}")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


async def test_individual_tools():
    """Test individual KV cache tools"""
    
    print("🔧 Testing Individual KV Cache Tools")
    print("=" * 60)
    
    workspace_id = "/tmp/kv_cache_test_workspace"
    workspace_path = Path(workspace_id)
    workspace_path.mkdir(exist_ok=True)
    
    # Test each tool individually
    tools_to_test = [
        ("get_cacheable_content", models.GetCacheableContentArgs(workspace_id=workspace_id)),
        ("build_stable_context_prefix", models.BuildStableContextPrefixArgs(workspace_id=workspace_id)),
        ("get_cache_state", models.GetCacheStateArgs(workspace_id=workspace_id, current_prefix_hash=None)),
        ("get_dynamic_context", models.GetDynamicContextArgs(
            workspace_id=workspace_id, 
            query_intent="test query"
        )),
        ("initialize_ollama_session", models.InitializeOllamaSessionArgs(workspace_id=workspace_id)),
        ("get_cache_performance", models.GetCachePerformanceArgs(workspace_id=workspace_id, session_id=None))
    ]
    
    results = {}
    
    for tool_name, args in tools_to_test:
        print(f"\n🔍 Testing {tool_name}...")
        
        try:
            handler = getattr(mcp_handlers, f"handle_{tool_name}")
            result = handler(args)
            
            # Show key information about the result
            if isinstance(result, dict):
                key_info = []
                for key in ["total_tokens", "cache_valid", "session_id", "hit_rate"]:
                    if key in result:
                        key_info.append(f"{key}: {result[key]}")
                
                if key_info:
                    print(f"  ✓ Result: {', '.join(key_info)}")
                else:
                    print(f"  ✓ Result: {len(str(result))} chars")
            elif isinstance(result, list):
                print(f"  ✓ Result: {len(result)} items")
            else:
                print(f"  ✓ Result: {type(result).__name__}")
            
            results[tool_name] = result
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results[tool_name] = None
    
    print(f"\n✅ Tool testing completed. {len([r for r in results.values() if r is not None])}/{len(tools_to_test)} tools successful.")
    
    return results


def main():
    """Main function"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Test KV cache optimization via MCP")
    parser.add_argument(
        "--mode",
        choices=["demo", "test", "both"],
        default="demo",
        help="Mode to run: demo (full workflow), test (individual tools), or both"
    )
    parser.add_argument(
        "--workspace",
        default="/tmp/kv_cache_demo",
        help="Workspace directory path"
    )
    
    args = parser.parse_args()
    
    if args.mode in ["demo", "both"]:
        print("Running KV cache workflow demo...")
        asyncio.run(demonstrate_kv_cache_workflow())
    
    if args.mode in ["test", "both"]:
        if args.mode == "both":
            print("\n" + "=" * 80 + "\n")
        
        print("Running individual tool tests...")
        asyncio.run(test_individual_tools())


if __name__ == "__main__":
    main()