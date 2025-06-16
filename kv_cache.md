# ConPort MCP Server - Ollama KV-Cache Implementation Strategy

## Overview
This document outlines how to enhance the ConPort MCP server to optimize for Ollama's KV-cache, providing faster responses and energy efficiency for local LLM usage.

## Core Implementation Areas

### 1. Enhanced Content Identification API

**New MCP Tool: `get_cacheable_content`**
```python
@server.call_tool()
async def get_cacheable_content(workspace_id: str, content_threshold: int = 1500):
    """Identify ConPort content suitable for Ollama KV-cache optimization"""
    
    cacheable_items = []
    
    # High priority: Product context
    product_ctx = await get_product_context_data(workspace_id)
    if product_ctx and len(json.dumps(product_ctx)) > content_threshold:
        cacheable_items.append({
            "type": "product_context",
            "content": product_ctx,
            "priority": "high",
            "estimated_tokens": estimate_tokens(product_ctx),
            "last_modified": product_ctx.get("updated_at")
        })
    
    # Medium priority: Substantial system patterns
    patterns = await get_system_patterns_data(workspace_id)
    for pattern in patterns:
        if len(pattern.get('description', '')) > 500:
            cacheable_items.append({
                "type": "system_pattern",
                "content": pattern,
                "priority": "medium",
                "estimated_tokens": estimate_tokens(pattern),
                "pattern_id": pattern.get("id")
            })
    
    # Check for explicit cache hints in custom data
    cache_hinted_data = await get_custom_data_with_cache_hints(workspace_id)
    for item in cache_hinted_data:
        cacheable_items.append({
            "type": "custom_data",
            "content": item,
            "priority": "high",
            "estimated_tokens": estimate_tokens(item),
            "category": item.get("category"),
            "key": item.get("key")
        })
    
    return {
        "cacheable_content": cacheable_items,
        "total_estimated_tokens": sum(item["estimated_tokens"] for item in cacheable_items),
        "cache_optimization_score": calculate_cache_score(cacheable_items)
    }
```

**Supporting Database Query:**
```python
async def get_custom_data_with_cache_hints(workspace_id: str):
    """Query custom data with cache_hint metadata"""
    query = """
    SELECT category, key, value, metadata
    FROM custom_data 
    WHERE workspace_id = ? 
    AND JSON_EXTRACT(metadata, '$.cache_hint') = true
    """
    # Implementation for SQLite JSON queries
```

### 2. Stable Context Assembly Service

**New MCP Tool: `build_stable_context_prefix`**
```python
@server.call_tool()
async def build_stable_context_prefix(workspace_id: str, format_type: str = "ollama_optimized"):
    """Build consistent, cacheable context prefix for Ollama KV-cache"""
    
    stable_context_parts = []
    
    # 1. Product Context (highest priority)
    product_ctx = await get_product_context_data(workspace_id)
    if product_ctx:
        formatted_product = format_product_context_for_cache(product_ctx)
        stable_context_parts.append({
            "section": "project_context",
            "content": formatted_product,
            "tokens": estimate_tokens(formatted_product),
            "last_modified": product_ctx.get("updated_at")
        })
    
    # 2. System Patterns (architectural stability)
    patterns = await get_system_patterns_data(workspace_id, limit=3)
    if patterns:
        formatted_patterns = format_patterns_for_cache(patterns)
        stable_context_parts.append({
            "section": "system_patterns", 
            "content": formatted_patterns,
            "tokens": estimate_tokens(formatted_patterns),
            "pattern_count": len(patterns)
        })
    
    # 3. Critical Custom Data
    critical_data = await get_custom_data_with_cache_hints(workspace_id)
    if critical_data:
        formatted_critical = format_critical_data_for_cache(critical_data)
        stable_context_parts.append({
            "section": "critical_specs",
            "content": formatted_critical,
            "tokens": estimate_tokens(formatted_critical),
            "item_count": len(critical_data)
        })
    
    # Assemble final prefix
    stable_prefix = assemble_stable_prefix(stable_context_parts, format_type)
    prefix_hash = hashlib.md5(stable_prefix.encode()).hexdigest()
    
    return {
        "stable_prefix": stable_prefix,
        "prefix_hash": prefix_hash,
        "total_tokens": sum(part["tokens"] for part in stable_context_parts),
        "sections": stable_context_parts,
        "format_version": "1.0",
        "generated_at": datetime.utcnow().isoformat()
    }
```

