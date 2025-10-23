# src/utils/logger.py
import logging
import sys
import os
from datetime import datetime
from typing import Optional
import inspect


# Add this to your logger.py or create a new streaming logger utility

class StreamingLogger:
    """Special logger for handling streaming content"""
    
    def __init__(self):
        self.logger = get_logger()
        self.current_line = ""
        self.line_started = False
    
    def stream_chunk(self, chunk: str):
        """Stream a chunk of text with proper line handling"""
        if not chunk.strip():
            return
            
        # If chunk contains newlines, split and handle properly
        if '\n' in chunk:
            lines = chunk.split('\n')
            for i, line in enumerate(lines):
                if i == 0 and self.line_started:
                    # Continue current line
                    self.current_line += line
                    self.logger.info(f"   📝 {self.current_line}")
                    self.current_line = ""
                    self.line_started = False
                elif line.strip():
                    # Start new line
                    self.logger.info(f"   📝 {line}")
        else:
            # Single line chunk
            if not self.line_started:
                self.current_line = chunk
                self.line_started = True
            else:
                self.current_line += chunk
    
    def end_stream(self):
        """End the current stream and flush any remaining content"""
        if self.current_line.strip():
            self.logger.info(f"   📝 {self.current_line}")
            self.current_line = ""
            self.line_started = False




class CodeReviewLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CodeReviewLogger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.logger = None
        self.original_print = print
        self.setup_logger()
    
    def setup_logger(self, log_dir: str = "logs", log_level: str = "INFO"):
        """Setup the centralized logger"""
        # Create logs directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Generate log filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"code_review.log")
        
        # Create logger
        self.logger = logging.getLogger("CodeReviewAgent")
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # File handler (detailed)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        
        # Console handler (simple)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(simple_formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Replace print function
        self._replace_print()
        
        self.logger.info(f"Logger initialized. Log file: {log_file}")
        return log_file
    
    def _replace_print(self):
        """Replace the built-in print function to capture all print statements"""
        def logged_print(*args, **kwargs):
            # Get caller information
            frame = inspect.currentframe().f_back
            filename = os.path.basename(frame.f_code.co_filename)
            lineno = frame.f_lineno
            caller_info = f"[{filename}:{lineno}]"
            
            # Convert arguments to string
            message = ' '.join(str(arg) for arg in args)
            
            # Log the message
            if self.logger:
                self.logger.info(f"{caller_info} {message}")
            
            # Also call original print if needed
            self.original_print(*args, **kwargs)
        
        # Replace built-in print - Python 3 compatible
        import builtins
        builtins.print = logged_print
    
    def restore_print(self):
        """Restore the original print function"""
        import builtins
        builtins.print = self.original_print
    
    def get_logger(self) -> logging.Logger:
        """Get the logger instance"""
        return self.logger
    
    def log_function_call(self, func):
        """Decorator to log function calls"""
        def wrapper(*args, **kwargs):
            class_name = ""
            if args and hasattr(args[0], '__class__'):
                class_name = f"{args[0].__class__.__name__}."
            
            self.logger.debug(f"CALL {class_name}{func.__name__}")
            try:
                result = func(*args, **kwargs)
                self.logger.debug(f"RETURN {class_name}{func.__name__}")
                return result
            except Exception as e:
                self.logger.error(f"ERROR {class_name}{func.__name__} - {str(e)}", exc_info=True)
                raise
        return wrapper

# Global logger instance
logger_manager = CodeReviewLogger()

def setup_logging(log_dir: str = "logs", log_level: str = "INFO"):
    """Setup logging for the entire application"""
    return logger_manager.setup_logger(log_dir, log_level)

def get_logger() -> logging.Logger:
    """Get the application logger"""
    return logger_manager.get_logger()