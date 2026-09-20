import logging
import json
import time
from datetime import datetime
from functools import wraps
import os

class JsonFormatter(logging.Formatter):
    """
    Custom formatter to output logs in JSON format.
    """
    def format(self, record):
        log_record = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra_data"):
            log_record.update(record.extra_data)
        
        # Include exception info if it exists
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

def setup_logger(name="maestro"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers if setup multiple times
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        
        # Optionally log to a file
        log_file = os.path.join(os.getcwd(), "maestro.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)
        
    return logger

logger = setup_logger()

def log_tool_performance(tool_name):
    """
    Decorator to log tool execution time and status.
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            extra_data = {
                "event_type": "tool_call",
                "tool_name": tool_name,
                "status": "started"
            }
            logger.info(f"Tool {tool_name} started", extra={"extra_data": extra_data})
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                extra_data.update({
                    "status": "success",
                    "duration_seconds": round(duration, 4)
                })
                logger.info(f"Tool {tool_name} completed", extra={"extra_data": extra_data})
                return result
            except Exception as e:
                duration = time.time() - start_time
                extra_data.update({
                    "status": "error",
                    "error_message": str(e),
                    "duration_seconds": round(duration, 4)
                })
                logger.error(f"Tool {tool_name} failed", extra={"extra_data": extra_data})
                raise e
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            extra_data = {
                "event_type": "tool_call",
                "tool_name": tool_name,
                "status": "started"
            }
            logger.info(f"Tool {tool_name} started", extra={"extra_data": extra_data})
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                extra_data.update({
                    "status": "success",
                    "duration_seconds": round(duration, 4)
                })
                logger.info(f"Tool {tool_name} completed", extra={"extra_data": extra_data})
                return result
            except Exception as e:
                duration = time.time() - start_time
                extra_data.update({
                    "status": "error",
                    "error_message": str(e),
                    "duration_seconds": round(duration, 4)
                })
                logger.error(f"Tool {tool_name} failed", extra={"extra_data": extra_data})
                raise e

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator

def log_agent_transition(from_agent, to_agent, message="Transitioning agent"):
    extra_data = {
        "event_type": "agent_transition",
        "from_agent": from_agent,
        "to_agent": to_agent
    }
    logger.info(message, extra={"extra_data": extra_data})
