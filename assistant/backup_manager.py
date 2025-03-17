import shutil
from pathlib import Path
from datetime import datetime
import json

class BackupManager:
    def __init__(self, base_dir: str = "d:/Projects/Ai-Anna"):
        self.base_dir = Path(base_dir)
        self.backup_dir = self.base_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_backup(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        
        # Backup database
        db_backup = backup_path / "database"
        db_backup.mkdir(parents=True)
        shutil.copy2(self.base_dir / "assistant/database.db", db_backup)
        
        # Backup configuration
        config_backup = backup_path / "config"
        config_backup.mkdir(exist_ok=True)
        shutil.copy2(self.base_dir / "config.json", config_backup)
        
        return str(backup_path)
        
    def restore_backup(self, backup_path: str):
        backup_path = Path(backup_path)
        if not backup_path.exists():
            raise FileNotFoundError("Backup not found")
            
        # Restore database
        shutil.copy2(backup_path / "database/database.db", self.base_dir / "assistant")
        
        # Restore configuration
        shutil.copy2(backup_path / "config/config.json", self.base_dir)