**Content Formatters:**
```python
def format_product_context_for_cache(context: dict) -> str:
    """Format product context for consistent Ollama caching"""
    return f"""=== PROJECT CONTEXT ===
PROJECT: {context.get('name', 'Current Project')}
DESCRIPTION: {context.get('description', '')}
GOALS: {context.get('goals', '')}
ARCHITECTURE: {context.get('architecture', '')}
TECHNOLOGIES: {context.get('technologies', '')}
"""

def format_patterns_for_cache(patterns: List[dict]) -> str:
    """Format system patterns for consistent caching"""
    formatted = ["=== SYSTEM PATTERNS ==="]
    for pattern in patterns:
        formatted.append(f"PATTERN: {pattern['name']}")
        formatted.append(f"DESCRIPTION: {pattern['description']}")
        if pattern.get('tags'):
            formatted.append(f"TAGS: {', '.join(pattern['tags'])}")
        formatted.append("")  # Blank line separator
    return "\n".join(formatted)
```

### 3. Cache State Management

**New MCP Tool: `get_cache_state`**
```python
@server.call_tool()
async def get_cache_state(workspace_id: str, current_prefix_hash: str = None):
    """Check if stable context cache needs refresh"""
    
    # Get current state hash
    current_state = await build_stable_context_prefix(workspace_id)
    current_hash = current_state["prefix_hash"]
    
    # Compare with provided hash
    cache_valid = current_prefix_hash == current_hash if current_prefix_hash else False
    
    # Identify what changed if cache invalid
    changes = []
    if not cache_valid and current_prefix_hash:
        changes = await identify_context_changes(workspace_id, current_prefix_hash)
    
    return {
        "cache_valid": cache_valid,
        "current_hash": current_hash,
        "provided_hash": current_prefix_hash,
        "changes_detected": changes,
        "recommendation": "refresh" if not cache_valid else "reuse",
        "stable_content_size": current_state["total_tokens"]
    }
```

**Change Detection:**
```python
async def identify_context_changes(workspace_id: str, previous_hash: str):
    """Identify what content changed to trigger cache refresh"""
    changes = []
    
    # Check product context modification time
    product_modified = await get_last_modified_time("product_context", workspace_id)
    if product_modified > get_hash_timestamp(previous_hash):
        changes.append({"type": "product_context", "last_modified": product_modified})
    
    # Check system patterns
    patterns_modified = await get_last_modified_time("system_patterns", workspace_id)
    if patterns_modified > get_hash_timestamp(previous_hash):
        changes.append({"type": "system_patterns", "last_modified": patterns_modified})
    
    # Check critical custom data
    critical_modified = await get_last_modified_time("custom_data_cached", workspace_id)
    if critical_modified > get_hash_timestamp(previous_hash):
        changes.append({"type": "critical_custom_data", "last_modified": critical_modified})
    
    return changes
```

### 4. Query-Specific Context Assembly

**Enhanced MCP Tool: `get_dynamic_context`**
```python
@server.call_tool()
async def get_dynamic_context(workspace_id: str, query_intent: str, context_budget: int = 2000):
    """Get query-specific context to append after stable prefix"""
    
    dynamic_parts = []
    remaining_budget = context_budget
    
    # Always include active context (session-level)
    active_ctx = await get_active_context_data(workspace_id)
    if active_ctx and remaining_budget > 0:
        formatted_active = format_active_context(active_ctx)
        tokens_used = estimate_tokens(formatted_active)
        if tokens_used <= remaining_budget:
            dynamic_parts.append({
                "section": "active_context",
                "content": formatted_active,
                "tokens": tokens_used
            })
            remaining_budget -= tokens_used
    
    # Query-specific context based on intent
    if "decision" in query_intent.lower() and remaining_budget > 0:
        recent_decisions = await get_decisions_data(workspace_id, limit=3)
        if recent_decisions:
            formatted_decisions = format_decisions_for_context(recent_decisions)
            tokens_used = estimate_tokens(formatted_decisions)
            if tokens_used <= remaining_budget:
                dynamic_parts.append({
                    "section": "recent_decisions",
                    "content": formatted_decisions,
                    "tokens": tokens_used
                })
                remaining_budget -= tokens_used
    
    if any(word in query_intent.lower() for word in ["task", "progress", "todo"]) and remaining_budget > 0:
        current_progress = await get_progress_data(workspace_id, status_filter="IN_PROGRESS", limit=5)
        if current_progress:
            formatted_progress = format_progress_for_context(current_progress)
            tokens_used = estimate_tokens(formatted_progress)
            if tokens_used <= remaining_budget:
                dynamic_parts.append({
                    "section": "current_progress",
                    "content": formatted_progress,
                    "tokens": tokens_used
                })
    
    return {
        "dynamic_context": "\n".join(part["content"] for part in dynamic_parts),
        "sections": dynamic_parts,
        "total_tokens": sum(part["tokens"] for part in dynamic_parts),
        "budget_used": context_budget - remaining_budget,
        "budget_remaining": remaining_budget
    }
```

