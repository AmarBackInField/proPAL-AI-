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

load_dotenv()

console = Console()


class MetricsAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""
                You are a helpful AI assistant that can help with various tasks and questions.
            """,
            stt=deepgram.STT(model="nova-2", language="en"),
            llm=openai.LLM(model="gpt-4o-mini"),
            tts=cartesia.TTS(model="sonic-2", voice="f786b574-daa5-4673-aa0c-cbe3e8534c02"),
            vad=silero.VAD.load()
        )
        
        # Initialize metrics storage
        self.llm_metrics_data = []
        self.tts_metrics_data = []
        self.stt_metrics_data = []
        self.eou_metrics_data = []
        
        # Create metrics directory if it doesn't exist
        self.metrics_dir = Path("metrics_reports")
        self.metrics_dir.mkdir(exist_ok=True)
        
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.excel_filename = self.metrics_dir / f"agent_metrics_{timestamp}.xlsx"

    def save_to_excel(self):
        """Save all collected metrics to Excel file with multiple sheets"""
        try:
            with pd.ExcelWriter(self.excel_filename, engine='openpyxl') as writer:
                # Save LLM metrics
                if self.llm_metrics_data:
                    llm_df = pd.DataFrame(self.llm_metrics_data)
                    llm_df.to_excel(writer, sheet_name='LLM_Metrics', index=False)
                    console.print(f"[green]✅ Saved {len(self.llm_metrics_data)} LLM metrics records[/green]")
                
                # Save TTS metrics
                if self.tts_metrics_data:
                    tts_df = pd.DataFrame(self.tts_metrics_data)
                    tts_df.to_excel(writer, sheet_name='TTS_Metrics', index=False)
                    console.print(f"[blue]✅ Saved {len(self.tts_metrics_data)} TTS metrics records[/blue]")
                
                # Save STT metrics
                if self.stt_metrics_data:
                    stt_df = pd.DataFrame(self.stt_metrics_data)
                    stt_df.to_excel(writer, sheet_name='STT_Metrics', index=False)
                    console.print(f"[cyan]✅ Saved {len(self.stt_metrics_data)} STT metrics records[/cyan]")
                
                # Save EOU metrics
                if self.eou_metrics_data:
                    eou_df = pd.DataFrame(self.eou_metrics_data)
                    eou_df.to_excel(writer, sheet_name='EOU_Metrics', index=False)
                    console.print(f"[yellow]✅ Saved {len(self.eou_metrics_data)} EOU metrics records[/yellow]")
                
                # Create summary sheet
                summary_data = {
                    'Metric Type': ['LLM', 'TTS', 'STT', 'EOU'],
                    'Total Records': [
                        len(self.llm_metrics_data),
                        len(self.tts_metrics_data), 
                        len(self.stt_metrics_data),
                        len(self.eou_metrics_data)
                    ],
                    'Report Generated': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')] * 4,
                    'Configuration Notes': [
                        'LLM metrics from GPT-4o-mini',
                        'TTS metrics from Cartesia Sonic-2',
                        'STT metrics from Deepgram Nova-2 (may be 0 with some configs)',
                        'EOU metrics require VAD/turn detection (may be 0)'
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
            console.print(f"[bold green]📊 Excel report saved to: {self.excel_filename}[/bold green]")
            
        except Exception as e:
            console.print(f"[red]❌ Error saving Excel file: {str(e)}[/red]")

    def handle_metrics(self, metrics):
        """Handle different types of metrics"""
        if isinstance(metrics, LLMMetrics):
            self.handle_llm_metrics(metrics)
        elif isinstance(metrics, TTSMetrics):
            self.handle_tts_metrics(metrics)
        elif isinstance(metrics, STTMetrics):
            self.handle_stt_metrics(metrics)
        elif isinstance(metrics, EOUMetrics):
            self.handle_eou_metrics(metrics)
        else:
            console.print(f"[dim]🔍 Unknown metrics type: {type(metrics)}[/dim]")

    def handle_llm_metrics(self, metrics: LLMMetrics) -> None:
        # Store metrics data
        metrics_dict = {
            'timestamp': datetime.fromtimestamp(metrics.timestamp).strftime('%Y-%m-%d %H:%M:%S'),
            'type': str(metrics.type),
            'label': str(metrics.label),
            'request_id': str(metrics.request_id),
            'duration_seconds': round(metrics.duration, 4),
            'time_to_first_token_seconds': round(metrics.ttft, 4),
            'cancelled': metrics.cancelled,
            'completion_tokens': metrics.completion_tokens,
            'prompt_tokens': metrics.prompt_tokens,
            'total_tokens': metrics.total_tokens,
            'tokens_per_second': round(metrics.tokens_per_second, 2),
            'speech_id': getattr(metrics, 'speech_id', 'N/A')
        }
        self.llm_metrics_data.append(metrics_dict)
        
        # Display table
        table = Table(
            title="[bold red]LLM Metrics Report[/bold red]",
            box=box.ROUNDED,
            highlight=True,
            show_header=True,
            header_style="bold cyan"
        )
        
        table.add_column("Metric", style="bold green")
        table.add_column("Value", style="yellow")
        
        table.add_row("Type", str(metrics.type))
        table.add_row("Label", str(metrics.label))
        table.add_row("Request ID", str(metrics.request_id))
        table.add_row("Timestamp", metrics_dict['timestamp'])
        table.add_row("Duration", f"[white]{metrics_dict['duration_seconds']}[/white]s")
        table.add_row("Time to First Token", f"[white]{metrics_dict['time_to_first_token_seconds']}[/white]s")
        table.add_row("Cancelled", "✓" if metrics.cancelled else "✗")
        table.add_row("Completion Tokens", str(metrics.completion_tokens))
        table.add_row("Prompt Tokens", str(metrics.prompt_tokens))
        table.add_row("Total Tokens", str(metrics.total_tokens))
        table.add_row("Tokens/Second", str(metrics_dict['tokens_per_second']))
        table.add_row("Speech ID", str(metrics_dict['speech_id']))
        
        console.print("\n")
        console.print(table)
        console.print(f"[dim]📝 LLM Record #{len(self.llm_metrics_data)} saved[/dim]")
        console.print("\n")
        
        # Auto-save every 3 records
        if len(self.llm_metrics_data) % 3 == 0:
            self.save_to_excel()
    
    def handle_tts_metrics(self, metrics: TTSMetrics) -> None:
        # Store metrics data
        metrics_dict = {
            'timestamp': datetime.fromtimestamp(metrics.timestamp).strftime('%Y-%m-%d %H:%M:%S'),
            'type': str(metrics.type),
            'label': str(metrics.label),
            'request_id': str(metrics.request_id),
            'ttfb_seconds': round(metrics.ttfb, 4),
            'duration_seconds': round(metrics.duration, 4),
            'audio_duration_seconds': round(metrics.audio_duration, 4),
            'cancelled': metrics.cancelled,
            'characters_count': metrics.characters_count,
            'streamed': metrics.streamed,
            'speech_id': str(getattr(metrics, 'speech_id', 'N/A'))
        }
        self.tts_metrics_data.append(metrics_dict)
        
        # Display table
        table = Table(
            title="[bold blue]TTS Metrics Report[/bold blue]",
            box=box.ROUNDED,
            highlight=True,
            show_header=True,
            header_style="bold cyan"
        )
        
        table.add_column("Metric", style="bold green")
        table.add_column("Value", style="yellow")
        
        table.add_row("Type", str(metrics.type))
        table.add_row("Label", str(metrics.label))
        table.add_row("Request ID", str(metrics.request_id))
        table.add_row("Timestamp", metrics_dict['timestamp'])
        table.add_row("TTFB", f"[white]{metrics_dict['ttfb_seconds']}[/white]s")
        table.add_row("Duration", f"[white]{metrics_dict['duration_seconds']}[/white]s")
        table.add_row("Audio Duration", f"[white]{metrics_dict['audio_duration_seconds']}[/white]s")
        table.add_row("Cancelled", "✓" if metrics.cancelled else "✗")
        table.add_row("Characters Count", str(metrics.characters_count))
        table.add_row("Streamed", "✓" if metrics.streamed else "✗")
        table.add_row("Speech ID", str(metrics_dict['speech_id']))
        
        console.print("\n")
        console.print(table)
        console.print(f"[dim]📝 TTS Record #{len(self.tts_metrics_data)} saved[/dim]")
        console.print("\n")
        
        # Auto-save every 3 records
        if len(self.tts_metrics_data) % 3 == 0:
            self.save_to_excel()

    def handle_stt_metrics(self, metrics: STTMetrics) -> None:
        # Store metrics data
        metrics_dict = {
            'timestamp': datetime.fromtimestamp(metrics.timestamp).strftime('%Y-%m-%d %H:%M:%S'),
            'type': str(metrics.type),
            'label': str(metrics.label),
            'request_id': str(metrics.request_id),
            'duration_seconds': round(metrics.duration, 4),
            'audio_duration_seconds': round(metrics.audio_duration, 4),
            'streamed': metrics.streamed,
            'speech_id': str(getattr(metrics, 'speech_id', 'N/A')),
            'error': str(getattr(metrics, 'error', 'None'))
        }
        self.stt_metrics_data.append(metrics_dict)
        
        # Display table
        table = Table(
            title="[bold green]STT Metrics Report[/bold green]",
            box=box.ROUNDED,
            highlight=True,
            show_header=True,
            header_style="bold cyan"
        )
        
        table.add_column("Metric", style="bold green")
        table.add_column("Value", style="yellow")
        
        table.add_row("Type", str(metrics.type))
        table.add_row("Label", str(metrics.label))
        table.add_row("Request ID", str(metrics.request_id))
        table.add_row("Timestamp", metrics_dict['timestamp'])
        table.add_row("Duration", f"[white]{metrics_dict['duration_seconds']}[/white]s")
        table.add_row("Audio Duration", f"[white]{metrics_dict['audio_duration_seconds']}[/white]s")
        table.add_row("Streamed", "✓" if metrics.streamed else "✗")
        table.add_row("Speech ID", str(metrics_dict['speech_id']))
        table.add_row("Error", str(metrics_dict['error']))
        
        console.print("\n")
        console.print(table)
        console.print(f"[dim]📝 STT Record #{len(self.stt_metrics_data)} saved[/dim]")
        console.print("\n")
        
        # Auto-save every 3 records
        if len(self.stt_metrics_data) % 3 == 0:
            self.save_to_excel()
    
    def handle_eou_metrics(self, metrics: EOUMetrics) -> None:
        # Store metrics data
        metrics_dict = {
            'timestamp': datetime.fromtimestamp(metrics.timestamp).strftime('%Y-%m-%d %H:%M:%S'),
            'type': str(metrics.type),
            'end_of_utterance_delay_seconds': round(metrics.end_of_utterance_delay, 4),
            'transcription_delay_seconds': round(metrics.transcription_delay, 4),
            'on_user_turn_completed_delay_seconds': round(getattr(metrics, 'on_user_turn_completed_delay', 0), 4),
            'speech_id': str(metrics.speech_id)
        }
        self.eou_metrics_data.append(metrics_dict)
        
        # Display table
        table = Table(
            title="[bold yellow]End of Utterance Metrics Report[/bold yellow]",
            box=box.ROUNDED,
            highlight=True,
            show_header=True,
            header_style="bold cyan"
        )
        
        table.add_column("Metric", style="bold green")
        table.add_column("Value", style="yellow")
        
        table.add_row("Type", str(metrics.type))
        table.add_row("Timestamp", metrics_dict['timestamp'])
        table.add_row("End of Utterance Delay", f"[white]{metrics_dict['end_of_utterance_delay_seconds']}[/white]s")
        table.add_row("Transcription Delay", f"[white]{metrics_dict['transcription_delay_seconds']}[/white]s")
        table.add_row("Turn Completed Delay", f"[white]{metrics_dict['on_user_turn_completed_delay_seconds']}[/white]s")
        table.add_row("Speech ID", str(metrics.speech_id))
        
        console.print("\n")
        console.print(table)
        console.print(f"[dim]📝 EOU Record #{len(self.eou_metrics_data)} saved[/dim]")
        console.print("\n")
        
        # Auto-save every 3 records
        if len(self.eou_metrics_data) % 3 == 0:
            self.save_to_excel()

    async def finalize_metrics(self):
        """Final save when agent shuts down"""
        console.print("[bold cyan]🔄 Finalizing metrics and saving to Excel...[/bold cyan]")
        self.save_to_excel()
        
        # Print final summary
        total_records = (len(self.llm_metrics_data) + len(self.tts_metrics_data) + 
                        len(self.stt_metrics_data) + len(self.eou_metrics_data))
        
        console.print(f"[bold green]📊 Final Summary:[/bold green]")
        console.print(f"  • LLM Metrics: {len(self.llm_metrics_data)} records")
        console.print(f"  • TTS Metrics: {len(self.tts_metrics_data)} records")
        console.print(f"  • STT Metrics: {len(self.stt_metrics_data)} records")
        console.print(f"  • EOU Metrics: {len(self.eou_metrics_data)} records")
        console.print(f"  • Total Records: {total_records}")
        console.print(f"[bold green]📁 Excel file: {self.excel_filename}[/bold green]")
        
        # Print diagnostic info if no STT/EOU metrics
        if len(self.stt_metrics_data) == 0:
            console.print("[yellow]ℹ️  No STT metrics: This is normal with some configurations[/yellow]")
        if len(self.eou_metrics_data) == 0:
            console.print("[yellow]ℹ️  No EOU metrics: Requires VAD-based turn detection[/yellow]")

