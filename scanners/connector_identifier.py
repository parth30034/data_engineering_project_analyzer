"""
Connector Identifier - Detects database and service connections in code
"""
import re
import yaml
from pathlib import Path
from typing import Dict, List, Set
from utils.logger import Logger


class ConnectorIdentifier:
    """Identifies connectors and connections in code files"""
    
    def __init__(self, config_path: str = None):
        """
        Initialize connector identifier
        
        Args:
            config_path: Path to connector patterns YAML file
        """
        self.logger = Logger.get_logger(__name__)
        
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'config' / 'connector_patterns.yaml'
        
        self.config = self._load_config(config_path)
        self.connectors = self.config.get('connectors', {})
        self.file_types = self.config.get('file_types', {})
        
        self.logger.info(f"Loaded {len(self.connectors)} connector patterns")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load connector patterns from YAML config"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            return {'connectors': {}, 'file_types': {}}
    
    def identify_file_type(self, file_info: Dict, content: str) -> str:
        """
        Identify specific file type based on extension and content
        
        Args:
            file_info: Dictionary with file metadata
            content: File content
            
        Returns:
            File type string
        """
        extension = file_info['extension']
        
        # Check for Databricks notebook
        if any(keyword in content for keyword in self.file_types.get('databricks_notebook', {}).get('keywords', [])):
            return 'databricks_notebook'
        
        # Check for PySpark
        if extension == '.py':
            if any(keyword in content for keyword in self.file_types.get('pyspark', {}).get('keywords', [])):
                return 'pyspark'
            return 'python'
        
        # Match by extension
        for file_type, props in self.file_types.items():
            if extension in props.get('extensions', []):
                return file_type
        
        return 'unknown'
    
    def identify_connectors(self, content: str) -> Dict[str, List[Dict]]:
        """
        Identify all connectors used in the code
        
        Args:
            content: File content
            
        Returns:
            Dictionary mapping connector names to detected instances
        """
        detected = {}
        
        for connector_name, patterns in self.connectors.items():
            keywords = patterns.get('keywords', [])
            connection_patterns = patterns.get('connection_patterns', [])
            connector_type = patterns.get('type', 'unknown')
            
            instances = []
            
            # Check for keywords
            for keyword in keywords:
                if keyword in content:
                    instances.append({
                        'type': 'keyword',
                        'pattern': keyword,
                        'connector_type': connector_type
                    })
            
            # Check for connection patterns using regex
            for pattern in connection_patterns:
                try:
                    matches = re.finditer(pattern, content, re.MULTILINE)
                    for match in matches:
                        instances.append({
                            'type': 'connection',
                            'pattern': pattern,
                            'match': match.group(0),
                            'line_number': content[:match.start()].count('\n') + 1,
                            'connector_type': connector_type
                        })
                except re.error as e:
                    self.logger.warning(f"Invalid regex pattern {pattern}: {e}")
            
            if instances:
                detected[connector_name] = {
                    'count': len(instances),
                    'type': connector_type,
                    'instances': instances
                }
        
        return detected
    
    def extract_imports(self, content: str, file_type: str) -> List[str]:
        """
        Extract import statements from Python/PySpark files
        
        Args:
            content: File content
            file_type: Type of file
            
        Returns:
            List of import statements
        """
        imports = []
        
        if file_type in ['python', 'pyspark', 'databricks_notebook']:
            # Match import statements
            import_patterns = [
                r'^import\s+[\w\.]+',
                r'^from\s+[\w\.]+\s+import\s+.*'
            ]
            
            for line in content.split('\n'):
                line = line.strip()
                for pattern in import_patterns:
                    if re.match(pattern, line):
                        imports.append(line)
                        break
        
        return imports
    
    def extract_sql_objects(self, content: str, file_type: str) -> Dict[str, Set[str]]:
        """
        Extract SQL objects (tables, views, schemas) from SQL or code
        
        Args:
            content: File content
            file_type: Type of file
            
        Returns:
            Dictionary with sets of tables, views, schemas
        """
        objects = {
            'tables': set(),
            'views': set(),
            'schemas': set()
        }
        
        # Patterns for SQL objects
        patterns = {
            'tables': [
                r'FROM\s+([`\"]?\w+[`\"]?\.)?([`\"]?\w+[`\"]?\.)?([`\"]?\w+[`\"]?)',
                r'JOIN\s+([`\"]?\w+[`\"]?\.)?([`\"]?\w+[`\"]?\.)?([`\"]?\w+[`\"]?)',
                r'INTO\s+([`\"]?\w+[`\"]?\.)?([`\"]?\w+[`\"]?\.)?([`\"]?\w+[`\"]?)',
                r'UPDATE\s+([`\"]?\w+[`\"]?\.)?([`\"]?\w+[`\"]?\.)?([`\"]?\w+[`\"]?)'
            ],
            'views': [
                r'CREATE\s+VIEW\s+([`\"]?\w+[`\"]?\.)?([`\"]?\w+[`\"]?\.)?([`\"]?\w+[`\"]?)',
                r'CREATE\s+OR\s+REPLACE\s+VIEW\s+([`\"]?\w+[`\"]?\.)?([`\"]?\w+[`\"]?\.)?([`\"]?\w+[`\"]?)'
            ]
        }
        
        content_upper = content.upper()
        
        for obj_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.finditer(pattern, content_upper, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    # Get the last captured group (table/view name)
                    groups = [g for g in match.groups() if g]
                    if groups:
                        obj_name = groups[-1].strip('`"\' ')
                        if obj_name and not obj_name.upper() in ['SELECT', 'AS', 'ON']:
                            objects[obj_type].add(obj_name.lower())
        
        return {k: list(v) for k, v in objects.items()}
    
    def analyze_file(self, file_info: Dict, content: str) -> Dict:
        """
        Complete analysis of a single file
        
        Args:
            file_info: File metadata dictionary
            content: File content
            
        Returns:
            Analysis results dictionary
        """
        file_type = self.identify_file_type(file_info, content)
        connectors = self.identify_connectors(content)
        imports = self.extract_imports(content, file_type)
        sql_objects = self.extract_sql_objects(content, file_type)
        
        # Count lines of code (excluding empty lines and comments)
        lines = content.split('\n')
        loc = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
        
        return {
            'file_type': file_type,
            'lines_of_code': loc,
            'total_lines': len(lines),
            'connectors': connectors,
            'imports': imports,
            'sql_objects': sql_objects,
            'has_spark': 'pyspark' in file_type or 'spark' in content.lower(),
            'has_sql': len(sql_objects.get('tables', [])) > 0 or file_type == 'sql'
        }
