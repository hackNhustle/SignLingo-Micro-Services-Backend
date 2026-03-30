import time
import psutil
import os
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger("profiling")
logger.setLevel(logging.INFO)
# Basic logging setup if not already configured
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class ProfilingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if os.getenv("ENABLE_PROFILING", "true").lower() != "true":
            return await call_next(request)

        # Get current process
        process = psutil.Process(os.getpid())
        
        # Snapshot BEFORE
        start_cpu_time = time.process_time()
        start_wall_time = time.perf_counter()
        start_mem = process.memory_info().rss / (1024 * 1024) # MB
        
        response = await call_next(request)
        
        # Snapshot AFTER
        end_cpu_time = time.process_time()
        end_wall_time = time.perf_counter()
        end_mem = process.memory_info().rss / (1024 * 1024) # MB
        
        # Calculations
        cpu_time_used_ms = (end_cpu_time - start_cpu_time) * 1000 # ms
        wall_time_ms = (end_wall_time - start_wall_time) * 1000 # ms
        mem_delta_mb = end_mem - start_mem
        
        # Log the metrics
        logger.info(
            f"PROFILING: {request.method} {request.url.path} | "
            f"CPU: {cpu_time_used_ms:.3f}ms | "
            f"Wall-Clock: {wall_time_ms:.3f}ms | "
            f"Mem-Delta: {mem_delta_mb:+.3f}MB | "
            f"RSS: {end_mem:.3f}MB"
        )
        
        # Optional: Add headers to response (very useful for testing)
        response.headers["X-Profiling-CPU-Time-MS"] = f"{cpu_time_used_ms:.3f}"
        response.headers["X-Profiling-Mem-Delta-MB"] = f"{mem_delta_mb:.3f}"
        response.headers["X-Profiling-RSS-MB"] = f"{end_mem:.3f}"
        
        return response
