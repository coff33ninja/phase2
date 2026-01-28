"""CLI interface for Guardian."""
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from pathlib import Path
from loguru import logger

from config import config
from profiles import ProfileManager
from execution import ActionExecutor
from actions import *
from models import ActionType

console = Console()


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def cli(verbose):
    """Guardian - Auto-Tuning & Optimization Engine.
    
    Automatically optimize system performance based on learned patterns.
    """
    if verbose:
        logger.remove()
        logger.add(lambda msg: console.print(msg, style="dim"), level="DEBUG")


@cli.command()
@click.argument('action_type', type=click.Choice([t.value for t in ActionType]))
@click.argument('target')
@click.option('--params', '-p', multiple=True, help='Action parameters (key=value)')
@click.option('--approve', '-y', is_flag=True, help='Auto-approve action')
def execute(action_type, target, params, approve):
    """Execute a single action.
    
    Examples:
        guardian execute close_process chrome.exe
        guardian execute set_priority game.exe -p priority=high
        guardian execute power_plan performance
    """
    console.print(f"\n[bold cyan]Executing Action:[/bold cyan] {action_type}")
    console.print(f"[cyan]Target:[/cyan] {target}\n")
    
    # Parse parameters
    parameters = {}
    for param in params:
        if '=' in param:
            key, value = param.split('=', 1)
            parameters[key] = value
    
    # Create action
    action_class = get_action_class(action_type)
    if not action_class:
        console.print(f"[red]Error:[/red] Unknown action type: {action_type}")
        return
    
    action = action_class(target=target, parameters=parameters)
    
    # Execute
    executor = ActionExecutor()
    result = executor.execute_action(action, user_approved=approve)
    
    # Display result
    if result.success:
        console.print(f"[green]✓ Success:[/green] {result.message}")
        if result.data:
            console.print(f"[dim]Data: {result.data}[/dim]")
    else:
        console.print(f"[red]✗ Failed:[/red] {result.message}")
        if result.error:
            console.print(f"[red]Error: {result.error}[/red]")


@cli.command()
@click.argument('profile_name')
def activate(profile_name):
    """Activate an automation profile.
    
    Examples:
        guardian activate gaming
        guardian activate work
        guardian activate power_saver
    """
    console.print(f"\n[bold cyan]Activating Profile:[/bold cyan] {profile_name}\n")
    
    manager = ProfileManager()
    
    # Load profile
    profile = manager.get_profile(profile_name)
    if not profile:
        console.print(f"[red]Error:[/red] Profile not found: {profile_name}")
        console.print("\n[yellow]Available profiles:[/yellow]")
        for name in manager.list_profiles():
            console.print(f"  • {name}")
        return
    
    # Activate
    if manager.activate_profile(profile_name):
        console.print(f"[green]✓ Activated:[/green] {profile.name}")
        console.print(f"[dim]{profile.description}[/dim]\n")
        
        # Show actions
        console.print("[cyan]Actions:[/cyan]")
        for action in profile.actions:
            console.print(f"  • {action.get('type')}: {action.get('target', 'N/A')}")
    else:
        console.print(f"[red]✗ Failed to activate profile[/red]")


@cli.command()
def status():
    """Show Guardian status and current profile."""
    console.print("\n[bold cyan]Guardian Status[/bold cyan]\n")
    
    # Configuration
    table = Table(title="Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Automation Level", config.automation_level)
    table.add_row("Rollback Enabled", str(config.enable_rollback))
    table.add_row("Snapshot Before Action", str(config.snapshot_before_action))
    table.add_row("Max Concurrent Actions", str(config.max_concurrent_actions))
    
    console.print(table)
    
    # Active profile
    manager = ProfileManager()
    active = manager.get_active_profile()
    
    if active:
        console.print(f"\n[green]Active Profile:[/green] {active.name}")
        console.print(f"[dim]{active.description}[/dim]")
    else:
        console.print("\n[yellow]No active profile[/yellow]")
    
    # Protected processes
    console.print(f"\n[cyan]Protected Processes:[/cyan]")
    for proc in config.get_protected_processes_list():
        console.print(f"  • {proc}")


