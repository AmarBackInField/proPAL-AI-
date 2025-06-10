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

## Metrics



![Screenshot 2025-06-10 112300](https://github.com/user-attachments/assets/4905486c-f1d2-4356-8f4e-cb9f0b99d86c)
![Screenshot 2025-06-10 112309](https://github.com/user-attachments/assets/9ed9b9be-5d29-4bcd-9f2e-e8f1a07559a2)
![Screenshot 2025-06-10 112322](https://github.com/user-attachments/assets/29101c84-55a8-4a98-a827-f9044b598bd2)
![Screenshot 2025-06-10 102244](https://github.com/user-attachments/assets/95bf55ea-d449-43f7-ba70-4d5d3bc9e7d1)

## Final Result:-

*total_latency = eou.end_of_utterance_delay + llm.ttft + tts.ttfb*

![image](https://github.com/user-attachments/assets/43c8dc75-b8c0-4d71-8441-089118036b71)


## Video demo Link

https://drive.google.com/file/d/1UXeviEbYPHKgD1jUWfyc5Ugb7dVtrLBI/view?usp=sharing




