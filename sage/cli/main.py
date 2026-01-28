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
            predictions=context.get("predictions")
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
    console.print("\n[bold cyan]Sage Status[/bold cyan]\n")
    
    console.print(f"Model: [green]{config.gemini_model}[/green]")
    console.print(f"API Key: [green]{'Set' if config.gemini_api_key else 'Not Set'}[/green]")
    console.print(f"Temperature: {config.temperature}")
    console.print(f"Max Output Tokens: {config.max_output_tokens}")
    
    console.print(f"\n[bold]Databases:[/bold]")
    console.print(f"Conversations: {config.conversation_db_path}")
    console.print(f"Sentinel: {config.sentinel_db_path}")
    console.print(f"Oracle: {config.oracle_patterns_db_path}")
    
    console.print(f"\n[bold]Integration:[/bold]")
    console.print(f"Sentinel: [{'green' if config.sentinel_db_path.exists() else 'red'}]"
                 f"{'Connected' if config.sentinel_db_path.exists() else 'Not Found'}[/]")
    console.print(f"Oracle: [{'green' if config.oracle_patterns_db_path.exists() else 'red'}]"
                 f"{'Connected' if config.oracle_patterns_db_path.exists() else 'Not Found'}[/]")
    
    console.print()


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
