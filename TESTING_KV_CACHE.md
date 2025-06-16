# KV Cache Optimization System - Testing Guide

## Overview

This guide provides comprehensive testing procedures for the ConPort MCP Server's KV cache optimization system designed for Ollama integration. The system includes content identification, stable context assembly, cache state management, and performance monitoring.

## Prerequisites

### System Requirements
- Python 3.8+
- ConPort MCP Server installed and configured
- SQLite database with KV cache schema enhancements
- Access to test workspace directory

### Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize Test Database**
   ```bash
   # The database will be automatically created with migrations
   # Ensure your test workspace has proper permissions
   ```

3. **Verify KV Cache Schema**
   - Check that `custom_data` table has `metadata` and `cache_score` columns
   - Verify cache hint index exists: `idx_custom_data_cache_hint`

## Testing Framework

### Test Categories

1. **Basic Functionality Tests** - Core tool operations
2. **Integration Tests** - End-to-end workflows with sample data
3. **Performance Tests** - Cache optimization and efficiency
4. **Error Handling Tests** - Edge cases and failure scenarios

## Core KV Cache Tools Testing

### 1. get_cacheable_content

**Purpose**: Identifies content suitable for Ollama KV-cache optimization

**Test Procedure**:
```python
# Basic functionality test
result = await mcp_client.call_tool("get_cacheable_content", {
    "workspace_id": "/path/to/test/workspace",
    "content_threshold": 1500
})

# Validation criteria
assert "cacheable_content" in result
assert "total_estimated_tokens" in result
assert "cache_optimization_score" in result
assert isinstance(result["cacheable_content"], list)
```

**Expected Output Structure**:
```json
{
    "cacheable_content": [
        {
            "source": "product_context",
            "priority": "high",
            "token_estimate": 2500,
            "content": {...}
        }
    ],
    "total_estimated_tokens": 5000,
    "cache_optimization_score": 85.5
}
```

**Validation Criteria**:
- Returns content with priority levels (high, medium, low)
- Token estimates are reasonable (> 0)
- Cache score is between 0-100
- High priority items appear first

### 2. build_stable_context_prefix

**Purpose**: Build consistent, cacheable context prefix for Ollama KV-cache

**Test Procedure**:
```python
result = await mcp_client.call_tool("build_stable_context_prefix", {
    "workspace_id": "/path/to/test/workspace",
    "format_type": "ollama_optimized"
})

# Validation
assert "stable_prefix" in result
assert "prefix_hash" in result
assert "total_tokens" in result
assert len(result["prefix_hash"]) == 32  # MD5 hash
```

**Expected Output Structure**:
```json
{
    "stable_prefix": "=== PROJECT CONTEXT ===\n...",
    "prefix_hash": "abc123def456...",
    "total_tokens": 3200,
    "sections": [...],
    "format_version": "1.0",
    "generated_at": "2025-01-16T18:52:00Z"
}
```

**Validation Criteria**:
- Stable prefix is consistently formatted
- Hash changes when content changes
- Token count is accurate
- Sections are properly ordered by priority

### 3. get_cache_state

**Purpose**: Check if stable context cache needs refresh

**Test Procedure**:
```python
# First, get current state
current_state = await mcp_client.call_tool("build_stable_context_prefix", {
    "workspace_id": "/path/to/test/workspace"
})

# Then check cache state
result = await mcp_client.call_tool("get_cache_state", {
    "workspace_id": "/path/to/test/workspace",
    "current_prefix_hash": current_state["prefix_hash"]
})

# Validation
assert result["cache_valid"] == True
assert result["recommendation"] == "reuse"
```

**Expected Output Structure**:
```json
{
    "cache_valid": true,
    "current_hash": "abc123...",
    "provided_hash": "abc123...",
    "changes_detected": [],
    "recommendation": "reuse",
    "stable_content_size": 3200
}
```

### 4. get_dynamic_context

**Purpose**: Get query-specific context to append after stable prefix

**Test Procedure**:
```python
result = await mcp_client.call_tool("get_dynamic_context", {
    "workspace_id": "/path/to/test/workspace",
    "query_intent": "decision making process",
    "context_budget": 2000
})

# Validation
assert "dynamic_context" in result
assert "total_tokens" in result
assert result["total_tokens"] <= 2000  # Respects budget
```

### 5. log_custom_data_with_cache_hint

**Purpose**: Enhanced custom data logging with cache optimization

**Test Procedure**:
```python
result = await mcp_client.call_tool("log_custom_data_with_cache_hint", {
    "workspace_id": "/path/to/test/workspace",
    "category": "Architecture",
    "key": "database_schema",
    "value": {"tables": ["users", "products"], "relationships": "..."},
    "cache_hint": True
})

# Validation
assert "cache_score" in result
assert result["cache_score"] > 0
```

### 6. initialize_ollama_session

**Purpose**: Initialize ConPort session optimized for Ollama KV-cache

**Test Procedure**:
```python
result = await mcp_client.call_tool("initialize_ollama_session", {
    "workspace_id": "/path/to/test/workspace"
})

# Validation
assert result["session_initialized"] == True
assert "session_id" in result
assert "stable_context_ready" == True
assert len(result["recommendations"]) > 0
```

### 7. get_cache_performance

**Purpose**: Monitor Ollama cache optimization performance

**Test Procedure**:
```python
result = await mcp_client.call_tool("get_cache_performance", {
    "workspace_id": "/path/to/test/workspace",
    "session_id": "optional-session-id"
})

# Validation
assert "hit_rate" in result
assert 0 <= result["hit_rate"] <= 1
assert "recommendations" in result
```

