# Data Engineering Project Analyzer - Implementation Guide

## 🎯 Project Overview

This tool provides comprehensive analysis of data engineering projects, identifying:
- File metadata and statistics
- Database connectors and connections
- SQL objects (tables, views)
- Import dependencies
- Code patterns (PySpark, Databricks)

## 📁 Current Implementation (Phase 1: COMPLETE ✅)

### Architecture Components Built

```
data_engineering_analyzer/
│
├── config/
│   └── connector_patterns.yaml       # Pattern definitions for 13 connectors
│
├── scanners/
│   ├── metadata_scanner.py           # Main orchestrator
│   └── connector_identifier.py       # Connector detection engine
│
├── utils/
│   ├── file_utils.py                 # File system utilities
│   └── logger.py                     # Logging framework
│
└── main.py                           # CLI entry point
```

### Supported Technologies

**File Types:**
- Python (.py)
- PySpark (.py with Spark imports)
- SQL (.sql, .ddl, .dml)
- Databricks Notebooks (.py with MAGIC commands)
- Configuration files (.yaml, .yml, .json, .conf)

**Connectors Detected:**
1. **Databases:** Snowflake, PostgreSQL, MySQL, Redshift
2. **NoSQL:** MongoDB, Cassandra
3. **Cloud Storage:** AWS S3, Azure Blob, Google Cloud Storage
4. **Data Warehouses:** BigQuery
5. **Platforms:** Databricks
6. **Messaging:** Kafka
7. **APIs:** REST APIs (requests library)

### JSON Output Structure

```json
{
  "scan_metadata": {
    "project_path": "...",
    "project_name": "...",
    "scan_timestamp": "...",
    "analyzer_version": "1.0.0"
  },
  "project_statistics": {
    "total_files": 6,
    "total_loc": 504,
    "files_with_spark": 3,
    "files_with_sql": 5,
    "file_types": {...}
  },
  "connector_summary": {
    "snowflake": {
      "total_files": 1,
      "total_instances": 3,
      "type": "database",
      "files": ["..."]
    }
  },
  "sql_objects_summary": {
    "total_tables": 19,
    "tables": ["customers_staging", "orders_staging", ...],
    "views": ["customer_daily_metrics"]
  },
  "import_summary": {...},
  "files": [...]  // Detailed per-file analysis
}
```

## 🚀 How to Use

### Basic Usage

```bash
# Analyze a project
python main.py \
  --project-path /path/to/de/project \
  --output metadata_report.json \
  --print-summary

# With custom connector patterns
python main.py \
  --project-path /path/to/project \
  --config /path/to/custom_patterns.yaml \
  --output report.json
```

### Testing with Sample Project

A sample project is included for testing:

```bash
python main.py \
  --project-path sample_de_project \
  --output test_report.json \
  --print-summary
```

## 📊 Key Insights Generated

### Project-Level KPIs
- Total files and directories
- Total lines of code (LOC)
- File type distribution
- Files using Spark vs. SQL
- Project size (bytes)

### Connector Analysis
- Types of databases/services used
- Number of files per connector
- Total connection instances
- File-to-connector mapping

### Code Patterns
- Import frequency analysis
- SQL object references (tables/views)
- Databricks-specific patterns
- PySpark usage detection

## 🔄 Next Steps: Phase 2 - Dependency Analysis

### What to Build Next

#### 1. **Dependency Graph Builder** (`analyzers/dependency_graph.py`)

**Purpose:** Create relationships between files based on:
- Import statements (Python module dependencies)
- Table lineage (SQL table → table dependencies)
- Function calls between modules
- Configuration references

**Implementation Approach:**
```python
class DependencyGraph:
    def __init__(self, metadata: Dict):
        self.nodes = {}  # file_path -> node data
        self.edges = []  # (source, target, relationship_type)
    
    def build_import_dependencies(self):
        """Map Python import dependencies"""
        # Parse imports from each file
        # Create edges between importing and imported files
        
    def build_table_lineage(self):
        """Map table → table dependencies from SQL"""
        # Track: source tables (FROM/JOIN) → target tables (INTO)
        # Build lineage graph
        
    def detect_circular_dependencies(self):
        """Find circular dependency chains"""
        
    def find_orphan_files(self):
        """Files not imported/used anywhere"""
        
    def export_graph(self, format='json'):
        """Export as JSON/GraphML for visualization"""
```

**Output Format:**
```json
{
  "nodes": [
    {
      "id": "customer_etl.py",
      "type": "pyspark",
      "metrics": {"loc": 120}
    }
  ],
  "edges": [
    {
      "source": "customer_etl.py",
      "target": "data_validator.py",
      "type": "imports",
      "weight": 1
    },
    {
      "source": "customers_staging",
      "target": "customer_metrics",
      "type": "table_dependency",
      "operation": "INSERT FROM"
    }
  ]
}
```

#### 2. **Code Similarity Detector** (`analyzers/similarity_detector.py`)

**Purpose:** Find redundant/duplicate code

**Techniques:**
- **Function-level similarity:** Compare function signatures and body
- **SQL pattern matching:** Similar SELECT/JOIN patterns
- **Code clone detection:** Identical or near-identical blocks

