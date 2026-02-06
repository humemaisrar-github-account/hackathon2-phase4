# Todo Web Application - Phase II Implementation

This is a full-stack todo web application implementing the Phase II specifications with Next.js frontend, FastAPI backend, BetterAuth authentication, and PostgreSQL database.

## Tech Stack

- **Frontend**: Next.js 14+, TypeScript, Tailwind CSS
- **Backend**: Python FastAPI
- **ORM**: SQLModel
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: Better Auth with JWT tokens

## Features Implemented

1. **Authentication System**
   - Email/password login without email verification
   - JWT token issuance on login
   - Frontend attaches JWT to all API requests in `Authorization: Bearer <token>`
   - Backend verifies JWT and extracts `user_id`
   - All endpoints require valid JWT; otherwise return 401

2. **Todo API Endpoints** (FastAPI)
   - GET `/api/{user_id}/tasks` → List all tasks for that user
   - POST `/api/{user_id}/tasks` → Create a new task
   - GET `/api/{user_id}/tasks/{id}` → Get a specific task
   - PUT `/api/{user_id}/tasks/{id}` → Update a task
   - DELETE `/api/{user_id}/tasks/{id}` → Delete a task
   - PATCH `/api/{user_id}/tasks/{id}/complete` → Toggle completion status
   - All responses are valid JSON
   - Filter all tasks by authenticated `user_id`

3. **Database Schema**
   - `users` table managed by Better Auth
   - `tasks` table with required fields
   - Indexed `tasks.user_id` and `tasks.completed`

4. **Frontend Components**
   - Reusable API client in `/lib/api.ts`
   - Example fetch calls for all required operations

## Environment Variables

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_BETTER_AUTH_SECRET=your_better_auth_secret_here
```

### Backend (.env)
```env
DATABASE_URL=your_postgresql_connection_string
BETTER_AUTH_SECRET=your_better_auth_secret_here
SECRET_KEY=your_jwt_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Running the Application

### Backend Setup
1. Navigate to the backend directory: `cd backend`
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables (copy `.env.example` to `.env` and update values)
4. Run the server: `uvicorn src.main:app --reload --port 8000`

### Frontend Setup
1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Set up environment variables
4. Run the development server: `npm run dev`

## API Client Usage

The application includes a reusable API client in `frontend/lib/api.ts` with functions for:
- `signUp(email, password)`
- `signIn(email, password)`
- `getTasks(userId)`
- `createTask(userId, title, description)`
- `updateTask(userId, id, title, description)`
- `deleteTask(userId, id)`
- `toggleComplete(userId, id)`

## AI Chatbot Feature

The application includes an AI-powered chatbot that allows users to manage their todos using natural language commands.

### Setup
1. Obtain a Google Gemini API key from the Google AI Studio
2. Add the `GEMINI_API_KEY` to your backend `.env` file
3. The chatbot is accessible from the dashboard via the "AI Assistant" button

### Supported Commands
- **Add tasks**: "Add a task to buy groceries" or "Create a task to call mom"
- **List tasks**: "Show me my pending tasks" or "What have I completed?"
- **Complete tasks**: "Mark task 1 as complete" or "Finish the meeting task"
- **Delete tasks**: "Delete the old task" or "Remove task 2"
- **Update tasks**: "Change task 1 to 'Call mom tonight'"

### Technical Architecture
- The chatbot uses Google's Gemini AI through an OpenAI-compatible interface
- MCP (Model Context Protocol) tools are used to enable the AI to interact with the todo management system
- Conversation history is persisted in the database for context continuity
- All operations are secured with the same authentication system as the rest of the application