"""
Main CLI entry point
Provides commands for data collection and monitoring
"""
import asyncio
import sys
from datetime import datetime
from pathlib import Path
import click
from loguru import logger
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel

from config import Config
from aggregator import Pipeline
from utils.logger import setup_logger


console = Console()


@click.group()
@click.option('--log-level', default='INFO', help='Logging level')
def cli(log_level):
    """System Metrics Collector - Phase 2.1"""
    # Configure logging with file output
    log_file = Path(__file__).parent.parent / "logs" / "sentinel.log"
    setup_logger(log_level=log_level, log_file=log_file)


@cli.command()
@click.option('--interval', default=1, help='Collection interval in seconds')
@click.option('--duration', default=None, type=int, help='Duration in seconds (default: infinite)')
def monitor(interval, duration):
    """Start continuous monitoring"""
    asyncio.run(_monitor(interval, duration))


async def _monitor(interval: int, duration: int = None):
    """Monitor system metrics continuously"""
    config = Config.load()
    pipeline = Pipeline(config)
    
    try:
        await pipeline.initialize()
        console.print("[green]Starting monitoring...[/green]")
        logger.info(f"Monitoring started (interval: {interval}s, duration: {duration or 'infinite'})")
        
        start_time = datetime.now()
        count = 0
        
        while True:
            try:
                # Check duration
                if duration and (datetime.now() - start_time).seconds >= duration:
                    logger.info(f"Duration limit reached ({duration}s), stopping monitoring")
                    break
                
                # Collect and store
                snapshot_id = await pipeline.collect_and_store()
                count += 1
                logger.info(f"Collected snapshot {snapshot_id} (iteration {count})")
                
                # Display current metrics (only if console is available)
                try:
                    snapshot = await pipeline.collect_once()
                    _display_snapshot(snapshot, count)
                except Exception as display_error:
                    # Console display failed (likely running in background), just log
                    logger.debug(f"Console display skipped: {display_error}")
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop (iteration {count}): {e}", exc_info=True)
                console.print(f"[red]Error: {e}[/red]")
                # Continue monitoring despite errors
                await asyncio.sleep(interval)
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Monitoring stopped by user[/yellow]")
        logger.info("Monitoring stopped by user (KeyboardInterrupt)")
    except Exception as e:
        console.print(f"\n[red]Fatal error: {e}[/red]")
        logger.critical(f"Fatal error in monitor command: {e}", exc_info=True)
        raise
    finally:
        logger.info("Shutting down pipeline...")
        await pipeline.shutdown()
        logger.info("Monitoring stopped")


def _display_snapshot(snapshot, count):
    """Display snapshot in terminal"""
    table = Table(title=f"System Metrics (Sample #{count})")
    
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Timestamp", str(snapshot.timestamp))
    table.add_row("CPU Usage", f"{snapshot.cpu.usage_percent:.1f}%")
    table.add_row("RAM Usage", f"{snapshot.ram.usage_percent:.1f}%")
    table.add_row("Disk Read", f"{snapshot.disk.read_mbps:.2f} MB/s")
    table.add_row("Disk Write", f"{snapshot.disk.write_mbps:.2f} MB/s")
    table.add_row("Network Down", f"{snapshot.network.download_mbps:.2f} MB/s")
    table.add_row("Network Up", f"{snapshot.network.upload_mbps:.2f} MB/s")
    
    if snapshot.gpu:
        for idx, gpu in enumerate(snapshot.gpu):
            table.add_row(f"GPU {idx} Usage", f"{gpu.usage_percent:.1f}%")
    
    console.clear()
    console.print(table)


@cli.command()
def collect():
    """Collect data once and display"""
    asyncio.run(_collect())


async def _collect():
    """Collect data once"""
    config = Config.load()
    pipeline = Pipeline(config)
    
    try:
        await pipeline.initialize()
        
        console.print("[cyan]Collecting system metrics...[/cyan]")
        snapshot_id = await pipeline.collect_and_store()
        
        snapshot = await pipeline.collect_once()
        _display_snapshot(snapshot, 1)
        
        console.print(f"\n[green]Data saved with ID: {snapshot_id}[/green]")
    
    finally:
        await pipeline.shutdown()


@cli.command()
def status():
    """Show database status and statistics"""
    asyncio.run(_status())


async def _status():
    """Show status"""
    config = Config.load()
    pipeline = Pipeline(config)
    
    try:
        await pipeline.initialize()
        
        stats = await pipeline.get_statistics()
        
        table = Table(title="Database Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Snapshots", str(stats['total_snapshots']))
        table.add_row("Database Size", f"{stats['database_size_mb']} MB")
        table.add_row("Oldest Snapshot", str(stats['oldest_snapshot'] or 'N/A'))
        table.add_row("Newest Snapshot", str(stats['newest_snapshot'] or 'N/A'))
        
        console.print(table)
    
    finally:
        await pipeline.shutdown()


@cli.command()
@click.option('--metric', required=True, help='Metric name (cpu, ram, disk_read, network_download)')
@click.option('--hours', default=24, help='Hours of history to show')
def history(metric, hours):
    """View historical data for a metric"""
    asyncio.run(_history(metric, hours))


async def _history(metric: str, hours: int):
    """Show historical data"""
    config = Config.load()
    pipeline = Pipeline(config)
    
    try:
        await pipeline.initialize()
        
        data = await pipeline.repository.get_metric_history(metric, hours)
        
        if not data:
            console.print(f"[yellow]No data found for metric: {metric}[/yellow]")
            return
        
        table = Table(title=f"{metric.upper()} History (Last {hours} hours)")
        table.add_column("Timestamp", style="cyan")
        table.add_column("Value", style="green")
        
        for point in data[-20:]:  # Show last 20 points
            table.add_row(str(point['timestamp']), f"{point['value']:.2f}")
        
        console.print(table)
        console.print(f"\n[dim]Showing last 20 of {len(data)} data points[/dim]")
    
    finally:
        await pipeline.shutdown()


@cli.command()
@click.option('--format', default='json', help='Export format (json, csv)')
@click.option('--output', required=True, help='Output file path')
@click.option('--hours', default=24, help='Hours of data to export')
def export(format, output, hours):
    """Export data to file"""
    asyncio.run(_export(format, output, hours))


async def _export(format: str, output: str, hours: int):
    """Export data"""
    config = Config.load()
    pipeline = Pipeline(config)
    
    try:
        await pipeline.initialize()
        
        data = await pipeline.repository.get_recent_snapshots(limit=hours * 3600)
        
        if format == 'json':
            import json
            with open(output, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        elif format == 'csv':
            import csv
            if data:
                with open(output, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
        
        console.print(f"[green]Exported {len(data)} records to {output}[/green]")
    
    finally:
        await pipeline.shutdown()


if __name__ == '__main__':
    cli()
