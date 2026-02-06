# Tasks: Todo AI Chatbot

**Feature**: Todo AI Chatbot with Gemini AI and MCP Server
**Branch**: 001-todo-ai-chatbot
**Date**: 2026-02-06

## Implementation Strategy

**MVP First**: Begin with User Story 1 (P1) - AI-Powered Todo Management as it's the core value proposition. This delivers basic functionality first, then incrementally adds conversation context and MCP integration.

**Incremental Delivery**: Each user story builds upon the previous, delivering value at each stage:
- Phase 1: Project setup and foundational components
- Phase 2: Core todo functionality with basic AI integration
- Phase 3: Persistent conversation context
- Phase 4: MCP server integration
- Phase 5: Polish and cross-cutting concerns

## Dependencies

**User Story Order**:
- US1 (P1) must complete before US2 (P2) - conversation context requires basic chat functionality
- US2 (P2) must complete before US3 (P3) - MCP integration requires persistent context
- US3 (P3) completes the full architecture

**Parallel Opportunities**:
- Database setup can run in parallel with AI/Gemini API integration
- Frontend components can be developed in parallel with backend API
- MCP server can be developed in parallel with main backend during US3

## Parallel Execution Examples

**Per User Story**:
- **US1**: While AI chat service is being implemented, the todo models and services can be built in parallel
- **US2**: While conversation context is being added to the API, the database migration for conversation entities can run in parallel
- **US3**: While MCP tools are being implemented, the AI integration can be enhanced to use these tools

---

## Phase 1: Setup

### Goal
Establish project structure and foundational components needed for all user stories.

### Independent Test
Project structure is set up and basic API endpoint returns a response.

### Tasks

- [x] T001 Create project directories: backend/, frontend/
- [x] T002 [P] Set up backend requirements.txt with FastAPI, SQLModel, openai, psycopg2, mcp-sdk
- [x] T003 [P] Set up frontend package.json with Next.js, react, react-dom
- [x] T005 Initialize git repository with proper .gitignore
- [x] T006 Create basic backend/src/main.py with minimal FastAPI app
- [x] T007 [P] Set up environment variables structure (.env.example files)
- [x] T008 Create database migration scripts for initial setup
- [x] T009 Set up basic testing configuration (pytest, jest)
- [x] T010 [P] Create project README.md with setup instructions

---

## Phase 2: Foundational Components

### Goal
Implement core models, services, and authentication that all user stories depend on.

### Independent Test
Database models are defined and basic CRUD operations work for todos.

### Tasks

- [x] T011 Create Task model in backend/src/models/todo.py
- [x] T012 [P] Create Conversation model in backend/src/models/conversation.py
- [x] T013 [P] Create Message model in backend/src/models/message.py
- [x] T014 Implement TodoService in backend/src/services/todo_service.py
- [x] T015 [P] Implement ConversationService in backend/src/services/conversation_service.py
- [x] T016 Set up database connection and session in backend/src/database/
- [x] T017 [P] Create todo API routes in backend/src/api/routes/todos.py
- [x] T018 Create basic auth middleware for user identification
- [x] T019 Set up SQLModel table definitions with proper constraints
- [x] T020 [P] Create database migration scripts for all entities

---

## Phase 3: [US1] AI-Powered Todo Management via Natural Language

### Goal
Enable users to interact with their todo list through a conversational interface using natural language commands.

### Independent Test
Can send natural language messages to the chatbot and verify it performs correct todo operations while maintaining conversation context.

### Acceptance Scenarios:
1. Given user wants to add a task, When user says "Add a task to buy groceries", Then a new todo item "buy groceries" is created and confirmed back to the user
2. Given user has existing tasks, When user says "Show me my pending tasks", Then the bot lists all incomplete tasks in a readable format
3. Given user wants to update a task, When user says "Mark task 1 as complete", Then the specified task is marked as completed and the user receives confirmation

### Tasks

- [x] T021 [US1] Set up OpenAI client with Gemini configuration in backend/src/services/
- [x] T022 [P] [US1] Create AiChatService in backend/src/services/ai_chat_service.py
- [x] T023 [P] [US1] Create chat API endpoint in backend/src/api/routes/chat.py
- [x] T024 [US1] Implement basic message handling in AiChatService
- [x] T025 [P] [US1] Create simple prompt templates for natural language processing
- [x] T026 [US1] Integrate todo operations with AI responses
- [x] T027 [P] [US1] Add basic conversation history to AI context
- [x] T028 [US1] Implement error handling for invalid commands
- [x] T029 [P] [US1] Create basic frontend chat UI component
- [x] T030 [US1] Connect frontend to chat API endpoint
- [x] T031 [P] [US1] Test natural language commands for todo operations
- [x] T032 [US1] Implement validation for user inputs

