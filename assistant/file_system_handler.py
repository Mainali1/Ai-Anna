import os
import platform
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Union
import psutil

class FileSystemHandler:
    def __init__(self):
        self.system_dirs = self._get_system_directories()
        self.user_home = str(Path.home())
        self._initialize_safe_paths()

    def _get_system_directories(self) -> List[str]:
        """Get system-critical directories that should be protected"""
        system = platform.system().lower()
        if system == 'windows':
            return [
                os.environ.get('SystemRoot', 'C:\\Windows'),
                os.environ.get('SystemDrive', 'C:') + '\\Program Files',
                os.environ.get('SystemDrive', 'C:') + '\\Program Files (x86)',
                os.environ.get('SystemDrive', 'C:') + '\\ProgramData'
            ]
        return ['/sys', '/boot', '/bin', '/sbin', '/etc', '/var', '/usr']

    def _initialize_safe_paths(self):
        """Initialize paths that are safe to access"""
        self.safe_paths = {
            'documents': os.path.join(self.user_home, 'Documents'),
            'downloads': os.path.join(self.user_home, 'Downloads'),
            'pictures': os.path.join(self.user_home, 'Pictures'),
            'music': os.path.join(self.user_home, 'Music'),
            'videos': os.path.join(self.user_home, 'Videos')
        }
        # Create directories if they don't exist
        for path in self.safe_paths.values():
            os.makedirs(path, exist_ok=True)

    def is_path_safe(self, path: str) -> bool:
        """Check if a path is safe to access"""
        try:
            path = os.path.abspath(path)
            
            # Check for system directories
            if any(path.lower().startswith(sys_dir.lower()) for sys_dir in self.system_dirs):
                return False
            
            # Check for suspicious patterns
            suspicious_patterns = ['%temp%', 'system32', 'windows']
            if any(pattern in path.lower() for pattern in suspicious_patterns):
                return False
            
            # Check if path exists and is accessible
            if os.path.exists(path):
                return os.access(path, os.R_OK)
            
            # If path doesn't exist, check parent directory
            parent = os.path.dirname(path)
            return os.access(parent, os.W_OK)
        except Exception:
            return False

    def list_directory(self, path: Optional[str] = None) -> Dict[str, Union[str, List[str], str]]:
        """List contents of a directory with detailed information"""
        try:
            if not path:
                path = self.user_home
            path = os.path.abspath(path)

            if not self.is_path_safe(path):
                return {'error': 'Access denied: Path is not safe or accessible'}

            items = []
            total_size = 0
            for entry in os.scandir(path):
                try:
                    item_info = {
                        'name': entry.name,
                        'type': 'directory' if entry.is_dir() else 'file',
                        'size': 0 if entry.is_dir() else entry.stat().st_size,
                        'modified': entry.stat().st_mtime
                    }
                    items.append(item_info)
                    if not entry.is_dir():
                        total_size += entry.stat().st_size
                except Exception as e:
                    continue

            return {
                'path': path,
                'items': items,
                'total_size': total_size,
                'free_space': psutil.disk_usage(path).free
            }
        except Exception as e:
            return {'error': f'Failed to list directory: {str(e)}'}

    def create_directory(self, path: str) -> Dict[str, str]:
        """Create a new directory with proper permissions"""
        try:
            path = os.path.abspath(path)
            if not self.is_path_safe(path):
                return {'error': 'Access denied: Path is not safe'}

            os.makedirs(path, exist_ok=True)
            return {'success': f'Created directory: {path}'}
        except Exception as e:
            return {'error': f'Failed to create directory: {str(e)}'}

    def delete_item(self, path: str) -> Dict[str, str]:
        """Delete a file or directory safely"""
        try:
            path = os.path.abspath(path)
            if not self.is_path_safe(path):
                return {'error': 'Access denied: Path is not safe'}

            if os.path.isdir(path):
                shutil.rmtree(path)
                return {'success': f'Deleted directory: {path}'}
            else:
                os.remove(path)
                return {'success': f'Deleted file: {path}'}
        except Exception as e:
            return {'error': f'Failed to delete item: {str(e)}'}

    def move_item(self, source: str, destination: str) -> Dict[str, str]:
        """Move a file or directory safely"""
        try:
            source = os.path.abspath(source)
            destination = os.path.abspath(destination)

            if not (self.is_path_safe(source) and self.is_path_safe(destination)):
                return {'error': 'Access denied: One or both paths are not safe'}

            if os.path.exists(destination):
                return {'error': 'Destination already exists'}

            shutil.move(source, destination)
            return {'success': f'Moved {source} to {destination}'}
        except Exception as e:
            return {'error': f'Failed to move item: {str(e)}'}

    def copy_item(self, source: str, destination: str) -> Dict[str, str]:
        """Copy a file or directory safely"""
        try:
            source = os.path.abspath(source)
            destination = os.path.abspath(destination)

            if not (self.is_path_safe(source) and self.is_path_safe(destination)):
                return {'error': 'Access denied: One or both paths are not safe'}

            if os.path.exists(destination):
                return {'error': 'Destination already exists'}

            if os.path.isdir(source):
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)
            return {'success': f'Copied {source} to {destination}'}
        except Exception as e:
            return {'error': f'Failed to copy item: {str(e)}'}

    def get_file_info(self, path: str) -> Dict[str, Union[str, int, float]]:
        """Get detailed information about a file or directory"""
        try:
            path = os.path.abspath(path)
            if not self.is_path_safe(path):
                return {'error': 'Access denied: Path is not safe'}

            stats = os.stat(path)
            return {
                'path': path,
                'type': 'directory' if os.path.isdir(path) else 'file',
                'size': stats.st_size,
                'created': stats.st_ctime,
                'modified': stats.st_mtime,
                'accessed': stats.st_atime,
                'permissions': oct(stats.st_mode)[-3:]
            }
        except Exception as e:
            return {'error': f'Failed to get file info: {str(e)}'}