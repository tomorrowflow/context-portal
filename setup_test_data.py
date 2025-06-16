"""
Sample data setup script for KV cache testing.
Populates the database with realistic test data for comprehensive testing.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from context_portal_mcp.handlers import mcp_handlers
from context_portal_mcp.db import models


class TestDataGenerator:
    """Generates comprehensive test data for KV cache testing"""
    
    def __init__(self, workspace_id: str):
        self.workspace_id = workspace_id
        
    def setup_comprehensive_test_data(self):
        """Setup comprehensive test data covering all KV cache scenarios"""
        
        print(f"Setting up test data for workspace: {self.workspace_id}")
        
        # 1. Product Context - Comprehensive project information
        self.setup_product_context()
        
        # 2. System Patterns - Architectural patterns
        self.setup_system_patterns()
        
        # 3. Custom Data with Cache Hints - Critical specifications
        self.setup_custom_data_with_cache_hints()
        
        # 4. Decisions - Recent architectural decisions
        self.setup_decisions()
        
        # 5. Active Context - Current focus areas
        self.setup_active_context()
        
        # 6. Progress Entries - Current tasks
        self.setup_progress_entries()
        
        print("Test data setup completed successfully!")
    
    def setup_product_context(self):
        """Setup comprehensive product context"""
        
        print("Setting up product context...")
        
        product_context = {
            "name": "Advanced E-Commerce Platform",
            "version": "3.0",
            "description": """
            A next-generation e-commerce platform built with modern microservices architecture.
            The platform handles millions of transactions daily, supports real-time inventory management,
            provides AI-powered personalized recommendations, and integrates with multiple payment
            providers and shipping carriers. Built for scale, security, and performance.
            """.strip(),
            
            "business_goals": [
                "Achieve 99.99% uptime with sub-50ms API response times",
                "Support 50M+ concurrent users during peak shopping events",
                "Process 1M+ transactions per hour with zero data loss",
                "Provide personalized experiences using ML/AI algorithms",
                "Maintain PCI DSS Level 1 compliance and SOC 2 certification"
            ],
            
            "technical_goals": [
                "Implement event-driven architecture with CQRS pattern",
                "Achieve horizontal scalability across all services",
                "Implement comprehensive observability and monitoring",
                "Maintain 99.9% test coverage across all services",
                "Zero-downtime deployments with blue-green strategy"
            ],
            
            "architecture": {
                "style": "Event-driven microservices with domain-driven design",
                "communication": "Async messaging via Apache Kafka + REST APIs",
                "data_storage": "Polyglot persistence - PostgreSQL, Redis, Elasticsearch",
                "deployment": "Kubernetes with Istio service mesh",
                "monitoring": "Prometheus, Grafana, Jaeger, ELK stack"
            },
            
            "technology_stack": {
                "backend": ["Python 3.11", "FastAPI", "Django", "Celery"],
                "frontend": ["React 18", "TypeScript", "Next.js", "Tailwind CSS"],
                "databases": ["PostgreSQL 15", "Redis 7", "Elasticsearch 8"],
                "messaging": ["Apache Kafka", "RabbitMQ"],
                "infrastructure": ["Kubernetes", "Docker", "Terraform", "AWS"],
                "monitoring": ["Prometheus", "Grafana", "Jaeger", "DataDog"]
            },
            
            "team_structure": {
                "engineering": {
                    "backend_engineers": 12,
                    "frontend_engineers": 8,
                    "mobile_engineers": 4,
                    "devops_engineers": 6,
                    "qa_engineers": 8,
                    "security_engineers": 3
                },
                "product": {
                    "product_managers": 4,
                    "designers": 6,
                    "analysts": 3
                },
                "leadership": {
                    "engineering_managers": 3,
                    "tech_leads": 5,
                    "architects": 2
                }
            },
            
            "compliance_requirements": [
                "PCI DSS Level 1 - Payment card data protection",
                "SOC 2 Type II - Security and availability controls",
                "GDPR - European data protection regulation",
                "CCPA - California consumer privacy act",
                "ISO 27001 - Information security management"
            ],
            
            "performance_requirements": {
                "api_response_times": {
                    "p50": "< 25ms",
                    "p95": "< 50ms",
                    "p99": "< 100ms"
                },
                "throughput": {
                    "orders_per_second": 5000,
                    "search_queries_per_second": 50000,
                    "page_views_per_second": 100000
                },
                "availability": {
                    "uptime_target": "99.99%",
                    "planned_downtime": "< 2 hours/quarter",
                    "disaster_recovery": "RTO < 30 minutes, RPO < 5 minutes"
                }
            }
        }
        
        update_args = models.UpdateContextArgs(
            workspace_id=self.workspace_id,
            content=product_context,
            patch_content=None
        )
        mcp_handlers.handle_update_product_context(update_args)
        print("✓ Product context setup complete")
    
    def setup_system_patterns(self):
        """Setup architectural system patterns"""
        
        print("Setting up system patterns...")
        
        patterns = [
            {
                "name": "Event Sourcing Pattern",
                "description": """
                Captures all changes to application state as a sequence of events rather than storing
                just the current state. This provides complete audit trail, enables temporal queries,
                supports event replay for debugging and analytics, and facilitates building read models
                optimized for specific query patterns. Critical for our order processing, inventory
                management, and financial transaction systems where auditability is paramount.
                """.strip(),
                "tags": ["architecture", "events", "audit", "microservices", "cqrs"]
            },
            
            {
                "name": "CQRS (Command Query Responsibility Segregation)",
                "description": """
                Separates read and write operations into different models, allowing independent
                optimization of each. Commands handle business logic and state changes, while
                queries are optimized for specific read patterns. This enables independent scaling
                of read and write workloads, supports multiple specialized read models, and allows
                for eventual consistency where appropriate. Essential for high-performance systems
                with complex query requirements.
                """.strip(),
                "tags": ["architecture", "scalability", "performance", "separation-of-concerns"]
            },
            
            {
                "name": "Circuit Breaker Pattern",
                "description": """
                Prevents cascading failures in distributed systems by monitoring service calls and
                'opening' the circuit when failure rates exceed configured thresholds. Provides
                fallback mechanisms, automatic recovery detection, and fail-fast behavior to
                maintain system stability. Includes half-open state for gradual recovery testing.
                Essential for maintaining system resilience when external services become unavailable.
                """.strip(),
                "tags": ["resilience", "fault-tolerance", "microservices", "monitoring"]
            },
            
            {
                "name": "Saga Pattern",
                "description": """
                Manages distributed transactions across multiple microservices using a sequence of
                local transactions. Each step publishes events that trigger the next step, with
                compensating actions for rollback scenarios. Supports both orchestration and
                choreography approaches. Critical for complex business workflows like order
                processing that span inventory, payment, shipping, and notification services.
                """.strip(),
                "tags": ["transactions", "distributed-systems", "consistency", "workflow"]
            },
            
            {
                "name": "API Gateway Pattern",
                "description": """
                Provides a single entry point for all client requests, handling cross-cutting
                concerns like authentication, authorization, rate limiting, request/response
                transformation, and routing. Enables service composition, protocol translation,
                and centralized monitoring. Reduces client complexity and provides a stable
                interface while allowing backend services to evolve independently.
                """.strip(),
                "tags": ["api", "gateway", "security", "routing", "cross-cutting"]
            },
            
            {
                "name": "Bulkhead Pattern",
                "description": """
                Isolates critical resources to prevent failures in one area from affecting others.
                Similar to watertight compartments in ships, this pattern partitions system
                resources (thread pools, connection pools, memory) to contain failures. Ensures
                that high-priority operations can continue even when lower-priority operations
                are experiencing issues. Essential for maintaining service availability under load.
                """.strip(),
                "tags": ["resilience", "isolation", "resource-management", "availability"]
            }
        ]
        
        for pattern in patterns:
            pattern_args = models.LogSystemPatternArgs(
                workspace_id=self.workspace_id,
                **pattern
            )
            mcp_handlers.handle_log_system_pattern(pattern_args)
        
        print(f"✓ {len(patterns)} system patterns setup complete")
    
    def setup_custom_data_with_cache_hints(self):
        """Setup custom data with cache optimization hints"""
        
        print("Setting up custom data with cache hints...")
        
        custom_data_items = [
            {
                "category": "Architecture",
                "key": "database_schema_design",
                "value": {
                    "primary_database": "PostgreSQL 15",
                    "connection_pooling": "PgBouncer with 100 connections per service",
                    "tables": {
                        "users": {
                            "columns": 18,
                            "indexes": 12,
                            "estimated_rows": 100000000,
                            "partitioning": "hash_partitioning_by_user_id"
                        },
                        "products": {
                            "columns": 32,
                            "indexes": 18,
                            "estimated_rows": 50000000,
                            "partitioning": "range_partitioning_by_category"
                        },
                        "orders": {
                            "columns": 25,
                            "indexes": 15,
                            "estimated_rows": 500000000,
                            "partitioning": "monthly_range_partitioning"
                        },
                        "inventory": {
                            "columns": 15,
                            "indexes": 8,
                            "estimated_rows": 50000000,
                            "partitioning": "hash_partitioning_by_product_id"
                        }
                    },
                    "relationships": {
                        "users_orders": "one_to_many",
                        "products_orders": "many_to_many_through_order_items",
                        "products_inventory": "one_to_one",
                        "users_addresses": "one_to_many"
                    },
                    "performance_optimizations": {
                        "read_replicas": 3,
                        "connection_pooling": "enabled",
                        "query_caching": "enabled",
                        "materialized_views": ["user_order_summary", "product_analytics"]
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
                    "version": "v3",
                    "authentication": {
                        "methods": ["JWT", "OAuth2", "API_KEY"],
                        "jwt_expiry": 3600,
                        "refresh_token_expiry": 604800,
                        "api_key_rotation": "monthly"
                    },
                    "endpoints": {
                        "authentication": {
                            "path": "/auth",
                            "methods": ["POST"],
                            "rate_limit": "10/minute"
                        },
                        "users": {
                            "path": "/users",
                            "methods": ["GET", "POST", "PUT", "DELETE"],
                            "rate_limit": "1000/minute"
                        },
                        "products": {
                            "path": "/products",
                            "methods": ["GET", "POST", "PUT", "DELETE"],
                            "rate_limit": "5000/minute"
                        },
                        "orders": {
                            "path": "/orders",
                            "methods": ["GET", "POST", "PUT"],
                            "rate_limit": "2000/minute"
                        },
                        "payments": {
                            "path": "/payments",
                            "methods": ["POST", "GET"],
                            "rate_limit": "500/minute"
                        }
                    },
                    "rate_limits": {
                        "anonymous": 100,
                        "authenticated": 5000,
                        "premium": 25000,
                        "enterprise": 100000
                    },
                    "response_formats": ["JSON", "XML"],
                    "compression": "gzip",
                    "caching": {
                        "etag_support": True,
                        "cache_control": True,
                        "max_age": 300
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
                        "api_endpoints": {
                            "p50": "< 25ms",
                            "p95": "< 50ms",
                            "p99": "< 100ms",
                            "p99.9": "< 200ms"
                        },
                        "search_queries": {
                            "p50": "< 50ms",
                            "p95": "< 100ms",
                            "p99": "< 200ms"
                        },
                        "checkout_process": {
                            "end_to_end": "< 2000ms",
                            "payment_processing": "< 1000ms"
                        }
                    },
                    "throughput": {
                        "orders_per_second": 5000,
                        "search_queries_per_second": 50000,
                        "concurrent_users": 1000000,
                        "page_views_per_second": 100000
                    },
                    "availability": {
                        "uptime_target": "99.99%",
                        "planned_downtime": "< 2 hours/quarter",
                        "disaster_recovery": {
                            "rto": "< 30 minutes",
                            "rpo": "< 5 minutes"
                        }
                    },
                    "scalability": {
                        "horizontal_scaling": "auto-scaling based on CPU/memory",
                        "database_scaling": "read replicas + sharding",
                        "cdn_usage": "global CDN for static assets"
                    }
                },
                "suggest_caching": None,
                "cache_hint": True
            },
            
            {
                "category": "Security",
                "key": "security_specifications",
                "value": {
                    "authentication": {
                        "multi_factor": "required_for_admin",
                        "password_policy": {
                            "min_length": 12,
                            "complexity": "uppercase_lowercase_numbers_symbols",
                            "expiry": "90_days"
                        },
                        "session_management": {
                            "timeout": "30_minutes_idle",
                            "concurrent_sessions": "limited_to_5"
                        }
                    },
                    "encryption": {
                        "data_at_rest": "AES-256",
                        "data_in_transit": "TLS 1.3",
                        "key_management": "AWS KMS with rotation"
                    },
                    "compliance": {
                        "pci_dss": "Level 1",
                        "soc2": "Type II",
                        "gdpr": "compliant",
                        "ccpa": "compliant"
                    },
                    "monitoring": {
                        "security_events": "real_time_alerting",
                        "vulnerability_scanning": "daily",
                        "penetration_testing": "quarterly"
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
        
        print(f"✓ {len(custom_data_items)} custom data items with cache hints setup complete")
    
    def setup_decisions(self):
        """Setup architectural and technical decisions"""
        
        print("Setting up decisions...")
        
        decisions = [
            {
                "summary": "Adopt Event Sourcing for Order Management System",
                "rationale": """
                Traditional CRUD operations don't provide sufficient audit trail for financial
                transactions. Event sourcing gives us complete history of all state changes,
                enables temporal queries for analytics, and supports building multiple read
                models optimized for different use cases. The complexity is justified by the
                business requirements for auditability and the analytical capabilities it enables.
                """.strip(),
                "implementation_details": """
                - Use Apache Kafka as the event store with 30-day retention
                - Implement event versioning strategy for schema evolution
                - Build separate read models for order status, analytics, and reporting
                - Start with order domain, expand to inventory and payments in phases
                - Implement event replay capability for debugging and testing
                """.strip(),
                "tags": ["architecture", "event-sourcing", "orders", "audit", "kafka"]
            },
            
            {
                "summary": "Implement Circuit Breaker Pattern for External Service Calls",
                "rationale": """
                Payment gateway and shipping provider outages were causing cascading failures
                across the entire checkout process. Circuit breaker pattern will isolate failures,
                provide graceful degradation, and prevent system-wide outages. This is critical
                for maintaining customer experience during external service disruptions.
                """.strip(),
                "implementation_details": """
                - Use Hystrix-style circuit breaker with configurable thresholds
                - Implement fallback mechanisms for non-critical services
                - Add monitoring and alerting for circuit state changes
                - Configure different thresholds for different service criticality levels
                - Implement half-open state for gradual recovery testing
                """.strip(),
                "tags": ["resilience", "payments", "fault-tolerance", "monitoring", "circuit-breaker"]
            },
            
            {
                "summary": "Migrate to Kubernetes for Container Orchestration",
                "rationale": """
                Current Docker Swarm setup lacks advanced networking features, sophisticated
                scheduling capabilities, and ecosystem tooling needed for our microservices
                architecture. Kubernetes provides better service discovery, load balancing,
                auto-scaling, and has a rich ecosystem of tools for monitoring and management.
                """.strip(),
                "implementation_details": """
                - Gradual migration starting with stateless services
                - Implement Istio service mesh for traffic management and security
                - Use Helm charts for deployment automation and configuration management
                - Set up monitoring with Prometheus and Grafana
                - Implement GitOps workflow with ArgoCD for deployments
                """.strip(),
                "tags": ["infrastructure", "kubernetes", "scalability", "deployment", "service-mesh"]
            },
            
            {
                "summary": "Adopt GraphQL for Mobile API Layer",
                "rationale": """
                Mobile clients need flexible data fetching to minimize network requests and
                battery usage. REST APIs require multiple round trips for complex data needs.
                GraphQL allows clients to request exactly the data they need in a single request,
                reducing bandwidth usage and improving mobile app performance.
                """.strip(),
                "implementation_details": """
                - Implement GraphQL gateway using Apollo Federation
                - Keep REST APIs for backward compatibility and third-party integrations
                - Use DataLoader pattern to prevent N+1 query problems
                - Implement query complexity analysis and rate limiting
                - Add GraphQL-specific monitoring and performance tracking
                """.strip(),
                "tags": ["api", "graphql", "mobile", "performance", "federation"]
            },
            
            {
                "summary": "Implement Redis Cluster for Distributed Caching",
                "rationale": """
                Single Redis instance is becoming a bottleneck and single point of failure.
                Database query load is increasing, and we need distributed caching to improve
                response times and reduce database load. Redis Cluster provides high availability,
                automatic failover, and horizontal scaling capabilities.
                """.strip(),
                "implementation_details": """
                - Deploy 6-node Redis cluster (3 masters, 3 replicas)
                - Implement cache-aside pattern with automatic TTL management
                - Use Redis Streams for real-time event processing
                - Add monitoring for cache hit rates and performance metrics
                - Implement cache warming strategies for critical data
                """.strip(),
                "tags": ["caching", "redis", "performance", "scalability", "high-availability"]
            }
        ]
        
        for decision in decisions:
            decision_args = models.LogDecisionArgs(
                workspace_id=self.workspace_id,
                **decision
            )
            mcp_handlers.handle_log_decision(decision_args)
        
        print(f"✓ {len(decisions)} decisions setup complete")
    
    def setup_active_context(self):
        """Setup current active context"""
        
        print("Setting up active context...")
        
        active_context = {
            "current_sprint": "Sprint 28 - Performance & Scalability",
            "sprint_goals": [
                "Implement Redis cluster for distributed caching",
                "Optimize database queries for order history endpoint",
                "Complete load testing for Black Friday preparation",
                "Implement circuit breaker for payment gateway integration"
            ],
            
            "focus_areas": [
                "Database query optimization and indexing strategy",
                "Redis caching implementation and cache warming",
                "API response time improvements across all endpoints",
                "Load testing and capacity planning for peak traffic",
                "Circuit breaker implementation for external services"
            ],
            
            "recent_changes": [
                "Implemented database connection pooling with PgBouncer",
                "Added Redis cluster for session storage and caching",
                "Optimized product search queries with new indexes",
                "Enhanced monitoring dashboards with custom metrics",
                "Completed security audit and vulnerability remediation"
            ],
            
            "current_issues": [
                {
                    "priority": "high",
                    "issue": "Memory leaks in recommendation service causing OOM errors",
                    "assigned_to": "Backend Team",
                    "eta": "End of sprint"
                },
                {
                    "priority": "high", 
                    "issue": "Intermittent timeout issues with payment gateway during peak hours",
                    "assigned_to": "Platform Team",
                    "eta": "Next sprint"
                },
                {
                    "priority": "medium",
                    "issue": "Search relevance scoring needs improvement for long-tail queries",
                    "assigned_to": "Search Team",
                    "eta": "2 sprints"
                },
                {
                    "priority": "medium",
                    "issue": "Mobile app performance degradation on older Android devices",
                    "assigned_to": "Mobile Team", 
                    "eta": "Next release"
                }
            ],
            
            "upcoming_milestones": [
                {
                    "date": "2025-02-15",
                    "milestone": "Q1 Performance Review",
                    "description": "Comprehensive performance analysis and optimization results"
                },
                {
                    "date": "2025-03-01",
                    "milestone": "Security Audit Completion",
                    "description": "Annual security audit and compliance verification"
                },
                {
                    "date": "2025-03-15",
                    "milestone": "Mobile App v3.0 Release",
                    "description": "Major mobile app update with performance improvements"
                },
                {
                    "date": "2025-10-01",
                    "milestone": "Black Friday Preparation Complete",
                    "description": "All systems ready for peak holiday traffic"
                }
            ],
            
            "metrics_tracking": {
                "performance": {
                    "api_response_time_p95": "45ms (target: <50ms)",
                    "database_query_time_p95": "15ms (target: <20ms)",
                    "cache_hit_rate": "85% (target: >90%)"
                },
                "reliability": {
                    "uptime": "99.95% (target: 99.99%)",
                    "error_rate": "0.05% (target: <0.01%)",
                    "mttr": "12 minutes (target: <15 minutes)"
                },
                "business": {
                    "conversion_rate": "3.2% (target: >3.5%)",
                    "cart_abandonment": "68% (target: <65%)",
                    "customer_satisfaction": "4.3/5 (target: >4.5)"
                }
            }
        }
        
        active_args = models.UpdateContextArgs(
            workspace_id=self.workspace_id,
            content=active_context,
            patch_content=None
        )
        mcp_handlers.handle_update_active_context(active_args)
        print("✓ Active context setup complete")
    
    def setup_progress_entries(self):
        """Setup current progress entries and tasks"""
        
        print("Setting up progress entries...")
        
        progress_entries = [
            # In Progress Tasks
            {
                "status": "IN_PROGRESS",
                "description": "Implement Redis cluster for distributed caching across all services",
                "parent_id": None
            },
            {
                "status": "IN_PROGRESS",
                "description": "Optimize database queries for order history endpoint - 60% complete",
                "parent_id": None
            },
            {
                "status": "IN_PROGRESS",
                "description": "Set up comprehensive load testing environment for Black Friday simulation",
                "parent_id": None
            },
            {
                "status": "IN_PROGRESS",
                "description": "Implement circuit breaker pattern for payment gateway integration",
                "parent_id": None
            },
            {
                "status": "IN_PROGRESS",
                "description": "Debug memory leaks in recommendation service ML pipeline",
                "parent_id": None
            },
            
            # TODO Tasks
            {
                "status": "TODO",
                "description": "Implement cache warming strategy for product catalog data",
                "parent_id": None
            },
            {
                "status": "TODO",
                "description": "Add monitoring dashboards for Redis cluster performance metrics",
                "parent_id": None
            },
            {
                "status": "TODO",
                "description": "Conduct performance testing for checkout flow under peak load",
                "parent_id": None
            },
            {
                "status": "TODO",
                "description": "Implement GraphQL federation for mobile API optimization",
                "parent_id": None
            },
            {
                "status": "TODO",
                "description": "Set up automated security scanning in CI/CD pipeline",
                "parent_id": None
            },
            
            # Completed Tasks
            {
                "status": "DONE",
                "description": "Complete annual security vulnerability assessment and remediation",
                "parent_id": None
            },
            {
                "status": "DONE",
                "description": "Implement database connection pooling with PgBouncer configuration",
                "parent_id": None
            },
            {
                "status": "DONE",
                "description": "Add comprehensive monitoring for API response times and error rates",
                "parent_id": None
            },
            {
                "status": "DONE",
                "description": "Optimize product search indexing strategy for Elasticsearch",
                "parent_id": None
            },
            {
                "status": "DONE",
                "description": "Implement automated backup and disaster recovery procedures",
                "parent_id": None
            }
        ]
        
        for entry in progress_entries:
            progress_args = models.LogProgressArgs(
                workspace_id=self.workspace_id,
                **entry
            )
            mcp_handlers.handle_log_progress(progress_args)
        
        print(f"✓ {len(progress_entries)} progress entries setup complete")


def main():
    """Main function to setup test data"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup test data for KV cache testing")
    parser.add_argument(
        "workspace_id",
        help="Workspace ID (absolute path to workspace directory)"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify the setup by running basic KV cache operations"
    )
    
    args = parser.parse_args()
    
    # Validate workspace path
    workspace_path = Path(args.workspace_id)
    if not workspace_path.exists():
        print(f"Creating workspace directory: {workspace_path}")
        workspace_path.mkdir(parents=True, exist_ok=True)
    
    # Setup test data
    generator = TestDataGenerator(args.workspace_id)
    generator.setup_comprehensive_test_data()
    
    # Verify setup if requested
    if args.verify:
        print("\nVerifying test data setup...")
        verify_test_data_setup(args.workspace_id)
    
    print(f"\nTest data setup completed for workspace: {args.workspace_id}")
    print("You can now run the KV cache tests using this workspace.")


def verify_test_data_setup(workspace_id: str):
    """Verify that test data was setup correctly"""
    
    try:
        # Test get_cacheable_content
        cacheable_args = models.GetCacheableContentArgs(workspace_id=workspace_id)
        cacheable_result = mcp_handlers.handle_get_cacheable_content(cacheable_args)
        print(f"✓ Found {len(cacheable_result)} cacheable content items")
        
        # Test build_stable_context_prefix
        build_args = models.BuildStableContextPrefixArgs(workspace_id=workspace_id)
        stable_result = mcp_handlers.handle_build_stable_context_prefix(build_args)
        print(f"✓ Built stable context with {stable_result['total_tokens']} tokens")
        
        # Test initialize_ollama_session
        init_args = models.InitializeOllamaSessionArgs(workspace_id=workspace_id)
        session_result = mcp_handlers.handle_initialize_ollama_session(init_args)
        print(f"✓ Initialized Ollama session: {session_result['session_id']}")
        
        print("✓ All verification tests passed!")
        
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()