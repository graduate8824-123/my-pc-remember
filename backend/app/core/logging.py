import logging
import sys
from typing import Optional

def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Configures structured logging for MY PC REMEMBERS.
    Respects privacy: Never logs document contents or credentials.
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    logger = logging.getLogger("mypc_remembers")
    logger.setLevel(numeric_level)
    
    # Avoid duplicate handlers if reloaded
    if not logger.handlers:
        logger.addHandler(handler)
        
    logger.propagate = False
    return logger

logger = setup_logging()
