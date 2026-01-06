"""
HVALF Elected Offices Dashboard
================================
A Streamlit dashboard for the Huron Valley Area Labor Federation
Committee on Political Education (CoPE)

USAGE:
1. Install requirements: pip install streamlit pandas openpyxl plotly
2. Run: streamlit run hvalf_dashboard.py
3. Make sure your Excel file is in the same directory (or update DATA_FILE path)

To update data: Just edit the Excel file and refresh the dashboard!
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ============================================================
# CONFIGURATION - Update this path to your Excel file location
# ============================================================
DATA_FILE = "HVALF_Elected_Offices_Database_v2.xlsx"

# Page config
st.set_page_config(
    page_title="HVALF Elected Offices Database",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1e3a5f;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-top: 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    .dem-badge {
        background-color: #2563eb;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    .rep-badge {
        background-color: #dc2626;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    .nonpartisan-badge {
        background-color: #7c3aed;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    .tbd-row {
        background-color: #fef3c7 !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2.5rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data(file_path):
    """Load all sheets from the Excel file."""
    xlsx = pd.ExcelFile(file_path)
    sheets = {}
    for sheet_name in xlsx.sheet_names:
        df = pd.read_excel(xlsx, sheet_name=sheet_name)
        # Clean up: remove completely empty rows
        df = df.dropna(how='all')
        sheets[sheet_name] = df
    return sheets


def get_party_color(party):
    """Return color based on party affiliation."""
    if pd.isna(party):
        return "#gray"
    party_str = str(party).lower()
    if 'democrat' in party_str:
        return "#2563eb"
    elif 'republican' in party_str:
        return "#dc2626"
    elif 'nonpartisan' in party_str:
        return "#7c3aed"
    return "#6b7280"


def get_party_abbrev(party):
    """Return party abbreviation."""
    if pd.isna(party):
        return ""
    party_str = str(party).lower()
    if 'democrat' in party_str:
        return "D"
    elif 'republican' in party_str:
        return "R"
    elif 'nonpartisan' in party_str:
        return "NP"
    return ""


def count_by_party(df):
    """Count officeholders by party, excluding TBD and section headers."""
    # Filter to actual position rows (not headers)
    positions = df[df['Position'].notna() & ~df['Position'].str.isupper().fillna(False)]
    
    # Filter out TBD entries for party counting
    filled = positions[positions['Current Officeholder'].notna() & 
                       (positions['Current Officeholder'] != 'TBD') &
                       ~positions['Current Officeholder'].str.contains('Multiple|See county', case=False, na=False)]
    
    counts = {'Democratic': 0, 'Republican': 0, 'Nonpartisan': 0, 'TBD': 0}
    
    for _, row in positions.iterrows():
        holder = str(row.get('Current Officeholder', ''))
        party = str(row.get('Party', ''))
        
        if holder == 'TBD' or holder == 'nan' or 'Multiple' in holder or 'See county' in holder:
            counts['TBD'] += 1
        elif 'democrat' in party.lower():
            counts['Democratic'] += 1
        elif 'republican' in party.lower():
            counts['Republican'] += 1
        elif 'nonpartisan' in party.lower():
            counts['Nonpartisan'] += 1
    
    return counts


def style_dataframe(df):
    """Apply styling to dataframe for display."""
    def highlight_tbd(row):
        if str(row.get('Current Officeholder', '')) == 'TBD':
            return ['background-color: #fef3c7'] * len(row)
        return [''] * len(row)
    
    return df.style.apply(highlight_tbd, axis=1)


# ============================================================
# MAIN APP
# ============================================================

def main():
    # Check if data file exists
    if not Path(DATA_FILE).exists():
        st.error(f"❌ Data file not found: {DATA_FILE}")
        st.info("Please update the DATA_FILE variable at the top of this script to point to your Excel file.")
        st.stop()
    
    # Load data
    try:
        sheets = load_data(DATA_FILE)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()
    
    # Header
    st.markdown('<p class="main-header">🗳️ HVALF Elected Offices Database</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Huron Valley Area Labor Federation • Committee on Political Education</p>', unsafe_allow_html=True)
    st.markdown(f"*Jackson, Hillsdale, Washtenaw, and Livingston Counties* — Last updated: January 2026")
    
    st.divider()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    page = st.sidebar.radio(
        "Select View:",
        ["📊 Overview Dashboard", "🏛️ County Details", "🏠 State Legislature", 
         "🎪 Party Infrastructure", "🔍 Search All Records"]
    )
    
    # ============================================================
    # OVERVIEW DASHBOARD
    # ============================================================
    if page == "📊 Overview Dashboard":
        st.header("Regional Overview")
        
        # Aggregate stats across all county sheets
        county_sheets = ['Washtenaw County', 'Jackson County', 'Livingston County', 'Hillsdale County']
        
        total_dem = 0
        total_rep = 0
        total_np = 0
        total_tbd = 0
        
        county_data = []
        
        for county in county_sheets:
            if county in sheets:
                counts = count_by_party(sheets[county])
                total_dem += counts['Democratic']
                total_rep += counts['Republican']
                total_np += counts['Nonpartisan']
                total_tbd += counts['TBD']
                county_data.append({
                    'County': county.replace(' County', ''),
                    'Democratic': counts['Democratic'],
                    'Republican': counts['Republican'],
                    'Nonpartisan': counts['Nonpartisan'],
                    'TBD/Vacant': counts['TBD']
                })
        
        # Top metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Democrats", total_dem, help="Filled Democratic positions")
        with col2:
            st.metric("Republicans", total_rep, help="Filled Republican positions")
        with col3:
            st.metric("Nonpartisan", total_np, help="Nonpartisan positions (judges, school boards, etc)")
        with col4:
            st.metric("TBD / Vacant", total_tbd, help="Positions needing verification or currently vacant", delta_color="inverse")
        
        st.divider()
        
        # County comparison chart
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Party Control by County")
            county_df = pd.DataFrame(county_data)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Democratic', x=county_df['County'], y=county_df['Democratic'], marker_color='#2563eb'))
            fig.add_trace(go.Bar(name='Republican', x=county_df['County'], y=county_df['Republican'], marker_color='#dc2626'))
            fig.add_trace(go.Bar(name='Nonpartisan', x=county_df['County'], y=county_df['Nonpartisan'], marker_color='#7c3aed'))
            fig.add_trace(go.Bar(name='TBD', x=county_df['County'], y=county_df['TBD/Vacant'], marker_color='#fbbf24'))
            
            fig.update_layout(barmode='group', height=400, showlegend=True, 
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Regional Totals")
            pie_data = pd.DataFrame({
                'Party': ['Democratic', 'Republican', 'Nonpartisan', 'TBD'],
                'Count': [total_dem, total_rep, total_np, total_tbd]
            })
            
            fig = px.pie(pie_data, values='Count', names='Party', 
                        color='Party',
                        color_discrete_map={
                            'Democratic': '#2563eb',
                            'Republican': '#dc2626', 
                            'Nonpartisan': '#7c3aed',
                            'TBD': '#fbbf24'
                        })
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # County summary table
        st.subheader("County Summary")
        st.dataframe(county_df, use_container_width=True, hide_index=True)
        
        # Key dates callout
        st.info("""
        **📅 Key 2026 Dates:**
        - **August Primary:** Precinct Delegate elections (2-year terms)
        - **November General:** County commissioners, executives, state legislature
        - Check with County Clerks and Secretary of State for specific filing deadlines
        """)
    
    # ============================================================
    # COUNTY DETAILS
    # ============================================================
    elif page == "🏛️ County Details":
        st.header("County Office Details")
        
        county_sheets = ['Washtenaw County', 'Jackson County', 'Livingston County', 'Hillsdale County']
        available_counties = [c for c in county_sheets if c in sheets]
        
        selected_county = st.selectbox("Select County:", available_counties)
        
        if selected_county:
            df = sheets[selected_county].copy()
            
            # Show party breakdown for this county
            counts = count_by_party(df)
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Democratic", counts['Democratic'])
            col2.metric("Republican", counts['Republican'])
            col3.metric("Nonpartisan", counts['Nonpartisan'])
            col4.metric("TBD / Needs Update", counts['TBD'])
            
            st.divider()
            
            # Filter options
            col1, col2 = st.columns(2)
            
            with col1:
                # Get unique position categories (uppercase headers)
                all_positions = df['Position'].dropna().unique()
                categories = [p for p in all_positions if isinstance(p, str) and p.isupper()]
                categories.insert(0, "All Categories")
                
                selected_category = st.selectbox("Filter by Category:", categories)
            
            with col2:
                show_tbd_only = st.checkbox("Show only TBD/Vacant positions", value=False)
            
            # Filter the dataframe
            display_df = df.copy()
            
            # If a category is selected, filter to that section
            if selected_category != "All Categories":
                # Find the start and end of the section
                start_idx = None
                end_idx = None
                for i, pos in enumerate(display_df['Position'].values):
                    if pos == selected_category:
                        start_idx = i
                    elif start_idx is not None and isinstance(pos, str) and pos.isupper():
                        end_idx = i
                        break
                
                if start_idx is not None:
                    if end_idx is None:
                        end_idx = len(display_df)
                    display_df = display_df.iloc[start_idx:end_idx]
            
            # Filter for TBD only
            if show_tbd_only:
                display_df = display_df[display_df['Current Officeholder'] == 'TBD']
            
            # Remove section headers for display
            display_df = display_df[~display_df['Position'].fillna('').str.isupper()]
            display_df = display_df[display_df['Position'].notna()]
            
            # Display the data
            st.subheader(f"Positions in {selected_county}")
            st.caption(f"Showing {len(display_df)} positions")
            
            # Format for display
            display_cols = ['Position', 'District/Jurisdiction', 'Current Officeholder', 'Party', 'Term Expires', 'Notes']
            display_cols = [c for c in display_cols if c in display_df.columns]
            
            st.dataframe(
                display_df[display_cols],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Position": st.column_config.TextColumn("Position", width="medium"),
                    "Current Officeholder": st.column_config.TextColumn("Officeholder", width="medium"),
                    "Party": st.column_config.TextColumn("Party", width="small"),
                    "Term Expires": st.column_config.TextColumn("Term", width="small"),
                }
            )
    
    # ============================================================
    # STATE LEGISLATURE
    # ============================================================
    elif page == "🏠 State Legislature":
        st.header("State Legislature - HVALF Region")
        
        if 'State Legislature' in sheets:
            df = sheets['State Legislature'].copy()
            
            # Separate Senate and House
            senate_start = None
            house_start = None
            
            for i, pos in enumerate(df['Position'].values):
                if pos == 'STATE SENATE':
                    senate_start = i
                elif pos == 'STATE HOUSE':
                    house_start = i
            
            # Display Senate
            st.subheader("🏛️ Michigan State Senate")
            if senate_start is not None and house_start is not None:
                senate_df = df.iloc[senate_start+1:house_start]
                senate_df = senate_df[senate_df['Position'].notna() & ~senate_df['Position'].str.isupper().fillna(False)]
                
                for _, row in senate_df.iterrows():
                    party = row.get('Party', '')
                    color = get_party_color(party)
                    name = row.get('Current Officeholder', 'TBD')
                    district = row.get('District/Jurisdiction', '')
                    area = row.get('Notes', '')
                    term = row.get('Term Expires', '')
                    
                    with st.container():
                        col1, col2, col3 = st.columns([1, 2, 2])
                        with col1:
                            st.markdown(f"**{district}**")
                        with col2:
                            badge_class = 'dem-badge' if 'Democrat' in str(party) else 'rep-badge'
                            if name == 'TBD':
                                st.markdown(f"⚠️ *TBD*")
                            else:
                                st.markdown(f"**{name}** ({get_party_abbrev(party)})")
                        with col3:
                            st.caption(f"{area} | Term: {term}")
            
            st.divider()
            
            # Display House
            st.subheader("🏠 Michigan State House")
            if house_start is not None:
                house_df = df.iloc[house_start+1:]
                house_df = house_df[house_df['Position'].notna() & ~house_df['Position'].str.isupper().fillna(False)]
                
                # Create a grid layout
                cols = st.columns(3)
                for i, (_, row) in enumerate(house_df.iterrows()):
                    party = row.get('Party', '')
                    name = row.get('Current Officeholder', 'TBD')
                    district = row.get('District/Jurisdiction', '')
                    area = row.get('Notes', '')
                    
                    with cols[i % 3]:
                        color = get_party_color(party)
                        st.markdown(f"""
                        <div style="padding: 10px; border-left: 4px solid {color}; background: #f8f9fa; margin-bottom: 10px; border-radius: 4px;">
                            <strong>{district}</strong><br>
                            {'⚠️ <em>TBD</em>' if name == 'TBD' else f'<strong>{name}</strong> ({get_party_abbrev(party)})'}<br>
                            <small style="color: #666;">{area}</small>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.warning("State Legislature sheet not found in the Excel file.")
    
    # ============================================================
    # PARTY INFRASTRUCTURE
    # ============================================================
    elif page == "🎪 Party Infrastructure":
        st.header("Party Infrastructure")
        st.caption("Precinct delegates, county party officers, and state convention delegates")
        
        if 'Party Infrastructure' in sheets:
            df = sheets['Party Infrastructure'].copy()
            
            # Get sections
            sections = df[df['Position'].fillna('').str.isupper()]['Position'].tolist()
            
            selected_section = st.selectbox("Select Section:", ["All Sections"] + sections)
            
            if selected_section == "All Sections":
                display_df = df[~df['Position'].fillna('').str.isupper()]
            else:
                # Find section boundaries
                start_idx = None
                end_idx = None
                for i, pos in enumerate(df['Position'].values):
                    if pos == selected_section:
                        start_idx = i
                    elif start_idx is not None and isinstance(pos, str) and pos.isupper():
                        end_idx = i
                        break
                
                if start_idx is not None:
                    if end_idx is None:
                        end_idx = len(df)
                    display_df = df.iloc[start_idx+1:end_idx]
                    display_df = display_df[display_df['Position'].notna()]
            
            display_df = display_df[display_df['Position'].notna()]
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.warning("Party Infrastructure sheet not found.")
    
    # ============================================================
    # SEARCH
    # ============================================================
    elif page == "🔍 Search All Records":
        st.header("Search All Records")
        
        search_term = st.text_input("🔎 Search for names, positions, jurisdictions...", placeholder="e.g., 'Ann Arbor' or 'Commissioner' or 'Smith'")
        
        if search_term:
            results = []
            
            for sheet_name, df in sheets.items():
                if sheet_name == 'Summary':
                    continue
                    
                # Search across all text columns
                for col in df.columns:
                    mask = df[col].astype(str).str.contains(search_term, case=False, na=False)
                    matches = df[mask].copy()
                    if len(matches) > 0:
                        matches['_source'] = sheet_name
                        results.append(matches)
            
            if results:
                combined = pd.concat(results).drop_duplicates()
                st.success(f"Found {len(combined)} matching records")
                
                # Group by source sheet
                for source in combined['_source'].unique():
                    st.subheader(f"📁 {source}")
                    source_df = combined[combined['_source'] == source].drop(columns=['_source'])
                    st.dataframe(source_df, use_container_width=True, hide_index=True)
            else:
                st.warning("No matching records found.")
        else:
            st.info("Enter a search term to find records across all sheets.")
    
    # Footer
    st.divider()
    st.caption("HVALF Elected Offices Database • Prepared for CoPE Review • Data maintained in Excel file")
    st.caption(f"📄 Data source: {DATA_FILE}")


if __name__ == "__main__":
    main()
