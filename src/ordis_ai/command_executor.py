"""
Command Executor Module for ORDIS-A.I.
Handles safe execution of Python and Bash commands.
"""

import os
import sys
import subprocess
import threading
import tempfile
import signal
import logging
from typing import Optional, Tuple, Dict, Any, List
from pathlib import Path
import shlex
import time

logger = logging.getLogger(__name__)

class CommandExecutor:
    def __init__(self, config: dict):
        """
        Initialize command executor with configuration.

        Args:
            config: Configuration dictionary containing command execution settings
        """
        self.config = config
        self.allow_python = config.get('command_execution', {}).get('allow_python', True)
        self.allow_bash = config.get('command_execution', {}).get('allow_bash', True)
        self.require_confirmation = config.get('command_execution', {}).get('require_confirmation', True)
        self.timeout_seconds = config.get('command_execution', {}).get('timeout_seconds', 30)
        self.allowed_paths = [Path(p).resolve() for p in config.get('file_access', {}).get('allowed_paths', [])]
        self.restricted_paths = [Path(p).resolve() for p in config.get('file_access', {}).get('restricted_paths', [])]

        # Security settings
        self.confirm_dangerous = config.get('security', {}).get('confirm_dangerous_commands', True)
        self.allow_network = config.get('security', {}).get('allow_network_requests', True)
        self.sandbox_mode = config.get('security', {}).get('sandbox_mode', False)

        # Dangerous command patterns
        self.dangerous_patterns = [
            'rm -rf', 'dd if=', 'mkfs', 'fdisk', '>', '>>',  # Destructive commands
            'sudo ', 'su ', 'su -',  # Privilege escalation
            'chmod 777', 'chown ',  # Dangerous permission changes
            ':(){:|:&};:',  # Fork bomb
            'wget', 'curl',  # Network downloads (if network disabled)
            'nc ', 'netcat',  # Netcat
        ]

        # If network requests are disallowed, add download tools to dangerous list
        if not self.allow_network:
            self.dangerous_patterns.extend(['wget', 'curl', 'wget', 'aria2c'])

        logger.info(f"CommandExecutor initialized - Python: {self.allow_python}, Bash: {self.allow_bash}")

    def _is_path_allowed(self, path: Path) -> bool:
        """
        Check if a path is allowed based on file access configuration.

        Args:
            path: Path to check

        Returns:
            bool: True if path is allowed, False otherwise
        """
        try:
            resolved_path = path.resolve()

            # Check against restricted paths
            for restricted in self.restricted_paths:
                if restricted in resolved_path.parents or restricted == resolved_path:
                    logger.warning(f"Access denied to restricted path: {resolved_path}")
                    return False

            # Check against allowed paths
            if self.allowed_paths:
                is_allowed = any(allowed in resolved_path.parents or allowed == resolved_path
                               for allowed in self.allowed_paths)
                if not is_allowed:
                    logger.warning(f"Access denied to path not in allowed list: {resolved_path}")
                    return False

            return True

        except Exception as e:
            logger.error(f"Error checking path permissions: {e}")
            return False

    def _is_command_dangerous(self, command: str) -> bool:
        """
        Check if a command contains dangerous patterns.

        Args:
            command: Command string to check

        Returns:
            bool: True if command appears dangerous, False otherwise
        """
        if not self.confirm_dangerous:
            return False

        command_lower = command.lower().strip()

        for pattern in self.dangerous_patterns:
            if pattern in command_lower:
                logger.warning(f"Potentially dangerous command detected: '{command}' (matched pattern: '{pattern}')")
                return True

        return False

    def _get_user_confirmation(self, command: str) -> bool:
        """
        Get user confirmation for executing a potentially dangerous command.

        Args:
            command: Command to be executed

        Returns:
            bool: True if user confirms, False otherwise
        """
        try:
            response = input(f"\n⚠️  WARNING: This command may be dangerous:\n   {command}\n\nAre you sure you want to execute it? (yes/no): ")
            return response.lower().strip() in ['yes', 'y']
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled by user.")
            return False

    def _execute_with_timeout(self, cmd: List[str], timeout: int,
                            cwd: Optional[str] = None,
                            env: Optional[Dict[str, str]] = None,
                            capture_output: bool = True) -> Tuple[int, str, str]:
        """
        Execute a command with timeout handling.

        Args:
            cmd: Command and arguments as list
            timeout: Timeout in seconds
            cwd: Working directory
            env: Environment variables
            capture_output: Whether to capture stdout/stderr

        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        try:
            # Set up subprocess parameters
            kwargs = {
                'cwd': cwd,
                'env': env
            }

            if capture_output:
                kwargs['stdout'] = subprocess.PIPE
                kwargs['stderr'] = subprocess.PIPE
                kwargs['text'] = True

            # Execute the process
            process = subprocess.Popen(cmd, **kwargs)

            try:
                stdout, stderr = process.communicate(timeout=timeout)
                return_code = process.returncode
                return return_code, stdout or "", stderr or ""
            except subprocess.TimeoutExpired:
                # Kill the process if it times out
                process.kill()
                stdout, stderr = process.communicate()
                return_code = process.returncode
                error_msg = f"Command timed out after {timeout} seconds"
                logger.warning(error_msg)
                return return_code, (stdout or "") + f"\n{error_msg}", (stderr or "")

        except FileNotFoundError:
            error_msg = f"Command not found: {cmd[0]}"
            logger.error(error_msg)
            return 127, "", error_msg
        except Exception as e:
            error_msg = f"Error executing command: {str(e)}"
            logger.error(error_msg)
            return 1, "", error_msg

    def execute_bash_command(self, command: str, cwd: Optional[str] = None,
                           timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute a bash command safely.

        Args:
            command: Bash command string to execute
            cwd: Working directory (optional)
            timeout: Timeout in seconds (optional, uses config default if not provided)

        Returns:
            Dictionary with keys: success, return_code, stdout, stderr, error
        """
        result = {
            'success': False,
            'return_code': None,
            'stdout': '',
            'stderr': '',
            'error': ''
        }

        # Check if bash commands are allowed
        if not self.allow_bash:
            result['error'] = "Bash command execution is disabled in configuration"
            logger.warning("Attempted to execute bash command when disabled")
            return result

        # Validate command
        if not command or not command.strip():
            result['error'] = "Empty command provided"
            return result

        command = command.strip()

        # Check for dangerous commands
        if self._is_command_dangerous(command):
            if self.require_confirmation:
                if not self._get_user_confirmation(command):
                    result['error'] = "Command execution cancelled by user"
                    return result
            else:
                # Still log the warning even if we don't require confirmation
                logger.warning(f"Executing potentially dangerous command without confirmation: {command}")

        # Validate working directory if provided
        if cwd:
            cwd_path = Path(cwd)
            if not self._is_path_allowed(cwd_path):
                result['error'] = f"Working directory not allowed: {cwd}"
                return result

        # Set timeout
        if timeout is None:
            timeout = self.timeout_seconds

        # Prepare command for execution
        try:
            # Use shell=True for bash commands to support shell features
            cmd = ['bash', '-c', command]
        except Exception as e:
            result['error'] = f"Error preparing command: {str(e)}"
            return result

        logger.info(f"Executing bash command: {command}")

        # Execute the command
        return_code, stdout, stderr = self._execute_with_timeout(cmd, timeout, cwd)

        result['return_code'] = return_code
        result['stdout'] = stdout
        result['stderr'] = stderr
        result['success'] = (return_code == 0)

        if not result['success']:
            result['error'] = stderr if stderr else f"Command failed with exit code {return_code}"
            logger.warning(f"Bash command failed: {command} (exit code {return_code})")
        else:
            logger.info(f"Bash command executed successfully: {command}")

        return result

    def execute_python_code(self, code: str, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute Python code safely.

        Args:
            code: Python code string to execute
            timeout: Timeout in seconds (optional, uses config default if not provided)

        Returns:
            Dictionary with keys: success, return_code, stdout, stderr, error
        """
        result = {
            'success': False,
            'return_code': None,
            'stdout': '',
            'stderr': '',
            'error': ''
        }

        # Check if Python execution is allowed
        if not self.allow_python:
            result['error'] = "Python code execution is disabled in configuration"
            logger.warning("Attempted to execute Python code when disabled")
            return result

        # Validate code
        if not code or not code.strip():
            result['error'] = "Empty code provided"
            return result

        code = code.strip()

        # Set timeout
        if timeout is None:
            timeout = self.timeout_seconds

        # Create a temporary file for the Python code
        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name

            logger.info(f"Executing Python code from temporary file: {temp_file}")

            # Execute the Python script
            cmd = [sys.executable, temp_file]
            return_code, stdout, stderr = self._execute_with_timeout(cmd, timeout)

            result['return_code'] = return_code
            result['stdout'] = stdout
            result['stderr'] = stderr
            result['success'] = (return_code == 0)

            if not result['success']:
                result['error'] = stderr if stderr else f"Python script failed with exit code {return_code}"
                logger.warning(f"Python code execution failed: {code[:100]}... (exit code {return_code})")
            else:
                logger.info(f"Python code executed successfully")

        except Exception as e:
            result['error'] = f"Error executing Python code: {str(e)}"
            logger.error(result['error'])
        finally:
            # Clean up temporary file
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except Exception as e:
                    logger.warning(f"Failed to delete temporary file {temp_file}: {e}")

        return result

    def execute_python_file(self, file_path: Union[str, Path],
                          timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute a Python file.

        Args:
            file_path: Path to the Python file to execute
            timeout: Timeout in seconds (optional, uses config default if not provided)

        Returns:
            Dictionary with keys: success, return_code, stdout, stderr, error
        """
        result = {
            'success': False,
            'return_code': None,
            'stdout': '',
            'stderr': '',
            'error': ''
        }

        # Check if Python execution is allowed
        if not self.allow_python:
            result['error'] = "Python code execution is disabled in configuration"
            logger.warning("Attempted to execute Python file when disabled")
            return result

        # Validate file path
        path = Path(file_path)

        # Check if file is allowed
        if not self._is_path_allowed(path):
            result['error'] = f"File path not allowed: {file_path}"
            return result

        # Check if file exists
        if not path.exists():
            result['error'] = f"File does not exist: {file_path}"
            return result

        # Check if it's a Python file
        if path.suffix.lower() != '.py':
            result['error'] = f"File is not a Python file: {file_path}"
            return result

        # Set timeout
        if timeout is None:
            timeout = self.timeout_seconds

        logger.info(f"Executing Python file: {file_path}")

        # Execute the Python file
        cmd = [sys.executable, str(path)]
        return_code, stdout, stderr = self._execute_with_timeout(cmd, timeout)

        result['return_code'] = return_code
        result['stdout'] = stdout
        result['stderr'] = stderr
        result['success'] = (return_code == 0)

        if not result['success']:
            result['error'] = stderr if stderr else f"Python script failed with exit code {return_code}"
            logger.warning(f"Python file execution failed: {file_path} (exit code {return_code})")
        else:
            logger.info(f"Python file executed successfully: {file_path}")

        return result

    def is_command_available(self, command: str) -> bool:
        """
        Check if a command is available in the system PATH.

        Args:
            command: Command name to check

        Returns:
            bool: True if command is available, False otherwise
        """
        try:
            result = subprocess.run(['which', command],
                                  capture_output=True,
                                  text=True,
                                  timeout=5)
            return result.returncode == 0
        except Exception:
            return False

    def get_available_commands(self, commands: List[str]) -> List[str]:
        """
        Filter a list of commands to only those available in the system.

        Args:
            commands: List of command names to check

        Returns:
            List of available command names
        """
        return [cmd for cmd in commands if self.is_command_available(cmd)]

# Example usage
if __name__ == "__main__":
    # Simple test
    config = {
        "command_execution": {
            "allow_python": True,
            "allow_bash": True,
            "require_confirmation": True,
            "timeout_seconds": 30
        },
        "file_access": {
            "allowed_paths": ["/tmp", "."],
            "restricted_paths": ["/root", "/etc/passwd"],
            "allow_hidden_files": False
        },
        "security": {
            "confirm_dangerous_commands": True,
            "allow_network_requests": True,
            "sandbox_mode": False
        }
    }

    executor = CommandExecutor(config)

    # Test bash command
    print("Testing bash command: echo 'Hello from ORDIS-A.I.'")
    result = executor.execute_bash_command("echo 'Hello from ORDIS-A.I.'")
    print(f"Result: {result}")

    # Test Python code
    print("\nTesting Python code: print('Hello from Python in ORDIS-A.I.')")
    result = executor.execute_python_code("print('Hello from Python in ORDIS-A.I.')")
    print(f"Result: {result}")

    # Test Python file
    test_file = "/tmp/test_script.py"
    with open(test_file, 'w') as f:
        f.write("print('Hello from test script in ORDIS-A.I.')\n")

    print(f"\nTesting Python file: {test_file}")
    result = executor.execute_python_file(test_file)
    print(f"Result: {result}")

    # Clean up
    try:
        os.unlink(test_file)
    except:
        pass