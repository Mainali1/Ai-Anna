from abc import ABC, abstractmethod

class CommandBase(ABC):
    """Abstract base class for all commands"""
    
    def __init__(self, container=None):
        """Initialize the command with optional dependency container"""
        self.container = container
    
    @abstractmethod
    def matches(self, command: str) -> bool:
        """Check if the command matches this handler
        
        Args:
            command (str): The command string to check
            
        Returns:
            bool: True if this command can handle the input
        """
        pass
        
    @abstractmethod
    def execute(self, command: str) -> str:
        """Execute the command
        
        Args:
            command (str): The command string to execute
            
        Returns:
            str: The result of executing the command
        """
        pass