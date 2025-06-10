# AI Assistant with Metrics Tracking

This project implements an AI voice assistant with real-time performance monitoring and metrics tracking capabilities. The assistant uses LiveKit for real-time communication and includes features like noise cancellation, speech-to-text, text-to-speech, and comprehensive metrics reporting.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A LiveKit server instance
- Environment variables for API keys (see Configuration section)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-directory>
```

2. Create and activate a virtual environment (recommended):
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/MacOS
python -m venv venv
source venv/bin/activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
pip install pandas openpyxl  # Additional required packages
```

## Configuration

Create a `.env` file in the project root directory with the following environment variables:

```env
LIVEKIT_URL=your_livekit_server_url
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
OPENAI_API_KEY=your_openai_api_key
DEEPGRAM_API_KEY=your_deepgram_api_key
```

## Running the Application

The application consists of two main components that need to be run in separate terminal windows:

1. Start the AI Assistant Agent:
```bash
python entry.py
```
This will start the agent in the room "my-assistant-room" with metrics tracking enabled.

2. In a separate terminal, run the call script to connect to the room:
```bash
python call.py
```

## Features

- Real-time voice communication
- Noise cancellation
- Speech-to-Text (STT) with Deepgram
- Text-to-Speech (TTS)
- Large Language Model (LLM) integration
- Comprehensive metrics tracking:
  - LLM Performance Metrics
  - TTS Performance Metrics
  - STT Performance Metrics
  - End-of-Utterance Metrics
- Real-time console output with rich formatting
- Automatic Excel export with multiple sheets
- Auto-save functionality (every 3 records)
- Summary statistics

## Metrics Reports

Metrics are automatically saved to Excel files in the `./metrics_reports/` directory. The reports include:
- Detailed performance metrics
- Multiple sheets for different metric types
- Summary statistics
- Timestamp-based tracking

## Troubleshooting

1. If you see "Missing required packages!" error:
   - Run: `pip install pandas openpyxl`

2. If metrics are showing as 0:
   - This is normal for STT/EOU metrics depending on your configuration
   - Check your API keys and environment variables
   - Ensure your LiveKit server is running and accessible

3. Connection issues:
   - Verify your LiveKit server URL and credentials
   - Check your network connection
   - Ensure both entry.py and call.py are running

## License

[Add your license information here]

## Contributing

[Add contribution guidelines if applicable] 