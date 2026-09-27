import streamlit as st
import pandas as pd
import numpy as np

# Title and page configuration
st.set_page_config(page_title="ONS Data Visualiser & Explorer", layout="wide")

st.title("📊 ONS Population Data Visualiser & Explorer")

# --- Sidebar Inputs & Data Handling ---
st.sidebar.header("1. Data Input")
uploaded_file = st.sidebar.file_uploader("Upload CSV Data", type=["csv"], key="csv_uploader")
generate_btn = st.sidebar.button("Generate Synthetic Dataset")

if 'df' not in st.session_state:
    st.session_state.df = None

# --- Handle File Upload with Dynamic Column Mapping ---
if uploaded_file is not None:
    raw_df = pd.read_csv(uploaded_file)
    st.sidebar.success("Dataset uploaded successfully!")
    st.sidebar.subheader("Map Your Columns")
    
    columns_list = raw_df.columns.tolist()
    
    # Let the user map their columns
    date_col = st.sidebar.selectbox("Select Date / Period Column", columns_list, key="map_date")
    area_col = st.sidebar.selectbox("Select Region / Area Column", columns_list, key="map_area")
    value_col = st.sidebar.selectbox("Select Numeric Value Column", columns_list, key="map_value")
    
    # Standardize names dynamically
    df = raw_df.copy()
    df['Period_Date'] = df[date_col]
    df['Area_Name'] = df[area_col]
    df['Population_Count'] = pd.to_numeric(df[value_col], errors='coerce')
    
    st.session_state.df = df

# --- Handle Synthetic Data Generation (Fallback) ---
elif generate_btn:
    np.random.seed(42)
    
    # Sample Welsh Local Authorities and their official GSS codes
    la_data = [
        ('W06000015', 'Cardiff'),
        ('W06000016', 'Swansea'),
        ('W06000017', 'Newport'),
        ('W06000018', 'Caerphilly'),
        ('W06000022', 'Rhondda Cynon Taf')
    ]
    
    n_rows = 300
    
    # Randomly sample areas, ages (0 to 90), and sex categories
    selected_las = np.random.choice(len(la_data), n_rows)
    codes = [la_data[i][0] for i in selected_las]
    names = [la_data[i][1] for i in selected_las]
    
    df = pd.DataFrame({
        'Local Authority Code': codes,
        'Local Authority Name': names,
        'Age': np.random.randint(0, 91, size=n_rows),
        'Sex': np.random.choice(['Persons', 'Males', 'Females'], size=n_rows),
        'Count': np.random.randint(500, 5000, size=n_rows)
    })
    
    st.sidebar.success("Synthetic Demographic dataset loaded!")
    st.session_state.df = df

# --- Main Dashboard Logic ---
if st.session_state.df is not None:
    df = st.session_state.df.copy()
    
    st.sidebar.divider()
    st.sidebar.header("2. Variable Filters")
    
    # Check what columns are available for filtering
    all_areas = sorted(df['Local Authority Name'].dropna().unique().tolist())
    selected_areas = st.sidebar.multiselect("Filter by Area Name:", options=all_areas, default=all_areas)
    
    # Optional Age filter if the column exists
    if 'Age' in df.columns:
        min_age, max_age = int(df['Age'].min()), int(df['Age'].max())
        selected_age_range = st.sidebar.slider("Filter by Age Range:", min_age, max_age, (min_age, max_age))
    
    # Optional Sex filter if the column exists
    if 'Sex' in df.columns:
        all_sexes = sorted(df['Sex'].dropna().unique().tolist())
        selected_sexes = st.sidebar.multiselect("Filter by Sex:", options=all_sexes, default=all_sexes)

    # --- Apply Filters ---
    filtered_df = df[df['Local Authority Name'].isin(selected_areas)]
    
    if 'Age' in df.columns:
        filtered_df = filtered_df[(filtered_df['Age'] >= selected_age_range[0]) & (filtered_df['Age'] <= selected_age_range[1])]
        
    if 'Sex' in df.columns:
        filtered_df = filtered_df[filtered_df['Sex'].isin(selected_sexes)]

    # --- Metrics Bar ---
    m1, m2, m3 = st.columns(3)
    m1.metric("Filtered Record Count", f"{len(filtered_df):,}")
    m2.metric("Total Count", f"{filtered_df['Count'].sum():,}")
    m3.metric("Selected Areas", f"{len(selected_areas)} / {len(all_areas)}")

    st.divider()
    st.subheader("📊 Visual Data Breakdown")
    
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.markdown("### Count by Area Name")
        if not filtered_df.empty:
            area_summary = filtered_df.groupby('Local Authority Name')['Count'].sum()
            st.bar_chart(area_summary)
        else:
            st.warning("No data matches the current filters.")
            
    with col_chart2:
        st.markdown("### Breakdown by Age")
        if not filtered_df.empty and 'Age' in filtered_df.columns:
            age_summary = filtered_df.groupby('Age')['Count'].sum()
            st.line_chart(age_summary)
        else:
            st.info("Age breakdown unavailable.")

    st.divider()
    st.subheader("📋 Filtered Dataset Table")
    st.dataframe(filtered_df, use_container_width=True)

else:
    st.info("Please upload a file or click 'Generate Synthetic Dataset' in the sidebar to begin.")