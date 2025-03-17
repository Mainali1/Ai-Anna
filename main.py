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
from assistant.external_services import ExternalServices
from ttkthemes import ThemedTk
from assistant.dependency_container import DependencyContainer
from assistant.event_system import EventSystem
from assistant.session_manager import SessionManager
from assistant.backup_manager import BackupManager
from assistant.logger import LogManager
import json

def main():
    try:
        # Initialize root window and config
        try:
            root = ThemedTk(theme="black")
            config = ConfigManager()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize window or config: {str(e)}")

        
        # Initialize core components with error handling
        try:
            db_handler = DatabaseHandler()
            spaced_repetition = SpacedRepetitionSystem(db_handler)
            study_manager = StudyManager(db_handler)
            music_controller = MusicController()
            email_manager = EmailManager()
            ai_service = AIServiceHandler(config.config)
            file_system = FileSystemHandler()
            external_services = ExternalServices(config.config)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize core components: {str(e)}")
        
        # Initialize GUI first
        try:
            gui = AssistantGUI(root, config)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize GUI: {str(e)}")
        
        # Initialize VoiceEngine and CommandHandler AFTER GUI
        try:
            voice_engine = VoiceEngine(gui, None, config)  # Initialize voice engine first
            command_handler = CommandHandler(
                gui=gui,
                voice_engine=voice_engine,  # Pass initialized voice engine
                study_manager=study_manager,
                music_controller=music_controller,
                email_manager=email_manager,
                config=config,
                spaced_repetition=spaced_repetition,
                ai_service=ai_service,
                file_system=file_system,
                external_services=external_services
            )
            voice_engine.command_handler = command_handler  # Update voice engine's reference
        except Exception as e:
            raise RuntimeError(f"Failed to initialize voice engine or command handler: {str(e)}")
        
        # Connect components PROPERLY
        gui.command_handler = command_handler  # Fixes text input
        voice_engine.command_handler = command_handler  # Fixes voice commands
        music_controller.config = config
        
        root.mainloop()
    except Exception as e:
        print(f"Critical error during initialization: {str(e)}")
        logging.error(f"Critical initialization error: {str(e)}")
        raise SystemExit(1)


def setup_application():
    # Initialize container
    container = DependencyContainer()
    
    # Setup logger
    log_manager = LogManager()
    logger = log_manager.get_logger()
    container.register_service('logger', logger)
    
    # Setup event system
    event_system = EventSystem()
    container.register_service('events', event_system)
    
    # Setup session manager
    with open('config.json', 'r') as f:
        config = json.load(f)
    session_manager = SessionManager(config['secret_key'])
    container.register_service('session_manager', session_manager)
    
    # Setup backup manager
    backup_manager = BackupManager()
    container.register_service('backup_manager', backup_manager)
    
    return container

if __name__ == "__main__":
    container = setup_application()
    logger = container.get_service('logger')
    logger.info("Application started")
    
    # Start the application
    try:
        from assistant.gui import GUI
        app = GUI(container)
        app.run()
    except Exception as e:
        logger.error(f"Application error: {str(e)}")