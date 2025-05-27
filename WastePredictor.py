import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import pgeocode

# Configure Streamlit page Title
st.set_page_config(page_title="Waste Estimation Model", layout="wide")
st.title("Waste Estimation Model")

# Step 1: Create USPS Shipping Rate Table
rate = {
    "weight": [
        0.25, 0.5, 0.75, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17,
        18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37,
        38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57,
        58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 80
    ],
    "Zone 1": [5.25, 6.00, 6.75, 8.35, 9.45, 9.85, 10.70, 11.35, 11.80, 12.25, 12.75, 13.20, 13.95, 14.65, 15.25, 15.90, 16.55, 17.20, 17.85, 18.50, 19.10, 19.50, 19.90, 22.95, 25.00, 26.30, 27.30, 28.35, 29.30, 30.30, 31.05, 31.85, 32.60, 33.45, 34.10, 34.85, 35.60, 36.35, 37.00, 37.75, 38.45, 39.15, 39.80, 40.50, 41.20, 41.80, 42.50, 43.10, 43.75, 44.35, 44.95, 45.55, 46.15, 46.75, 47.35, 47.90, 48.45, 48.95, 49.55, 50.05, 50.55, 51.10, 51.55, 52.05, 52.55, 53.05, 53.45, 53.90, 54.35, 54.75, 55.25, 55.60, 56.05, 98.00],
    "Zone 2": [5.35, 6.10, 6.90, 8.55, 10.05, 10.50, 11.15, 11.85, 12.15, 12.60, 13.00, 13.45, 14.25, 15.10, 15.65, 16.20, 16.65, 17.30, 18.00, 18.70, 19.30, 19.75, 20.05, 24.05, 26.75, 28.35, 29.40, 30.55, 31.70, 32.80, 33.70, 34.55, 35.45, 36.25, 37.10, 37.90, 38.70, 39.50, 40.25, 41.00, 41.75, 42.50, 43.30, 44.00, 44.65, 45.40, 46.10, 46.75, 47.45, 48.15, 48.75, 49.35, 50.00, 50.60, 51.20, 51.75, 52.35, 52.90, 53.45, 54.00, 54.45, 55.05, 55.50, 56.00, 56.45, 56.95, 57.35, 57.85, 58.25, 58.65, 59.05, 59.45, 59.85, 108.75],
    "Zone 3": [5.40, 6.15, 6.95, 8.65, 10.65, 11.05, 11.95, 12.70, 13.00, 13.45, 13.85, 14.20, 15.05, 15.85, 16.30, 16.75, 17.20, 17.85, 18.55, 19.15, 19.80, 20.65, 21.40, 26.00, 29.45, 31.35, 32.70, 34.00, 35.35, 36.70, 37.75, 38.70, 39.70, 40.65, 41.60, 42.55, 43.45, 44.35, 45.20, 46.10, 46.85, 47.75, 48.55, 49.40, 50.15, 50.95, 51.65, 52.45, 53.15, 53.90, 54.55, 55.30, 55.95, 56.55, 57.20, 57.75, 58.40, 59.00, 59.55, 60.10, 60.60, 61.20, 61.65, 62.15, 62.60, 63.05, 63.45, 63.95, 64.30, 64.70, 65.05, 65.45, 65.75, 124.85],
    "Zone 4": [5.50, 6.20, 7.00, 8.85, 11.40, 12.00, 13.00, 13.85, 14.30, 14.95, 15.45, 16.00, 16.95, 17.85, 18.60, 19.05, 19.75, 20.30, 21.25, 22.20, 22.70, 23.10, 23.90, 30.65, 35.55, 38.20, 39.95, 41.80, 43.60, 45.50, 46.80, 48.20, 49.45, 50.70, 52.00, 53.25, 54.40, 55.65, 56.75, 58.00, 59.10, 60.25, 61.40, 62.50, 63.55, 64.60, 65.65, 66.70, 67.70, 68.70, 69.65, 70.60, 71.55, 72.45, 73.35, 74.25, 75.05, 75.95, 76.80, 77.50, 78.35, 79.05, 79.85, 80.55, 81.25, 82.00, 82.60, 83.25, 83.90, 84.45, 85.10, 85.60, 86.20, 151.65],
    "Zone 5": [5.65, 6.30, 7.10, 9.00, 12.30, 13.10, 14.35, 15.25, 16.10, 17.00, 17.85, 18.70, 19.95, 21.15, 22.20, 23.10, 24.30, 25.30, 26.40, 27.50, 28.65, 29.55, 30.75, 37.90, 43.10, 46.20, 48.45, 50.60, 52.75, 55.00, 56.75, 58.50, 60.15, 61.80, 63.45, 65.10, 66.60, 68.25, 69.75, 71.30, 72.80, 74.35, 75.80, 77.35, 78.75, 80.20, 81.60, 83.00, 84.35, 85.70, 87.05, 88.40, 89.65, 90.95, 92.20, 93.40, 94.60, 95.80, 97.00, 98.15, 99.30, 100.40, 101.45, 102.55, 103.60, 104.55, 105.60, 106.60, 107.55, 108.50, 109.45, 110.35, 111.25, 178.20],
    "Zone 6": [5.70, 6.35, 7.15, 9.10, 13.20, 14.40, 16.00, 17.15, 18.40, 19.75, 21.05, 22.35, 24.05, 25.75, 27.35, 28.95, 30.85, 32.15, 33.45, 34.95, 36.50, 37.45, 38.65, 46.80, 52.55, 56.05, 58.75, 61.30, 63.90, 66.55, 68.65, 70.65, 72.70, 74.70, 76.70, 78.60, 80.50, 82.45, 84.25, 86.05, 87.90, 89.70, 91.50, 93.30, 94.95, 96.65, 98.40, 99.95, 101.65, 103.15, 104.80, 106.30, 107.85, 109.40, 110.80, 112.25, 113.65, 115.00, 116.40, 117.75, 119.05, 120.35, 121.60, 122.85, 124.05, 125.20, 126.35, 127.50, 128.65, 129.70, 130.75, 131.75, 132.75, 204.90],
    "Zone 7": [5.75, 6.40, 7.25, 9.25, 14.40, 16.55, 18.25, 19.60, 21.30, 22.95, 24.90, 26.85, 29.15, 31.45, 33.80, 36.45, 39.20, 40.80, 42.40, 44.45, 46.45, 47.30, 48.55, 56.80, 62.55, 66.35, 69.30, 72.20, 75.10, 77.95, 80.35, 82.70, 85.10, 87.30, 89.60, 91.75, 93.95, 96.20, 98.25, 100.35, 102.45, 104.50, 106.50, 108.50, 110.40, 112.35, 114.25, 116.15, 117.90, 119.75, 121.55, 123.25, 124.95, 126.65, 128.25, 129.85, 131.50, 132.95, 134.55, 135.95, 137.45, 138.85, 140.30, 141.60, 142.90, 144.20, 145.45, 146.65, 147.85, 149.00, 150.15, 151.20, 152.25, 230.55],
    "Zone 8": [5.85, 6.55, 7.35, 9.45, 16.65, 19.60, 21.20, 22.75, 24.80, 26.75, 29.00, 31.20, 34.50, 37.85, 40.65, 44.55, 48.00, 50.15, 52.35, 54.95, 57.55, 59.45, 60.65, 68.65, 73.95, 77.85, 81.10, 84.25, 87.45, 90.60, 93.40, 96.05, 98.65, 101.25, 103.80, 106.30, 108.70, 111.20, 113.50, 115.95, 118.25, 120.50, 122.75, 125.00, 127.15, 129.30, 131.35, 133.45, 135.45, 137.45, 139.35, 141.30, 143.15, 144.90, 146.70, 148.45, 150.20, 151.85, 153.45, 155.05, 156.60, 158.05, 159.60, 160.95, 162.40, 163.70, 165.05, 166.30, 167.60, 168.75, 169.85, 170.95, 172.05, 257.25]
   
}