---

## Phase 4: [US2] Persistent Conversation Context

### Goal
Maintain conversation history and context across multiple interactions, remembering previous exchanges.

### Independent Test
Can have multi-turn conversations where the bot refers back to earlier statements or maintains context across different types of requests.

### Acceptance Scenarios:
1. Given user has had previous conversations, When user returns to chat, Then the bot can continue the conversation with appropriate context
2. Given user references a task number mentioned earlier, When user says "Update that to include organic items", Then the bot correctly identifies and updates the referenced task

### Tasks

- [x] T033 [US2] Enhance Conversation model with additional context fields
- [x] T034 [P] [US2] Update ConversationService to handle full conversation lifecycle
- [x] T035 [US2] Modify chat endpoint to use conversation persistence
- [x] T036 [P] [US2] Implement conversation history retrieval in AiChatService
- [x] T037 [US2] Add conversation context to AI prompt construction
- [x] T038 [P] [US2] Create conversation listing API endpoint
- [x] T039 [US2] Implement message persistence in chat flow
- [x] T040 [P] [US2] Add user data isolation for conversations
- [x] T041 [US2] Create message retrieval API endpoint
- [x] T042 [P] [US2] Update frontend to maintain conversation context
- [x] T043 [US2] Test multi-turn conversation functionality
- [x] T044 [US2] Implement conversation context summarization for long histories

---

## Phase 5: [US3] MCP Server Integration with Gemini AI

### Goal
Integrate Google's Gemini AI through MCP server architecture to expose todo operations as standardized tools.

### Independent Test
MCP server correctly exposes todo operations as tools that the AI agent can invoke.

### Acceptance Scenarios:
1. Given AI agent needs to perform a todo operation, When it calls an MCP tool like add_task, Then the operation is executed and results returned to the AI agent

### Tasks

- [x] T045 [US3] Create MCP project structure in backend/src/mcp/
- [x] T046 [P] [US3] Implement add_task MCP tool in backend/src/mcp/tools/add_task.py
- [x] T047 [US3] Implement list_tasks MCP tool in backend/src/mcp/tools/list_tasks.py
- [x] T048 [P] [US3] Implement complete_task MCP tool in backend/src/mcp/tools/complete_task.py
- [x] T049 [US3] Implement delete_task MCP tool in backend/src/mcp/tools/delete_task.py
- [x] T050 [P] [US3] Implement update_task MCP tool in backend/src/mcp/tools/update_task.py
- [x] T051 [US3] Create MCP server main application in backend/src/mcp/server.py
- [x] T052 [P] [US3] Configure MCP server with proper endpoints
- [x] T053 [US3] Update AiChatService to use MCP tools instead of direct service calls
- [x] T054 [P] [US3] Configure MCP client in backend to connect to server
- [x] T055 [US3] Test MCP tool invocation from AI agent
- [x] T056 [US3] Implement error handling for MCP tool calls

---

## Phase 6: Polish & Cross-Cutting Concerns

### Goal
Complete the implementation with proper error handling, security, performance, and documentation.

### Independent Test
All edge cases handled properly, security implemented, performance targets met, and system ready for production.

### Tasks

- [x] T057 Add comprehensive error handling for task ID not found
- [x] T058 [P] Implement rate limiting for API endpoints
- [x] T059 Add proper validation for natural language that can't be parsed
- [x] T060 [P] Implement conversation history management to handle context limits
- [x] T061 Add user data isolation validation to all endpoints
- [x] T062 [P] Add logging and monitoring capabilities
- [x] T063 Implement proper security headers and CORS configuration
- [x] T064 [P] Add input sanitization for user messages
- [x] T065 Create comprehensive API documentation
- [x] T066 [P] Add unit and integration tests for all components
- [x] T067 Optimize database queries and add proper indexing
- [x] T068 [P] Add health check endpoints
- [x] T069 Update frontend UI for better user experience
- [x] T070 Create deployment configuration files
- [x] T071 Conduct security review of all endpoints
- [x] T072 [P] Performance test with 100 concurrent users