@cli.command()
@click.option('--limit', '-n', default=10, help='Number of actions to show')
def history(limit):
    """Show action execution history."""
    console.print(f"\n[bold cyan]Action History[/bold cyan] (last {limit})\n")
    
    from execution.logger import ActionLogger
    logger_instance = ActionLogger()
    
    actions = logger_instance.get_recent_actions(limit=limit)
    
    if not actions:
        console.print("[yellow]No actions in history[/yellow]")
        return
    
    table = Table()
    table.add_column("Time", style="cyan")
    table.add_column("Action", style="yellow")
    table.add_column("Target", style="blue")
    table.add_column("Status", style="green")
    
    for action in actions:
        status_style = "green" if action.status == "success" else "red"
        table.add_row(
            action.started_at.strftime("%H:%M:%S"),
            action.action_type.value,
            action.target,
            f"[{status_style}]{action.status.value}[/{status_style}]"
        )
    
    console.print(table)


@cli.command()
@click.argument('action_id', required=False)
def rollback(action_id):
    """Rollback an action or the last action."""
    if action_id:
        console.print(f"\n[bold cyan]Rolling back action:[/bold cyan] {action_id}\n")
    else:
        console.print("\n[bold cyan]Rolling back last action[/bold cyan]\n")
    
    executor = ActionExecutor()
    result = executor.rollback_last_action()
    
    if result.success:
        console.print(f"[green]✓ Rollback successful:[/green] {result.message}")
    else:
        console.print(f"[red]✗ Rollback failed:[/red] {result.message}")
        if result.error:
            console.print(f"[red]Error: {result.error}[/red]")


@cli.command()
@click.option('--key', '-k', help='Configuration key to show/set')
@click.option('--value', '-v', help='Value to set')
def config_cmd(key, value):
    """Show or modify configuration."""
    if not key:
        # Show all config
        console.print("\n[bold cyan]Guardian Configuration[/bold cyan]\n")
        
        table = Table()
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="green")
        
        for field_name, field_info in config.model_fields.items():
            field_value = getattr(config, field_name)
            table.add_row(field_name, str(field_value))
        
        console.print(table)
    else:
        if value:
            # Set config value
            console.print(f"[yellow]Setting {key} = {value}[/yellow]")
            console.print("[dim]Note: Configuration changes require restart[/dim]")
        else:
            # Show specific key
            if hasattr(config, key):
                console.print(f"[cyan]{key}:[/cyan] {getattr(config, key)}")
            else:
                console.print(f"[red]Unknown configuration key:[/red] {key}")


@cli.command()
def profiles():
    """List all available profiles."""
    console.print("\n[bold cyan]Available Profiles[/bold cyan]\n")
    
    manager = ProfileManager()
    profile_names = manager.list_profiles()
    
    if not profile_names:
        console.print("[yellow]No profiles found[/yellow]")
        return
    
    for name in profile_names:
        profile = manager.get_profile(name)
        if profile:
            status = "[green]●[/green]" if profile.enabled else "[red]○[/red]"
            console.print(f"{status} [cyan]{name}[/cyan]")
            console.print(f"  [dim]{profile.description}[/dim]")
            console.print(f"  [dim]Actions: {len(profile.actions)}[/dim]\n")


def get_action_class(action_type: str):
    """Get action class by type string.
    
    Args:
        action_type: Action type string
        
    Returns:
        Action class or None
    """
    from actions.process_actions import CloseProcess, StartProcess, SetPriority, KillProcess
    from actions.resource_actions import ClearRAM, SetCPUAffinity, DiskCleanup
    from actions.system_actions import PowerPlan, DisplayBrightness, Sleep, Hibernate
    
    action_map = {
        'close_process': CloseProcess,
        'start_process': StartProcess,
        'set_priority': SetPriority,
        'kill_process': KillProcess,
        'clear_ram': ClearRAM,
        'set_cpu_affinity': SetCPUAffinity,
        'disk_cleanup': DiskCleanup,
        'power_plan': PowerPlan,
        'display_brightness': DisplayBrightness,
        'sleep': Sleep,
        'hibernate': Hibernate,
    }
    
    return action_map.get(action_type)


if __name__ == '__main__':
    cli()
