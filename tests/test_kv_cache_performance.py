"""
Performance tests for KV cache optimization system.
Tests cache efficiency, response times, and optimization metrics.
"""

import time
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, List
import statistics

# Import the MCP handlers directly for testing
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from context_portal_mcp.handlers import mcp_handlers
from context_portal_mcp.db import models, database
from context_portal_mcp.core.exceptions import ContextPortalError


class TestKVCachePerformance:
    """Performance tests for KV cache operations"""
    
    def setup_method(self):
        """Setup test workspace for each test method"""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace_path = Path(self.temp_dir) / "performance_test_workspace"
        self.workspace_path.mkdir()
        self.workspace_id = str(self.workspace_path)
        
        # Performance thresholds (in milliseconds)
        self.thresholds = {
            "get_cacheable_content": 100,
            "build_stable_context_prefix": 200,
            "get_cache_state": 50,
            "get_dynamic_context": 150,
            "initialize_ollama_session": 300,
            "get_cache_performance": 30
        }
    
    def teardown_method(self):
        """Cleanup after each test"""
        import shutil
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def setup_performance_test_data(self, size: str = "medium"):
        """Setup test data of different sizes for performance testing"""
        
        if size == "small":
            content_multiplier = 1
            pattern_count = 2
            custom_data_count = 3
        elif size == "medium":
            content_multiplier = 3
            pattern_count = 5
            custom_data_count = 8
        elif size == "large":
            content_multiplier = 10
            pattern_count = 15
            custom_data_count = 25
        else:
            raise ValueError("Size must be 'small', 'medium', or 'large'")
        
        # Product Context
        base_description = "Performance test project with comprehensive documentation and specifications. "
        product_context = {
            "name": f"Performance Test Project - {size.title()}",
            "description": base_description * content_multiplier,
            "goals": [f"Goal {i}: Performance objective {i}" for i in range(content_multiplier * 2)],
            "architecture": f"Microservices architecture with {content_multiplier * 5} services",
            "technologies": ["Python", "FastAPI", "PostgreSQL", "Redis", "Docker"] * content_multiplier,
            "requirements": {
                "performance": f"Sub-{50 + content_multiplier * 10}ms response times",
                "scalability": f"Handle {content_multiplier * 1000} concurrent users",
                "availability": "99.9% uptime"
            }
        }
        
        update_args = models.UpdateContextArgs(
            workspace_id=self.workspace_id,
            content=product_context,
            patch_content=None
        )
        mcp_handlers.handle_update_product_context(update_args)
        
        # System Patterns
        for i in range(pattern_count):
            pattern = {
                "name": f"Pattern {i}: Design Pattern {i}",
                "description": f"Detailed description of design pattern {i}. " * content_multiplier + 
                              f"This pattern addresses architectural concerns and provides solutions for common problems in software design.",
                "tags": [f"pattern-{i}", "architecture", "design", f"category-{i % 3}"]
            }
            
            pattern_args = models.LogSystemPatternArgs(
                workspace_id=self.workspace_id,
                **pattern
            )
            mcp_handlers.handle_log_system_pattern(pattern_args)
        
        # Custom Data with Cache Hints
        for i in range(custom_data_count):
            custom_data = {
                "category": f"Category{i % 5}",
                "key": f"config_item_{i}",
                "value": {
                    "id": i,
                    "name": f"Configuration Item {i}",
                    "description": "Detailed configuration specification. " * content_multiplier,
                    "settings": {
                        f"setting_{j}": f"value_{j}" for j in range(content_multiplier * 3)
                    },
                    "metadata": {
                        "created": "2025-01-16",
                        "version": f"1.{i}",
                        "size": size
                    }
                },
                "suggest_caching": None,
                "cache_hint": True
            }
            
            custom_args = models.LogCustomDataWithCacheHintArgs(
                workspace_id=self.workspace_id,
                **custom_data
            )
            mcp_handlers.handle_log_custom_data_with_cache_hint(custom_args)
    
    def measure_execution_time(self, func, *args, **kwargs):
        """Measure execution time of a function"""
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time_ms = (end_time - start_time) * 1000
        return result, execution_time_ms
    
    def test_get_cacheable_content_performance(self):
        """Test performance of get_cacheable_content operation"""
        
        # Test with different data sizes
        sizes = ["small", "medium", "large"]
        results = {}
        
        for size in sizes:
            # Setup data
            self.setup_performance_test_data(size)
            
            # Measure performance
            args = models.GetCacheableContentArgs(
                workspace_id=self.workspace_id,
                content_threshold=1000
            )
            
            # Run multiple times for average
            times = []
            for _ in range(5):
                _, exec_time = self.measure_execution_time(
                    mcp_handlers.handle_get_cacheable_content, args
                )
                times.append(exec_time)
            
            avg_time = statistics.mean(times)
            results[size] = {
                "avg_time_ms": avg_time,
                "min_time_ms": min(times),
                "max_time_ms": max(times),
                "std_dev": statistics.stdev(times) if len(times) > 1 else 0
            }
            
            # Cleanup for next iteration
            self.teardown_method()
            self.setup_method()
        
        # Validate performance
        for size, metrics in results.items():
            print(f"get_cacheable_content ({size}): {metrics['avg_time_ms']:.2f}ms avg")
            
            # Small and medium should be well under threshold
            if size in ["small", "medium"]:
                assert metrics["avg_time_ms"] < self.thresholds["get_cacheable_content"], \
                    f"get_cacheable_content too slow for {size} data: {metrics['avg_time_ms']:.2f}ms"
        
        # Performance should scale reasonably
        assert results["medium"]["avg_time_ms"] < results["large"]["avg_time_ms"] * 2, \
            "Performance scaling is unreasonable"
    
    def test_build_stable_context_prefix_performance(self):
        """Test performance of build_stable_context_prefix operation"""
        
        self.setup_performance_test_data("medium")
        
        args = models.BuildStableContextPrefixArgs(
            workspace_id=self.workspace_id,
            format_type="ollama_optimized"
        )
        
        # Measure multiple runs
        times = []
        for _ in range(10):
            _, exec_time = self.measure_execution_time(
                mcp_handlers.handle_build_stable_context_prefix, args
            )
            times.append(exec_time)
        
        avg_time = statistics.mean(times)
        print(f"build_stable_context_prefix: {avg_time:.2f}ms avg")
        
        # Should be under threshold
        assert avg_time < self.thresholds["build_stable_context_prefix"], \
            f"build_stable_context_prefix too slow: {avg_time:.2f}ms"
        
        # Consistency check - standard deviation should be reasonable
        std_dev = statistics.stdev(times)
        assert std_dev < avg_time * 0.3, \
            f"Performance too inconsistent: {std_dev:.2f}ms std dev"
    
    def test_get_cache_state_performance(self):
        """Test performance of get_cache_state operation"""
        
        self.setup_performance_test_data("medium")
        
        # First build stable context to get hash
        build_args = models.BuildStableContextPrefixArgs(workspace_id=self.workspace_id)
        stable_result = mcp_handlers.handle_build_stable_context_prefix(build_args)
        
        # Test cache state check
        cache_args = models.GetCacheStateArgs(
            workspace_id=self.workspace_id,
            current_prefix_hash=stable_result["prefix_hash"]
        )
        
        # Measure multiple runs
        times = []
        for _ in range(20):  # More runs since this should be very fast
            _, exec_time = self.measure_execution_time(
                mcp_handlers.handle_get_cache_state, cache_args
            )
            times.append(exec_time)
        
        avg_time = statistics.mean(times)
        print(f"get_cache_state: {avg_time:.2f}ms avg")
        
        # Should be very fast
        assert avg_time < self.thresholds["get_cache_state"], \
            f"get_cache_state too slow: {avg_time:.2f}ms"
    
    def test_get_dynamic_context_performance(self):
        """Test performance of get_dynamic_context with different budgets"""
        
        self.setup_performance_test_data("medium")
        
        # Add active context and decisions for dynamic content
        active_context = {
            "current_focus": "Performance optimization and testing",
            "recent_changes": ["Added caching layer", "Optimized queries"],
            "open_issues": ["Memory usage", "Response times"]
        }
        
        active_args = models.UpdateContextArgs(
            workspace_id=self.workspace_id,
            content=active_context,
            patch_content=None
        )
        mcp_handlers.handle_update_active_context(active_args)
        
        # Test different budget sizes
        budgets = [500, 1000, 2000, 5000]
        results = {}
        
        for budget in budgets:
            args = models.GetDynamicContextArgs(
                workspace_id=self.workspace_id,
                query_intent="performance optimization",
                context_budget=budget
            )
            
            # Measure multiple runs
            times = []
            for _ in range(5):
                _, exec_time = self.measure_execution_time(
                    mcp_handlers.handle_get_dynamic_context, args
                )
                times.append(exec_time)
            
            avg_time = statistics.mean(times)
            results[budget] = avg_time
            print(f"get_dynamic_context (budget {budget}): {avg_time:.2f}ms avg")
            
            # Should be under threshold
            assert avg_time < self.thresholds["get_dynamic_context"], \
                f"get_dynamic_context too slow for budget {budget}: {avg_time:.2f}ms"
        
        # Performance should not degrade significantly with larger budgets
        # (since budget limits the work done)
        max_time = max(results.values())
        min_time = min(results.values())
        assert max_time < min_time * 3, \
            "Performance varies too much across different budgets"
    
    def test_initialize_ollama_session_performance(self):
        """Test performance of session initialization"""
        
        self.setup_performance_test_data("medium")
        
        args = models.InitializeOllamaSessionArgs(workspace_id=self.workspace_id)
        
        # Measure multiple initializations
        times = []
        for _ in range(3):  # Fewer runs since this is more expensive
            _, exec_time = self.measure_execution_time(
                mcp_handlers.handle_initialize_ollama_session, args
            )
            times.append(exec_time)
        
        avg_time = statistics.mean(times)
        print(f"initialize_ollama_session: {avg_time:.2f}ms avg")
        
        # Should be under threshold (this is allowed to be slower)
        assert avg_time < self.thresholds["initialize_ollama_session"], \
            f"initialize_ollama_session too slow: {avg_time:.2f}ms"
    
    def test_cache_efficiency_metrics(self):
        """Test cache efficiency and optimization metrics"""
        
        self.setup_performance_test_data("medium")
        
        # Initialize session
        init_args = models.InitializeOllamaSessionArgs(workspace_id=self.workspace_id)
        session_result = mcp_handlers.handle_initialize_ollama_session(init_args)
        
        # Build stable context multiple times (should be consistent)
        build_args = models.BuildStableContextPrefixArgs(workspace_id=self.workspace_id)
        
        hashes = []
        token_counts = []
        times = []
        
        for _ in range(5):
            start_time = time.perf_counter()
            result = mcp_handlers.handle_build_stable_context_prefix(build_args)
            end_time = time.perf_counter()
            
            hashes.append(result["prefix_hash"])
            token_counts.append(result["total_tokens"])
            times.append((end_time - start_time) * 1000)
        
        # Hash consistency (cache efficiency)
        unique_hashes = set(hashes)
        assert len(unique_hashes) == 1, \
            f"Stable context hash should be consistent, got {len(unique_hashes)} different hashes"
        
        # Token count consistency
        unique_token_counts = set(token_counts)
        assert len(unique_token_counts) == 1, \
            f"Token count should be consistent, got {unique_token_counts}"
        
        # Performance consistency
        avg_time = statistics.mean(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0
        
        print(f"Stable context consistency: {avg_time:.2f}ms avg, {std_dev:.2f}ms std dev")
        
        # Should be consistent (low standard deviation)
        assert std_dev < avg_time * 0.2, \
            f"Performance too inconsistent: {std_dev:.2f}ms std dev on {avg_time:.2f}ms avg"
    
    def test_memory_efficiency(self):
        """Test memory usage during cache operations"""
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Baseline memory
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Setup large dataset
        self.setup_performance_test_data("large")
        
        # Memory after data setup
        after_setup_memory = process.memory_info().rss / 1024 / 1024
        
        # Perform cache operations
        operations = [
            (models.GetCacheableContentArgs(workspace_id=self.workspace_id), 
             mcp_handlers.handle_get_cacheable_content),
            (models.BuildStableContextPrefixArgs(workspace_id=self.workspace_id),
             mcp_handlers.handle_build_stable_context_prefix),
            (models.InitializeOllamaSessionArgs(workspace_id=self.workspace_id),
             mcp_handlers.handle_initialize_ollama_session)
        ]
        
        peak_memory = after_setup_memory
        
        for args, handler in operations:
            # Measure memory before operation
            before_memory = process.memory_info().rss / 1024 / 1024
            
            # Perform operation
            result = handler(args)
            
            # Measure memory after operation
            after_memory = process.memory_info().rss / 1024 / 1024
            peak_memory = max(peak_memory, after_memory)
            
            # Memory should not grow excessively during operation
            memory_growth = after_memory - before_memory
            assert memory_growth < 50, \
                f"Excessive memory growth during {handler.__name__}: {memory_growth:.2f}MB"
        
        # Total memory usage should be reasonable
        total_growth = peak_memory - baseline_memory
        print(f"Memory usage: baseline {baseline_memory:.1f}MB, peak {peak_memory:.1f}MB, growth {total_growth:.1f}MB")
        
        # Should not use excessive memory (adjust threshold based on data size)
        assert total_growth < 100, \
            f"Excessive total memory usage: {total_growth:.2f}MB"
    
    def test_concurrent_operations_performance(self):
        """Test performance under concurrent operations"""
        
        import threading
        import queue
        
        self.setup_performance_test_data("medium")
        
        # Prepare operations
        operations = [
            (models.GetCacheableContentArgs(workspace_id=self.workspace_id),
             mcp_handlers.handle_get_cacheable_content),
            (models.BuildStableContextPrefixArgs(workspace_id=self.workspace_id),
             mcp_handlers.handle_build_stable_context_prefix),
            (models.GetCacheStateArgs(workspace_id=self.workspace_id, current_prefix_hash="test"),
             mcp_handlers.handle_get_cache_state)
        ]
        
        results_queue = queue.Queue()
        
        def worker(op_args, handler, thread_id):
            """Worker function for concurrent testing"""
            try:
                start_time = time.perf_counter()
                result = handler(op_args)
                end_time = time.perf_counter()
                
                execution_time = (end_time - start_time) * 1000
                results_queue.put({
                    'thread_id': thread_id,
                    'handler': handler.__name__,
                    'execution_time': execution_time,
                    'success': True,
                    'result_size': len(str(result))
                })
            except Exception as e:
                results_queue.put({
                    'thread_id': thread_id,
                    'handler': handler.__name__,
                    'execution_time': 0,
                    'success': False,
                    'error': str(e)
                })
        
        # Launch concurrent operations
        threads = []
        thread_count = 6  # 2 threads per operation type
        
        for i in range(thread_count):
            op_args, handler = operations[i % len(operations)]
            thread = threading.Thread(target=worker, args=(op_args, handler, i))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=10)  # 10 second timeout
        
        # Collect results
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
        
        # Analyze results
        successful_results = [r for r in results if r['success']]
        failed_results = [r for r in results if not r['success']]
        
        print(f"Concurrent operations: {len(successful_results)} successful, {len(failed_results)} failed")
        
        # All operations should succeed
        assert len(failed_results) == 0, \
            f"Some concurrent operations failed: {[r['error'] for r in failed_results]}"
        
        # Performance should not degrade significantly under concurrency
        avg_time = statistics.mean([r['execution_time'] for r in successful_results])
        max_time = max([r['execution_time'] for r in successful_results])
        
        print(f"Concurrent performance: {avg_time:.2f}ms avg, {max_time:.2f}ms max")
        
        # Should complete within reasonable time
        assert max_time < 1000, \
            f"Some concurrent operations too slow: {max_time:.2f}ms"
    
    def test_scalability_characteristics(self):
        """Test how performance scales with data size"""
        
        sizes = ["small", "medium", "large"]
        scalability_results = {}
        
        for size in sizes:
            # Setup data of different sizes
            self.setup_performance_test_data(size)
            
            # Test key operations
            operations = {
                "get_cacheable_content": (
                    models.GetCacheableContentArgs(workspace_id=self.workspace_id),
                    mcp_handlers.handle_get_cacheable_content
                ),
                "build_stable_context": (
                    models.BuildStableContextPrefixArgs(workspace_id=self.workspace_id),
                    mcp_handlers.handle_build_stable_context_prefix
                )
            }
            
            size_results = {}
            
            for op_name, (args, handler) in operations.items():
                # Measure performance
                times = []
                for _ in range(3):
                    _, exec_time = self.measure_execution_time(handler, args)
                    times.append(exec_time)
                
                avg_time = statistics.mean(times)
                size_results[op_name] = avg_time
            
            scalability_results[size] = size_results
            
            # Cleanup for next iteration
            self.teardown_method()
            self.setup_method()
        
        # Analyze scalability
        operation_names = ["get_cacheable_content", "build_stable_context"]
        for op_name in operation_names:
            small_time = scalability_results["small"][op_name]
            medium_time = scalability_results["medium"][op_name]
            large_time = scalability_results["large"][op_name]
            
            print(f"{op_name} scalability: {small_time:.1f}ms -> {medium_time:.1f}ms -> {large_time:.1f}ms")
            
            # Performance should scale sub-linearly (not worse than linear)
            # Medium should be less than 5x small, large should be less than 10x small
            assert medium_time < small_time * 5, \
                f"{op_name} scales poorly from small to medium: {medium_time/small_time:.1f}x"
            
            assert large_time < small_time * 10, \
                f"{op_name} scales poorly from small to large: {large_time/small_time:.1f}x"


