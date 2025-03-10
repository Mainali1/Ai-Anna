import os
import pyautogui
import subprocess
from datetime import datetime

class SystemController:
    def __init__(self):
        self.screenshot_dir = os.path.expanduser('~/Pictures/Screenshots')
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        # Initialize common application paths
        self.app_paths = {
            'calculator': 'calc.exe',
            'notepad': 'notepad.exe',
            'paint': 'mspaint.exe',
            'explorer': 'explorer.exe',
            'task_manager': 'taskmgr.exe',
            'control_panel': 'control.exe'
        }
    
    def take_screenshot(self, region=None):
        """Take a screenshot of the entire screen or a specific region"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'screenshot_{timestamp}.png'
            filepath = os.path.join(self.screenshot_dir, filename)
            
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()
                
            screenshot.save(filepath)
            return f'Screenshot saved to {filepath}'
        except Exception as e:
            return f'Failed to take screenshot: {str(e)}'
    
    def open_application(self, app_name):
        """Open a system application by name"""
        try:
            app_path = self.app_paths.get(app_name.lower())
            if app_path:
                subprocess.Popen(app_path)
                return f'Opened {app_name}'
            else:
                return f'Application {app_name} not found'
        except Exception as e:
            return f'Failed to open {app_name}: {str(e)}'
    
    def get_system_info(self):
        """Get basic system information"""
        import platform
        system_info = {
            'system': platform.system(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor()
        }
        return system_info
    
    def list_directory(self, path=None):
        """List contents of a directory"""
        try:
            if not path:
                path = os.getcwd()
            items = os.listdir(path)
            return {'path': path, 'items': items}
        except Exception as e:
            return f'Failed to list directory: {str(e)}'
    
    def create_directory(self, path):
        """Create a new directory"""
        try:
            os.makedirs(path, exist_ok=True)
            return f'Created directory: {path}'
        except Exception as e:
            return f'Failed to create directory: {str(e)}'
    
    def delete_file(self, path):
        """Delete a file"""
        try:
            if os.path.exists(path):
                os.remove(path)
                return f'Deleted file: {path}'
            return f'File not found: {path}'
        except Exception as e:
            return f'Failed to delete file: {str(e)}'