"""
GPU metrics collector
Supports NVIDIA (via nvidia-smi), AMD (via rocm-smi), and Intel GPUs
"""
import subprocess
from typing import List, Optional
from collectors.base import BaseCollector
from models import GPUMetrics


class GPUCollector(BaseCollector):
    """Collects GPU metrics from multiple vendors"""
    
    def __init__(self):
        super().__init__("GPU")
        self._nvidia_available = self._check_nvidia()
        self._amd_available = self._check_amd()
    
    def _check_nvidia(self) -> bool:
        """Check if NVIDIA GPU tools are available"""
        try:
            subprocess.run(
                ["nvidia-smi", "--version"],
                capture_output=True,
                timeout=2,
                check=False
            )
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _check_amd(self) -> bool:
        """Check if AMD GPU tools are available"""
        try:
            subprocess.run(
                ["rocm-smi", "--version"],
                capture_output=True,
                timeout=2,
                check=False
            )
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    async def collect(self) -> Optional[List[GPUMetrics]]:
        """Collect GPU metrics from all available GPUs"""
        gpus = []
        
        if self._nvidia_available:
            nvidia_gpus = await self._collect_nvidia()
            if nvidia_gpus:
                gpus.extend(nvidia_gpus)
        
        if self._amd_available:
            amd_gpus = await self._collect_amd()
            if amd_gpus:
                gpus.extend(amd_gpus)
        
        # Try GPUtil as fallback
        if not gpus:
            try:
                import GPUtil
                gpu_list = GPUtil.getGPUs()
                for gpu in gpu_list:
                    gpus.append(GPUMetrics(
                        name=gpu.name,
                        usage_percent=gpu.load * 100,
                        memory_used_gb=gpu.memoryUsed / 1024,
                        memory_total_gb=gpu.memoryTotal / 1024,
                        temperature_celsius=gpu.temperature,
                        power_draw_watts=None
                    ))
            except (ImportError, Exception):
                pass
        
        return gpus if gpus else None
    
    async def _collect_nvidia(self) -> List[GPUMetrics]:
        """Collect NVIDIA GPU metrics using nvidia-smi"""
        try:
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw",
                    "--format=csv,noheader,nounits"
                ],
                capture_output=True,
                text=True,
                timeout=2,
                check=False
            )
            
            if result.returncode != 0:
                return []
            
            gpus = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 6:
                    gpus.append(GPUMetrics(
                        name=parts[0],
                        usage_percent=float(parts[1]),
                        memory_used_gb=float(parts[2]) / 1024,
                        memory_total_gb=float(parts[3]) / 1024,
                        temperature_celsius=float(parts[4]) if parts[4] != 'N/A' else None,
                        power_draw_watts=float(parts[5]) if parts[5] != 'N/A' else None
                    ))
            
            return gpus
        except (subprocess.TimeoutExpired, ValueError, IndexError):
            return []
    
    async def _collect_amd(self) -> List[GPUMetrics]:
        """Collect AMD GPU metrics using rocm-smi"""
        try:
            result = subprocess.run(
                ["rocm-smi", "--showuse", "--showmeminfo", "vram", "--showtemp"],
                capture_output=True,
                text=True,
                timeout=2,
                check=False
            )
            
            if result.returncode != 0:
                return []
            
            # Parse rocm-smi output (format varies, this is a basic implementation)
            # TODO: Improve AMD GPU parsing based on actual rocm-smi output format
            gpus = []
            # Placeholder for AMD GPU parsing
            return gpus
        except subprocess.TimeoutExpired:
            return []