class TestKVCacheOptimizationMetrics:
    """Test cache optimization effectiveness"""
    
    def setup_method(self):
        """Setup test workspace"""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace_path = Path(self.temp_dir) / "optimization_test_workspace"
        self.workspace_path.mkdir()
        self.workspace_id = str(self.workspace_path)
    
    def teardown_method(self):
        """Cleanup after each test"""
        import shutil
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_cache_score_optimization(self):
        """Test that cache scoring works effectively"""
        
        # Create content with different cache worthiness
        test_cases = [
            # (category, key, content_size, expected_min_score)
            ("Architecture", "database_schema", 3000, 50),  # High value
            ("ProjectGlossary", "api_config", 2500, 45),    # High value category
            ("Other", "small_note", 100, 0),                # Small content
            ("Requirements", "performance_specs", 4000, 60), # Large + good category
        ]
        
        scores = []
        
        for category, key, content_size, expected_min_score in test_cases:
            # Create content of specified size
            content = {
                "data": "A" * content_size,
                "metadata": {"category": category, "key": key}
            }
            
            # Log with cache hint
            args = models.LogCustomDataWithCacheHintArgs(
                workspace_id=self.workspace_id,
                category=category,
                key=key,
                value=content,
                suggest_caching=None,
                cache_hint=True
            )
            
            result = mcp_handlers.handle_log_custom_data_with_cache_hint(args)
            actual_score = result["cache_score"]
            scores.append(actual_score)
            
            print(f"{category}/{key}: score {actual_score} (expected min {expected_min_score})")
            
            # Should meet minimum expected score
            assert actual_score >= expected_min_score, \
                f"Cache score too low for {category}/{key}: {actual_score} < {expected_min_score}"
        
        # High-value items should have higher scores than low-value items
        high_value_scores = scores[:3]  # First 3 are high value
        low_value_score = scores[2]     # "Other/small_note" should be lowest
        
        for high_score in high_value_scores[:2]:  # Exclude the low-value one
            assert high_score > low_value_score, \
                f"High-value content should have higher cache score: {high_score} vs {low_value_score}"
    
    def test_token_estimation_accuracy(self):
        """Test accuracy of token estimation"""
        
        # Test cases with known approximate token counts
        test_cases = [
            ("Simple text", 5),
            ("A longer piece of text with multiple words and sentences.", 15),
            ({"key": "value", "description": "A structured object"}, 12),
            (["item1", "item2", "item3", "item4", "item5"], 8),
        ]
        
        for content, expected_tokens in test_cases:
            estimated = mcp_handlers.estimate_tokens(content)
            
            print(f"Content: {str(content)[:50]}... -> {estimated} tokens (expected ~{expected_tokens})")
            
            # Should be within reasonable range (±50% for simple estimation)
            assert estimated >= expected_tokens * 0.5, \
                f"Token estimate too low: {estimated} < {expected_tokens * 0.5}"
            
            assert estimated <= expected_tokens * 2, \
                f"Token estimate too high: {estimated} > {expected_tokens * 2}"
    
    def test_cache_hit_simulation(self):
        """Simulate cache hit scenarios"""
        
        # Setup data
        product_context = {
            "name": "Cache Hit Test Project",
            "description": "Testing cache hit rates and efficiency"
        }
        
        update_args = models.UpdateContextArgs(
            workspace_id=self.workspace_id,
            content=product_context,
            patch_content=None
        )
        mcp_handlers.handle_update_product_context(update_args)
        
        # Build stable context multiple times
        build_args = models.BuildStableContextPrefixArgs(workspace_id=self.workspace_id)
        
        results = []
        times = []
        
        for i in range(10):
            start_time = time.perf_counter()
            result = mcp_handlers.handle_build_stable_context_prefix(build_args)
            end_time = time.perf_counter()
            
            results.append(result)
            times.append((end_time - start_time) * 1000)
        
        # All results should be identical (perfect cache hit simulation)
        first_hash = results[0]["prefix_hash"]
        for i, result in enumerate(results[1:], 1):
            assert result["prefix_hash"] == first_hash, \
                f"Result {i} has different hash: cache miss detected"
        
        # Performance should be consistent (simulating cache hits)
        avg_time = statistics.mean(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0
        
        print(f"Cache hit simulation: {avg_time:.2f}ms avg, {std_dev:.2f}ms std dev")
        
        # Should be very consistent
        assert std_dev < avg_time * 0.15, \
            f"Too much variation in cache hit times: {std_dev:.2f}ms std dev"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])