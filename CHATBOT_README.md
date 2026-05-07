 Office Chatbot with LangChain

This project includes an AI chatbot powered by LangChain and Google's Gemini AI model.

## Features

- **Conversational AI**: Chat with an AI assistant for office-related tasks
- **Tool Integration**: Built-in tools for time checking and calculations
- **Memory Management**: Maintains conversation history
- **Authentication**: Requires user authentication
- **RESTful API**: Easy integration with frontend applications

## API Endpoints

### POST /api/v1/chatbot/chat

Chat with the AI assistant.

**Request Body:**

```json
{
  "message": "Hello, what time is it?",
  "user_id": "optional_user_id"
}
```

**Response:**

```json
{
  "response": "The current time is: 2024-01-15 14:30:25",
  "success": true,
  "tools_used": ["tool_call"],
  "user_id": "optional_user_id"
}
```

### POST /api/v1/chatbot/chat/clear-memory

Clear conversation memory.

**Response:**

```json
{
  "message": "Chat memory cleared successfully"
}
```

### GET /api/v1/chatbot/chat/history

Get conversation history.

**Response:**

```json
{
  "history": [
    { "role": "user", "content": "Hello" },
    { "role": "assistant", "content": "Hi there!" }
  ]
}
```

## Built-in Tools

The chatbot includes these built-in tools:

1. **Time Tool**: Responds to queries about current time
   - Triggers: "time", "current time", "what time", "now"

2. **Calculator Tool**: Performs mathematical calculations
   - Triggers: "calculate", "compute", "math", "solve"
   - Supports: basic arithmetic, functions like sqrt, pow, etc.

## Usage Examples

### Time Queries

```
User: What time is it?
Bot: The current time is: 2024-01-15 14:30:25

User: Tell me the current time
Bot: The current time is: 2024-01-15 14:30:25
```

### Calculations

```
User: Calculate 2 + 2
Bot: The result is: 4

User: What is 5 * 3?
Bot: The result is: 15

User: Solve sqrt(16)
Bot: The result is: 4.0
```

### General Chat

```
User: Hello, how are you?
Bot: Hello! I'm doing well, thank you for asking. How can I help you with your office tasks today?
```

## Technical Implementation

- **Framework**: LangChain for AI orchestration
- **LLM**: Google Gemini 2.5 Flash
- **Memory**: In-memory conversation history
- **Tools**: Custom tool implementations
- **Authentication**: JWT-based user authentication
- **Database**: PostgreSQL with SQLAlchemy

## Dependencies

- langchain
- langchain-core
- langchain-community
- google-genai (for Gemini AI)
- fastapi
- sqlalchemy
- pydantic

## Installation

1. Install dependencies:

```bash
pip install -r requirements-chatbot.txt
```

2. Set up environment variables:

```bash
export GOOGLE_API_KEY="your_gemini_api_key"
```

3. Run the application:

```bash
uvicorn main:app --reload
```

## Security Notes

- All endpoints require authentication
- Tool executions are sandboxed for security
- Mathematical expressions are evaluated safely
- Conversation history is stored in memory (not persistent)
