import os
from dotenv import load_dotenv
import logging

def load_environment_variables():
    """
    Load environment variables from .env file
    """
    try:
        # Get the project root directory (parent of assistant directory)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env_path = os.path.join(project_root, '.env')
        
        # Load environment variables from .env file
        load_dotenv(env_path)
        
        # Verify critical environment variables
        critical_vars = ['PICOVOICE_ACCESS_KEY', 'WOLFRAM_APP_ID']
        missing_vars = [var for var in critical_vars if not os.getenv(var)]
        
        if missing_vars:
            logging.error(f"Missing critical environment variables: {', '.join(missing_vars)}")
            return False
        
        return True
    except Exception as e:
        logging.error(f"Error loading environment variables: {str(e)}")
        return False