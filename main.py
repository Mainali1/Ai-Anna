from assistant.gui import StudentAssistantGUI
from assistant.voice_engine import VoiceEngine
from assistant.command_handler import CommandHandler
from assistant.study_manager import StudyManager
from assistant.database import DatabaseHandler
from assistant.music_controller import MusicController
from assistant.email_manager import EmailManager
from assistant.config_manager import ConfigManager
from assistant.spaced_repetition import SpacedRepetitionSystem
from ttkthemes import ThemedTk

def main():
    root = ThemedTk(theme="black")
    config = ConfigManager()
    
    # Initialize core components
    db_handler = DatabaseHandler()
    spaced_repetition = SpacedRepetitionSystem(db_handler)
    study_manager = StudyManager(db_handler)
    music_controller = MusicController()
    email_manager = EmailManager()
    
    # Initialize GUI first
    gui = StudentAssistantGUI(root, config)  # Do NOT pass command_handler here
    
    # Initialize VoiceEngine and CommandHandler AFTER GUI
    voice_engine = VoiceEngine(gui, None, config)
    command_handler = CommandHandler(
        gui=gui,
        voice_engine=voice_engine,
        study_manager=study_manager,
        music_controller=music_controller,
        email_manager=email_manager,
        config=config,
        spaced_repetition=spaced_repetition
    )
    
    # Connect components PROPERLY
    gui.command_handler = command_handler  # Fixes text input
    voice_engine.command_handler = command_handler  # Fixes voice commands
    music_controller.config = config
    
    root.mainloop()

if __name__ == "__main__":
    main()