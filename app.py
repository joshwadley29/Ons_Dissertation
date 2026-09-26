import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="ONS Data Visualiser & Explorer", layout="wide")

st.title("📊 ONS Population Data Visualiser & Explorer")

# --- Sidebar Inputs ---
st.sidebar.header("1. Data Input")
uploaded_file = st.sidebar.file_uploader("Upload CSV Data", type=["csv"])
generate_btn = st.sidebar.button("Generate Synthetic Dataset")

if 'df' not in st.session_state:
    st.session_state.df = None

# --- Synthetic Data Generation (Spanning 2023-2025) ---
if generate_btn:
    np.random.seed(42)
    date_range = pd.date_range(start="2023-01-01", end="2025-12-31", freq="MS").strftime("%Y-%m-%d")
    n_rows = 200
    st.session_state.df = pd.DataFrame({
        'GSS_CODE': np.random.choice(['W06000015', 'W06000016', 'W06000017', 'E08000001'], n_rows),
        'Area_Name': np.random.choice(['Cardiff', 'Swansea', 'Newport', 'Rhondda Cynon Taf'], n_rows),
        'Period_Date': np.random.choice(date_range, n_rows),
        'Population_Count': np.random.randint(15000, 85000, size=n_rows)
    })
    st.sidebar.success("Synthetic 2023–2025 dataset loaded!")

elif uploaded_file is not None:
    st.session_state.df = pd.read_csv(uploaded_file)

# --- Main Dashboard Logic ---
if st.session_state.df is not None:
    df = st.session_state.df.copy()
    df['Period_Date_dt'] = pd.to_datetime(df['Period_Date'], errors='coerce')
    
    st.sidebar.divider()
    st.sidebar.header("2. Variable Filters")
    
    all_areas = sorted(df['Area_Name'].dropna().unique().tolist())
    selected_areas = st.sidebar.multiselect("Filter by Area Name:", options=all_areas, default=all_areas)
    
    min_date = df['Period_Date_dt'].min().date() if not df['Period_Date_dt'].isnull().all() else pd.to_datetime("2023-01-01").date()
    max_date = df['Period_Date_dt'].max().date() if not df['Period_Date_dt'].isnull().all() else pd.to_datetime("2025-12-31").date()
    
    selected_date_range = st.sidebar.date_input("Filter by Date Range:", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    
    filtered_df = df[df['Area_Name'].isin(selected_areas)]
    if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
        start_d, end_d = selected_date_range
        filtered_df = filtered_df[(filtered_df['Period_Date_dt'].dt.date >= start_d) & (filtered_df['Period_Date_dt'].dt.date <= end_d)]

    m1, m2, m3 = st.columns(3)
    m1.metric("Filtered Record Count", f"{len(filtered_df):,}")
    m2.metric("Total Population", f"{int(filtered_df['Population_Count'].sum()):,}")
    m3.metric("Selected Areas", f"{len(selected_areas)} of {len(all_areas)}")

    st.divider()
    st.subheader("📈 Visual Data Breakdown")
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("### Total Population by Area")
        if not filtered_df.empty:
            area_summary = filtered_df.groupby('Area_Name')['Population_Count'].sum()
            st.bar_chart(area_summary)
        else:
            st.warning("No data available for the selected filters.")

    with col_chart2:
        st.markdown("### Population Trend Over Time")
        if not filtered_df.empty:
            time_summary = filtered_df.groupby('Period_Date')['Population_Count'].sum()
            st.line_chart(time_summary)
        else:
            st.warning("No data available for the selected filters.")

    st.divider()
    st.subheader("📋 Filtered Dataset Table")
    st.dataframe(filtered_df.drop(columns=['Period_Date_dt']), use_container_width=True)
else:
    st.info("Please upload a file or click 'Generate Synthetic Dataset' in the sidebar to begin.")