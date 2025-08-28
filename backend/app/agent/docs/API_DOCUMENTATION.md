# SigmaSight Agent API Documentation

## Overview

The SigmaSight Agent provides chat-based portfolio analysis through a combination of REST endpoints for conversation management and Server-Sent Events (SSE) for real-time response streaming. The agent uses OpenAI GPT-5-2025-08-07 with function calling to analyze portfolios.

**Base URL**: `https://api.sigmasight.com/api/v1`

## Authentication

All endpoints require JWT Bearer token authentication:

```http
Authorization: Bearer <jwt_token>
```

For SSE endpoints, dual authentication is supported:
1. **Bearer Token**: In Authorization header
2. **Cookie**: `auth_token` cookie (for browser SSE support)

## Chat Endpoints

### Create Conversation

Creates a new conversation with the specified mode.

```http
POST /api/v1/chat/conversations
```

#### Request Body

```json
{
  "mode": "green",
  "name": "Portfolio Review Session"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| mode | string | No | Conversation mode: `green` (default), `blue`, `indigo`, `violet` |
| name | string | No | Optional conversation name |

#### Response

```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "550e8400-e29b-41d4-a716-446655440001",
  "mode": "green",
  "name": "Portfolio Review Session",
  "created_at": "2025-08-28T14:30:00Z",
  "updated_at": "2025-08-28T14:30:00Z",
  "message_count": 0
}
```

#### Status Codes

- `201 Created`: Conversation created successfully
- `400 Bad Request`: Invalid mode specified
- `401 Unauthorized`: Invalid or missing authentication
- `429 Too Many Requests`: Rate limit exceeded

---

### Send Message (SSE Stream)

Sends a message to the agent and receives streaming response via Server-Sent Events.

```http
POST /api/v1/chat/send
```

#### Request Body

```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "text": "What's my portfolio value?"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| conversation_id | string (UUID) | Yes | Conversation to send message to |
| text | string | Yes | User message text |

#### SSE Response Events

The response is a stream of Server-Sent Events:

##### Event: `start`
Signals the start of response streaming.

```
event: start
data: {"mode": "green", "timestamp": "2025-08-28T14:30:00Z"}
```

##### Event: `tool_started`
Indicates a tool function is being called.

```
event: tool_started
data: {"name": "get_portfolio_complete", "args": {"portfolio_id": "..."}}
```

##### Event: `tool_finished`
Tool execution completed.

```
event: tool_finished
data: {"name": "get_portfolio_complete", "duration_ms": 450}
```

##### Event: `content_delta`
Streaming text content from the model.

```
event: content_delta
data: {"delta": "Your portfolio is worth $125,430"}
```

##### Event: `heartbeat`
Periodic keepalive signal (every 15 seconds).

```
event: heartbeat
data: {"timestamp": "2025-08-28T14:30:15Z"}
```

##### Event: `error`
Error occurred during processing.

```
event: error
data: {"message": "Tool execution failed", "code": "TOOL_ERROR"}
```

##### Event: `done`
Response streaming completed.

```
event: done
data: {"total_tokens": 1250, "duration_ms": 3500}
```

#### Status Codes

- `200 OK`: SSE stream established
- `400 Bad Request`: Invalid request format
- `401 Unauthorized`: Invalid authentication
- `404 Not Found`: Conversation not found
- `429 Too Many Requests`: Rate limit exceeded

#### Example Client Code

```javascript
const evtSource = new EventSource('/api/v1/chat/send', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    conversation_id: conversationId,
    text: userMessage
  })
});

evtSource.addEventListener('content_delta', (e) => {
  const data = JSON.parse(e.data);
  appendToResponse(data.delta);
});

evtSource.addEventListener('done', (e) => {
  evtSource.close();
});
```

---

### Get Conversation History

Retrieves all messages in a conversation.

```http
GET /api/v1/chat/conversations/{conversation_id}/messages
```

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| conversation_id | string (UUID) | Conversation ID |

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| limit | integer | 50 | Maximum messages to return |
| offset | integer | 0 | Pagination offset |

#### Response

