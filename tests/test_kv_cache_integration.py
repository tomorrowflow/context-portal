"""
Integration tests for KV cache optimization system.
Tests end-to-end workflows with realistic data scenarios.
"""

import asyncio
import json
import tempfile
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Import the MCP handlers directly for testing
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from context_portal_mcp.handlers import mcp_handlers
from context_portal_mcp.db import models, database
from context_portal_mcp.core.exceptions import ContextPortalError


class TestKVCacheIntegrationWorkflows:
    """Integration tests for complete KV cache workflows"""
    
    def setup_method(self):
        """Setup test workspace for each test method"""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace_path = Path(self.temp_dir) / "integration_test_workspace"
        self.workspace_path.mkdir()
        self.workspace_id = str(self.workspace_path)
    
    def teardown_method(self):
        """Cleanup after each test"""
        import shutil
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def setup_comprehensive_test_data(self):
        """Setup comprehensive test data for integration testing"""
        
        # 1. Product Context - Large, comprehensive project info
        product_context = {
            "name": "E-Commerce Platform Integration",
            "description": "A comprehensive e-commerce platform built with microservices architecture, featuring real-time inventory management, advanced analytics, and AI-powered recommendations. The system handles millions of transactions daily and integrates with multiple payment providers, shipping carriers, and third-party services.",
            "goals": [
                "Achieve 99.9% uptime with sub-100ms response times",
                "Support 10M+ concurrent users during peak traffic",
                "Implement real-time fraud detection and prevention",
                "Provide personalized shopping experiences using ML",
                "Ensure PCI DSS compliance and data security"
            ],
            "architecture": "Event-driven microservices with CQRS pattern, using Apache Kafka for event streaming, Redis for caching, PostgreSQL for transactional data, and Elasticsearch for search and analytics",
            "technologies": [
                "Python", "FastAPI", "PostgreSQL", "Redis", "Kafka", 
                "Docker", "Kubernetes", "Elasticsearch", "React", "TypeScript"
            ],
            "requirements": {
                "performance": "Sub-100ms API response times, 99.9% uptime",
                "scalability": "Auto-scaling to handle 10x traffic spikes",
                "security": "PCI DSS Level 1 compliance, end-to-end encryption",
                "monitoring": "Real-time metrics, alerting, and distributed tracing"
            },
            "team_structure": {
                "backend_team": 8,
                "frontend_team": 6,
                "devops_team": 4,
                "qa_team": 5
            }
        }
        
        # Update product context
        update_args = models.UpdateContextArgs(
            workspace_id=self.workspace_id,
            content=product_context,
            patch_content=None
        )
        mcp_handlers.handle_update_product_context(update_args)
        
        # 2. System Patterns - Architectural patterns used
        system_patterns = [
            {
                "name": "Event Sourcing Pattern",
                "description": "Captures all changes to application state as a sequence of events. Instead of storing just the current state, we store the sequence of state-changing events. This provides complete audit trail, enables temporal queries, and supports event replay for debugging and analytics. Critical for our order processing and inventory management systems.",
                "tags": ["architecture", "events", "audit", "microservices"]
            },
            {
                "name": "CQRS (Command Query Responsibility Segregation)",
                "description": "Separates read and write operations into different models. Commands handle updates and business logic, while queries handle read operations optimized for specific use cases. This allows independent scaling of read and write workloads, and enables specialized data models for different query patterns.",
                "tags": ["architecture", "scalability", "performance", "separation-of-concerns"]
            },
            {
                "name": "Circuit Breaker Pattern",
                "description": "Prevents cascading failures in distributed systems by monitoring service calls and 'opening' the circuit when failure rates exceed thresholds. Provides fallback mechanisms and automatic recovery detection. Essential for maintaining system stability when external services become unavailable.",
                "tags": ["resilience", "fault-tolerance", "microservices", "monitoring"]
            },
            {
                "name": "Saga Pattern",
                "description": "Manages distributed transactions across multiple microservices using a sequence of local transactions. Each step publishes events that trigger the next step, with compensating actions for rollback scenarios. Critical for order processing workflows that span inventory, payment, and shipping services.",
                "tags": ["transactions", "distributed-systems", "consistency", "workflow"]
            }
        ]
        
        for pattern in system_patterns:
            pattern_args = models.LogSystemPatternArgs(
                workspace_id=self.workspace_id,
                **pattern
            )
            mcp_handlers.handle_log_system_pattern(pattern_args)
        
        # 3. Custom Data with Cache Hints - Critical specifications
        custom_data_items = [
            {
                "category": "Architecture",
                "key": "database_schema",
                "value": {
                    "primary_database": "PostgreSQL 14",
                    "tables": {
                        "users": {"columns": 15, "indexes": 8, "estimated_rows": 50000000},
                        "products": {"columns": 25, "indexes": 12, "estimated_rows": 10000000},
                        "orders": {"columns": 20, "indexes": 10, "estimated_rows": 100000000},
                        "inventory": {"columns": 12, "indexes": 6, "estimated_rows": 10000000}
                    },
                    "relationships": {
                        "users_orders": "one_to_many",
                        "products_orders": "many_to_many_through_order_items",
                        "products_inventory": "one_to_one"
                    },
                    "partitioning": {
                        "orders": "monthly_partitions",
                        "analytics_events": "daily_partitions"
                    }
                },
                "suggest_caching": None,
                "cache_hint": True
            },
            {
                "category": "Configuration",
                "key": "api_specifications",
                "value": {
                    "base_url": "https://api.ecommerce-platform.com",
                    "version": "v2",
                    "endpoints": {
                        "authentication": "/auth",
                        "users": "/users",
                        "products": "/products",
                        "orders": "/orders",
                        "payments": "/payments",
                        "inventory": "/inventory",
                        "analytics": "/analytics",
                        "recommendations": "/recommendations"
                    },
                    "rate_limits": {
                        "authenticated": 10000,
                        "anonymous": 1000,
                        "premium": 50000
                    },
                    "authentication": {
                        "methods": ["JWT", "OAuth2", "API_KEY"],
                        "token_expiry": 3600,
                        "refresh_token_expiry": 604800
                    }
                },
                "suggest_caching": None,
                "cache_hint": True
            },
            {
                "category": "Requirements",
                "key": "performance_specifications",
                "value": {
                    "response_times": {
                        "api_endpoints": "< 100ms p95",
                        "search_queries": "< 200ms p95",
                        "checkout_process": "< 500ms end-to-end"
                    },
                    "throughput": {
                        "orders_per_second": 10000,
                        "search_queries_per_second": 50000,
                        "concurrent_users": 1000000
                    },
                    "availability": {
                        "uptime_target": "99.9%",
                        "planned_downtime": "< 4 hours/month",
                        "disaster_recovery": "< 1 hour RTO, < 15 minutes RPO"
                    }
                },
                "suggest_caching": None,
                "cache_hint": True
            }
        ]
        
        for item in custom_data_items:
            custom_args = models.LogCustomDataWithCacheHintArgs(
                workspace_id=self.workspace_id,
                **item
            )
            mcp_handlers.handle_log_custom_data_with_cache_hint(custom_args)
        
        # 4. Decisions - Recent architectural decisions
        decisions = [
            {
                "summary": "Adopt Event Sourcing for Order Management",
                "rationale": "Need complete audit trail for financial transactions and ability to replay events for analytics. Traditional CRUD operations don't provide sufficient visibility into state changes.",
                "implementation_details": "Implement using Apache Kafka as event store, with separate read models for different query patterns. Start with order domain, expand to inventory and payments.",
                "tags": ["architecture", "event-sourcing", "orders", "audit"]
            },
            {
                "summary": "Implement Circuit Breaker for External Services",
                "rationale": "Payment gateway outages were causing cascading failures across the entire checkout process. Need to isolate failures and provide graceful degradation.",
                "implementation_details": "Use Hystrix pattern with configurable thresholds. Implement fallback mechanisms for non-critical services. Add monitoring and alerting for circuit state changes.",
                "tags": ["resilience", "payments", "fault-tolerance", "monitoring"]
            },
            {
                "summary": "Migrate to Kubernetes for Container Orchestration",
                "rationale": "Current Docker Swarm setup doesn't provide sufficient scaling capabilities and lacks advanced networking features needed for microservices communication.",
                "implementation_details": "Gradual migration starting with stateless services. Implement service mesh using Istio for traffic management and security. Use Helm for deployment automation.",
                "tags": ["infrastructure", "kubernetes", "scalability", "deployment"]
            }
        ]
        
        for decision in decisions:
            decision_args = models.LogDecisionArgs(
                workspace_id=self.workspace_id,
                **decision
            )
            mcp_handlers.handle_log_decision(decision_args)
        
        # 5. Active Context - Current focus areas
        active_context = {
            "current_sprint": "Sprint 23 - Performance Optimization",
            "focus_areas": [
                "Database query optimization",
                "Redis caching strategy implementation",
                "API response time improvements",
                "Load testing and capacity planning"
            ],
            "recent_changes": [
                "Implemented database connection pooling",
                "Added Redis cluster for session storage",
                "Optimized product search queries",
                "Enhanced monitoring dashboards"
            ],
            "open_issues": [
                "Memory leaks in recommendation service",
                "Intermittent timeout issues with payment gateway",
                "Search relevance scoring needs improvement",
                "Mobile app performance on older devices"
            ],
            "upcoming_milestones": [
                "Q1 Performance Review - March 15",
                "Security Audit - March 30",
                "Mobile App Release - April 10",
                "Black Friday Preparation - October 1"
            ]
        }
        
        active_args = models.UpdateContextArgs(
            workspace_id=self.workspace_id,
            content=active_context,
            patch_content=None
        )
        mcp_handlers.handle_update_active_context(active_args)
        
        # 6. Progress Entries - Current tasks
        progress_entries = [
            {
                "status": "IN_PROGRESS",
                "description": "Implement Redis caching layer for product catalog",
                "parent_id": None
            },
            {
                "status": "IN_PROGRESS", 
                "description": "Optimize database queries for order history endpoint",
                "parent_id": None
            },
            {
                "status": "TODO",
                "description": "Set up load testing environment for Black Friday simulation",
                "parent_id": None
            },
            {
                "status": "DONE",
                "description": "Complete security vulnerability assessment",
                "parent_id": None
            }
        ]
        
        for entry in progress_entries:
            progress_args = models.LogProgressArgs(
                workspace_id=self.workspace_id,
                **entry
            )
            mcp_handlers.handle_log_progress(progress_args)
    
    def test_complete_kv_cache_workflow(self):
        """Test complete KV cache workflow from initialization to performance monitoring"""
        
        # Setup comprehensive test data
        self.setup_comprehensive_test_data()
        
        # Step 1: Initialize Ollama session
        init_args = models.InitializeOllamaSessionArgs(workspace_id=self.workspace_id)
        session_result = mcp_handlers.handle_initialize_ollama_session(init_args)
        
        assert session_result["session_initialized"] is True
        assert session_result["stable_context_ready"] is True
        session_id = session_result["session_id"]
        initial_hash = session_result["stable_context_hash"]
        
        # Step 2: Verify stable context was built correctly
        build_args = models.BuildStableContextPrefixArgs(workspace_id=self.workspace_id)
        stable_result = mcp_handlers.handle_build_stable_context_prefix(build_args)
        
        assert stable_result["prefix_hash"] == initial_hash
        assert stable_result["total_tokens"] > 5000  # Should be substantial
        assert len(stable_result["sections"]) >= 3  # Product context, patterns, custom data
        
        # Step 3: Check cache state (should be valid)
        cache_args = models.GetCacheStateArgs(
            workspace_id=self.workspace_id,
            current_prefix_hash=initial_hash
        )
        cache_result = mcp_handlers.handle_get_cache_state(cache_args)
        
        assert cache_result["cache_valid"] is True
        assert cache_result["recommendation"] == "reuse"
        
        # Step 4: Get dynamic context for different query types
        query_scenarios = [
            ("architecture decision making", 2000),
            ("performance optimization tasks", 1500),
            ("current progress and issues", 1000)
        ]
        
        for query_intent, budget in query_scenarios:
            dynamic_args = models.GetDynamicContextArgs(
                workspace_id=self.workspace_id,
                query_intent=query_intent,
                context_budget=budget
            )
            dynamic_result = mcp_handlers.handle_get_dynamic_context(dynamic_args)
            
            assert dynamic_result["total_tokens"] <= budget
            assert len(dynamic_result["dynamic_context"]) > 0
            assert len(dynamic_result["sections"]) > 0
        
        # Step 5: Monitor cache performance
        perf_args = models.GetCachePerformanceArgs(
            workspace_id=self.workspace_id,
            session_id=session_id
        )
        perf_result = mcp_handlers.handle_get_cache_performance(perf_args)
        
        assert perf_result["session_specific"] is True
        assert perf_result["session_id"] == session_id
        assert 0 <= perf_result["hit_rate"] <= 1
        assert len(perf_result["recommendations"]) > 0
    
    def test_cache_invalidation_workflow(self):
        """Test cache invalidation when content changes"""
        
        # Setup initial data
        self.setup_comprehensive_test_data()
        
        # Build initial stable context
        build_args = models.BuildStableContextPrefixArgs(workspace_id=self.workspace_id)
        initial_result = mcp_handlers.handle_build_stable_context_prefix(build_args)
        initial_hash = initial_result["prefix_hash"]
        
        # Verify cache is valid
        cache_args = models.GetCacheStateArgs(
            workspace_id=self.workspace_id,
            current_prefix_hash=initial_hash
        )
        cache_result = mcp_handlers.handle_get_cache_state(cache_args)
        assert cache_result["cache_valid"] is True
        
        # Modify product context (should invalidate cache)
        updated_context = {
            "name": "E-Commerce Platform Integration - Updated",
            "description": "Updated description with new requirements and features",
            "goals": ["New goal: Implement AI-powered chatbot support"],
            "version": "2.0"
        }
        
        update_args = models.UpdateContextArgs(
            workspace_id=self.workspace_id,
            content=updated_context,
            patch_content=None
        )
        mcp_handlers.handle_update_product_context(update_args)
        
        # Check cache state again (should be invalid now)
        cache_result_after = mcp_handlers.handle_get_cache_state(cache_args)
        assert cache_result_after["cache_valid"] is False
        assert cache_result_after["recommendation"] == "refresh"
        assert cache_result_after["current_hash"] != initial_hash
        
        # Build new stable context
        new_result = mcp_handlers.handle_build_stable_context_prefix(build_args)
        assert new_result["prefix_hash"] != initial_hash
        assert new_result["prefix_hash"] == cache_result_after["current_hash"]
    
    def test_content_prioritization_workflow(self):
        """Test that content is properly prioritized in cache operations"""
        
        # Setup data with different priorities
        self.setup_comprehensive_test_data()
        
        # Get cacheable content
        cacheable_args = models.GetCacheableContentArgs(
            workspace_id=self.workspace_id,
            content_threshold=1000
        )
        cacheable_result = mcp_handlers.handle_get_cacheable_content(cacheable_args)
        
        # Verify priority ordering
        priorities = [item["priority"] for item in cacheable_result]
        priority_values = {"high": 3, "medium": 2, "low": 1}
        
        for i in range(len(priorities) - 1):
            current_priority = priority_values[priorities[i]]
            next_priority = priority_values[priorities[i + 1]]
            assert current_priority >= next_priority, "Items should be ordered by priority (high to low)"
        
        # Verify high priority items are included
        high_priority_items = [item for item in cacheable_result if item["priority"] == "high"]
        assert len(high_priority_items) > 0, "Should have high priority items"
        
        # Product context should be high priority
        product_context_items = [item for item in cacheable_result if item["source"] == "product_context"]
        assert len(product_context_items) > 0
        assert product_context_items[0]["priority"] == "high"
    
    def test_large_content_handling_workflow(self):
        """Test handling of large content volumes"""
        
        # Setup base data
        self.setup_comprehensive_test_data()
        
        # Add large custom data items
        large_data_items = []
        for i in range(10):
            large_content = {
                "id": f"large_item_{i}",
                "data": "A" * 5000,  # 5KB per item
                "metadata": {
                    "size": "large",
                    "index": i,
                    "description": f"Large data item {i} for testing cache performance with substantial content volumes"
                }
            }
            
            large_args = models.LogCustomDataWithCacheHintArgs(
                workspace_id=self.workspace_id,
                category="LargeData",
                key=f"item_{i}",
                value=large_content,
                suggest_caching=None,
                cache_hint=True
            )
            result = mcp_handlers.handle_log_custom_data_with_cache_hint(large_args)
            large_data_items.append(result)
        
        # Build stable context with large content
        build_args = models.BuildStableContextPrefixArgs(workspace_id=self.workspace_id)
        stable_result = mcp_handlers.handle_build_stable_context_prefix(build_args)
        
        # Should handle large content without errors
        assert stable_result["total_tokens"] > 10000  # Should be substantial
        assert len(stable_result["stable_prefix"]) > 50000  # Large content
        
        # Test dynamic context with budget constraints
        dynamic_args = models.GetDynamicContextArgs(
            workspace_id=self.workspace_id,
            query_intent="large data analysis",
            context_budget=3000  # Limited budget
        )
        dynamic_result = mcp_handlers.handle_get_dynamic_context(dynamic_args)
        
        # Should respect budget constraints
        assert dynamic_result["total_tokens"] <= 3000
        assert dynamic_result["budget_remaining"] >= 0
    
    def test_multi_session_workflow(self):
        """Test multiple concurrent sessions"""
        
        # Setup data
        self.setup_comprehensive_test_data()
        
        # Initialize multiple sessions
        sessions = []
        for i in range(3):
            init_args = models.InitializeOllamaSessionArgs(workspace_id=self.workspace_id)
            session_result = mcp_handlers.handle_initialize_ollama_session(init_args)
            sessions.append(session_result)
        
        # Verify each session has unique ID but same stable context
        session_ids = [s["session_id"] for s in sessions]
        assert len(set(session_ids)) == 3, "Each session should have unique ID"
        
        stable_hashes = [s["stable_context_hash"] for s in sessions]
        assert len(set(stable_hashes)) == 1, "All sessions should have same stable context hash"
        
        # Test performance monitoring for each session
        for session in sessions:
            perf_args = models.GetCachePerformanceArgs(
                workspace_id=self.workspace_id,
                session_id=session["session_id"]
            )
            perf_result = mcp_handlers.handle_get_cache_performance(perf_args)
            
            assert perf_result["session_specific"] is True
            assert perf_result["session_id"] == session["session_id"]
    
    def test_error_recovery_workflow(self):
        """Test error handling and recovery scenarios"""
        
        # Test with minimal data (edge case)
        minimal_context = {"name": "Minimal Test"}
        update_args = models.UpdateContextArgs(
            workspace_id=self.workspace_id,
            content=minimal_context,
            patch_content=None
        )
        mcp_handlers.handle_update_product_context(update_args)
        
        # Should still work with minimal data
        build_args = models.BuildStableContextPrefixArgs(workspace_id=self.workspace_id)
        result = mcp_handlers.handle_build_stable_context_prefix(build_args)
        
        assert "stable_prefix" in result
        assert "prefix_hash" in result
        assert result["total_tokens"] > 0
        
        # Test cache state with no previous hash
        cache_args = models.GetCacheStateArgs(
            workspace_id=self.workspace_id,
            current_prefix_hash=None
        )
        cache_result = mcp_handlers.handle_get_cache_state(cache_args)
        
        assert cache_result["cache_valid"] is False
        assert cache_result["provided_hash"] is None
        assert cache_result["recommendation"] == "refresh"
    
    def test_performance_optimization_workflow(self):
        """Test performance optimization features"""
        
        # Setup comprehensive data
        self.setup_comprehensive_test_data()
        
        # Test content threshold filtering
        high_threshold_args = models.GetCacheableContentArgs(
            workspace_id=self.workspace_id,
            content_threshold=5000  # High threshold
        )
        high_threshold_result = mcp_handlers.handle_get_cacheable_content(high_threshold_args)
        
        low_threshold_args = models.GetCacheableContentArgs(
            workspace_id=self.workspace_id,
            content_threshold=500   # Low threshold
        )
        low_threshold_result = mcp_handlers.handle_get_cacheable_content(low_threshold_args)
        
        # Low threshold should return more items
        assert len(low_threshold_result) >= len(high_threshold_result)
        
        # Test dynamic context budget management
        budgets = [500, 1000, 2000, 5000]
        for budget in budgets:
            dynamic_args = models.GetDynamicContextArgs(
                workspace_id=self.workspace_id,
                query_intent="performance testing",
                context_budget=budget
            )
            dynamic_result = mcp_handlers.handle_get_dynamic_context(dynamic_args)
            
            # Should respect budget
            assert dynamic_result["total_tokens"] <= budget
            assert dynamic_result["budget_used"] + dynamic_result["budget_remaining"] == budget
            
            # Larger budgets should generally include more content
            if budget > 1000:
                assert dynamic_result["budget_used"] > 0


