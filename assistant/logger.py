from colorama import init, Fore, Back, Style
from datetime import datetime
from typing import Optional
import sys
import logging
from pathlib import Path

# Initialize colorama
init(autoreset=True)

class Logger:
    def __init__(self, app_name: str = 'AI-Anna'):
        self.app_name = app_name
        self.debug_mode = False

    def set_debug_mode(self, enabled: bool) -> None:
        """Enable or disable debug mode logging."""
        self.debug_mode = enabled

    def _format_message(self, level: str, message: str, module: Optional[str] = None) -> str:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        module_str = f'[{module}] ' if module else ''
        return f'{timestamp} {level} {module_str}{message}'

    def info(self, message: str, module: Optional[str] = None) -> None:
        """Log an info message in blue."""
        formatted = self._format_message('INFO', message, module)
        print(f'{Fore.BLUE}{formatted}{Style.RESET_ALL}')

    def success(self, message: str, module: Optional[str] = None) -> None:
        """Log a success message in green."""
        formatted = self._format_message('SUCCESS', message, module)
        print(f'{Fore.GREEN}{formatted}{Style.RESET_ALL}')

    def warning(self, message: str, module: Optional[str] = None) -> None:
        """Log a warning message in yellow."""
        formatted = self._format_message('WARNING', message, module)
        print(f'{Fore.YELLOW}{formatted}{Style.RESET_ALL}')

    def error(self, message: str, module: Optional[str] = None) -> None:
        """Log an error message in red."""
        formatted = self._format_message('ERROR', message, module)
        print(f'{Fore.RED}{formatted}{Style.RESET_ALL}', file=sys.stderr)

    def debug(self, message: str, module: Optional[str] = None) -> None:
        """Log a debug message in cyan if debug mode is enabled."""
        if self.debug_mode:
            formatted = self._format_message('DEBUG', message, module)
            print(f'{Fore.CYAN}{formatted}{Style.RESET_ALL}')

    def critical(self, message: str, module: Optional[str] = None) -> None:
        """Log a critical error message in white text with red background."""
        formatted = self._format_message('CRITICAL', message, module)
        print(f'{Back.RED}{Fore.WHITE}{formatted}{Style.RESET_ALL}', file=sys.stderr)

    def system(self, message: str, module: Optional[str] = None) -> None:
        """Log a system message in magenta."""
        formatted = self._format_message('SYSTEM', message, module)
        print(f'{Fore.MAGENTA}{formatted}{Style.RESET_ALL}')


class LogManager:
    def __init__(self):
        log_dir = Path("d:/Projects/Ai-Anna/logs")
        log_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger('Anna')
        self.logger.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler(
            log_dir / f'anna_{datetime.now().strftime("%Y%m%d")}.log'
        )
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter('%(levelname)s: %(message)s')
        )
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def get_logger(self):
        return self.logger