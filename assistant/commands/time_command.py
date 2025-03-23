from . import Command
from datetime import datetime

class TimeCommand(Command):
    def validate(self, command: str) -> bool:
        return any(word in command.lower() for word in ['time', 'date', 'day', 'month', 'year'])
        
    def execute(self, command: str) -> str:
        try:
            now = datetime.now()
            
            if 'time' in command.lower():
                return f"The current time is {now.strftime('%I:%M %p')}."
            elif 'date' in command.lower():
                return f"Today's date is {now.strftime('%A, %B %d, %Y')}."
            elif 'day' in command.lower():
                return f"Today is {now.strftime('%A')}."
            elif 'month' in command.lower():
                return f"The current month is {now.strftime('%B')}."
            elif 'year' in command.lower():
                return f"The current year is {now.strftime('%Y')}."
            else:
                return f"It's {now.strftime('%A, %B %d, %Y')} and the time is {now.strftime('%I:%M %p')}."
        except Exception as e:
            print(f"Error in time command: {str(e)}")
            return f"I encountered an error getting the time: {str(e)}"
