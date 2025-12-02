"""
Metadata Scanner - Main orchestrator for scanning data engineering projects
"""
from typing import Dict, List
from datetime import datetime
from pathlib import Path
import json

from utils.file_utils import FileUtils
from utils.logger import Logger
from scanners.connector_identifier import ConnectorIdentifier


class MetadataScanner:
    """
    Main scanner class that orchestrates project analysis
    """
    
    def __init__(self, project_path: str, config_path: str = None):
        """
        Initialize metadata scanner
        
        Args:
            project_path: Root path of the project to scan
            config_path: Optional path to connector patterns config
        """
        self.project_path = Path(project_path).resolve()
        self.logger = Logger.get_logger(__name__)
        self.connector_identifier = ConnectorIdentifier(config_path)
        
        if not self.project_path.exists():
            raise ValueError(f"Project path does not exist: {project_path}")
        
        self.logger.info(f"Initialized scanner for project: {self.project_path}")
    
    def scan(self) -> Dict:
        """
        Perform complete project scan
        
        Returns:
            Dictionary containing complete metadata and analysis
        """
        self.logger.info("Starting project scan...")
        
        # Step 1: Discover all files
        self.logger.info("Discovering files...")
        files = FileUtils.scan_project(str(self.project_path))
        self.logger.info(f"Found {len(files)} files to analyze")
        
        # Step 2: Get project statistics
        project_stats = FileUtils.get_project_stats(files)
        
        # Step 3: Analyze each file
        self.logger.info("Analyzing files for connectors and metadata...")
        analyzed_files = []
        connector_summary = {}
        import_summary = {}
        sql_objects_summary = {
            'tables': set(),
            'views': set()
        }
        
        for idx, file_info in enumerate(files, 1):
            if idx % 10 == 0:
                self.logger.info(f"Processed {idx}/{len(files)} files...")
            
            try:
                content = FileUtils.read_file_content(file_info['absolute_path'])
                analysis = self.connector_identifier.analyze_file(file_info, content)
                
                # Merge file info with analysis
                analyzed_file = {**file_info, **analysis}
                analyzed_files.append(analyzed_file)
                
                # Aggregate connector usage
                for connector_name, connector_data in analysis['connectors'].items():
                    if connector_name not in connector_summary:
                        connector_summary[connector_name] = {
                            'total_files': 0,
                            'total_instances': 0,
                            'type': connector_data['type'],
                            'files': []
                        }
                    connector_summary[connector_name]['total_files'] += 1
                    connector_summary[connector_name]['total_instances'] += connector_data['count']
                    connector_summary[connector_name]['files'].append(file_info['relative_path'])
                
                # Aggregate imports
                for imp in analysis['imports']:
                    import_summary[imp] = import_summary.get(imp, 0) + 1
                
                # Aggregate SQL objects
                for table in analysis['sql_objects'].get('tables', []):
                    sql_objects_summary['tables'].add(table)
                for view in analysis['sql_objects'].get('views', []):
                    sql_objects_summary['views'].add(view)
                
            except Exception as e:
                self.logger.error(f"Error analyzing {file_info['relative_path']}: {e}")
                analyzed_files.append({
                    **file_info,
                    'error': str(e),
                    'file_type': 'error'
                })
        
        self.logger.info("Scan complete!")
        
        # Step 4: Build final metadata structure
        metadata = {
            'scan_metadata': {
                'project_path': str(self.project_path),
                'project_name': self.project_path.name,
                'scan_timestamp': datetime.now().isoformat(),
                'analyzer_version': '1.0.0'
            },
            'project_statistics': {
                **project_stats,
                'total_loc': sum(f.get('lines_of_code', 0) for f in analyzed_files),
                'files_with_spark': sum(1 for f in analyzed_files if f.get('has_spark', False)),
                'files_with_sql': sum(1 for f in analyzed_files if f.get('has_sql', False)),
            },
            'connector_summary': connector_summary,
            'import_summary': {
                'total_unique_imports': len(import_summary),
                'top_imports': sorted(import_summary.items(), key=lambda x: x[1], reverse=True)[:20]
            },
            'sql_objects_summary': {
                'total_tables': len(sql_objects_summary['tables']),
                'total_views': len(sql_objects_summary['views']),
                'tables': sorted(list(sql_objects_summary['tables'])),
                'views': sorted(list(sql_objects_summary['views']))
            },
            'files': analyzed_files
        }
        
        return metadata
    
    def save_metadata(self, metadata: Dict, output_path: str):
        """
        Save metadata to JSON file
        
        Args:
            metadata: Metadata dictionary
            output_path: Path to save JSON file
        """
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Metadata saved to: {output_path}")
        except Exception as e:
            self.logger.error(f"Failed to save metadata: {e}")
            raise
    
    def generate_summary_report(self, metadata: Dict) -> str:
        """
        Generate human-readable summary report
        
        Args:
            metadata: Metadata dictionary
            
        Returns:
            Formatted summary string
        """
        stats = metadata['project_statistics']
        connectors = metadata['connector_summary']
        sql_summary = metadata['sql_objects_summary']
        
        report = f"""
{'='*80}
DATA ENGINEERING PROJECT ANALYSIS REPORT
{'='*80}

Project: {metadata['scan_metadata']['project_name']}
Scan Date: {metadata['scan_metadata']['scan_timestamp']}
Path: {metadata['scan_metadata']['project_path']}

{'='*80}
PROJECT STATISTICS
{'='*80}

Total Files: {stats['total_files']}
Total Directories: {stats['total_directories']}
Total Size: {stats['total_size_bytes'] / 1024 / 1024:.2f} MB
Total Lines of Code: {stats['total_loc']:,}

Files with Spark: {stats['files_with_spark']}
Files with SQL: {stats['files_with_sql']}

File Type Breakdown:
"""
        for file_type, count in stats['file_types'].items():
            report += f"  {file_type}: {count}\n"
        
        report += f"""
{'='*80}
CONNECTORS DETECTED ({len(connectors)})
{'='*80}
"""
        
        if connectors:
            for connector_name, connector_data in sorted(connectors.items()):
                report += f"\n{connector_name.upper()} ({connector_data['type']})\n"
                report += f"  Files: {connector_data['total_files']}\n"
                report += f"  Instances: {connector_data['total_instances']}\n"
        else:
            report += "No connectors detected\n"
        
        report += f"""
{'='*80}
SQL OBJECTS
{'='*80}

Total Tables Referenced: {sql_summary['total_tables']}
Total Views Referenced: {sql_summary['total_views']}
"""
        
        if sql_summary['tables']:
            report += f"\nTop 10 Tables:\n"
            for table in sorted(sql_summary['tables'])[:10]:
                report += f"  - {table}\n"
        
        report += f"\n{'='*80}\n"
        
        return report