## Integration Testing Scenarios

### Scenario 1: Complete KV Cache Workflow

1. Initialize session
2. Build stable context
3. Check cache state
4. Get dynamic context for specific query
5. Monitor performance

### Scenario 2: Cache Invalidation Testing

1. Build initial stable context
2. Modify product context
3. Check cache state (should be invalid)
4. Rebuild stable context
5. Verify new hash

### Scenario 3: Content Threshold Testing

1. Add small content (< 1500 chars)
2. Add large content (> 1500 chars)
3. Run get_cacheable_content
4. Verify only large content is included

## Performance Testing

### Cache Efficiency Metrics

- **Cache Hit Rate**: Should be > 70% for optimal performance
- **Context Assembly Time**: Should be < 100ms for stable context
- **Token Efficiency**: Stable context should be 60-80% of total context

### Load Testing

1. **Concurrent Sessions**: Test multiple simultaneous sessions
2. **Large Content**: Test with content > 10,000 tokens
3. **Frequent Updates**: Test cache invalidation under frequent changes

## Error Handling Tests

### Invalid Input Tests

```python
# Test invalid workspace_id
try:
    result = await mcp_client.call_tool("get_cacheable_content", {
        "workspace_id": "/nonexistent/path"
    })
    assert False, "Should have raised error"
except Exception as e:
    assert "workspace" in str(e).lower()
```

### Database Error Tests

1. Test with corrupted database
2. Test with missing tables
3. Test with invalid JSON in custom_data

### Memory Limit Tests

1. Test with extremely large content
2. Test memory usage during cache operations
3. Test cleanup after operations

## Troubleshooting Common Issues

### Issue: Cache Always Invalid

**Symptoms**: `get_cache_state` always returns `cache_valid: false`

**Diagnosis**:
1. Check if content is being modified between calls
2. Verify hash calculation consistency
3. Check timestamp precision issues

**Solution**:
```python
# Debug hash generation
result1 = await build_stable_context_prefix(workspace_id)
result2 = await build_stable_context_prefix(workspace_id)
assert result1["prefix_hash"] == result2["prefix_hash"]
```

### Issue: Low Cache Scores

**Symptoms**: `cache_score` values consistently low (< 20)

**Diagnosis**:
1. Check content size calculation
2. Verify category/key patterns
3. Review scoring algorithm

**Solution**:
- Use high-value categories: "Architecture", "Requirements", "Specifications"
- Include keywords: "config", "schema", "template", "pattern"

### Issue: Performance Degradation

**Symptoms**: Slow response times for cache operations

**Diagnosis**:
1. Check database query performance
2. Monitor memory usage
3. Verify index usage

**Solution**:
```sql
-- Verify cache hint index
EXPLAIN QUERY PLAN 
SELECT * FROM custom_data 
WHERE JSON_EXTRACT(metadata, '$.cache_hint') = true;
```

### Issue: Session Initialization Fails

**Symptoms**: `initialize_ollama_session` returns errors

**Diagnosis**:
1. Check workspace permissions
2. Verify database connectivity
3. Check for missing dependencies

## Test Data Requirements

### Minimum Test Dataset

1. **Product Context**: Complete project information (> 2000 chars)
2. **System Patterns**: 3-5 architectural patterns
3. **Custom Data**: Mix of cacheable and non-cacheable entries
4. **Decisions**: 5-10 recent decisions
5. **Progress Entries**: Various status types

### Sample Test Data Structure

```json
{
    "product_context": {
        "name": "Test Project",
        "description": "Comprehensive test project for KV cache validation",
        "goals": ["Performance", "Reliability", "Scalability"],
        "architecture": "Microservices with event-driven communication"
    },
    "system_patterns": [
        {
            "name": "Repository Pattern",
            "description": "Data access abstraction layer...",
            "tags": ["data-access", "architecture"]
        }
    ]
}
```

## Automated Testing

### Continuous Integration

```yaml
# .github/workflows/kv-cache-tests.yml
name: KV Cache Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run KV Cache Tests
        run: python -m pytest tests/test_kv_cache_*.py -v
```

### Test Coverage Goals

- **Unit Tests**: 90%+ coverage for KV cache handlers
- **Integration Tests**: All major workflows covered
- **Performance Tests**: Baseline metrics established
- **Error Handling**: All error paths tested

## Validation Checklist

### Pre-Testing
- [ ] Database schema includes KV cache enhancements
- [ ] Test workspace has sample data
- [ ] All dependencies installed
- [ ] MCP server running

### During Testing
- [ ] All basic functionality tests pass
- [ ] Integration scenarios complete successfully
- [ ] Performance metrics within acceptable ranges
- [ ] Error handling behaves correctly

### Post-Testing
- [ ] Test results documented
- [ ] Performance baselines recorded
- [ ] Issues logged and prioritized
- [ ] Cleanup completed

## Performance Baselines

### Expected Metrics

| Operation | Target Time | Acceptable Range |
|-----------|-------------|------------------|
| get_cacheable_content | < 50ms | 10-100ms |
| build_stable_context_prefix | < 100ms | 50-200ms |
| get_cache_state | < 20ms | 5-50ms |
| get_dynamic_context | < 75ms | 25-150ms |

### Memory Usage

| Operation | Expected Memory | Max Acceptable |
|-----------|----------------|----------------|
| Stable Context | < 10MB | 25MB |
| Dynamic Context | < 5MB | 15MB |
| Cache State Check | < 1MB | 5MB |

This comprehensive testing guide ensures thorough validation of the KV cache optimization system across all functional and performance requirements.