**Implementation:**
```python
class SimilarityDetector:
    def find_duplicate_functions(self, threshold=0.85):
        """Find functions with similar implementations"""
        # Use AST parsing + fuzzy matching
        
    def find_duplicate_sql_patterns(self):
        """Find similar SQL queries"""
        # Normalize SQL, compare structure
        
    def find_code_clones(self):
        """Detect copy-pasted code blocks"""
        # Token-based comparison
```

#### 3. **Impact Analyzer** (`analyzers/impact_analyzer.py`)

**Purpose:** Answer "What breaks if I change X?"

```python
class ImpactAnalyzer:
    def analyze_file_change(self, file_path: str):
        """List all files/tables affected by changing this file"""
        
    def analyze_table_change(self, table_name: str):
        """List all queries/jobs affected by table change"""
        
    def find_downstream_dependencies(self, node_id: str):
        """Get all downstream dependencies"""
```

## 🏗️ Phase 3 Roadmap: Visualization & API

### Components to Build

1. **API Layer** (`api/app.py`)
   - FastAPI REST endpoints
   - Serve metadata JSON
   - Query dependency graph
   - Search functionality

2. **Visualization Dashboard** (`dashboard/`)
   - Interactive dependency graph (D3.js/Cytoscape.js)
   - Project metrics dashboard
   - Connector usage charts
   - Table lineage diagrams

3. **Report Generator** (`output/report_generator.py`)
   - PDF reports with charts
   - Excel exports
   - Markdown documentation

## 🔧 Extending the System

### Adding New Connector Patterns

Edit `config/connector_patterns.yaml`:

```yaml
connectors:
  your_new_db:
    keywords:
      - "import your_db"
      - "your_db.connect"
    connection_patterns:
      - "your_db\\.connect\\("
    type: "database"
```

### Custom File Type Detection

Add to `file_types` section in config:

```yaml
file_types:
  your_type:
    extensions: [".custom"]
    keywords: ["# CUSTOM_MARKER"]
    description: "Custom file type"
```

### Adding Custom Analyzers

Create new analyzer in `analyzers/` directory:

```python
from scanners.metadata_scanner import MetadataScanner

class MyCustomAnalyzer:
    def __init__(self, metadata: Dict):
        self.metadata = metadata
    
    def analyze(self) -> Dict:
        # Your custom analysis logic
        return results
```

## 📈 Sample KPIs for Consultants

Based on the current implementation, you can calculate:

### Code Quality KPIs
- **LOC per file** (average, median, outliers)
- **File complexity** (number of imports, connectors)
- **Code reuse ratio** (shared imports vs unique)

### Architecture KPIs
- **Connector diversity** (# of different systems)
- **Coupling metric** (files per connector)
- **SQL complexity** (# of tables joined per query)

### Data Flow KPIs
- **Table usage frequency** (most referenced tables)
- **Orphan tables** (tables never used)
- **Source-to-sink paths** (# of hops in pipeline)

### Technical Debt KPIs
- **Duplicate code %** (to be added in Phase 2)
- **Circular dependencies** (to be added in Phase 2)
- **Dead code files** (files never imported)

## 🎓 Advanced Use Cases

### 1. Migration Assessment
Use connector summary to plan cloud migration:
```python
# Count on-premise vs cloud connectors
metadata = json.load('report.json')
on_prem = [c for c in metadata['connector_summary'] 
           if c in ['postgresql', 'mysql']]
cloud = [c for c in metadata['connector_summary'] 
         if c in ['snowflake', 'bigquery']]
```

### 2. Cost Optimization
Identify expensive Spark jobs by LOC and connector usage.

### 3. Documentation Generation
Auto-generate data dictionaries from SQL objects.

### 4. Compliance Auditing
Track which files access PII tables for GDPR compliance.

## 🐛 Known Limitations

1. **SQL Parsing:** Complex SQL (CTEs, nested queries) may not fully parse
2. **Dynamic Code:** Runtime imports/connections not detected
3. **Databricks:** Limited to file-level detection (not cell-level)
4. **Cross-Repository:** Can't track dependencies across multiple repos

## 📝 Next Implementation Priority

**Recommended Order:**

1. ✅ **Phase 1: Metadata Scanning** (COMPLETE)
2. 🔄 **Phase 2a: Import Dependency Graph** (NEXT - High Value)
3. 🔄 **Phase 2b: Table Lineage** (NEXT - High Value)
4. 🔄 **Phase 2c: Similarity Detection** (Medium Priority)
5. 🔜 **Phase 3a: Basic API** (For integration)
6. 🔜 **Phase 3b: Simple Dashboard** (For visualization)
7. 🔜 **Phase 3c: Advanced Analytics** (ML-based insights)

## 💡 Tips for Success

1. **Start Small:** Run on small projects first to validate
2. **Iterative Refinement:** Adjust connector patterns based on your stack
3. **Version Control:** Track changes to patterns config
4. **Performance:** For large projects (1000+ files), consider parallel processing
5. **Integration:** Export JSON to your existing tools (Confluence, Jira, etc.)

---

## 🤝 Contributing

To extend this tool:

1. Add new connector patterns in `config/`
2. Create custom analyzers in `analyzers/`
3. Enhance output formats in `output/`
4. Add tests (recommended: pytest)

## 📧 Support

For questions or issues, refer to the code comments and docstrings in each module.
