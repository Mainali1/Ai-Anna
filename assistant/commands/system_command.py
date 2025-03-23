from . import Command
# Ensure proper imports for Windows Registry
import os
import subprocess
import webbrowser
import re
import glob
import winreg
import ctypes
from pathlib import Path

class SystemCommand(Command):
    def __init__(self, handler):
        super().__init__(handler)
        # Common paths are just fallbacks now
        self.app_paths = {
            'chrome': r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            'firefox': r'C:\Program Files\Mozilla Firefox\firefox.exe',
            'edge': r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
            'notepad': r'C:\Windows\System32\notepad.exe',
            'calculator': r'C:\Windows\System32\calc.exe',
            'explorer': r'C:\Windows\explorer.exe',
        }
        
    def validate(self, command: str) -> bool:
        return 'open' in command.lower() or 'launch' in command.lower() or 'start' in command.lower()
        
    def execute(self, command: str) -> str:
        try:
            # Extract application name
            app_name = self._extract_app_name(command)
            if not app_name:
                return "I couldn't understand which application you want to open."
                
            # Try to open the application
            result, app_path = self._open_application(app_name)
            if result:
                return f"I've opened {app_name} for you."
            else:
                return f"I couldn't find or open {app_name}. Please make sure it's installed."
        except Exception as e:
            print(f"Error in system command: {str(e)}")
            return f"I encountered an error opening the application: {str(e)}"
            
    def _extract_app_name(self, command: str) -> str:
        # Extract app name from command
        # Examples: "open chrome", "launch vscode", "start notepad"
        command = command.lower()
        for action in ['open', 'launch', 'start']:
            if action in command:
                return command.split(action)[-1].strip()
        return ""
        
    def _open_application(self, app_name: str) -> tuple:
        """
        Dynamically find and open an application
        Returns: (success, path_or_error_message)
        """
        # Normalize app name
        app_name = app_name.lower().strip()
        
        # Handle web applications first
        if app_name in ['google', 'gmail', 'youtube', 'maps']:
            urls = {
                'google': 'https://www.google.com',
                'gmail': 'https://mail.google.com',
                'youtube': 'https://www.youtube.com',
                'maps': 'https://maps.google.com'
            }
            webbrowser.open(urls[app_name])
            return True, urls[app_name]
        
        # 1. Try direct command first (for simple apps like notepad, calc)
        try:
            subprocess.Popen(app_name)
            return True, app_name
        except:
            pass
            
        # 2. Check common paths from our dictionary
        if app_name in self.app_paths:
            path = os.path.expandvars(self.app_paths[app_name])
            if os.path.exists(path):
                subprocess.Popen(path)
                return True, path
        
        # 3. Search in Start Menu
        start_menu_paths = [
            os.path.join(os.environ.get('APPDATA', ''), 'Microsoft', 'Windows', 'Start Menu', 'Programs'),
            os.path.join(os.environ.get('ProgramData', ''), 'Microsoft', 'Windows', 'Start Menu', 'Programs')
        ]
        
        for start_path in start_menu_paths:
            # Look for .lnk files that match the app name
            for root, dirs, files in os.walk(start_path):
                for file in files:
                    if file.lower().endswith('.lnk') and app_name in file.lower():
                        shortcut_path = os.path.join(root, file)
                        try:
                            os.startfile(shortcut_path)
                            return True, shortcut_path
                        except:
                            pass
        
        # 4. Search in Program Files directories
        program_dirs = [
            os.environ.get('ProgramFiles', 'C:\\Program Files'),
            os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)'),
            os.environ.get('LocalAppData', '')
        ]
        
        for program_dir in program_dirs:
            if not program_dir or not os.path.exists(program_dir):
                continue
                
            # Search for executable with name containing the app_name
            for root, dirs, files in os.walk(program_dir):
                # Skip deep directories to improve performance
                if root.count(os.sep) - program_dir.count(os.sep) > 3:
                    continue
                    
                for file in files:
                    if file.lower().endswith('.exe') and app_name in file.lower():
                        exe_path = os.path.join(root, file)
                        try:
                            subprocess.Popen(exe_path)
                            return True, exe_path
                        except:
                            pass
        
        # 5. Try to find in registry (for installed applications)
        try:
            app_paths = self._get_app_paths_from_registry()
            for reg_app_name, reg_app_path in app_paths.items():
                if app_name in reg_app_name.lower():
                    subprocess.Popen(reg_app_path)
                    return True, reg_app_path
        except:
            pass
            
        return False, "Application not found"
    
    def _get_app_paths_from_registry(self):
        """Get application paths from Windows registry"""
        app_paths = {}
        try:
            # Check both HKLM and HKCU for App Paths
            registry_locations = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths")
            ]
            
            for root_key, subkey_path in registry_locations:
                try:
                    with winreg.OpenKey(root_key, subkey_path) as key:
                        # Enumerate all subkeys
                        i = 0
                        while True:
                            try:
                                # Get subkey name
                                subkey_name = winreg.EnumKey(key, i)
                                # Open the subkey
                                with winreg.OpenKey(key, subkey_name) as subkey:
                                    try:
                                        # Get the default value (path to the executable)
                                        path, _ = winreg.QueryValueEx(subkey, "")
                                        # Add to dictionary
                                        app_paths[subkey_name.lower()] = path
                                    except WindowsError:
                                        pass
                                i += 1
                            except WindowsError:
                                break
                except WindowsError:
                    pass
                    
            # Also check the Uninstall registry keys for installed applications
            uninstall_paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
            ]
            
            for root_key, subkey_path in uninstall_paths:
                try:
                    with winreg.OpenKey(root_key, subkey_path) as key:
                        i = 0
                        while True:
                            try:
                                subkey_name = winreg.EnumKey(key, i)
                                with winreg.OpenKey(key, subkey_name) as subkey:
                                    try:
                                        display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                                        install_location, _ = winreg.QueryValueEx(subkey, "InstallLocation")
                                        
                                        if display_name and install_location:
                                            # Look for executable files in the install location
                                            exe_path = self._find_exe_in_directory(install_location, display_name)
                                            if exe_path:
                                                app_paths[display_name.lower()] = exe_path
                                    except (WindowsError, FileNotFoundError):
                                        pass
                                i += 1
                            except WindowsError:
                                break
                except WindowsError:
                    pass
                    
        except Exception as e:
            print(f"Error reading registry: {e}")
            
        return app_paths
        
    def _find_exe_in_directory(self, directory, app_name):
        """Find executable files in a directory that match the app name"""
        try:
            directory_path = Path(directory)
            if not directory_path.exists():
                return None
                
            # Look for .exe files
            exe_files = list(directory_path.glob("*.exe"))
            
            # First try to find an exact match
            app_name_lower = app_name.lower()
            for exe_file in exe_files:
                if app_name_lower in exe_file.stem.lower():
                    return str(exe_file)
                    
            # If no match, return the first .exe file
            if exe_files:
                return str(exe_files[0])
                
            return None
        except Exception as e:
            print(f"Error finding executable: {e}")
            return None