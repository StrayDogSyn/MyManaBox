"""
Performance monitoring utilities for CardForge.
Tracks execution time, success rates, and error rates.
"""

import time
import logging
import functools
import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class Metric:
    """Performance metric for a single operation."""
    operation: str
    start_time: float
    end_time: Optional[float] = None
    success: bool = False
    error: Optional[str] = None
    
    @property
    def duration_ms(self) -> float:
        if not self.end_time:
            return 0.0
        return (self.end_time - self.start_time) * 1000

class PerformanceMonitor:
    """System-wide performance monitor."""
    
    _metrics: list[Metric] = []
    
    @classmethod
    def record(cls, metric: Metric):
        cls._metrics.append(metric)
        # Log immediately
        status = "SUCCESS" if metric.success else "FAILURE"
        logger.info(
            f"[MONITOR] {metric.operation}: {status} in {metric.duration_ms:.2f}ms"
            + (f" Error: {metric.error}" if metric.error else "")
        )

    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """Calculate statistics from recorded metrics."""
        if not cls._metrics:
            return {"count": 0}
            
        total_ops = len(cls._metrics)
        successful = sum(1 for m in cls._metrics if m.success)
        failed = total_ops - successful
        
        durations = [m.duration_ms for m in cls._metrics if m.end_time]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            "total_operations": total_ops,
            "success_rate": (successful / total_ops) * 100 if total_ops > 0 else 0,
            "failure_rate": (failed / total_ops) * 100 if total_ops > 0 else 0,
            "avg_response_time_ms": avg_duration,
            "total_errors": failed
        }

def monitor_performance(operation_name: str):
    """Decorator to monitor function performance."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            success = False
            error = None
            try:
                result = await func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                error = str(e)
                raise
            finally:
                end = time.time()
                metric = Metric(
                    operation=operation_name,
                    start_time=start,
                    end_time=end,
                    success=success,
                    error=error
                )
                PerformanceMonitor.record(metric)
        return wrapper
    return decorator
