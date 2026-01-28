"""Proactive system monitoring and insights generation."""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger

from config import config
from context import ContextAggregator
from gemini_client import GeminiClient
from prompts import PromptBuilder


class ProactiveMonitor:
    """Generate proactive insights without user queries."""
    
    def __init__(self):
        """Initialize proactive monitor."""
        self.context_agg = ContextAggregator()
        self.client = None  # Lazy initialization
        self.monitoring = False
        self.check_interval = 300  # 5 minutes
    
    async def start_monitoring(self):
        """Start proactive monitoring loop."""
        if not config.enable_proactive_insights:
            logger.info("Proactive insights disabled in config")
            return
        
        self.monitoring = True
        logger.info("Started proactive monitoring")
        
        while self.monitoring:
            try:
                await self._check_system()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    def stop_monitoring(self):
        """Stop proactive monitoring."""
        self.monitoring = False
        logger.info("Stopped proactive monitoring")
    
    async def _check_system(self):
        """Check system and generate insights if needed."""
        # Get current context
        context = await self.context_agg.get_system_context()
        
        # Check for anomalies
        anomalies = context.get("anomalies", [])
        if anomalies:
            await self._generate_anomaly_insight(anomalies, context)
        
        # Check predictions
        predictions = context.get("predictions")
        if predictions:
            await self._generate_prediction_insight(predictions, context)
        
        # Check patterns
        patterns = context.get("patterns")
        if patterns:
            await self._check_pattern_changes(patterns, context)
    
    async def _generate_anomaly_insight(
        self,
        anomalies: List[Dict],
        context: Dict
    ):
        """Generate insight for detected anomalies."""
        logger.info(f"Generating insight for {len(anomalies)} anomalies")
        
        # Build prompt for anomaly analysis
        prompt = f"""
        Detected {len(anomalies)} system anomalies. Analyze and provide:
        1. Root cause analysis
        2. Impact assessment
        3. Recommended actions
        4. Urgency level (low/medium/high)
        
        Keep response concise and actionable.
        """
        
        if not self.client:
            self.client = GeminiClient()
        
        try:
            result = await self.client.generate_response(prompt, context=context)
            
            # Log insight
            logger.info(f"Proactive insight generated: {result['response'][:100]}...")
            
            # Store insight for user to see later
            self._store_insight("anomaly", result["response"], context)
            
        except Exception as e:
            logger.error(f"Error generating anomaly insight: {e}")
    
    async def _generate_prediction_insight(
        self,
        predictions: Dict,
        context: Dict
    ):
        """Generate insight for predictions."""
        logger.info("Generating prediction insight")
        
        prompt = """
        Based on system predictions, provide:
        1. What to expect in the next hour
        2. Potential issues to watch for
        3. Preventive actions
        
        Keep response brief and focused.
        """
        
        if not self.client:
            self.client = GeminiClient()
        
        try:
            result = await self.client.generate_response(prompt, context=context)
            self._store_insight("prediction", result["response"], context)
            
        except Exception as e:
            logger.error(f"Error generating prediction insight: {e}")
    
    async def _check_pattern_changes(
        self,
        patterns: Dict,
        context: Dict
    ):
        """Check for significant pattern changes."""
        # This would compare current patterns with historical patterns
        # and generate insights if significant changes detected
        pass
    
    def _store_insight(
        self,
        insight_type: str,
        content: str,
        context: Dict
    ):
        """Store generated insight for later retrieval.
        
        Args:
            insight_type: Type of insight (anomaly, prediction, pattern)
            content: Insight content
            context: System context
        """
        # Store in a simple file-based system for now
        insights_dir = config.conversation_db_path.parent / "insights"
        insights_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = insights_dir / f"{insight_type}_{timestamp}.txt"
        
        try:
            with open(filename, "w") as f:
                f.write(f"Type: {insight_type}\n")
                f.write(f"Generated: {datetime.now()}\n")
                f.write(f"\n{content}\n")
            
            logger.info(f"Stored insight: {filename}")
            
        except Exception as e:
            logger.error(f"Error storing insight: {e}")
    
    def get_recent_insights(self, limit: int = 10) -> List[Dict]:
        """Get recent proactive insights.
        
        Args:
            limit: Maximum number of insights
            
        Returns:
            List of insights
        """
        insights_dir = config.conversation_db_path.parent / "insights"
        
        if not insights_dir.exists():
            return []
        
        insights = []
        
        try:
            # Get all insight files
            files = sorted(
                insights_dir.glob("*.txt"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )[:limit]
            
            for file in files:
                with open(file, "r") as f:
                    content = f.read()
                    
                    # Parse file
                    lines = content.split("\n")
                    insight_type = lines[0].replace("Type: ", "").strip()
                    generated = lines[1].replace("Generated: ", "").strip()
                    insight_content = "\n".join(lines[3:]).strip()
                    
                    insights.append({
                        "type": insight_type,
                        "generated": generated,
                        "content": insight_content,
                        "file": file.name
                    })
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting recent insights: {e}")
            return []
    
    async def generate_weekly_report(self) -> str:
        """Generate weekly system report.
        
        Returns:
            Weekly report content
        """
        logger.info("Generating weekly report")
        
        # Get context for the past week
        context = await self.context_agg.get_system_context()
        
        prompt = """
        Generate a weekly system report including:
        1. Performance summary
        2. Notable patterns or changes
        3. Optimization opportunities
        4. Upcoming predictions
        5. Recommended actions
        
        Format as a clear, actionable report.
        """
        
        if not self.client:
            self.client = GeminiClient()
        
        try:
            result = await self.client.generate_response(prompt, context=context)
            
            # Store report
            self._store_insight("weekly_report", result["response"], context)
            
            return result["response"]
            
        except Exception as e:
            logger.error(f"Error generating weekly report: {e}")
            return "Error generating report"
