"""
File Operations Module for ORDIS-A.I.
Handles file reading, writing, searching, and manipulation.
"""

import os
import os.path
from pathlib import Path
import json
import csv
import logging
from typing import List, Optional, Union, Dict, Any
import mimetypes

logger = logging.getLogger(__name__)

class FileOperations:
    def __init__(self, config: dict):
        """
        Initialize file operations with configuration.

        Args:
            config: Configuration dictionary containing file access settings
        """
        self.config = config
        self.allowed_paths = [Path(p).resolve() for p in config.get('file_access', {}).get('allowed_paths', [])]
        self.restricted_paths = [Path(p).resolve() for p in config.get('file_access', {}).get('restricted_paths', [])]
        self.allow_hidden = config.get('file_access', {}).get('allow_hidden_files', False)

        # Ensure at least one allowed path exists
        if not self.allowed_paths:
            self.allowed_paths = [Path.home().resolve()]

        logger.info(f"FileOperations initialized with {len(self.allowed_paths)} allowed paths")

    def _is_path_allowed(self, path: Path) -> bool:
        """
        Check if a path is allowed based on configuration.

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

            # Check for hidden files if not allowed
            if not self.allow_hidden and any(part.startswith('.') for part in resolved_path.parts):
                logger.warning(f"Access denied to hidden file: {resolved_path}")
                return False

            return True

        except Exception as e:
            logger.error(f"Error checking path permissions: {e}")
            return False

    def read_file(self, file_path: Union[str, Path]) -> Optional[str]:
        """
        Read contents of a file.

        Args:
            file_path: Path to the file to read

        Returns:
            str: File contents, or None if error
        """
        try:
            path = Path(file_path)

            if not self._is_path_allowed(path):
                return None

            if not path.exists():
                logger.error(f"File does not exist: {path}")
                return None

            if not path.is_file():
                logger.error(f"Path is not a file: {path}")
                return None

            # Try to detect encoding
            encodings = ['utf-8', 'latin-1', 'cp1252']
            content = None

            for encoding in encodings:
                try:
                    with open(path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue

            if content is None:
                logger.error(f"Could not decode file with any encoding: {path}")
                return None

            logger.info(f"Successfully read file: {path} ({len(content)} characters)")
            return content

        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None

    def write_file(self, file_path: Union[str, Path], content: str,
                   create_dirs: bool = True) -> bool:
        """
        Write content to a file.

        Args:
            file_path: Path to the file to write
            content: Content to write to the file
            create_dirs: Whether to create parent directories if they don't exist

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            path = Path(file_path)

            if not self._is_path_allowed(path):
                return False

            if create_dirs:
                path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"Successfully wrote to file: {path} ({len(content)} characters)")
            return True

        except Exception as e:
            logger.error(f"Error writing file {file_path}: {e}")
            return False

    def list_directory(self, directory_path: Union[str, Path]) -> Optional[List[Dict[str, Any]]]:
        """
        List contents of a directory.

        Args:
            directory_path: Path to the directory to list

        Returns:
            List of dictionaries containing file/directory info, or None if error
        """
        try:
            path = Path(directory_path)

            if not self._is_path_allowed(path):
                return None

            if not path.exists():
                logger.error(f"Directory does not exist: {path}")
                return None

            if not path.is_dir():
                logger.error(f"Path is not a directory: {path}")
                return None

            items = []
            for item in path.iterdir():
                # Skip hidden files if not allowed
                if not self.allow_hidden and item.name.startswith('.'):
                    continue

                stat_info = item.stat()
                item_info = {
                    'name': item.name,
                    'path': str(item),
                    'is_file': item.is_file(),
                    'is_directory': item.is_dir(),
                    'size': stat_info.st_size,
                    'modified': stat_info.st_mtime,
                    'created': stat_info.st_ctime
                }
                items.append(item_info)

            # Sort: directories first, then files, both alphabetically
            items.sort(key=lambda x: (not x['is_directory'], x['name'].lower()))

            logger.info(f"Listed directory: {path} ({len(items)} items)")
            return items

        except Exception as e:
            logger.error(f"Error listing directory {directory_path}: {e}")
            return None

    def search_files(self, directory_path: Union[str, Path],
                     pattern: str, recursive: bool = True) -> Optional[List[Path]]:
        """
        Search for files matching a pattern.

        Args:
            directory_path: Directory to search in
            pattern: Search pattern (supports wildcards like *.txt)
            recursive: Whether to search recursively

        Returns:
            List of matching file paths, or None if error
        """
        try:
            path = Path(directory_path)

            if not self._is_path_allowed(path):
                return None

            if not path.exists():
                logger.error(f"Directory does not exist: {path}")
                return None

            if not path.is_dir():
                logger.error(f"Path is not a directory: {path}")
                return None

            if recursive:
                matches = list(path.rglob(pattern))
            else:
                matches = list(path.glob(pattern))

            # Filter by allowed paths
            allowed_matches = [m for m in matches if self._is_path_allowed(m)]

            logger.info(f"Found {len(allowed_matches)} files matching '{pattern}' in {path}")
            return allowed_matches

        except Exception as e:
            logger.error(f"Error searching files in {directory_path}: {e}")
            return None

    def get_file_info(self, file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a file.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with file information, or None if error
        """
        try:
            path = Path(file_path)

            if not self._is_path_allowed(path):
                return None

            if not path.exists():
                logger.error(f"File does not exist: {path}")
                return None

            stat_info = path.stat()
            mime_type, _ = mimetypes.guess_type(str(path))

            info = {
                'name': path.name,
                'path': str(path.resolve()),
                'parent': str(path.parent.resolve()),
                'is_file': path.is_file(),
                'is_directory': path.is_dir(),
                'size': stat_info.st_size,
                'size_human': self._human_readable_size(stat_info.st_size),
                'modified': stat_info.st_mtime,
                'created': stat_info.st_ctime,
                'accessed': stat_info.st_atime,
                'mime_type': mime_type,
                'extension': path.suffix.lower(),
                'stem': path.stem
            }

            return info

        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            return None

    def _human_readable_size(self, size_bytes: int) -> str:
        """
        Convert bytes to human readable format.

        Args:
            size_bytes: Size in bytes

        Returns:
            Human readable size string
        """
        if size_bytes == 0:
            return "0B"
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f}{size_names[i]}"

    def copy_file(self, source_path: Union[str, Path],
                  dest_path: Union[str, Path]) -> bool:
        """
        Copy a file from source to destination.

        Args:
            source_path: Source file path
            dest_path: Destination file path

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            source = Path(source_path)
            dest = Path(dest_path)

            # Check both source and destination permissions
            if not self._is_path_allowed(source) or not self._is_path_allowed(dest):
                return False

            if not source.exists():
                logger.error(f"Source file does not exist: {source}")
                return False

            if not source.is_file():
                logger.error(f"Source is not a file: {source}")
                return False

            # Create destination directory if needed
            dest.parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            import shutil
            shutil.copy2(source, dest)

            logger.info(f"Copied file from {source} to {dest}")
            return True

        except Exception as e:
            logger.error(f"Error copying file from {source_path} to {dest_path}: {e}")
            return False

    def move_file(self, source_path: Union[str, Path],
                  dest_path: Union[str, Path]) -> bool:
        """
        Move a file from source to destination.

        Args:
            source_path: Source file path
            dest_path: Destination file path

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            source = Path(source_path)
            dest = Path(dest_path)

            # Check both source and destination permissions
            if not self._is_path_allowed(source) or not self._is_path_allowed(dest):
                return False

            if not source.exists():
                logger.error(f"Source file does not exist: {source}")
                return False

            # Create destination directory if needed
            dest.parent.mkdir(parents=True, exist_ok=True)

            # Move file
            import shutil
            shutil.move(str(source), str(dest))

            logger.info(f"Moved file from {source} to {dest}")
            return True

        except Exception as e:
            logger.error(f"Error moving file from {source_path} to {dest_path}: {e}")
            return False

    def delete_file(self, file_path: Union[str, Path]) -> bool:
        """
        Delete a file.

        Args:
            file_path: Path to the file to delete

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            path = Path(file_path)

            if not self._is_path_allowed(path):
                return False

            if not path.exists():
                logger.warning(f"File does not exist: {path}")
                return False

            if not path.is_file():
                logger.error(f"Path is not a file: {path}")
                return False

            path.unlink()

            logger.info(f"Deleted file: {path}")
            return True

        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return False

# Example usage
if __name__ == "__main__":
    # Simple test
    config = {
        "file_access": {
            "allowed_paths": ["/tmp", "."],
            "restricted_paths": ["/root", "/etc/passwd"],
            "allow_hidden_files": False
        }
    }

    file_ops = FileOperations(config)

    # Test writing a file
    test_file = "/tmp/test_ordis.txt"
    if file_ops.write_file(test_file, "Hello from ORDIS-A.I.!"):
        print(f"Successfully wrote to {test_file}")

        # Test reading the file
        content = file_ops.read_file(test_file)
        if content is not None:
            print(f"Read content: {content}")

        # Test getting file info
        info = file_ops.get_file_info(test_file)
        if info:
            print(f"File info: {info}")

        # Test listing directory
        files = file_ops.list_directory("/tmp")
        if files:
            print(f"Files in /tmp: {[f['name'] for f in files[:5]]}")  # Show first 5

        # Clean up
        file_ops.delete_file(test_file)
        print(f"Cleaned up {test_file}")
    else:
        print(f"Failed to write to {test_file}")