import logging
import sys

# Define logging levels that correspond to verbosity flags
LOGGING_LEVELS = {
    0: logging.WARNING,  # Default level - only warnings and errors
    1: logging.INFO,  # -v: Add informational messages
    2: logging.DEBUG,  # -vv: Add debug messages
    3: logging.NOTSET,  # -vvv: Show everything
}


class SilentFilter(logging.Filter):
    """Filter that blocks all messages when verbosity is 0"""

    def __init__(self, verbosity: int = 0):
        super().__init__()
        self.verbosity = verbosity

    def filter(self, record: logging.LogRecord) -> bool:
        # Allow messages only if verbosity > 0 or if it's an error/warning
        return self.verbosity > 0 or record.levelno >= logging.WARNING


def setup_logger(verbosity: int = 0) -> logging.Logger:
    """
    Set up and configure the logger based on verbosity level.

    Args:
        verbosity: Verbosity level (0-3), corresponding to -v flags

    Returns:
        Configured logger instance
    """
    # Clamp verbosity between 0 and 3
    verbosity = max(0, min(verbosity, 3))

    # Create logger
    logger = logging.getLogger("singingshark")
    logger.setLevel(LOGGING_LEVELS.get(verbosity, logging.WARNING))

    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(LOGGING_LEVELS.get(verbosity, logging.WARNING))

    # Create formatter
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    console_handler.setFormatter(formatter)

    # Add silent filter if verbosity is 0
    silent_filter = SilentFilter(verbosity)
    console_handler.addFilter(silent_filter)

    # Add handler to logger
    logger.addHandler(console_handler)

    return logger


# Global logger instance
logger = logging.getLogger("singingshark")