```json
{
  "messages": [
    {
      "message_id": "550e8400-e29b-41d4-a716-446655440002",
      "role": "user",
      "content": "What's my portfolio value?",
      "created_at": "2025-08-28T14:30:00Z"
    },
    {
      "message_id": "550e8400-e29b-41d4-a716-446655440003",
      "role": "assistant",
      "content": "Your portfolio is worth $125,430 as of 2:30 PM ET today...",
      "created_at": "2025-08-28T14:30:02Z",
      "tool_calls": [
        {
          "name": "get_portfolio_complete",
          "duration_ms": 450
        }
      ]
    }
  ],
  "total_count": 2,
  "has_more": false
}
```

---

### List Conversations

Retrieves all conversations for the authenticated user.

```http
GET /api/v1/chat/conversations
```

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| limit | integer | 20 | Maximum conversations to return |
| offset | integer | 0 | Pagination offset |
| order_by | string | "updated_at" | Sort field: `created_at`, `updated_at`, `message_count` |
| order | string | "desc" | Sort order: `asc`, `desc` |

#### Response

```json
{
  "conversations": [
    {
      "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Portfolio Review Session",
      "mode": "green",
      "message_count": 12,
      "created_at": "2025-08-28T14:00:00Z",
      "updated_at": "2025-08-28T14:30:00Z",
      "last_message_preview": "Your portfolio is worth $125,430..."
    }
  ],
  "total_count": 1,
  "has_more": false
}
```

---

### Delete Conversation

Deletes a conversation and all its messages.

```http
DELETE /api/v1/chat/conversations/{conversation_id}
```

#### Response

```json
{
  "message": "Conversation deleted successfully"
}
```

#### Status Codes

- `200 OK`: Conversation deleted
- `404 Not Found`: Conversation not found
- `401 Unauthorized`: Not authorized to delete

---

## Tool Functions

The agent has access to these tool functions for portfolio analysis:

### get_portfolio_complete

Retrieves complete portfolio snapshot including positions, values, and optional historical data.

**Parameters:**
- `portfolio_id` (string): Portfolio UUID
- `include_holdings` (boolean): Include detailed holdings (default: true)
- `include_timeseries` (boolean): Include historical data (default: false)
- `include_attrib` (boolean): Include attribution data (default: false)

**Limits:**
- Maximum 200 positions returned
- Data truncated with `meta.truncated = true` if exceeded

### get_portfolio_data_quality

Assesses data availability and quality for analysis feasibility.

**Parameters:**
- `portfolio_id` (string): Portfolio UUID
- `check_factors` (boolean): Check factor data availability
- `check_correlations` (boolean): Check correlation data availability

**Returns:**
- Data quality score (0-1)
- Feasibility assessment for various analyses
- Data gap identification

### get_positions_details

Retrieves detailed information about specific positions.

**Parameters:**
- `portfolio_id` (string, optional): Portfolio UUID
- `position_ids` (string, optional): Comma-separated position IDs
- `include_closed` (boolean): Include closed positions

**Requirements:**
- Either `portfolio_id` OR `position_ids` must be provided
- Maximum 200 positions returned

### get_prices_historical

Retrieves historical price data for portfolio positions.

**Parameters:**
- `portfolio_id` (string): Portfolio UUID
- `lookback_days` (integer): Days of history (max: 180, default: 90)
- `max_symbols` (integer): Maximum symbols (max: 5, default: 5)
- `include_factor_etfs` (boolean): Include factor ETFs
- `date_format` (string): "iso" or "unix"

**Business Logic:**
- Automatically selects top N symbols by market value
- Returns `meta.symbols_selected` with chosen symbols

### get_current_quotes

Retrieves real-time market quotes for specified symbols.

**Parameters:**
- `symbols` (string): Comma-separated symbol list
- `include_options` (boolean): Include options data

**Limits:**
- Maximum 5 symbols per request
- Truncates with `meta.truncated = true` if exceeded

### get_factor_etf_prices

Retrieves factor ETF prices for factor analysis.

**Parameters:**
- `lookback_days` (integer): Days of history (max: 180)
- `factors` (string, optional): Comma-separated factor names

**Returns:**
- Historical prices for factor proxy ETFs
- Factor mapping in meta object

---

## Conversation Modes

The agent supports four distinct conversation modes:

