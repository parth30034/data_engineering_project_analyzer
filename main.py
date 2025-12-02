"""
Main entry point for Data Engineering Project Analyzer
"""
import argparse
import sys
from pathlib import Path

from scanners.metadata_scanner import MetadataScanner
from utils.logger import Logger


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description='Analyze data engineering projects for metadata, connectors, and dependencies'
    )
    
    parser.add_argument(
        '--project-path',
        type=str,
        required=True,
        help='Path to the data engineering project to analyze'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='metadata_report.json',
        help='Output JSON file path (default: metadata_report.json)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to custom connector patterns config (optional)'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--print-summary',
        action='store_true',
        help='Print summary report to console'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logger = Logger.get_logger(__name__, level=args.log_level)
    
    try:
        logger.info("="*80)
        logger.info("DATA ENGINEERING PROJECT ANALYZER")
        logger.info("="*80)
        
        # Initialize scanner
        scanner = MetadataScanner(
            project_path=args.project_path,
            config_path=args.config
        )
        
        # Perform scan
        metadata = scanner.scan()
        
        # Save metadata
        scanner.save_metadata(metadata, args.output)
        
        # Print summary if requested
        if args.print_summary:
            summary = scanner.generate_summary_report(metadata)
            print(summary)
        
        logger.info("="*80)
        logger.info("Analysis complete!")
        logger.info(f"Results saved to: {args.output}")
        logger.info("="*80)
        
        return 0
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
