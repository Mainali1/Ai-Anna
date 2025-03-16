from assistant.gui import AssistantGUI
from assistant.voice_engine import VoiceEngine
from assistant.command_handler import CommandHandler
from assistant.study_manager import StudyManager
from assistant.database import DatabaseHandler
from assistant.music_controller import MusicController
from assistant.email_manager import EmailManager
from assistant.config_manager import ConfigManager
from assistant.spaced_repetition import SpacedRepetitionSystem
from assistant.ai_service_handler import AIServiceHandler
from assistant.file_system_handler import FileSystemHandler
from ttkthemes import ThemedTk

def main():
    try:
        # Initialize root window and config
        root = ThemedTk(theme="black")
        config = ConfigManager()
        
        # Initialize core components with error handling
        try:
            db_handler = DatabaseHandler()
            spaced_repetition = SpacedRepetitionSystem(db_handler)
            study_manager = StudyManager(db_handler)
            music_controller = MusicController()
            email_manager = EmailManager()
            ai_service = AIServiceHandler(config.config)
            file_system = FileSystemHandler()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize core components: {str(e)}")
        
        # Initialize GUI first
        try:
            gui = AssistantGUI(root, config)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize GUI: {str(e)}")
        
        # Initialize VoiceEngine and CommandHandler AFTER GUI
        try:
            command_handler = CommandHandler(
                gui=gui,
                voice_engine=None,  # Will be set after initialization
                study_manager=study_manager,
                music_controller=music_controller,
                email_manager=email_manager,
                config=config,
                spaced_repetition=spaced_repetition,
                ai_service=ai_service,
                file_system=file_system
            )
            voice_engine = VoiceEngine(gui, command_handler, config)
            command_handler.voice_engine = voice_engine  # Set voice engine after initialization
        except Exception as e:
            raise RuntimeError(f"Failed to initialize voice engine or command handler: {str(e)}")
        
        # Connect components PROPERLY
        gui.command_handler = command_handler  # Fixes text input
        voice_engine.command_handler = command_handler  # Fixes voice commands
        music_controller.config = config
        
        root.mainloop()
    except Exception as e:
        print(f"Critical error during initialization: {str(e)}")
        raise

if __name__ == "__main__":
    main()