class TestKVCacheRealWorldScenarios:
    """Test real-world usage scenarios"""
    
    def setup_method(self):
        """Setup test workspace for each test method"""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace_path = Path(self.temp_dir) / "realworld_test_workspace"
        self.workspace_path.mkdir()
        self.workspace_id = str(self.workspace_path)
    
    def teardown_method(self):
        """Cleanup after each test"""
        import shutil
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_development_team_workflow(self):
        """Simulate a development team's daily workflow"""
        
        # Morning: Team lead updates project context
        project_update = {
            "name": "Customer Portal Redesign",
            "current_phase": "Implementation",
            "team_size": 8,
            "deadline": "2025-03-15",
            "priority": "high"
        }
        
        update_args = models.UpdateContextArgs(
            workspace_id=self.workspace_id,
            content=project_update,
            patch_content=None
        )
        mcp_handlers.handle_update_product_context(update_args)
        
        # Developer logs architectural decision
        decision_args = models.LogDecisionArgs(
            workspace_id=self.workspace_id,
            summary="Use React Query for state management",
            rationale="Simplifies server state management and provides caching",
            implementation_details="Replace Redux with React Query for API calls",
            tags=["frontend", "state-management", "performance"]
        )
        mcp_handlers.handle_log_decision(decision_args)
        
        # Initialize session for AI assistance
        init_args = models.InitializeOllamaSessionArgs(workspace_id=self.workspace_id)
        session_result = mcp_handlers.handle_initialize_ollama_session(init_args)
        
        assert session_result["session_initialized"] is True
        
        # Get context for code review query
        dynamic_args = models.GetDynamicContextArgs(
            workspace_id=self.workspace_id,
            query_intent="code review and best practices",
            context_budget=1500
        )
        dynamic_result = mcp_handlers.handle_get_dynamic_context(dynamic_args)
        
        assert "React Query" in dynamic_result["dynamic_context"]
        assert dynamic_result["total_tokens"] <= 1500
    
    def test_architecture_review_scenario(self):
        """Simulate architecture review meeting preparation"""
        
        # Setup system architecture documentation
        arch_patterns = [
            {
                "name": "Microservices Architecture",
                "description": "Decomposed monolith into 12 microservices with clear domain boundaries",
                "tags": ["architecture", "microservices", "scalability"]
            },
            {
                "name": "API Gateway Pattern",
                "description": "Single entry point for all client requests with routing and authentication",
                "tags": ["api", "gateway", "security", "routing"]
            }
        ]
        
        for pattern in arch_patterns:
            pattern_args = models.LogSystemPatternArgs(
                workspace_id=self.workspace_id,
                **pattern
            )
            mcp_handlers.handle_log_system_pattern(pattern_args)
        
        # Add technical specifications
        tech_specs = {
            "category": "Architecture",
            "key": "service_specifications",
            "value": {
                "services": {
                    "user_service": {"port": 8001, "database": "postgres"},
                    "order_service": {"port": 8002, "database": "postgres"},
                    "payment_service": {"port": 8003, "database": "postgres"}
                },
                "communication": "REST APIs with event-driven async messaging",
                "deployment": "Kubernetes with Helm charts"
            },
            "suggest_caching": None,
            "cache_hint": True
        }
        
        spec_args = models.LogCustomDataWithCacheHintArgs(
            workspace_id=self.workspace_id,
            **tech_specs
        )
        mcp_handlers.handle_log_custom_data_with_cache_hint(spec_args)
        
        # Get comprehensive context for architecture review
        build_args = models.BuildStableContextPrefixArgs(workspace_id=self.workspace_id)
        stable_result = mcp_handlers.handle_build_stable_context_prefix(build_args)
        
        # Should include all architectural information
        stable_content = stable_result["stable_prefix"]
        assert "Microservices Architecture" in stable_content
        assert "API Gateway Pattern" in stable_content
        assert "service_specifications" in stable_content or "user_service" in stable_content
    
    def test_performance_monitoring_scenario(self):
        """Simulate performance monitoring and optimization workflow"""
        
        # Setup performance-related context
        perf_context = {
            "current_focus": "Performance Optimization Sprint",
            "metrics": {
                "response_time_p95": "150ms",
                "throughput": "5000 rps",
                "error_rate": "0.1%"
            },
            "targets": {
                "response_time_p95": "100ms",
                "throughput": "10000 rps",
                "error_rate": "0.05%"
            }
        }
        
        active_args = models.UpdateContextArgs(
            workspace_id=self.workspace_id,
            content=perf_context,
            patch_content=None
        )
        mcp_handlers.handle_update_active_context(active_args)
        
        # Log performance-related decisions
        perf_decision = {
            "summary": "Implement Redis caching for frequently accessed data",
            "rationale": "Database queries are the bottleneck, caching will reduce load",
            "implementation_details": "Redis cluster with 6 nodes, TTL-based expiration",
            "tags": ["performance", "caching", "redis", "optimization"]
        }
        
        decision_args = models.LogDecisionArgs(
            workspace_id=self.workspace_id,
            **perf_decision
        )
        mcp_handlers.handle_log_decision(decision_args)
        
        # Initialize session and monitor cache performance
        init_args = models.InitializeOllamaSessionArgs(workspace_id=self.workspace_id)
        session_result = mcp_handlers.handle_initialize_ollama_session(init_args)
        
        # Monitor cache performance
        perf_args = models.GetCachePerformanceArgs(
            workspace_id=self.workspace_id,
            session_id=session_result["session_id"]
        )
        perf_result = mcp_handlers.handle_get_cache_performance(perf_args)
        
        # Should provide performance insights
        assert perf_result["session_specific"] is True
        assert "recommendations" in perf_result
        assert len(perf_result["recommendations"]) > 0
        
        # Get dynamic context for performance query
        dynamic_args = models.GetDynamicContextArgs(
            workspace_id=self.workspace_id,
            query_intent="performance optimization recommendations",
            context_budget=2000
        )
        dynamic_result = mcp_handlers.handle_get_dynamic_context(dynamic_args)
        
        # Should include performance-related context
        assert "performance" in dynamic_result["dynamic_context"].lower()
        assert "redis" in dynamic_result["dynamic_context"].lower()


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])