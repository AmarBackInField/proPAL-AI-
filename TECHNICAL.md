# Technical Documentation: AI Assistant Architecture

This document explains the technical architecture and relationship between the main components of the AI Assistant system: `entry.py` (Agent Server) and `call.py` (Call Initiator).

## System Architecture Overview

The system operates as a client-server architecture with two main components:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  entry.py       │◄────┤  LiveKit        │◄────┤  call.py        │
│  (Agent Server) │     │  Server         │     │  (Call Client)  │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Component Details

### 1. entry.py (Agent Server)
- **Role**: Acts as the AI assistant server that processes and responds to voice interactions
- **Key Responsibilities**:
  - Initializes the AI assistant agent with metrics tracking
  - Manages the LiveKit room ("my-assistant-room")
  - Handles real-time voice processing
  - Collects and stores performance metrics
  - Manages noise cancellation and voice processing
  - Generates AI responses
  - Exports metrics to Excel reports

- **Key Features**:
  - Speech-to-Text (STT) processing
  - Text-to-Speech (TTS) generation
  - LLM integration for response generation
  - Real-time metrics collection
  - Noise cancellation
  - Participant connection management

### 2. call.py (Call Client)
- **Role**: Initiates outbound calls and connects callers to the AI assistant
- **Key Responsibilities**:
  - Establishes SIP connections
  - Creates participants in the LiveKit room
  - Manages outbound call connections
  - Handles call setup and teardown

- **Key Features**:
  - SIP trunk integration
  - Outbound call initiation
  - Participant creation in LiveKit room
  - Connection status monitoring
  - Error handling and reporting

## Interaction Flow

1. **Initialization**:
   ```
   entry.py starts → Creates LiveKit room → Waits for participants
   ```

2. **Call Initiation**:
   ```
   call.py starts → Connects to LiveKit → Creates SIP participant → Joins room
   ```

3. **Communication Flow**:
   ```
   Phone Caller → SIP Trunk → LiveKit Server → AI Assistant (entry.py)
   AI Assistant → LiveKit Server → SIP Trunk → Phone Caller
   ```

## Room Management

- Both components use the same room name: "my-assistant-room"
- `entry.py` creates and manages the room
- `call.py` connects participants to the existing room
- The room acts as the central communication hub

## Configuration Requirements

Both components require the following environment variables:
```env
LIVEKIT_URL=your_livekit_server_url
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
```

Additional requirements for `call.py`:
- Valid SIP trunk ID
- Properly formatted phone number
- Krisp noise suppression enabled

## Error Handling

### entry.py Errors
- Room creation failures
- Agent initialization issues
- Metrics collection problems
- Voice processing errors

### call.py Errors
- SIP connection failures
- Invalid phone numbers
- Room access issues
- Participant creation problems

## Best Practices

1. **Startup Order**:
   - Always start `entry.py` first
   - Wait for "Agent is ready" message
   - Then start `call.py`

2. **Monitoring**:
   - Watch console output from both components
   - Check metrics reports for performance data
   - Monitor LiveKit server status

3. **Troubleshooting**:
   - Verify environment variables
   - Check network connectivity
   - Ensure proper startup order
   - Monitor error messages in both consoles

## Metrics and Reporting

- Metrics are collected by `entry.py`
- Reports are automatically generated in `./metrics_reports/`
- Metrics include:
  - LLM performance
  - TTS latency
  - STT accuracy
  - End-of-utterance detection
  - Connection quality

## Security Considerations

1. **API Keys**:
   - Store securely in `.env` file
   - Never commit to version control
   - Rotate keys regularly

2. **Room Access**:
   - Room name should be consistent
   - Participant identities are tracked
   - SIP trunk access is authenticated

3. **Data Protection**:
   - Voice data is processed in real-time
   - Metrics are stored locally
   - No persistent storage of voice data 