"""Tests for prompt building."""
import pytest
from prompts.prompt_builder import PromptBuilder


class TestPromptBuilder:
    """Test prompt builder."""
    
    def test_build_analysis_prompt_basic(self):
        """Test building basic analysis prompt."""
        prompt = PromptBuilder.build_analysis_prompt(
            query="Why is my system slow?"
        )
        
        assert "Why is my system slow?" in prompt
        assert "User Query" in prompt
    
    def test_build_analysis_prompt_with_context(self, sample_context):
        """Test building prompt with full context."""
        prompt = PromptBuilder.build_analysis_prompt(
            query="Analyze my system",
            system_state=sample_context["system_state"],
            patterns=sample_context["patterns"],
            anomalies=sample_context["anomalies"],
            predictions=sample_context["predictions"]
        )
        
        assert "Analyze my system" in prompt
        assert "Current System State" in prompt
        assert "Learned Patterns" in prompt
        assert "Recent Anomalies" in prompt
        assert "Predictions" in prompt
    
    def test_format_system_state(self):
        """Test system state formatting."""
        state = {
            "cpu": 45.2,
            "ram": 16.5,
            "gpu": 12.0
        }
        
        formatted = PromptBuilder._format_system_state(state)
        
        assert "CPU: 45.2%" in formatted
        assert "RAM: 16.5GB" in formatted
        assert "GPU: 12.0%" in formatted
    
    def test_format_patterns(self):
        """Test patterns formatting."""
        patterns = {
            "typical_usage": "moderate",
            "work_hours": "9:00-17:00",
            "common_apps": ["chrome", "vscode"]
        }
        
        formatted = PromptBuilder._format_patterns(patterns)
        
        assert "moderate" in formatted
        assert "9:00-17:00" in formatted
        assert "chrome" in formatted
    
    def test_format_anomalies_empty(self):
        """Test formatting empty anomalies."""
        formatted = PromptBuilder._format_anomalies([])
        
        assert "No recent anomalies" in formatted
    
    def test_format_anomalies_with_data(self):
        """Test formatting anomalies with data."""
        anomalies = [
            {"type": "high_cpu", "description": "CPU spike detected"},
            {"type": "high_ram", "description": "Memory usage high"}
        ]
        
        formatted = PromptBuilder._format_anomalies(anomalies)
        
        assert "high_cpu" in formatted
        assert "CPU spike detected" in formatted
