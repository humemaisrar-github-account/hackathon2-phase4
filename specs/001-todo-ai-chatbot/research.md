# Research: Todo AI Chatbot

**Feature**: Todo AI Chatbot with Gemini AI and MCP Server
**Date**: 2026-02-06
**Status**: Completed

## Overview

This document captures research findings to resolve technical unknowns and inform architectural decisions for the AI-powered todo chatbot.

## Key Decisions & Rationale

### 1. AI Provider Selection: Gemini via OpenAI-compatible Interface

**Decision**: Use Google's Gemini AI through the OpenAI-compatible interface rather than OpenAI services directly.

**Rationale**:
- Cost-effectiveness of Google's Gemini API
- OpenAI-compatible interface allows using familiar SDK patterns
- Good performance for natural language understanding tasks
-符合 the specification requirement to use GEMINI_API_KEY

**Implementation**:
```python
AsyncOpenAI(
  api_key=GEMINI_API_KEY,
  base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
```

**Alternatives Considered**:
- OpenAI GPT models: More expensive but potentially higher accuracy
- Open-source models (LLaMA, Mistral): Require more infrastructure but lower cost
- Azure OpenAI: Enterprise features but vendor lock-in

### 2. MCP Server Architecture

**Decision**: Implement Model Context Protocol (MCP) server to expose todo operations as standardized tools.

**Rationale**:
- Standardized way to connect AI agents to application functionality
- Separates AI logic from data operations
- Enables tool composition for complex interactions
-符合 specification requirement for MCP tools

**Alternatives Considered**:
- Direct API calls from AI: Tightly couples AI to specific endpoints
- Plugin architecture: Similar concept but different standard
- Function calling without MCP: Less standardized approach

### 3. State Management Strategy

**Decision**: Implement stateless server with database-persisted conversation context.

**Rationale**:
- Scalability: Any server instance can handle any request
- Resilience: Server restarts don't lose conversation state
- Horizontal scaling: Load balancer can route to any backend
-符合 specification requirement for stateless architecture

**Implementation**:
- Conversation table to track chat sessions
- Message table to store chat history
- Service layer to reconstruct context for each request

### 4. Natural Language Processing Approach

**Decision**: Leverage Gemini's instruction-following capabilities to parse natural language into specific todo operations.

**Rationale**:
- Offloads complex NLP to powerful AI model
- Handles variations in user input naturally
- Reduces need for complex rule-based parsing
-符合 user expectation for natural interaction

**Implementation**:
- System prompt defines available tools and their purposes
- User messages trigger appropriate tool calls
- Structured responses enable accurate parsing

### 5. Tech Stack Alignment

**Decision**: Align with existing Phase II tech stack while adding AI/MCP capabilities.

**Rationale**:
- Maintains consistency with existing architecture
- Leverages familiar tools and patterns
-符合 constitution requirement for proper phase progression
- Reduces learning curve and integration complexity

**Stack**:
- Backend: Python FastAPI (existing)
- Database: Neon Serverless PostgreSQL with SQLModel (existing)
- Frontend: Next.js (existing) + ChatKit
- AI Integration: OpenAI SDK with Gemini endpoint
- MCP: Official MCP SDK

## Technical Unknowns Resolved

### Authentication & User Management
**Unknown**: How to handle user identification in the chatbot context
**Resolution**: Use existing authentication system from Phase II (Better Auth) to identify users and maintain data isolation

### Conversation Context Limitations
**Unknown**: How to handle very long conversations exceeding model context windows
**Resolution**: Implement conversation history summarization when context approaches limits, maintaining essential context while managing token usage

### Error Handling Strategy
**Unknown**: How to gracefully handle AI misinterpretations or invalid user requests
**Resolution**: Implement validation layers and graceful fallback responses with user-friendly error messages

## Best Practices Applied

1. **Separation of Concerns**: MCP server handles tool exposure, AI service handles language understanding, database manages persistence
2. **Defensive Programming**: Input validation, error handling, and graceful degradation
3. **Security**: User data isolation, secure API key handling, proper authentication
4. **Observability**: Structured logging, metrics collection, and error tracking
5. **Testing**: Unit tests for individual components, integration tests for workflows, contract tests for APIs