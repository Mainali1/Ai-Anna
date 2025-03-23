from assistant.gui import AssistantGUI
from assistant.voice_engine import VoiceEngine
from assistant.command_handler import CommandHandler
from assistant.study_manager import StudyManager
from assistant.database import DatabaseHandler
from assistant.music_controller import MediaController  # Changed from MusicController
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
from assistant.env_loader import load_environment_variables
from assistant.enhanced_context_manager import EnhancedContextManager
from assistant.dynamic_response_generator import DynamicResponseGenerator
import json
import logging
import os
import sys

def main():
    try:
        # Load environment variables first
        if not load_environment_variables():
            print("Failed to load environment variables. Check your .env file.")
            return
            
        # Initialize container and core services
        container = setup_application()
        logger = container.get_service('logger')
        config = container.get_service('config')
        
        # Initialize root window
        try:
            root = ThemedTk(theme="black")
        except Exception as e:
            logger.error(f"Failed to initialize window: {str(e)}")
            raise RuntimeError(f"Failed to initialize window: {str(e)}")

        # Initialize core components with error handling
        try:
            # Add more detailed logging for each component initialization
            print("Initializing database handler...")
            db_handler = DatabaseHandler()
            container.register_service('db_handler', db_handler)
            
            # Initialize conversation storage first
            print("Initializing conversation storage...")
            from assistant.conversation_storage import ConversationStorage
            conversation_storage = ConversationStorage()
            container.register_service('conversation_storage', conversation_storage)
            
            # Then initialize the rest of the components
            print("Initializing spaced repetition system...")
            spaced_repetition = SpacedRepetitionSystem(db_handler)
            container.register_service('spaced_repetition', spaced_repetition)
            
            print("Initializing study manager...")
            study_manager = StudyManager(db_handler)
            container.register_service('study_manager', study_manager)
            
            print("Initializing media controller...")
            # Update the import statement
            from assistant.music_controller import MediaController
            media_controller = MediaController()
            media_controller.config = config
            container.register_service('music_controller', media_controller)
            
            # Fix how we set the config on the media controller
            try:
                # Pass the config object properly
                media_controller.config = config
                print("Setting media path...")
                media_controller.set_music_path()
            except Exception as e:
                print(f"Error setting media path: {str(e)}")
                # Continue without setting the media path
            
            print("Initializing email manager...")
            email_manager = EmailManager()
            container.register_service('email_manager', email_manager)
            
            print("Initializing AI service...")
            ai_service = AIServiceHandler(config)
            container.register_service('ai_service', ai_service)
            
            print("Initializing file system handler...")
            file_system = FileSystemHandler()
            container.register_service('file_system', file_system)
            
            print("Initializing external services...")
            external_services = ExternalServices(config)
            container.register_service('external_services', external_services)
            
            # Initialize conversation storage and enhanced context components
            print("Initializing enhanced context manager...")
            enhanced_context = EnhancedContextManager(conversation_storage)
            container.register_service('enhanced_context', enhanced_context)
            
            # Initialize dynamic response generator
            print("Initializing dynamic response generator...")
            dynamic_response = DynamicResponseGenerator(conversation_storage, enhanced_context)
            container.register_service('dynamic_response', dynamic_response)
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Failed to initialize core components: {str(e)}\n{error_details}")
            print(f"Detailed error: {error_details}")
            raise RuntimeError(f"Failed to initialize core components: {str(e)}")
        
        # Initialize GUI with container
        try:
            gui = AssistantGUI(root, config, container)
            container.register_service('gui', gui)
        except Exception as e:
            logger.error(f"Failed to initialize GUI: {str(e)}")
            raise RuntimeError(f"Failed to initialize GUI: {str(e)}")
        
        # Initialize VoiceEngine and CommandHandler
        try:
            voice_engine = VoiceEngine(gui, None, config)
            container.register_service('voice_engine', voice_engine)
            
            # Update when passing to CommandHandler
            command_handler = CommandHandler(
                gui, 
                voice_engine, 
                study_manager, 
                media_controller,
                email_manager, 
                config, 
                spaced_repetition, 
                ai_service, 
                file_system, 
                external_services
            )
            container.register_service('command_handler', command_handler)
            
            # Connect components
            voice_engine.command_handler = command_handler
            gui.command_handler = command_handler
            media_controller.config = config
            
        except Exception as e:
            logger.error(f"Failed to initialize voice engine or command handler: {str(e)}")
            raise RuntimeError(f"Failed to initialize voice engine or command handler: {str(e)}")
        
        logger.info("Application initialized successfully")
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
    
    # Setup configuration with error handling
    try:
        config_manager = ConfigManager()
        # Print the loaded config for debugging
        print("Config loaded successfully:", config_manager.config.keys())
        container.register_service('config', config_manager)
    except Exception as e:
        print(f"Error loading configuration: {str(e)}")
        import traceback
        print(traceback.format_exc())
        # Create a minimal config to allow the application to continue
        config_manager = ConfigManager()
        container.register_service('config', config_manager)
    
    # Setup session manager with error handling
    try:
        session_manager = SessionManager(config_manager.get('secret_key', 'default_secret_key'))
        container.register_service('session_manager', session_manager)
    except Exception as e:
        print(f"Error setting up session manager: {str(e)}")
        # Create a minimal session manager
        session_manager = SessionManager('default_secret_key')
        container.register_service('session_manager', session_manager)
    
    # Setup backup manager
    backup_manager = BackupManager()
    container.register_service('backup_manager', backup_manager)
    
    return container

if __name__ == "__main__":
    main()