# Create the Data Frame
df_rate = pd.DataFrame(rate)


# Step 2: Get CSV and ZIP input from user
uploaded_file = st.file_uploader("Upload your Sold Orders CSV file", type="csv")
zipcode_from = st.text_input("Enter your origin ZIP code").strip()


# Step 3: Data Processing if Input is Valid
if uploaded_file is None:
    st.info("Please upload your CSV file.")
elif uploaded_file.type != "text/csv":
    st.warning("Please upload a CSV file.")
if zipcode_from == "":
    st.info("Please enter your ZIP code.")
elif not(zipcode_from.isdigit()) or len(zipcode_from) != 5:
    st.warning("Please enter a valid 5-digit origin ZIP code.")


if uploaded_file is not None and uploaded_file.type == "text/csv" and zipcode_from != "" and zipcode_from.isdigit() and len(zipcode_from) == 5:
    # Step 4: Read in sold order data
    df_order = pd.read_csv(uploaded_file)
    df_order['zipcode_to'] = df_order['Ship Zipcode'].astype(str).str[:5]

    # Step 5: Calculate distance bewtween origin zip code and destination
    dist = pgeocode.GeoDistance('us')
    df_order['distance_miles'] = df_order['zipcode_to'].apply(
        lambda dest: dist.query_postal_code(zipcode_from, dest) * 0.621371
    )

    # Assign distance categories
    conditions = [
        df_order['distance_miles'] <= 50,
        (df_order['distance_miles'] > 50) & (df_order['distance_miles'] <= 150),
        (df_order['distance_miles'] > 150) & (df_order['distance_miles'] <= 300),
        (df_order['distance_miles'] > 300) & (df_order['distance_miles'] <= 600),
        (df_order['distance_miles'] > 600) & (df_order['distance_miles'] <= 1000),
        (df_order['distance_miles'] > 1000) & (df_order['distance_miles'] <= 1400),
        (df_order['distance_miles'] > 1400) & (df_order['distance_miles'] <= 1800),
        df_order['distance_miles'] > 1800
    ]
    choices = list(range(1, 9))
    df_order['distance_cat'] = np.select(conditions, choices, default=np.nan).astype(int)
    # if foreign country, set it as 8
    df_order.loc[df_order['distance_miles'].isna(), 'distance_cat'] = 8
    df_order_new = df_order[(df_order["distance_cat"] >=1) & (df_order["distance_cat"] <=8) ]
    
    # Function to match USPS rate table
    def match_weight(distance_cat, shipping_cost):
        zone_col = f"Zone {distance_cat}"
        diffs = (df_rate[zone_col] - shipping_cost).abs()
        best_idx = diffs.idxmin()
        return df_rate.loc[best_idx, 'weight']

    df_order['shipping_cost'] = df_order['Order Shipping'] / 0.78
    df_order['matched_weight'] = df_order.apply(lambda r: match_weight(r['distance_cat'], r['shipping_cost']), axis=1)
    # 20% of weight is package weight
    df_order['package_weight'] = df_order['matched_weight'] * 0.2
    df_order['Sale Date'] = pd.to_datetime(df_order['Sale Date'])
    df_order = df_order.sort_values('Sale Date')


    st.divider()
    # Step 6: Visualization
    # Total estimated waste
    total_waste = df_order['package_weight'].sum()
    year = df_order['Sale Date'].dt.year.mode()[0]
    st.subheader("Total Estimated Packaging Waste (lbs)")
    st.markdown(f"<h2 style='color:green;'>{round(total_waste, 2)} lbs</h2>", unsafe_allow_html=True)

    st.divider()
    # Packaging Waste Trends
    st.subheader("Packaging Waste Trends")
    col1, spacer, col2 = st.columns([1, 0.2, 1])

    with col1: # monthly waste
        monthly = df_order.resample('M', on='Sale Date')['package_weight'].sum().reset_index()
        monthly['Month'] = monthly['Sale Date'].dt.strftime('%b')  # Format like "Jan"

        tab1, tab2 = st.tabs(["📊 Bar Chart", "📈 Line Graph"])

        with tab1: # bar chart
            fig1 = px.bar(monthly, x='Month', y='package_weight', title='Monthly Waste: Bar Chart')
            fig1.update_layout(xaxis_title='Month', yaxis_title='Waste Weight (lb)')
            st.plotly_chart(fig1)

        with tab2: # line graph
            fig2 = px.line(monthly, x='Month', y='package_weight', title='Monthly Waste: Line Graph')
            fig2.update_layout(xaxis_title='Month', yaxis_title='Waste Weight (lb)')
            st.plotly_chart(fig2)
    
    with col2: # cumulative line graph
        df_order['Cumulative Waste'] = df_order['package_weight'].cumsum()
        fig3 = px.line(df_order, x='Sale Date', y='Cumulative Waste', title='Cumulative Waste Over Time')
        fig3.update_layout(xaxis_title='Date', yaxis_title='Waste Weight (lb)')
        st.plotly_chart(fig3)


    st.divider()
    # State-level analysis
    st.subheader("Packaging Waste by State")
    us_sales = df_order[df_order['Ship Country'] == 'United States']
    state_sales = us_sales.groupby('Ship State')['package_weight'].sum().reset_index()
    # U.S. State Choropleth Map
    fig4 = px.choropleth(
        state_sales,
        locations='Ship State',
        locationmode='USA-states',
        color='package_weight',
        scope='usa',
        color_continuous_scale='Greens',
        labels={'package_weight': 'Waste Weight (lb)'},
        title='Waste by U.S. State'
    )
    fig4.update_layout(coloraxis_colorbar_title="Waste (lb)")
    st.plotly_chart(fig4)

    # Top 5 States Tables
    top_states = state_sales.sort_values(by='package_weight', ascending=False).head(5)
    top_states = top_states.rename(columns={
        'Ship State': 'State',
        'package_weight': 'Total Waste Weight (lb)'
    })
    top_states.insert(0, 'Rank', range(1, 6))

    st.table(top_states.reset_index(drop=True).style.hide(axis='index'))
