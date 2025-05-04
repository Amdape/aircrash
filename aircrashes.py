import streamlit as st
import altair as alt
import pandas as pd
import numpy as np

def load_data():
    df = pd.read_csv("./aircrashesFullData.csv")

    # clean column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_") \
        .str.replace("(", "", regrex=False).str.replace(")", "", regrex=False) \
        .str.replace("/", "_")
    
    # replace blank strings with NaN for object columns
    df[df.select_dtypes(include='object').columns] = df.select_dtypes(include='object').replace

    # now fill essential missing values
    df['country_region'] = df.get('country_region', pd.Series()).fillna("Unknown")
    df['operator'] = df.get('country_region', pd.Series()).fillna('Unknown')
    df['aircraft_manufacturer'] = df.get('aircraft_manufacturer', pd.Series()).fillna('Unknown')

    # convert numeric columns
    df['year'] = pd.to_numeric(df.get('year', pd.Series()), errors='coerce')
    df['day'] = pd.to_numeric(df.get('day', pd.Series()), errors='coerce')
    df['abroad'] = pd.to_numeric(df.get('abroad', pd.Series()), errors='coerce')
    df['fatalities_air'] = pd.to_numeric(df.get('fatalities_air', pd.Series()), errors='coerce')
    df['ground'] = pd.to_numeric(df.get('ground', pd.Series()), errors='coerce') 
                                                           

    # map month names to numbers
    month_map = {
    'January': 1, 'Feburary': 2, 'March': 3, 'April': 4, 
    'May': 5, 'June': 6, 'July': 7, 'August': 8, 'September': 9, 'October': 10,
    'November': 11, 'December': 12
}
    df["month_num"] = df['month'].map(month_map)

# create a datetime column from year and month_num
    df['month_date'] = pd.to_datetime(
        dict(year=df['year'], month=df['month_num'], day=1),
        errors="coerce"
    )

# add month name for charts
    df['month_name'] = df['month_date'].dt.month_name()

# add decade/period bins
    bins = [1908, 1920, 1932, 1944, 1956, 1968, 1980, 1992, 2004, 2016, 2020, 2024]
    labels = [
        "Early 1910s", "Mid 1920s", "Late 1930s", "Early 1940s",
        "Mid 1950s", "Late 1960s", "Early 1970s", "Late 1980s",
        "Early 2000s", "Mid 2010s", "Early 2020s"
    ]
    df['year_bin'] = pd.cut(df['year'], bins=bins, labels=labels, include_lowest=True)

    # drop exact duplicates
    df.drop_duplicates(inplace=True)
    return df




df = load_data()
# app title
st.title('Air Crash Data Analysis')
st.sidebar.header('Filters')

# --- Filters in the sidebar ---

# create filters
filters = {
    "Year": df["Year"].unique(),
    "Quarter": df["Quarter"].unique(),
    "Month": df["Month"].unique(),

}

# store user selection
selected_filters = {}

#generate multi-select widgets dynamically
for key, options in filters.items():
    selected_filters[key]=st.sidebar.multiselect(key,options)

# lets have the full data
filtered_df = df.copy()
for key, selected_values in selected_filters.items():
    if selected_values:
        filtered_df=filtered_df[filtered_df[key].\
                                isin(selected_values)]
        
#display the data                 
st.dataframe(filtered_df.head())

# calculations
no_of_fatalities = len(filtered_df)
total_year = filtered_df["Year"].sum()
Sum_of_Fatalities = filtered_df["Sum of Fatalities (air)"].sum()
no_of_aircrafts = filtered_df["Aircraft"].nunique()

# streamlit column component
col1, col2, col3, col4, = st.columns(4)
with col1:
    st.metric("Fatalities", no_of_fatalities )

with col2:
    st.metric("Year", total_year)

with col3:
    st.metric("Total Fatalities", Sum_of_Fatalities)

with col4:
    st.metric("Aircraft", no_of_aircrafts)


#charts
st.subheader("Year With Largest Fatalities")
crashes_per_year = filtered_df.groupby("Year")["Total Fatalities"].sum().nlargest(5).reset_index()

st.write(crashes_per_year)

# altair plotting libaray

st.subheader("Top 5 Yearly Fatalities")

# configure the bar chart


chart = alt.Chart(crashes_per_year).mark_bar().encode(
    x=alt.X('Number of Crashes:Q', title="Number of Crashes"),
    y=alt.Y("Aircraft Type:N"),
    color = alt.Color("Aircraft Type", legend = None)
).properties(height = 300)

# display the chart
st.altair_chart(chart, use_container_width= True)





