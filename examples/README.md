# Examples (planned)

Stub listing planned example categories. Full images and walkthroughs coming in v2.

| Category | Description | Status |
|----------|-------------|--------|
| **web** | News homepage, article layout, navigation chrome | planned |
| **dashboard** | Analytics panels, charts-as-screenshots, KPI cards | planned |
| **terminal** | CLI output, log panes, monospace UI | planned |
| **invoice** | Scanned/form PDFs, tables, line items | planned |

## Usage (when available)

```bash
samson-vision examples/web/homepage.png --md
python3 -c "from samson_vision import generate_svp; print(generate_svp('examples/web/homepage.png'))"
```
