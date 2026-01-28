"""Dynamic prompt builder for Gemini."""
from typing import Dict, Optional
from prompts.system_prompt import SYSTEM_PROMPT


class PromptBuilder:
    """Build dynamic prompts with context."""
    
    @staticmethod
    def build_analysis_prompt(
        query: str,
        system_state: Optional[Dict] = None,
        patterns: Optional[Dict] = None,
        anomalies: Optional[list] = None,
        predictions: Optional[Dict] = None,
        training_status: Optional[Dict] = None
    ) -> str:
        """Build analysis prompt with context.
        
        Args:
            query: User query
            system_state: Current system metrics
            patterns: Learned patterns from Oracle
            anomalies: Recent anomalies
            predictions: Predictions from Oracle
            training_status: Oracle training status and data collection info
            
        Returns:
            Complete prompt string
        """
        parts = [SYSTEM_PROMPT, "\n## Context\n"]
        
        # Always include training status first so AI knows what capabilities are available
        if training_status:
            parts.append("\n### Training Status")
            parts.append(PromptBuilder._format_training_status(training_status))
        
        if system_state:
            parts.append("\n### Current System State")
            parts.append(PromptBuilder._format_system_state(system_state))
        
        if patterns:
            parts.append("\n### Learned Patterns")
            parts.append(PromptBuilder._format_patterns(patterns))
        
        if anomalies:
            parts.append("\n### Recent Anomalies")
            parts.append(PromptBuilder._format_anomalies(anomalies))
        
        if predictions:
            parts.append("\n### Predictions")
            parts.append(PromptBuilder._format_predictions(predictions))
        
        parts.append(f"\n## User Query\n{query}")
        
        return "\n".join(parts)
    
    @staticmethod
    def _format_system_state(state: Dict) -> str:
        """Format system state for prompt."""
        lines = []
        if "cpu" in state:
            lines.append(f"- CPU: {state['cpu']}%")
        if "ram" in state:
            lines.append(f"- RAM: {state['ram']}GB")
        if "gpu" in state:
            lines.append(f"- GPU: {state['gpu']}%")
        if "disk" in state:
            lines.append(f"- Disk: {state['disk']}")
        if "network" in state:
            lines.append(f"- Network: {state['network']}")
        if "top_processes" in state:
            lines.append(f"- Top Processes: {', '.join(state['top_processes'])}")
        return "\n".join(lines)
    
    @staticmethod
    def _format_patterns(patterns: Dict) -> str:
        """Format learned patterns for prompt."""
        lines = []
        if "typical_usage" in patterns:
            lines.append(f"- Typical Usage: {patterns['typical_usage']}")
        if "work_hours" in patterns:
            lines.append(f"- Work Hours: {patterns['work_hours']}")
        if "common_apps" in patterns:
            lines.append(f"- Common Apps: {', '.join(patterns['common_apps'])}")
        return "\n".join(lines)
    
    @staticmethod
    def _format_training_status(status: Dict) -> str:
        """Format training status for prompt."""
        lines = [
            f"- Oracle Trained: {'Yes' if status.get('oracle_trained') else 'No'}",
            f"- Sentinel Active: {'Yes' if status.get('sentinel_active') else 'No'}",
            f"- Ready for Training: {'Yes' if status.get('ready_for_training') else 'No'}",
            f"- Snapshots Collected: {status.get('snapshot_count', 0)}",
            f"- Data Collection Hours: {status.get('data_collection_hours', 0)}",
            f"- Minimum Required: {status.get('min_samples_needed', 1000)} samples / {status.get('min_hours_needed', 1.0)} hours",
            f"- Recommended: {status.get('recommended_hours', 24.0)} hours for best results"
        ]
        return "\n".join(lines)
    
    @staticmethod
    def _format_anomalies(anomalies: list) -> str:
        """Format anomalies for prompt."""
        if not anomalies:
            return "No recent anomalies detected."
        
        lines = []
        for anomaly in anomalies[:5]:  # Limit to 5 most recent
            lines.append(
                f"- {anomaly.get('type', 'Unknown')}: "
                f"{anomaly.get('description', 'No description')}"
            )
        return "\n".join(lines)
    
    @staticmethod
    def _format_predictions(predictions: Dict) -> str:
        """Format predictions for prompt."""
        lines = []
        if "next_hour" in predictions:
            lines.append(f"- Next Hour: {predictions['next_hour']}")
        if "confidence" in predictions:
            lines.append(f"- Confidence: {predictions['confidence']:.0%}")
        return "\n".join(lines)
