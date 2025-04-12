from assistant.gui import AssistantGUI
from assistant.voice_engine import VoiceEngine
from assistant.command_handler import CommandHandler
from assistant.study_manager import StudyManager
from assistant.database import DatabaseHandler
from assistant.music_controller import MediaController
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

def setup_application():
    container = DependencyContainer()
    
    # Initialize config manager first
    config_manager = ConfigManager()
    container.register_service('config_manager', config_manager)
    container.register_service('config', config_manager)
    
    # Initialize logger
    log_manager = LogManager()
    container.register_service('logger', log_manager)
    
    return container

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
        
        # Validate critical configuration
        if not validate_critical_config(config, logger):
            logger.error("Critical configuration validation failed. Exiting application.")
            return
        
        # Initialize root window
        try:
            root = ThemedTk(theme="black")
        except Exception as e:
            logger.error(f"Failed to initialize window: {str(e)}")
            raise RuntimeError(f"Failed to initialize window: {str(e)}")

        # Initialize core components with error handling
        try:
            # Initialize components using dependency injection pattern
            initialize_core_components(container, config, logger)
            
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
            # Get required services from container
            db_handler = container.get_service('db_handler')
            study_manager = container.get_service('study_manager')
            media_controller = container.get_service('media_controller')
            email_manager = container.get_service('email_manager')
            spaced_repetition = container.get_service('spaced_repetition')
            ai_service = container.get_service('ai_service')
            file_system = container.get_service('file_system')
            external_services = container.get_service('external_services')
            
            # Initialize voice engine with proper dependency injection
            voice_engine = VoiceEngine(gui, None, config)
            container.register_service('voice_engine', voice_engine)
            
            # Initialize command handler with all dependencies
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
            
        except Exception as e:
            logger.error(f"Failed to initialize voice engine or command handler: {str(e)}")
            raise RuntimeError(f"Failed to initialize voice engine or command handler: {str(e)}")
        
        logger.info("Application initialized successfully")
        root.mainloop()
    except Exception as e:
        print(f"Critical error during initialization: {str(e)}")
        logging.error(f"Critical initialization error: {str(e)}")
        raise SystemExit(1)


def validate_critical_config(config, logger):
    """
    Validates that all critical configuration settings are present.
    Returns True if valid, False otherwise.
    """
    required_settings = [
        'voice_settings', 
        'gui_settings',
        'media_paths'
    ]
    
    missing_settings = []
    
    # Check for AI service configuration (could be under 'ai_service' or 'ai_services')
    if not config.get('ai_service') and not config.get('ai_services'):
        missing_settings.append('ai_service/ai_services')
    
    for setting in required_settings:
        if not config.get(setting):
            missing_settings.append(setting)
    
    if missing_settings:
        logger.error(f"Missing critical configuration settings: {', '.join(missing_settings)}")
        print(f"ERROR: Missing configuration: {', '.join(missing_settings)}")
        return False
    
    return True


def initialize_core_components(container, config, logger):
    """
    Initialize all core components with proper dependency injection.
    All components are registered with the container.
    """
    # Database initialization
    logger.info("Initializing database handler...")
    print("Initializing database handler...")
    db_handler = DatabaseHandler()
    container.register_service('db_handler', db_handler)
    
    # Conversation storage initialization
    logger.info("Initializing conversation storage...")
    print("Initializing conversation storage...")
    from assistant.conversation_storage import ConversationStorage
    conversation_storage = ConversationStorage()
    container.register_service('conversation_storage', conversation_storage)
    
    # Spaced repetition system
    logger.info("Initializing spaced repetition system...")
    print("Initializing spaced repetition system...")
    spaced_repetition = SpacedRepetitionSystem(db_handler)
    container.register_service('spaced_repetition', spaced_repetition)
    
    # Study manager
    logger.info("Initializing study manager...")
    print("Initializing study manager...")
    study_manager = StudyManager(db_handler)
    container.register_service('study_manager', study_manager)
    
    # Media controller with proper dependency injection
    logger.info("Initializing media controller...")
    print("Initializing media controller...")
    media_controller = MediaController(config=config)  # Pass config directly in constructor
    container.register_service('media_controller', media_controller)
    
    # Set media path with proper error handling
    try:
        logger.info("Setting media path...")
        print("Setting media path...")
        media_controller.set_music_path()
    except Exception as e:
        logger.warning(f"Media path setting failed: {str(e)}. Continuing without media path.")
        print(f"Error setting media path: {str(e)}")
    
    # Email manager
    logger.info("Initializing email manager...")
    print("Initializing email manager...")
    email_manager = EmailManager()
    container.register_service('email_manager', email_manager)
    
    # AI service
    logger.info("Initializing AI service...")
    print("Initializing AI service...")
    # Pass config.config instead of config directly to AIServiceHandler
    ai_service = AIServiceHandler(config.config)
    container.register_service('ai_service', ai_service)
    
    # File system handler
    logger.info("Initializing file system handler...")
    print("Initializing file system handler...")
    file_system = FileSystemHandler()
    container.register_service('file_system', file_system)
    
    # External services
    logger.info("Initializing external services...")
    print("Initializing external services...")
    external_services = ExternalServices(config)
    container.register_service('external_services', external_services)
    
    # Enhanced context manager with dependency injection
    logger.info("Initializing enhanced context manager...")
    print("Initializing enhanced context manager...")
    enhanced_context = EnhancedContextManager(conversation_storage)
    container.register_service('enhanced_context', enhanced_context)
    
    # Dynamic response generator with dependency injection
    logger.info("Initializing dynamic response generator...")
    print("Initializing dynamic response generator...")
    dynamic_response = DynamicResponseGenerator(conversation_storage, enhanced_context)
    container.register_service('dynamic_response', dynamic_response)
    
    return True


def setup_application():
    """
    Initialize the core application services and dependency container.
    
    This function sets up:
    - Dependency container for service management
    - Logging system
    - Event system for application-wide events
    - Configuration management
    - Session management for user sessions
    - Backup management for data protection
    
    Returns:
        DependencyContainer: Initialized container with core services
    """
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
        container.register_service('config_manager', config_manager)  # Register with both names
    except Exception as e:
        print(f"Error loading configuration: {str(e)}")
        import traceback
        print(traceback.format_exc())
        # Create a minimal config to allow the application to continue
        config_manager = ConfigManager()
        container.register_service('config', config_manager)
        container.register_service('config_manager', config_manager)  # Register with both names
    
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
    
    # Initialize feature toggle manager
    from assistant.feature_toggle import FeatureToggleManager
    feature_toggle = FeatureToggleManager(container)
    container.register_service('feature_toggle', feature_toggle)
    
    # Initialize search service
    from assistant.search_service import SearchService
    search_service = SearchService(container)
    container.register_service('search_service', search_service)
    
    # Initialize news service
    from assistant.news_service import NewsService
    news_service = NewsService(container)
    container.register_service('news_service', news_service)
    
    return container

if __name__ == "__main__":
    main()