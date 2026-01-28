"""CLI for Oracle ML engine."""
import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from loguru import logger
import json

from config import config
from training.data_loader import SentinelDataLoader
from training.feature_engineering import FeatureEngineer
from training.trainer import ModelTrainer
from models.lstm_forecaster import LSTMForecaster
from models.anomaly_detector import IsolationForestDetector
from models.clustering import KMeansClustering
from models.classifier import RandomForestClassifier
from inference.predictor import Predictor
from patterns.behavior_profiles import BehaviorProfileManager
from patterns.usage_patterns import UsagePatternStore
from patterns.baseline_manager import BaselineManager

console = Console()


@click.group()
@click.option('--log-level', default='INFO', help='Logging level')
def cli(log_level):
    """Oracle - ML Engine for Pattern Learning"""
    logger.remove()
    logger.add(lambda msg: console.print(msg, end=''), level=log_level)


@cli.command()
@click.option('--days', default=30, help='Days of data to use')
@click.option('--model', type=click.Choice(['lstm', 'anomaly', 'clustering', 'classifier', 'all']), default='all')
def train(days, model):
    """Train ML models"""
    console.print("[bold blue]Training Oracle models...[/bold blue]")
    
    try:
        # Load data
        loader = SentinelDataLoader(config.sentinel_db_path)
        stats = loader.get_statistics()
        
        console.print(f"Database: {stats['total_samples']} samples")
        
        if stats['total_samples'] < config.min_training_samples:
            console.print(f"[red]Not enough data. Need {config.min_training_samples}, have {stats['total_samples']}[/red]")
            return
        
        df = loader.load_time_series(days=days)
        console.print(f"Loaded {len(df)} samples")
        
        # Engineer features
        df = FeatureEngineer.create_all_features(df)
        console.print(f"Created features: {len(df.columns)} columns")
        
        # Train selected models
        if model in ['lstm', 'all']:
            console.print("\n[yellow]Training LSTM Forecaster...[/yellow]")
            _train_lstm(loader, df)
        
        if model in ['anomaly', 'all']:
            console.print("\n[yellow]Training Anomaly Detector...[/yellow]")
            _train_anomaly(df)
        
        if model in ['clustering', 'all']:
            console.print("\n[yellow]Training Clustering Model...[/yellow]")
            _train_clustering(df)
        
        console.print("\n[green]Training complete![/green]")
        
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("[yellow]Make sure Sentinel is installed and has collected data[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        logger.exception("Training failed")


def _train_lstm(loader, df):
    """Train LSTM model."""
    X, y = loader.create_sequences(
        df[['cpu_percent', 'ram_percent']].values,
        sequence_length=60
    )
    
    model = LSTMForecaster(
        config.model_dir,
        sequence_length=60,
        n_features=2
    )
    
    trainer = ModelTrainer(model)
    X_train, X_test, y_train, y_test = trainer.train_test_split(X, y)
    
    metrics = trainer.train_and_evaluate(
        X_train, y_train, X_test, y_test,
        epochs=config.epochs,
        batch_size=config.batch_size
    )
    
    trainer.save_model()
    console.print(f"[green]LSTM trained. MAE: {metrics.get('mae_5m', 0):.2f}[/green]")


def _train_anomaly(df):
    """Train anomaly detector."""
    features = df[['cpu_percent', 'ram_percent']].values
    
    model = IsolationForestDetector(
        config.model_dir,
        contamination=config.anomaly_contamination
    )
    
    trainer = ModelTrainer(model)
    X_train, X_test, _, _ = trainer.train_test_split(features, features)
    
    model.train(X_train)
    model.save()
    
    console.print("[green]Anomaly detector trained[/green]")


def _train_clustering(df):
    """Train clustering model."""
    features = df[['cpu_percent', 'ram_percent']].values
    
    model = KMeansClustering(config.model_dir, n_clusters=5)
    model.train(features)
    model.save()
    
    console.print("[green]Clustering model trained[/green]")


@cli.command()
def status():
    """Show model status"""
    table = Table(title="Oracle Model Status")
    table.add_column("Model", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Info", style="yellow")
    
    model_dir = Path(config.model_dir)
    
    models = [
        ("LSTM Forecaster", "lstm_forecaster.joblib"),
        ("Anomaly Detector", "isolation_forest_detector.joblib"),
        ("Clustering", "kmeans_clustering.joblib"),
        ("Classifier", "random_forest_classifier.joblib")
    ]
    
    for name, filename in models:
        filepath = model_dir / filename
        if filepath.exists():
            status_str = "✓ Trained"
            info = f"Size: {filepath.stat().st_size / 1024:.1f} KB"
        else:
            status_str = "✗ Not Trained"
            info = "Run 'train' command"
        
        table.add_row(name, status_str, info)
    
    console.print(table)
    
    # Pattern statistics
    if config.pattern_db_path.exists():
        console.print("\n[bold]Pattern Statistics:[/bold]")
        
        baseline_mgr = BaselineManager(config.pattern_db_path)
        stats = baseline_mgr.get_statistics()
        
        console.print(f"Baselines: {stats['total_baselines']}")
        console.print(f"Avg Confidence: {stats['avg_confidence']:.2%}")


@cli.command()
@click.option('--metric', default='cpu_percent', help='Metric to predict')
def predict(metric):
    """Make predictions on current data"""
    console.print("[bold blue]Making predictions...[/bold blue]")
    
    try:
        predictor = Predictor(config.model_dir)
        predictor.load_models()
        
        console.print("[green]Models loaded successfully[/green]")
        console.print("[yellow]Real-time prediction requires live data stream[/yellow]")
        console.print("[yellow]Integration with Sentinel pending[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.option('--days', default=7, help='Days of data to evaluate')
def evaluate(days):
    """Evaluate model performance"""
    console.print(f"[bold blue]Evaluating models on last {days} days...[/bold blue]")
    
    try:
        loader = SentinelDataLoader(config.sentinel_db_path)
        df = loader.load_time_series(days=days)
        df = FeatureEngineer.create_all_features(df)
        
        console.print(f"Loaded {len(df)} samples for evaluation")
        console.print("[yellow]Evaluation implementation pending[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.option('--output', default='patterns.json', help='Output file')
@click.option('--format', type=click.Choice(['json', 'csv']), default='json')
def export(output, format):
    """Export learned patterns"""
    console.print(f"[bold blue]Exporting patterns to {output}...[/bold blue]")
    
    try:
        if not config.pattern_db_path.exists():
            console.print("[red]No patterns found. Train models first.[/red]")
            return
        
        pattern_store = UsagePatternStore(config.pattern_db_path)
        patterns = pattern_store.get_all_patterns()
        
        if format == 'json':
            with open(output, 'w') as f:
                json.dump(patterns, f, indent=2, default=str)
        
        console.print(f"[green]Exported {len(patterns)} patterns to {output}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
def patterns():
    """Show learned patterns"""
    console.print("[bold blue]Learned Patterns[/bold blue]\n")
    
    try:
        if not config.pattern_db_path.exists():
            console.print("[yellow]No patterns found. Train models first.[/yellow]")
            return
        
        pattern_store = UsagePatternStore(config.pattern_db_path)
        all_patterns = pattern_store.get_all_patterns()
        
        if not all_patterns:
            console.print("[yellow]No patterns stored yet[/yellow]")
            return
        
        table = Table(title="Usage Patterns")
        table.add_column("Type", style="cyan")
        table.add_column("Time Period", style="green")
        table.add_column("Confidence", style="yellow")
        table.add_column("Occurrences", style="magenta")
        
        for pattern in all_patterns[:20]:  # Show top 20
            table.add_row(
                pattern['pattern_type'],
                pattern['time_period'],
                f"{pattern['confidence']:.2%}",
                str(pattern['occurrence_count'])
            )
        
        console.print(table)
        console.print(f"\nTotal patterns: {len(all_patterns)}")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.option('--interval', default=24, help='Update interval in hours')
def scheduler(interval):
    """Run automatic model update scheduler"""
    console.print(f"[bold blue]Starting model scheduler (interval: {interval}h)...[/bold blue]")
    
    try:
        from integration.model_scheduler import ModelScheduler
        
        scheduler = ModelScheduler(
            config.sentinel_db_path,
            config.model_dir,
            update_interval_hours=interval
        )
        
        scheduler.schedule_updates()
        console.print("[green]Scheduler started. Press Ctrl+C to stop.[/green]")
        
        scheduler.run()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Scheduler stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


if __name__ == '__main__':
    cli()
