"""
Basic tests for ORDIS-A.I. components
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ordis_ai.file_operations import FileOperations
from ordis_ai.command_executor import CommandExecutor

class TestFileOperations(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            "file_access": {
                "allowed_paths": ["/tmp", "."],
                "restricted_paths": ["/root", "/etc/passwd"],
                "allow_hidden_files": False
            }
        }
        self.file_ops = FileOperations(self.config)
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        # Clean up test directory
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_write_and_read_file(self):
        """Test writing and reading a file"""
        test_file = os.path.join(self.test_dir, "test.txt")
        test_content = "Hello, ORDIS-A.I.!"

        # Write file
        result = self.file_ops.write_file(test_file, test_content)
        self.assertTrue(result, "File should be written successfully")

        # Read file
        content = self.file_ops.read_file(test_file)
        self.assertEqual(content, test_content, "File content should match")

    def test_list_directory(self):
        """Test listing directory contents"""
        # Create a few test files
        test_file1 = os.path.join(self.test_dir, "file1.txt")
        test_file2 = os.path.join(self.test_dir, "file2.txt")

        self.file_ops.write_file(test_file1, "Content 1")
        self.file_ops.write_file(test_file2, "Content 2")

        # List directory
        items = self.file_ops.list_directory(self.test_dir)
        self.assertIsNotNone(items, "Should be able to list directory")
        self.assertGreaterEqual(len(items), 2, "Should have at least 2 files")

    def test_get_file_info(self):
        """Test getting file information"""
        test_file = os.path.join(self.test_dir, "info_test.txt")
        test_content = "Test content for info"

        self.file_ops.write_file(test_file, test_content)

        info = self.file_ops.get_file_info(test_file)
        self.assertIsNotNone(info, "Should get file info")
        self.assertEqual(info['name'], "info_test.txt")
        self.assertTrue(info['is_file'])
        self.assertFalse(info['is_directory'])
        self.assertGreater(info['size'], 0)

class TestCommandExecutor(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            "command_execution": {
                "allow_python": True,
                "allow_bash": True,
                "require_confirmation": False,  # Disable for testing
                "timeout_seconds": 10
            },
            "file_access": {
                "allowed_paths": ["/tmp", "."],
                "restricted_paths": ["/root", "/etc/passwd"],
                "allow_hidden_files": False
            },
            "security": {
                "confirm_dangerous_commands": False,  # Disable for testing
                "allow_network_requests": True,
                "sandbox_mode": False
            }
        }
        self.cmd_exec = CommandExecutor(self.config)

    def test_bash_command(self):
        """Test executing a bash command"""
        result = self.cmd_exec.execute_bash_command("echo 'Hello World'")
        self.assertTrue(result['success'], "Command should execute successfully")
        self.assertEqual(result['stdout'].strip(), "Hello World")

    def test_python_code(self):
        """Test executing Python code"""
        result = self.cmd_exec.execute_python_code("print('Hello from Python')")
        self.assertTrue(result['success'], "Python code should execute successfully")
        self.assertEqual(result['stdout'].strip(), "Hello from Python")

    def test_python_file(self):
        """Test executing a Python file"""
        # Create a temporary Python file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("print('Hello from temp file')\n")
            temp_file = f.name

        try:
            result = self.cmd_exec.execute_python_file(temp_file)
            self.assertTrue(result['success'], "Python file should execute successfully")
            self.assertEqual(result['stdout'].strip(), "Hello from temp file")
        finally:
            # Clean up
            os.unlink(temp_file)

if __name__ == '__main__':
    unittest.main()