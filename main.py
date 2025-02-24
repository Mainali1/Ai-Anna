from assistant.gui import StudentAssistantGUI
from assistant.voice_engine import VoiceEngine
from assistant.command_handler import CommandHandler
from assistant.study_manager import StudyManager  # Add this import
import tkinter as tk
from ttkthemes import ThemedTk

def main():
    root = ThemedTk(theme="equilux")
    
    # Initialize components
    study_manager = StudyManager()  # Create StudyManager instance
    command_handler = CommandHandler(None, None, study_manager)  # Add study_manager
    gui = StudentAssistantGUI(root, command_handler)
    voice_engine = VoiceEngine(gui, command_handler)
    
    # Connect components
    command_handler.gui = gui
    command_handler.voice_engine = voice_engine
    
    root.mainloop()

if __name__ == "__main__":
    main()