### Green Mode (Default)
- **Persona**: Teaching-focused financial analyst
- **Style**: Educational, step-by-step explanations
- **Token Budget**: 2000
- **Use Case**: Users new to investing or wanting to learn

### Blue Mode
- **Persona**: Quantitative analyst
- **Style**: Concise, data-forward, minimal prose
- **Token Budget**: 1500
- **Use Case**: Professional users wanting quick metrics

### Indigo Mode
- **Persona**: Strategic investment analyst
- **Style**: Narrative, forward-looking, thematic
- **Token Budget**: 1800
- **Use Case**: Users wanting strategic insights and market context

### Violet Mode
- **Persona**: Conservative risk analyst
- **Style**: Risk-focused, cautious, compliance-minded
- **Token Budget**: 1700
- **Use Case**: Risk-averse users focused on capital preservation

### Mode Switching

Users can switch modes mid-conversation:

```
/mode blue
```

The agent will acknowledge the change and adjust response style immediately.

---

## Rate Limits

| Endpoint | Rate Limit | Window |
|----------|------------|--------|
| Create Conversation | 10 requests | 1 minute |
| Send Message | 30 requests | 1 minute |
| Get History | 60 requests | 1 minute |
| List Conversations | 30 requests | 1 minute |

Rate limit headers:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Unix timestamp when limit resets

---

## Error Handling

All errors follow a consistent format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid conversation mode specified",
    "details": {
      "field": "mode",
      "allowed_values": ["green", "blue", "indigo", "violet"]
    }
  },
  "request_id": "req_550e8400e29b41d4",
  "timestamp": "2025-08-28T14:30:00Z"
}
```

### Error Codes

| Code | Description | Retryable |
|------|-------------|-----------|
| `VALIDATION_ERROR` | Invalid request parameters | No |
| `AUTH_ERROR` | Authentication failed | No |
| `NOT_FOUND` | Resource not found | No |
| `RATE_LIMIT` | Rate limit exceeded | Yes (with backoff) |
| `TOOL_ERROR` | Tool execution failed | Yes |
| `OPENAI_ERROR` | OpenAI API error | Yes |
| `TIMEOUT` | Request timeout | Yes |
| `INTERNAL_ERROR` | Server error | Yes |

---

## WebSocket Alternative (Future)

For clients that don't support SSE, a WebSocket endpoint is planned:

```
ws://api.sigmasight.com/api/v1/chat/ws
```

This will provide bidirectional communication with the same message format.

---

## SDK Examples

### Python

```python
import httpx
from sseclient import SSEClient

async def chat_with_agent(token: str, conversation_id: str, message: str):
    headers = {'Authorization': f'Bearer {token}'}
    
    async with httpx.AsyncClient() as client:
        # Send message
        response = await client.post(
            'https://api.sigmasight.com/api/v1/chat/send',
            headers=headers,
            json={
                'conversation_id': conversation_id,
                'text': message
            },
            timeout=30.0
        )
        
        # Process SSE stream
        client = SSEClient(response)
        full_response = ""
        
        for event in client.events():
            if event.event == 'content_delta':
                data = json.loads(event.data)
                full_response += data['delta']
            elif event.event == 'done':
                break
                
        return full_response
```

### TypeScript

```typescript
interface ChatMessage {
  conversation_id: string;
  text: string;
}

async function sendMessage(message: ChatMessage): Promise<string> {
  const response = await fetch('/api/v1/chat/send', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(message)
  });
  
  const reader = response.body!.getReader();
  const decoder = new TextDecoder();
  let fullResponse = '';
  
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    
    const chunk = decoder.decode(value);
    // Parse SSE and extract content_delta events
    fullResponse += parseSSE(chunk);
  }
  
  return fullResponse;
}
```

---

## Testing

### Health Check

```http
GET /api/v1/health
```

Returns:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "model": "gpt-5-2025-08-07"
}
```

### Test Conversation

A test portfolio is available for development:

- **Portfolio ID**: `51134ffd-2f13-49bd-b1f5-0c327e801b69`
- **User**: `demo_individual@sigmasight.com`
- **Password**: `demo12345`

---

## Changelog

### Version 1.0.0 (2025-08-28)
- Initial release
- 4 conversation modes
- 6 tool functions
- SSE streaming support
- JWT + Cookie dual authentication