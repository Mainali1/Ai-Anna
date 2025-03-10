import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import requests
from threading import Lock
from typing import Optional, List

class LLMHandler:
    def __init__(self, config):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.model_lock = Lock()
        self.is_online = True
        self.model_loaded = False
        self.model_path = os.path.join(os.path.dirname(__file__), 'resources', 'llama2')
        self.batch_size = config.get('batch_size', 4)
        self.max_length = config.get('max_length', 100)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
    def check_internet(self):
        try:
            requests.get('http://google.com', timeout=1)
            self.is_online = True
            return True
        except requests.RequestException:
            self.is_online = False
            return False
    
    def load_local_model(self) -> bool:
        if not self.model_loaded:
            try:
                with self.model_lock:
                    if not os.path.exists(self.model_path):
                        return False
                    
                    self.tokenizer = AutoTokenizer.from_pretrained(
                        self.model_path,
                        use_fast=True
                    )
                    self.model = AutoModelForCausalLM.from_pretrained(
                        self.model_path,
                        torch_dtype=torch.float16 if self.device == 'cuda' else torch.float32,
                        device_map='auto' if self.device == 'cuda' else None,
                        low_cpu_mem_usage=True
                    )
                    
                    if self.device == 'cpu':
                        self.model = self.model.to(self.device)
                    
                    self.model_loaded = True
                return True
            except Exception as e:
                print(f"Error loading local model: {str(e)}")
                return False
        return True
    
    def unload_local_model(self):
        with self.model_lock:
            if self.model:
                del self.model
                del self.tokenizer
                if self.device == 'cuda':
                    torch.cuda.empty_cache()
                self.model = None
                self.tokenizer = None
                self.model_loaded = False
    
    def generate_response(self, prompt: str, max_length: Optional[int] = None) -> str:
        if not self.check_internet() and not self.load_local_model():
            return "I apologize, but I'm currently offline and unable to load the local model."
            
        try:
            if self.is_online:
                # Use online API for response generation
                # Implement your preferred online API here
                pass
            else:
                # Use local model for response generation
                with self.model_lock:
                    inputs = self.tokenizer(
                        prompt,
                        return_tensors="pt",
                        padding=True,
                        truncation=True,
                        max_length=self.max_length
                    ).to(self.device)
                    
                    with torch.no_grad():
                        outputs = self.model.generate(
                            **inputs,
                            max_length=max_length or self.max_length,
                            num_return_sequences=1,
                            temperature=0.7,
                            do_sample=True,
                            pad_token_id=self.tokenizer.pad_token_id
                        )
                    
                    response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                    return response
        except Exception as e:
            return f"Error generating response: {str(e)}"
        
    def generate_batch_responses(self, prompts: List[str]) -> List[str]:
        """Generate responses for multiple prompts in batch"""
        if not self.check_internet() and not self.load_local_model():
            return ["I apologize, but I'm currently offline and unable to load the local model."] * len(prompts)
        
        try:
            if self.is_online:
                # Implement batch processing for online API
                pass
            else:
                responses = []
                for i in range(0, len(prompts), self.batch_size):
                    batch = prompts[i:i + self.batch_size]
                    with self.model_lock:
                        inputs = self.tokenizer(
                            batch,
                            return_tensors="pt",
                            padding=True,
                            truncation=True,
                            max_length=self.max_length
                        ).to(self.device)
                        
                        with torch.no_grad():
                            outputs = self.model.generate(
                                **inputs,
                                max_length=self.max_length,
                                num_return_sequences=1,
                                temperature=0.7,
                                do_sample=True,
                                pad_token_id=self.tokenizer.pad_token_id
                            )
                        
                        batch_responses = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)
                        responses.extend(batch_responses)
                return responses
        except Exception as e:
            return [f"Error generating response: {str(e)}"] * len(prompts)
    
    def cleanup(self):
        self.unload_local_model()