### 5. Enhanced Custom Data with Cache Hints

**Database Schema Enhancement:**
```sql
-- Add index for cache hint queries
CREATE INDEX IF NOT EXISTS idx_custom_data_cache_hint 
ON custom_data (workspace_id, JSON_EXTRACT(metadata, '$.cache_hint'));

-- Migration for existing data
ALTER TABLE custom_data ADD COLUMN cache_score INTEGER DEFAULT 0;
```

**Enhanced MCP Tool: `log_custom_data_with_cache_hint`**
```python
@server.call_tool()
async def log_custom_data_with_cache_hint(
    workspace_id: str, 
    category: str, 
    key: str, 
    value: Any,
    suggest_caching: bool = None,
    cache_hint: bool = None
):
    """Enhanced custom data logging with cache optimization suggestions"""
    
    # Auto-suggest caching for large content
    content_size = len(json.dumps(value))
    auto_suggest_cache = content_size > 1500 and suggest_caching is None
    
    metadata = {}
    if cache_hint is not None:
        metadata["cache_hint"] = cache_hint
    elif auto_suggest_cache:
        metadata["cache_suggestion"] = True
        metadata["content_size"] = content_size
    
    # Calculate cache score
    cache_score = calculate_content_cache_score(value, category, key)
    
    result = await standard_log_custom_data(workspace_id, category, key, value, metadata)
    
    # Return suggestion if applicable
    if auto_suggest_cache and cache_hint is None:
        result["cache_suggestion"] = {
            "recommended": True,
            "reason": f"Large content ({content_size} chars) suitable for caching",
            "estimated_tokens": estimate_tokens(value),
            "cache_score": cache_score
        }
    
    return result
```

### 6. Session Management Integration

**New MCP Tool: `initialize_ollama_session`**
```python
@server.call_tool()
async def initialize_ollama_session(workspace_id: str):
    """Initialize ConPort session optimized for Ollama KV-cache"""
    
    session_data = {
        "workspace_id": workspace_id,
        "session_id": generate_session_id(),
        "started_at": datetime.utcnow().isoformat(),
        "cache_optimization": True
    }
    
    # Build initial stable context
    stable_context = await build_stable_context_prefix(workspace_id)
    session_data["stable_context"] = stable_context
    
    # Get initial activity summary
    activity = await get_recent_activity_summary_data(workspace_id, hours_ago=24, limit_per_type=3)
    session_data["initial_activity"] = activity
    
    # Store session state (optional - could be client-side)
    await store_session_state(session_data)
    
    return {
        "session_initialized": True,
        "session_id": session_data["session_id"],
        "stable_context_ready": True,
        "stable_context_hash": stable_context["prefix_hash"],
        "stable_context_tokens": stable_context["total_tokens"],
        "cache_optimization_enabled": True,
        "recommendations": [
            "Use consistent prompt structure for optimal caching",
            "Stable context will be cached after first query",
            "Update stable context only when core project info changes"
        ]
    }
```

## Implementation Priority

1. **Phase 1:** Content identification and stable context assembly
2. **Phase 2:** Cache state management and change detection  
3. **Phase 3:** Enhanced session management and query optimization
4. **Phase 4:** Performance monitoring and auto-tuning

## Configuration Options

**New config section for `context_portal_mcp`:**
```yaml
ollama_optimization:
  enabled: true
  stable_context_max_tokens: 4000
  cache_hint_threshold: 1500
  auto_suggest_caching: true
  format_version: "1.0"
```

## Performance Monitoring

**New MCP Tool: `get_cache_performance`**
```python
@server.call_tool()
async def get_cache_performance(workspace_id: str, session_id: str = None):
    """Monitor Ollama cache optimization performance"""
    
    # This would track metrics like:
    # - Cache hit rates
    # - Context assembly times
    # - Stable context refresh frequency
    # - Token efficiency improvements
    
    return {
        "cache_hits": 15,
        "cache_misses": 3,
        "hit_rate": 0.83,
        "average_stable_tokens": 3200,
        "context_assembly_time_ms": 45,
        "recommendations": []
    }
```

This implementation strategy provides the foundation for optimizing ConPort MCP server for Ollama's KV-cache while maintaining compatibility with existing workflows.