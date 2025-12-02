# Quick Start Guide

## ⚡ 5-Minute Setup

### Prerequisites
- Python 3.8+
- pip

### Installation

```bash
# 1. Navigate to the project
cd data_engineering_analyzer

# 2. Install dependencies
pip install -r requirements.txt

# 3. Test with sample project
python main.py \
  --project-path ../sample_de_project \
  --output test_report.json \
  --print-summary
```

## 🎯 Common Use Cases

### Use Case 1: Quick Project Assessment
**Scenario:** You just inherited a data engineering project and need to understand it quickly.

```bash
python main.py \
  --project-path /path/to/de/project \
  --output assessment.json \
  --print-summary
```

**What you get:**
- Total files and LOC
- All connectors used
- Tables referenced
- File type breakdown

### Use Case 2: Migration Planning
**Scenario:** Planning a cloud migration and need to know what systems are in use.

```bash
python main.py \
  --project-path /path/to/project \
  --output migration_analysis.json

# Then parse the JSON
python -c "
import json
with open('migration_analysis.json') as f:
    data = json.load(f)
    print('Connectors found:')
    for conn, info in data['connector_summary'].items():
        print(f'  - {conn}: {info[\"total_files\"]} files')
"
```

### Use Case 3: Documentation Generation
**Scenario:** Need to document all tables used in the project.

```bash
python main.py \
  --project-path /path/to/project \
  --output docs.json

# Extract table list
python -c "
import json
with open('docs.json') as f:
    data = json.load(f)
    tables = data['sql_objects_summary']['tables']
    print('Tables Referenced:')
    for table in sorted(tables):
        print(f'  - {table}')
"
```

### Use Case 4: Tech Stack Inventory
**Scenario:** Create an inventory of all technologies used.

```bash
# Run analysis
python main.py --project-path /path/to/project --output inventory.json

# View connector summary
python -c "
import json
with open('inventory.json') as f:
    data = json.load(f)
    connectors = data['connector_summary']
    
    print('Technology Stack:')
    print('\nDatabases:')
    for conn, info in connectors.items():
        if info['type'] == 'database':
            print(f'  - {conn.capitalize()}')
    
    print('\nCloud Storage:')
    for conn, info in connectors.items():
        if info['type'] == 'storage':
            print(f'  - {conn.upper()}')
"
```

## 🔧 Configuration

### Custom Connector Patterns

Create `my_patterns.yaml`:

```yaml
connectors:
  oracle:
    keywords:
      - "import cx_Oracle"
      - "cx_Oracle.connect"
    connection_patterns:
      - "cx_Oracle\\.connect\\("
    type: "database"
    
  teradata:
    keywords:
      - "import teradatasql"
    connection_patterns:
      - "teradatasql\\.connect\\("
    type: "database"
```

Run with custom config:
```bash
python main.py \
  --project-path /path/to/project \
  --config my_patterns.yaml \
  --output report.json
```

## 📊 Understanding the Output

### JSON Structure Overview

```json
{
  "scan_metadata": {...},          // When and what was scanned
  "project_statistics": {...},     // High-level metrics
  "connector_summary": {...},      // All connectors found
  "import_summary": {...},         // Python imports
  "sql_objects_summary": {...},    // Tables and views
  "files": [...]                   // Per-file detailed analysis
}
```

### Key Metrics to Look At

1. **total_files** - Project size
2. **total_loc** - Total lines of code
3. **connector_summary** - What systems you're connected to
4. **files_with_spark** - How much Spark usage
5. **files_with_sql** - How much SQL usage

## 🚨 Troubleshooting

### Issue: "Project path does not exist"
**Solution:** Check the path is correct and absolute
```bash
# Use absolute path
python main.py --project-path /full/path/to/project --output report.json

# Or get absolute path first
cd /path/to/project
pwd  # Copy this path
python /path/to/analyzer/main.py --project-path $(pwd) --output report.json
```

### Issue: No connectors detected
**Possible causes:**
1. Connector patterns need updating
2. Code uses uncommon connection methods
3. Connection code is in config files (not currently parsed)

**Solution:** Add custom patterns or check existing patterns

### Issue: Out of memory on large projects
**Solution:** Process in batches (future enhancement) or increase system memory

### Issue: Unicode decode errors
**Solution:** The tool handles this automatically with fallback encodings

## 💡 Pro Tips

1. **Run regularly**: Track changes over time
2. **Version control output**: Compare reports across versions
3. **Combine with git**: 
   ```bash
   python main.py --project-path . --output report_$(git rev-parse --short HEAD).json
   ```
4. **CI/CD Integration**: Run in pipeline to track metrics
5. **Custom scripts**: Parse JSON output for specific insights

## 📈 Next Steps After First Scan

1. **Review connector summary** - Understand your dependencies
2. **Check LOC distribution** - Find complex files
3. **Analyze SQL objects** - Understand data flow
4. **Look for patterns** - Spot common imports/connections
5. **Plan Phase 2** - Dependency graph and lineage

## 🎓 Learning Path

1. **Week 1**: Use tool on 2-3 projects, understand output
2. **Week 2**: Customize connector patterns for your stack
3. **Week 3**: Build Phase 2 (dependency graph)
4. **Week 4**: Integrate with your existing tools
5. **Month 2+**: Build custom analyzers and visualizations

## 📞 Getting Help

- Check `IMPLEMENTATION_GUIDE.md` for detailed docs
- Review `ARCHITECTURE_DESIGN.md` for system design
- Look at code comments in Python files
- Test with `sample_de_project` first

## 🚀 Advanced Usage

### Batch Processing
```bash
# Analyze multiple projects
for project in /data/projects/*; do
  python main.py \
    --project-path "$project" \
    --output "reports/$(basename $project).json"
done
```

### Differential Analysis
```bash
# Before changes
python main.py --project-path . --output before.json

# After changes
python main.py --project-path . --output after.json

# Compare (requires jq)
diff <(jq -S . before.json) <(jq -S . after.json)
```

### Integration with Tools
```bash
# Export to CSV (requires jq)
jq -r '.connector_summary | to_entries[] | [.key, .value.total_files, .value.type] | @csv' report.json > connectors.csv

# Upload to S3
aws s3 cp report.json s3://my-bucket/analysis/$(date +%Y%m%d).json

# Send to Slack
curl -X POST -H 'Content-type: application/json' \
  --data "$(cat report.json)" \
  https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

---

## ✅ Checklist for First Use

- [ ] Install dependencies
- [ ] Test with sample project
- [ ] Run on your actual project
- [ ] Review JSON output
- [ ] Check connector summary
- [ ] Verify SQL objects found
- [ ] Customize patterns if needed
- [ ] Save report for future comparison
- [ ] Share insights with team
- [ ] Plan next phase implementation

**Happy Analyzing! 🎉**
