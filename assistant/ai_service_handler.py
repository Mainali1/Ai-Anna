import os
import json
from typing import Optional, Dict, List, Any
from pathlib import Path
import requests
from threading import Lock

class AIServiceHandler:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.service_lock = Lock()
        self.available_services = {}
        self.current_service = None
        self._initialize_services()

    def _initialize_services(self):
        """Initialize and detect available AI services"""
        # Detect local AI models
        self._detect_local_models()
        # Initialize cloud service configurations
        self._setup_cloud_services()
        # Select initial service
        self._select_optimal_service()

    def _detect_local_models(self):
        """Detect available local AI models"""
        local_model_paths = [
            Path.home() / '.local' / 'share' / 'ai_models',
            Path(__file__).parent / 'resources' / 'models'
        ]

        for path in local_model_paths:
            if path.exists():
                for model_dir in path.glob('*'):
                    if self._validate_local_model(model_dir):
                        self.available_services[model_dir.name] = {
                            'type': 'local',
                            'path': str(model_dir),
                            'capabilities': self._get_model_capabilities(model_dir)
                        }

    def _validate_local_model(self, model_path: Path) -> bool:
        """Validate if a local model is properly formatted and accessible"""
        try:
            config_file = model_path / 'config.json'
            if not config_file.exists():
                return False

            with open(config_file, 'r') as f:
                config = json.load(f)

            required_fields = ['model_type', 'version', 'capabilities']
            return all(field in config for field in required_fields)
        except Exception:
            return False

    def _get_model_capabilities(self, model_path: Path) -> List[str]:
        """Get the capabilities of a local model"""
        try:
            config_file = model_path / 'config.json'
            with open(config_file, 'r') as f:
                config = json.load(f)
            return config.get('capabilities', [])
        except Exception:
            return []

    def _setup_cloud_services(self):
        """Setup available cloud AI services"""
        cloud_services = {
            'openai': {
                'type': 'cloud',
                'url': 'https://api.openai.com/v1',
                'capabilities': ['text_generation', 'text_completion', 'summarization']
            },
            'huggingface': {
                'type': 'cloud',
                'url': 'https://api-inference.huggingface.co',
                'capabilities': ['text_generation', 'summarization', 'translation']
            }
        }

        for name, service in cloud_services.items():
            if self._validate_cloud_service(service):
                self.available_services[name] = service

    def _validate_cloud_service(self, service: Dict) -> bool:
        """Validate if a cloud service is accessible"""
        try:
            response = requests.get(
                f"{service['url']}/health",
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False

    def _select_optimal_service(self):
        """Select the best available AI service based on capabilities and performance"""
        with self.service_lock:
            # Prioritize local services if available
            local_services = {name: service for name, service in self.available_services.items()
                            if service['type'] == 'local'}
            if local_services:
                self.current_service = next(iter(local_services.items()))
                return

            # Fall back to cloud services
            cloud_services = {name: service for name, service in self.available_services.items()
                            if service['type'] == 'cloud'}
            if cloud_services:
                self.current_service = next(iter(cloud_services.items()))

    def process_text(self, text: str, task_type: str) -> Dict[str, Any]:
        """Process text using the current AI service"""
        if not self.current_service:
            return {'error': 'No AI service available'}

        service_name, service_config = self.current_service
        try:
            if service_config['type'] == 'local':
                return self._process_local(text, task_type, service_config)
            else:
                return self._process_cloud(text, task_type, service_config)
        except Exception as e:
            # If current service fails, try to switch to another service
            self._handle_service_failure(service_name)
            return {'error': f'Processing failed: {str(e)}'}

    def _process_local(self, text: str, task_type: str, service_config: Dict) -> Dict[str, Any]:
        """Process text using a local AI model"""
        # Implementation for local model processing
        pass

    def _process_cloud(self, text: str, task_type: str, service_config: Dict) -> Dict[str, Any]:
        """Process text using a cloud AI service"""
        # Implementation for cloud service processing
        pass

    def _handle_service_failure(self, failed_service: str):
        """Handle service failure by switching to another available service"""
        with self.service_lock:
            if failed_service in self.available_services:
                del self.available_services[failed_service]
            self._select_optimal_service()

    def get_service_status(self) -> Dict[str, Any]:
        """Get the current status of AI services"""
        return {
            'current_service': self.current_service[0] if self.current_service else None,
            'available_services': list(self.available_services.keys()),
            'service_types': {
                name: service['type']
                for name, service in self.available_services.items()
            }
        }