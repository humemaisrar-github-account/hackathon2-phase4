# Quickstart Guide: Todo AI Chatbot

**Feature**: Todo AI Chatbot with Gemini AI and MCP Server
**Date**: 2026-02-06
**Status**: Ready

## Overview

This guide provides the essential steps to set up and run the AI-powered todo chatbot system.

## Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend)
- PostgreSQL compatible database (Neon Serverless recommended)
- Google Gemini API key (GEMINI_API_KEY)

## Setup Instructions

### 1. Clone and Initialize Repository

```bash
# Clone your repository (if starting fresh)
git clone <your-repo-url>
cd <your-project-dir>
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### Environment Variables

Create `.env` file in the backend directory:

```env
DATABASE_URL=postgresql://user:password@host:port/database
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_secret_key_for_authentication
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### Database Setup

```bash
# Apply database migrations
python -m src.main db migrate
```

#### Run Backend Server

```bash
# Start the FastAPI backend
uvicorn src.main:app --reload --port 8000
```

### 3. MCP Server Setup

#### Install MCP Dependencies

```bash
cd mcp-server
pip install -r requirements.txt
```

#### Run MCP Server

```bash
# Start the MCP server
python -m src.server
```

### 4. Frontend Setup

#### Install Node Dependencies

```bash
cd frontend
npm install
```

#### Frontend Environment Variables

Create `.env.local` in the frontend directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GEMINI_API_KEY=your_gemini_api_key_here
NEXT_PUBLIC_CHATKIT_DOMAIN_KEY=your_chatkit_domain_key
```

#### Run Frontend

```bash
# Start the Next.js frontend
npm run dev
```

## Core Features Walkthrough

### 1. Natural Language Todo Management

Interact with the chatbot using natural language:

```
User: "Add a task to buy groceries"
Bot: "I've added the task 'buy groceries' to your list. You now have 3 pending tasks."

User: "Show me what I need to do today"
Bot: "Here are your pending tasks:
1. Buy groceries
2. Finish project report
3. Schedule dentist appointment"

User: "Mark task 1 as complete"
Bot: "I've marked 'buy groceries' as complete. You now have 2 pending tasks."
```

### 2. Conversation Context

The system maintains conversation history:

```
User: "I need to remember to call my mom"
Bot: "I've added 'call my mom' to your task list."

User: "Later add that it's about birthday planning"
Bot: "I've updated the task 'call my mom' to 'call my mom about birthday planning'."
```

## API Endpoints

### Chat Endpoint

```
POST /api/{user_id}/chat
```

**Request Body**:
```json
{
  "conversation_id": 123,
  "message": "Add a task to water plants"
}
```

**Response**:
```json
{
  "conversation_id": 123,
  "response": "I've added the task 'water plants' to your list.",
  "tool_calls": [
    {
      "tool_name": "add_task",
      "result": {"task_id": 456, "status": "created", "title": "water plants"}
    }
  ]
}
```

## Troubleshooting

### Common Issues

1. **Gemini API Errors**: Verify your GEMINI_API_KEY is correctly set and has sufficient quota
2. **Database Connection**: Ensure DATABASE_URL is properly configured
3. **Authentication**: Confirm user sessions are properly established

### Logging and Monitoring

- Backend logs: Check console output from uvicorn
- Database queries: Enable SQL logging in development
- API rate limits: Monitor Gemini API usage quotas

## Next Steps

1. Explore the MCP tools exposed by the server
2. Customize the conversation prompts for your specific use case
3. Extend the system with additional todo management capabilities
4. Implement additional error handling and validation