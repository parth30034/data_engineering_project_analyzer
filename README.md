# Data Engineering Project Analyzer

## Overview
A comprehensive tool to analyze data engineering projects, identify dependencies, connectors, and generate actionable insights.

## Project Structure
```
data_engineering_analyzer/
├── config/
│   └── connector_patterns.yaml      # Connector identification patterns
├── scanners/
│   ├── metadata_scanner.py          # File discovery and metadata extraction
│   ├── connector_identifier.py      # Identify DB/API connections
│   └── file_parsers/
│       ├── python_parser.py         # Python/PySpark parser
│       ├── sql_parser.py            # SQL parser
│       └── databricks_parser.py     # Databricks notebook parser
├── analyzers/
│   ├── dependency_graph.py          # Build dependency relationships
│   └── kpi_calculator.py            # Calculate project KPIs
├── output/
│   └── json_formatter.py            # Format results as JSON
├── utils/
│   ├── file_utils.py                # File system utilities
│   └── logger.py                    # Logging configuration
├── main.py                          # Entry point
└── requirements.txt
```

## Phase 1: Metadata Scanning & Connector Identification

### Features
- Recursive project scanning
- File type identification (Python, PySpark, SQL, Databricks notebooks)
- Connector pattern matching (Snowflake, Redshift, PostgreSQL, MySQL, MongoDB, etc.)
- JSON metadata output

### Usage
```bash
python main.py --project-path /path/to/de/project --output metadata_report.json
```

## Roadmap
- [x] Phase 1: Metadata scanning and connector identification
- [ ] Phase 2: Dependency parsing and graph building
- [ ] Phase 3: KPI calculation and redundancy detection
- [ ] Phase 4: API and visualization layer
