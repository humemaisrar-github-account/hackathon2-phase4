# Data Model: Todo AI Chatbot

**Feature**: Todo AI Chatbot with Gemini AI and MCP Server
**Date**: 2026-02-06
**Status**: Completed

## Overview

This document defines the data structures and relationships required for the AI-powered todo chatbot system.

## Key Entities

### 1. Task Entity

**Purpose**: Represents individual todo items managed by users

**Fields**:
- `id`: Integer (Primary Key, Auto-generated)
- `user_id`: String (Foreign Key to user, required for data isolation)
- `title`: String (Task title/description, required, max 255 chars)
- `description`: Text (Detailed task description, optional, max 1000 chars)
- `completed`: Boolean (Completion status, default: false)
- `created_at`: DateTime (Timestamp when task was created, auto-generated)
- `updated_at`: DateTime (Timestamp when task was last updated, auto-generated)

**Relationships**:
- Belongs to one User (many tasks per user)
- Owned by one specific user (data isolation)

**Validation Rules**:
- Title is required and must not be empty
- User_id is required and must reference a valid user
- Title length ≤ 255 characters
- Description length ≤ 1000 characters

**State Transitions**:
- `created` → `completed` (when marked complete)
- `completed` → `active` (when marked incomplete, if allowed)

### 2. Conversation Entity

**Purpose**: Manages chat session context and groups related messages

**Fields**:
- `id`: Integer (Primary Key, Auto-generated)
- `user_id`: String (Foreign Key to user, required for data isolation)
- `created_at`: DateTime (Timestamp when conversation started, auto-generated)
- `updated_at`: DateTime (Timestamp when conversation was last updated, auto-generated)

**Relationships**:
- Belongs to one User (many conversations per user)
- Has many Messages (one-to-many relationship)
- Owned by one specific user (data isolation)

**Validation Rules**:
- User_id is required and must reference a valid user

### 3. Message Entity

**Purpose**: Stores individual chat messages within conversations

**Fields**:
- `id`: Integer (Primary Key, Auto-generated)
- `user_id`: String (Foreign Key to user, required for data isolation)
- `conversation_id`: Integer (Foreign Key to conversation, required)
- `role`: String (Role of the message sender - "user" or "assistant", required)
- `content`: Text (Message content, required, max 10000 chars)
- `created_at`: DateTime (Timestamp when message was created, auto-generated)

**Relationships**:
- Belongs to one User (for data isolation)
- Belongs to one Conversation (many messages per conversation)
- Referenced by AI service for context retrieval

**Validation Rules**:
- User_id is required and must reference a valid user
- Conversation_id is required and must reference a valid conversation
- Role must be either "user" or "assistant"
- Content is required and must not be empty
- Content length ≤ 10000 characters

## Relationships Diagram

```
User (user_id)  ←  Task (user_id)
                   ↓
User (user_id)  ←  Conversation (user_id)
                   ↓
Conversation (id) → Message (conversation_id)
User (user_id)    ←  Message (user_id)
```

## Indexes

**Task Table**:
- Index on (user_id, completed) - for efficient queries by user and status
- Index on (user_id, created_at) - for chronological retrieval

**Conversation Table**:
- Index on (user_id, updated_at) - for retrieving recent conversations by user

**Message Table**:
- Index on (conversation_id, created_at) - for chronological message retrieval
- Index on (user_id, conversation_id) - for data isolation queries

## Constraints

1. **Data Integrity**:
   - Foreign key constraints ensure referential integrity
   - Not-null constraints on required fields
   - Check constraints on enum-like fields (role in Message)

2. **Data Isolation**:
   - All entities include user_id for proper multi-tenancy
   - Queries must always filter by user_id to prevent cross-user data access

3. **Timestamp Management**:
   - created_at is set once on creation
   - updated_at is updated on any modification
   - Database-level defaults for timestamps where possible

## Access Patterns

1. **Task Operations**:
   - Get all tasks for a user (filter by user_id)
   - Get pending tasks for a user (filter by user_id and completed=False)
   - Get completed tasks for a user (filter by user_id and completed=True)
   - Update specific task by id and user_id

2. **Conversation Operations**:
   - Get recent conversations for a user
   - Create new conversation for a user
   - Get conversation by id and user_id (validation)

3. **Message Operations**:
   - Get all messages in a conversation (ordered by created_at)
   - Add message to a conversation
   - Validate user access to conversation before reading/writing messages