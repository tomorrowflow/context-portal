# Context Portal

A database-backed MCP server for managing structured project context for AI assistants within IDEs.

## Overview

This project implements the "Context Portal" system proposed in the [Project Brief](projectBrief.md). It provides a structured way for AI assistants to store and retrieve project context (decisions, progress, architecture, etc.) via a dedicated MCP server.

Key features include:
*   Structured context storage using SQLite (one DB per workspace).
*   MCP server (`context_portal_mcp`) built with Python/FastAPI.
*   Defined MCP tools for interaction (e.g., `log_decision`, `get_active_context`).
*   Multi-workspace support via `workspace_id`.
*   Dual deployment modes: Stdio and Local HTTP.

## Setup

1.  Create a virtual environment: `python -m venv .venv`
2.  Activate it: `source .venv/bin/activate` (Linux/macOS) or `.venv\Scripts\activate` (Windows)
3.  Install dependencies: `pip install -r requirements.txt`

## Usage

*(Details on running the Stdio and HTTP modes will be added here)*

## Architecture

Refer to the [Memory Bank Decision Log](memory-bank/decisionLog.md) for details on the adopted architecture and database schema.