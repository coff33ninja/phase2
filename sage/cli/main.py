"""CLI interface for Sage."""
import click
import asyncio
from rich.console import Console
from rich.markdown import Markdown
from loguru import logger

from config import config
from gemini_client import GeminiClient
from context import ContextAggregator
from conversation import SessionManager
from prompts import PromptBuilder

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Sage - Gemini 2.5 Flash Integration for System Intelligence."""
    pass


@cli.command()
@click.argument("query", required=False)
@click.option("--session-id", default=None, help="Session ID for conversation")
def query(query: str, session_id: str):
    """Ask Sage a question about your system."""
    if not query:
        query = click.prompt("What would you like to know?")
    
    asyncio.run(_handle_query(query, session_id))


async def _handle_query(query: str, session_id: str = None):
    """Handle a query asynchronously."""
    try:
        # Initialize components
        client = GeminiClient()
        context_agg = ContextAggregator()
        session_mgr = SessionManager()
        
        # Generate session ID if not provided
        if not session_id:
            from datetime import datetime
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            session_mgr.create_session(session_id)
        
        console.print(f"\n[bold cyan]Sage:[/bold cyan] Analyzing your system...\n")
        
        # Get context
        context = await context_agg.get_system_context()
        
        # Build prompt
        prompt = PromptBuilder.build_analysis_prompt(
            query=query,
            system_state=context.get("system_state"),
            patterns=context.get("patterns"),
            anomalies=context.get("anomalies"),
            predictions=context.get("predictions"),
            training_status=context.get("training_status")
        )
        
        # Generate response
        result = await client.generate_response(prompt, context=context)
        
        # Save to session
        session_mgr.add_message(session_id, "user", query)
        session_mgr.add_message(
            session_id,
            "assistant",
            result["response"],
            context=context,
            tokens_used=result["total_tokens"]
        )
        
        # Display response
        console.print(Markdown(result["response"]))
        console.print(
            f"\n[dim]Tokens: {result['total_tokens']} | "
            f"Session: {session_id}[/dim]\n"
        )
        
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        console.print("\n[yellow]Please set GEMINI_API_KEY in .env file[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        logger.error(f"Query error: {e}")


@cli.command()
def status():
    """Show Sage status and configuration."""
    asyncio.run(_show_status())


async def _show_status():
    """Show comprehensive system status."""
    import sqlite3
    from datetime import datetime, timedelta
    from rich.table import Table
    from rich.panel import Panel
    
    console.print("\n[bold cyan]" + "="*63 + "[/bold cyan]")
    console.print("[bold cyan]" + " "*18 + "Phase 2 System Status" + " "*24 + "[/bold cyan]")
    console.print("[bold cyan]" + "="*63 + "[/bold cyan]\n")
    
    # Sage Configuration
    console.print("[bold yellow]AI Sage Configuration[/bold yellow]")
    console.print(f"  Model: [green]{config.gemini_model}[/green]")
    console.print(f"  API Key: [{'green' if config.gemini_api_key else 'red'}]"
                 f"{'OK Configured' if config.gemini_api_key else 'X Not Set'}[/]")
    console.print(f"  Temperature: {config.temperature}")
    console.print(f"  Max Tokens: {config.max_output_tokens}\n")
    
    # Sentinel Status
    console.print("[bold yellow]Data Sentinel (Data Collection)[/bold yellow]")
    if config.sentinel_db_path.exists():
        try:
            conn = sqlite3.connect(config.sentinel_db_path)
            cursor = conn.cursor()
            
            # Get snapshot count
            cursor.execute("SELECT COUNT(*) FROM system_snapshots")
            snapshot_count = cursor.fetchone()[0]
            
            # Get time range
            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM system_snapshots")
            min_time, max_time = cursor.fetchone()
            
            # Calculate collection duration
            if min_time and max_time:
                start = datetime.fromisoformat(min_time)
                end = datetime.fromisoformat(max_time)
                duration = end - start
                hours = duration.total_seconds() / 3600
                
                console.print(f"  Status: [green]OK Active[/green]")
                console.print(f"  Snapshots: [cyan]{snapshot_count:,}[/cyan]")
                console.print(f"  Duration: [cyan]{hours:.1f} hours[/cyan]")
                console.print(f"  Started: [dim]{start.strftime('%Y-%m-%d %H:%M:%S')}[/dim]")
                console.print(f"  Latest: [dim]{end.strftime('%Y-%m-%d %H:%M:%S')}[/dim]")
            else:
                console.print(f"  Status: [yellow]!! No data yet[/yellow]")
            
            conn.close()
        except Exception as e:
            console.print(f"  Status: [red]X Error: {e}[/red]")
    else:
        console.print(f"  Status: [red]X Database not found[/red]")
        console.print(f"  Path: [dim]{config.sentinel_db_path}[/dim]")
    
    console.print()
    
    # Oracle Training Readiness
    console.print("[bold yellow]Oracle (ML Training)[/bold yellow]")
    if config.oracle_patterns_db_path.exists():
        console.print(f"  Status: [green]OK Trained[/green]")
        console.print(f"  Database: [green]Found[/green]")
    else:
        console.print(f"  Status: [yellow].. Awaiting Training[/yellow]")
        
        # Calculate training readiness
        if config.sentinel_db_path.exists():
            try:
                conn = sqlite3.connect(config.sentinel_db_path)
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM system_snapshots")
                snapshot_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM system_snapshots")
                min_time, max_time = cursor.fetchone()
                
                if min_time and max_time:
                    start = datetime.fromisoformat(min_time)
                    end = datetime.fromisoformat(max_time)
                    duration_hours = (end - start).total_seconds() / 3600
                    
                    # Training requirements
                    MIN_HOURS = 1.0  # Minimum 1 hour of data
                    MIN_SAMPLES = 1000  # Minimum 1000 snapshots
                    RECOMMENDED_HOURS = 24.0  # Recommended 24 hours
                    
                    hours_progress = min(100, (duration_hours / MIN_HOURS) * 100)
                    samples_progress = min(100, (snapshot_count / MIN_SAMPLES) * 100)
                    
                    console.print(f"\n  [bold]Training Readiness:[/bold]")
                    
                    # Time progress bar
                    time_bar = "█" * int(hours_progress / 5) + "░" * (20 - int(hours_progress / 5))
                    time_bar = "#" * int(hours_progress / 5) + "-" * (20 - int(hours_progress / 5))
                    time_status = "✓" if duration_hours >= MIN_HOURS else "⏳"
                    time_status = "OK" if duration_hours >= MIN_HOURS else ".."
                    console.print(f"  {time_status} Time: [{time_bar}] {duration_hours:.1f}h / {MIN_HOURS}h minimum")
                    
                    # Samples progress bar
                    samples_bar = "█" * int(samples_progress / 5) + "░" * (20 - int(samples_progress / 5))
                    samples_bar = "#" * int(samples_progress / 5) + "-" * (20 - int(samples_progress / 5))
                    samples_status = "✓" if snapshot_count >= MIN_SAMPLES else "⏳"
                    samples_status = "OK" if snapshot_count >= MIN_SAMPLES else ".."
                    console.print(f"  {samples_status} Data: [{samples_bar}] {snapshot_count} / {MIN_SAMPLES} samples")
                    
                    # Overall readiness
                    if duration_hours >= MIN_HOURS and snapshot_count >= MIN_SAMPLES:
                        console.print(f"\n  [bold green]OK Ready for training![/bold green]")
                        console.print(r"  [dim]Run: cd oracle && .\.venv\Scripts\python.exe main.py train[/dim]")
                    else:
                        time_remaining = max(0, MIN_HOURS - duration_hours)
                        samples_remaining = max(0, MIN_SAMPLES - snapshot_count)
                        console.print(f"\n  [yellow].. Keep collecting data...[/yellow]")
                        if time_remaining > 0:
                            console.print(f"  [dim]Need {time_remaining:.1f} more hours[/dim]")
                        if samples_remaining > 0:
                            console.print(f"  [dim]Need {samples_remaining} more samples[/dim]")
                    
                    # Recommendation
                    if duration_hours < RECOMMENDED_HOURS:
                        console.print(f"\n  [dim]Tip: {RECOMMENDED_HOURS}h of data recommended for best results[/dim]")
                
                conn.close()
            except Exception as e:
                console.print(f"  Error checking readiness: {e}")
        else:
            console.print(f"  [yellow]!! Sentinel must be running first[/yellow]")
    
    console.print()
    
    # Guardian Status
    console.print("[bold yellow]Guardian (Auto-Tuning)[/bold yellow]")
    console.print(f"  Status: [cyan]Ready (on-demand)[/cyan]")
    console.print(f"  Profiles: Gaming, Work, Power Saver\n")
    
    # Nexus Status
    console.print("[bold yellow]Nexus (Dashboard)[/bold yellow]")
    console.print(f"  URL: [cyan]http://localhost:8001[/cyan]")
    console.print(f"  API Docs: [cyan]http://localhost:8001/docs[/cyan]\n")
    
    console.print("[bold cyan]" + "="*63 + "[/bold cyan]\n")


@cli.command()
@click.option("--limit", default=10, help="Number of sessions to show")
def history(limit: int):
    """Show conversation history."""
    session_mgr = SessionManager()
    sessions = session_mgr.get_recent_sessions(limit)
    
    if not sessions:
        console.print("\n[yellow]No conversation history found[/yellow]\n")
        return
    
    console.print(f"\n[bold cyan]Recent Sessions[/bold cyan]\n")
    
    for session in sessions:
        console.print(f"[bold]{session['session_id']}[/bold]")
        console.print(f"  Messages: {session['message_count']}")
        console.print(f"  Updated: {session['updated_at']}")
        console.print()


@cli.command()
@click.argument("session-id")
@click.option("--limit", default=50, help="Number of messages to show")
def show(session_id: str, limit: int):
    """Show messages from a specific session."""
    session_mgr = SessionManager()
    messages = session_mgr.get_session_history(session_id, limit)
    
    if not messages:
        console.print(f"\n[yellow]No messages found for session: {session_id}[/yellow]\n")
        return
    
    console.print(f"\n[bold cyan]Session: {session_id}[/bold cyan]\n")
    
    for msg in messages:
        role_color = "green" if msg["role"] == "user" else "cyan"
        console.print(f"[bold {role_color}]{msg['role'].title()}:[/bold {role_color}]")
        console.print(msg["content"])
        console.print(f"[dim]{msg['created_at']}[/dim]\n")


if __name__ == "__main__":
    cli()
