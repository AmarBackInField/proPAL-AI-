from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, MetricsCollectedEvent
from livekit.plugins import (
    openai,
    cartesia,
    deepgram,
    noise_cancellation,
    silero,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit.agents.metrics import STTMetrics, TTSMetrics, EOUMetrics, LLMMetrics
import asyncio
from rich.console import Console
from rich.table import Table
from rich import box
from datetime import datetime
import pandas as pd
import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import box
from datetime import datetime
import pandas as pd
import os
from pathlib import Path

load_dotenv()

console = Console()
from agent.agent import MetricsAgent

async def entrypoint(ctx: agents.JobContext):
    """
    Main entrypoint for the voice assistant with metrics tracking and Excel export
    """
    print(f"Agent connected to room: {ctx.room.name}")
    
    # Create the metrics agent
    metrics_agent = MetricsAgent()
    
    # Print Excel file location
    console.print(f"[bold blue]Metrics will be saved to: {metrics_agent.excel_filename}[/bold blue]")
    
    # Create session with turn detection configured for EOU metrics
    session = AgentSession(
        stt=metrics_agent.stt,
        llm=metrics_agent.llm,
        tts=metrics_agent.tts,
        vad=metrics_agent.vad,
        turn_detection=MultilingualModel(),  # This should enable EOU metrics
    )
    
    # Set up metrics collection from the session (this is the key fix!)
    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        console.print(f"[dim]🔍 Collected metrics: {type(ev.metrics).__name__}[/dim]")
        metrics_agent.handle_metrics(ev.metrics)
    
    await session.start(
        room=ctx.room,
        agent=metrics_agent,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(), 
        ),
    )
    
    await ctx.connect()
    
    # Set up room event handlers
    @ctx.room.on("participant_connected")
    def on_participant_connected(participant):
        print(f"Participant connected: {participant.identity}")
        console.print(f"[bold green]New participant joined:[/bold green] {participant.identity}")
        
    @ctx.room.on("participant_disconnected") 
    def on_participant_disconnected(participant):
        print(f"Participant disconnected: {participant.identity}")
        console.print(f"[bold red]Participant left:[/bold red] {participant.identity}")
        # Save metrics when participant disconnects
        asyncio.create_task(metrics_agent.finalize_metrics())
    
    # Wait for participants to join
    print("Waiting for participants to join...")
    await asyncio.sleep(2)
    
    # Generate initial greeting
    print("Generating initial greeting...")
    await session.generate_reply(
        instructions="Greet the user warmly and introduce yourself as an AI assistant with metrics tracking capabilities. Say 'Hello! I'm your AI assistant with real-time performance monitoring and Excel reporting. How can I help you today?'"
    )
    
    print("✅ Agent is ready and monitoring metrics!")
    console.print("[bold green]AI Assistant is live with metrics tracking and Excel export enabled![/bold green]")
    console.print("[dim]STT/EOU metrics may be 0 depending on configuration - this is normal[/dim]")
    
    try:
        # Keep the agent running
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        console.print("[bold yellow]Shutting down agent...[/bold yellow]")
        await metrics_agent.finalize_metrics()
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        await metrics_agent.finalize_metrics()


if __name__ == "__main__":
    print("=" * 70)
    print("Starting AI Assistant Agent with Metrics Tracking & Excel Export")
    print("=" * 70)
    print("Features enabled:")
    print("  • LLM Performance Metrics")
    print("  • TTS Performance Metrics") 
    print("  • STT Performance Metrics (config dependent)")
    print("  • End-of-Utterance Metrics (VAD dependent)")
    print("  • Real-time Rich Console Output")
    print("  • Excel Export with Multiple Sheets")
    print("  • Auto-save every 3 records")
    print("  • Summary Sheet with Statistics")
    print("=" * 70)
    print("Room name: my-assistant-room")
    print("Tip: Run the call script in another terminal after this starts")
    print("Excel files will be saved in: ./metrics_reports/")
    print("Note: STT/EOU metrics depend on your specific configuration")
    print("=" * 70)
    
    # Install required packages reminder
    try:
        import pandas as pd
        import openpyxl
    except ImportError:
        print("Missing required packages!")
        print("Please install: pip install pandas openpyxl")
        exit(1)
    
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))