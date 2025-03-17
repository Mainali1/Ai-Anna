from datetime import datetime, timedelta
import jwt
from typing import Optional

class SessionManager:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.session_duration = timedelta(hours=1)
        
    def create_session(self, user_id: str) -> str:
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + self.session_duration,
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
        
    def validate_session(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload if payload['exp'] > datetime.utcnow().timestamp() else None
        except jwt.InvalidTokenError:
            return None