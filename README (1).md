# HVALF Elected Offices Dashboard

Interactive dashboard for the Huron Valley Area Labor Federation Committee on Political Education (CoPE).

## Quick Start

1. **Install Python** (if you don't have it): https://www.python.org/downloads/

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Put your Excel file in the same folder** as `hvalf_dashboard.py`
   - The file should be named: `HVALF_Elected_Offices_Database_v2.xlsx`
   - Or update the `DATA_FILE` variable at the top of `hvalf_dashboard.py`

4. **Run the dashboard:**
   ```bash
   streamlit run hvalf_dashboard.py
   ```

5. **Open in browser:** It will automatically open, or go to http://localhost:8501

## Features

- **Overview Dashboard**: Regional stats, party control charts, county comparisons
- **County Details**: Drill into each county's offices with filtering
- **State Legislature**: Senate and House districts in HVALF region
- **Party Infrastructure**: Precinct delegates, county party officers
- **Search**: Find any official, position, or jurisdiction across all data

## Updating the Data

Just edit your Excel file! The dashboard reads directly from it.

- Add new officials
- Update TBD entries
- Add notes
- Refresh the browser to see changes

## For the CoPE Meeting

1. Run the dashboard on your laptop
2. Connect to projector/screen share
3. Use the sidebar to navigate between views
4. Use Search to quickly find specific info

## Customization

Edit the top of `hvalf_dashboard.py` to change:
- `DATA_FILE`: Path to your Excel file
- Colors, styling, etc.

## Troubleshooting

**"Data file not found"**: Make sure the Excel file is in the same folder, or update `DATA_FILE` path.

**Charts not showing**: Make sure you installed plotly (`pip install plotly`)

**Slow loading**: First load caches the data. Subsequent loads are fast.
