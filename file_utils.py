"""
File system utilities for scanning and reading project files
"""
import os
from pathlib import Path
from typing import List, Dict, Set
import mimetypes


class FileUtils:
    """Utility class for file operations"""
    
    # Directories to exclude from scanning
    EXCLUDED_DIRS = {
        '__pycache__', '.git', '.svn', 'node_modules', 
        'venv', 'env', '.venv', '.env', 'dist', 'build',
        '.idea', '.vscode', '.pytest_cache', '.mypy_cache',
        'htmlcov', 'coverage'
    }
    
    # File extensions to scan
    SUPPORTED_EXTENSIONS = {
        '.py', '.sql', '.ddl', '.dml', '.yaml', '.yml', 
        '.json', '.conf', '.ini', '.properties', '.sh', 
        '.bash', '.scala', '.r'
    }
    
    @staticmethod
    def scan_project(project_path: str) -> List[Dict[str, str]]:
        """
        Recursively scan project directory and return list of files
        
        Args:
            project_path: Root path of the project
            
        Returns:
            List of dictionaries containing file information
        """
        files = []
        project_path = Path(project_path).resolve()
        
        if not project_path.exists():
            raise ValueError(f"Project path does not exist: {project_path}")
        
        for root, dirs, filenames in os.walk(project_path):
            # Remove excluded directories from traversal
            dirs[:] = [d for d in dirs if d not in FileUtils.EXCLUDED_DIRS]
            
            for filename in filenames:
                file_path = Path(root) / filename
                extension = file_path.suffix.lower()
                
                # Check if file should be scanned
                if extension in FileUtils.SUPPORTED_EXTENSIONS:
                    try:
                        relative_path = file_path.relative_to(project_path)
                        files.append({
                            'absolute_path': str(file_path),
                            'relative_path': str(relative_path),
                            'filename': filename,
                            'extension': extension,
                            'directory': str(file_path.parent.relative_to(project_path)),
                            'size_bytes': file_path.stat().st_size,
                            'modified_time': file_path.stat().st_mtime
                        })
                    except Exception as e:
                        print(f"Error processing file {file_path}: {e}")
        
        return files
    
    @staticmethod
    def read_file_content(file_path: str, encoding: str = 'utf-8') -> str:
        """
        Read file content with error handling
        
        Args:
            file_path: Path to file
            encoding: File encoding (default: utf-8)
            
        Returns:
            File content as string
        """
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encodings
            for enc in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(file_path, 'r', encoding=enc) as f:
                        return f.read()
                except:
                    continue
            # If all fail, read as binary and decode with errors='ignore'
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            return f"ERROR: Could not read file - {str(e)}"
    
    @staticmethod
    def get_file_lines(file_path: str) -> int:
        """
        Count number of lines in a file
        
        Args:
            file_path: Path to file
            
        Returns:
            Number of lines
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except:
            return 0
    
    @staticmethod
    def get_project_stats(files: List[Dict[str, str]]) -> Dict:
        """
        Calculate basic statistics for the project
        
        Args:
            files: List of file dictionaries
            
        Returns:
            Dictionary with project statistics
        """
        stats = {
            'total_files': len(files),
            'total_size_bytes': sum(f['size_bytes'] for f in files),
            'file_types': {},
            'directories': set()
        }
        
        for file in files:
            ext = file['extension']
            stats['file_types'][ext] = stats['file_types'].get(ext, 0) + 1
            stats['directories'].add(file['directory'])
        
        stats['total_directories'] = len(stats['directories'])
        stats['directories'] = list(stats['directories'])
        
        return stats
