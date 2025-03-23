# Command pattern implementation for Anna AI assistant
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class Command(ABC):
    """Base class for all commands"""
    def __init__(self, handler):
        self.handler = handler
        # Safely access conversation context
        self.context = getattr(handler, 'conversation_context', {
            'last_topic': None,
            'follow_up_needed': False,
            'user_name': None,
            'mood': 'neutral'
        })

    @abstractmethod
    def execute(self, command: str) -> str:
        """Execute the command and return response"""
        pass

    def validate(self, command: str) -> bool:
        """Validate if the command can be executed"""
        return True

    def update_context(self, key: str, value: Any) -> None:
        """Update conversation context"""
        self.context[key] = value

    def get_context(self, key: str, default: Any = None) -> Any:
        """Get value from conversation context"""
        return self.context.get(key, default)

class CommandRegistry:
    """Registry for all available commands"""
    def __init__(self):
        self._commands = {}

    def register(self, intent: str, command_class: type) -> None:
        """Register a command class for an intent"""
        self._commands[intent] = command_class

    def get_command(self, intent: str) -> Optional[type]:
        """Get command class for an intent"""
        return self._commands.get(intent)

    def get_all_commands(self) -> Dict[str, type]:
        """Get all registered commands"""
        return self._commands.copy()