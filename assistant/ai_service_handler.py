import os
import json
import time
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
            # Add timeout and retry logic
            for attempt in range(3):
                try:
                    response = requests.get(
                        f"{service['url']}/health",
                        timeout=5,
                        headers={'User-Agent': 'Anna-AI-Assistant'}
                    )
                    if response.status_code == 200:
                        return True
                    time.sleep(1)
                except requests.RequestException:
                    continue
            return False
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
        # Check for AI configuration under either 'ai_service' or 'ai_services' key
        ai_config = None
        if self.config.get('ai_service'):
            ai_config = self.config['ai_service']
        elif self.config.get('ai_services'):
            ai_config = self.config['ai_services']
        
        if not ai_config:
            return {'error': 'AI service configuration missing'}
        provider = service_config.get('name', ai_config.get('preferred_provider'))

        if provider == 'openai':
            return self._process_openai(text, task_type, ai_config['openai'])
        elif provider == 'huggingface':
            return self._process_huggingface(text, task_type, ai_config['huggingface'])
        else:
            return {'error': f'Unsupported cloud provider: {provider}'}

    def _process_openai(self, text: str, task_type: str, config: Dict) -> Dict[str, Any]:
        """Process text using OpenAI API"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return {'error': 'OpenAI API key not configured in environment'}

        try:
            import openai
            openai.api_key = api_key

            response = openai.ChatCompletion.create(
                model=config.get('model', 'gpt-3.5-turbo'),
                messages=[
                    {"role": "system", "content": f"You are an AI assistant helping with {task_type}"},
                    {"role": "user", "content": text}
                ],
                temperature=0.7
            )

            return {
                'response': response.choices[0].message['content'],
                'provider': 'openai'
            }
        except Exception as e:
            return {'error': f'OpenAI processing failed: {str(e)}'}

    def _process_huggingface(self, text: str, task_type: str, config: Dict) -> Dict[str, Any]:
        """Process text using HuggingFace API"""
        api_key = os.getenv('HUGGINGFACE_API_KEY')
        if not api_key:
            return {'error': 'HuggingFace API key not configured in environment'}

        try:
            import requests
            headers = {"Authorization": f"Bearer {api_key}"}
            api_url = f"https://api-inference.huggingface.co/models/{config.get('model', 'gpt2')}"

            response = requests.post(api_url, headers=headers, json={"inputs": text})
            response.raise_for_status()

            return {
                'response': response.json()[0]['generated_text'],
                'provider': 'huggingface'
            }
        except Exception as e:
            return {'error': f'HuggingFace processing failed: {str(e)}'}

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