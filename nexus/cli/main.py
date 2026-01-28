"""CLI interface for Nexus."""
import click
from rich.console import Console
import uvicorn

from config import config

console = Console()


@click.group()
def cli():
    """Nexus - Dashboard & Interface.
    
    Central hub for Phase 2 system monitoring and control.
    """
    pass


@cli.command()
@click.option('--host', default=None, help='Server host')
@click.option('--port', default=None, type=int, help='Server port')
@click.option('--reload/--no-reload', default=None, help='Auto-reload on code changes')
def serve(host, port, reload):
    """Start the Nexus dashboard server.
    
    Examples:
        nexus serve
        nexus serve --host 0.0.0.0 --port 8080
        nexus serve --no-reload
    """
    console.print("\n[bold cyan]Starting Nexus Dashboard...[/bold cyan]\n")
    
    # Use config defaults if not specified
    server_host = host or config.host
    server_port = port or config.port
    server_reload = reload if reload is not None else config.reload
    
    console.print(f"[green]Server:[/green] http://{server_host}:{server_port}")
    console.print(f"[green]API Docs:[/green] http://{server_host}:{server_port}/docs")
    console.print(f"[green]WebSocket:[/green] ws://{server_host}:{server_port}/ws/metrics\n")
    
    uvicorn.run(
        "main:app",
        host=server_host,
        port=server_port,
        reload=server_reload,
        log_level=config.log_level.lower()
    )


@cli.command()
def status():
    """Check Nexus and component status."""
    console.print("\n[bold cyan]Nexus Status[/bold cyan]\n")
    
    # Check component databases
    components = {
        "Sentinel": config.sentinel_db_path,
        "Oracle": config.oracle_db_path,
        "Sage": config.sage_db_path,
        "Guardian": config.guardian_db_path
    }
    
    for name, path in components.items():
        status_icon = "[green]✓[/green]" if path.exists() else "[red]✗[/red]"
        console.print(f"{status_icon} {name}: {path}")
    
    console.print(f"\n[cyan]Server Configuration:[/cyan]")
    console.print(f"  Host: {config.host}")
    console.print(f"  Port: {config.port}")
    console.print(f"  Reload: {config.reload}")
    console.print()


@cli.command()
def config_cmd():
    """Show Nexus configuration."""
    console.print("\n[bold cyan]Nexus Configuration[/bold cyan]\n")
    
    console.print("[cyan]Server Settings:[/cyan]")
    console.print(f"  Host: {config.host}")
    console.print(f"  Port: {config.port}")
    console.print(f"  Reload: {config.reload}")
    
    console.print("\n[cyan]Integration Paths:[/cyan]")
    console.print(f"  Sentinel: {config.sentinel_db_path}")
    console.print(f"  Oracle: {config.oracle_db_path}")
    console.print(f"  Sage: {config.sage_db_path}")
    console.print(f"  Guardian: {config.guardian_db_path}")
    
    console.print("\n[cyan]WebSocket:[/cyan]")
    console.print(f"  Heartbeat Interval: {config.ws_heartbeat_interval}s")
    console.print(f"  Max Connections: {config.ws_max_connections}")
    
    console.print()


if __name__ == '__main__':
    cli()
