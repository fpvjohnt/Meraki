import logging
from rich.logging import RichHandler

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    
    logger = logging.getLogger(name)
    return logger

# Create a global logger instance
logger = setup_logger("meraki_health_check")