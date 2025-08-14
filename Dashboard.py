import streamlit as st
import pandas as pd
import datetime
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go

# ========== CONFIGURATION ==========
st.set_page_config(layout="wide", page_title="Adidas Interactive Sales Dashboard")
st.markdown("""
    <style>
    div.block-container {padding-top:1rem; padding-bottom:1rem;}
    .stExpander > div:first-child {background-color: #f0f2f6; padding: 10px;}
    .stDownloadButton button {width: 100%;}
    .metric-box {
        background-color: #0c1e3c;
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 2px 2px 10px #00000033;
    }s
    .metric-label {
        font-size: 18px;
        font-weight: bold;
        color: #89CFF0;
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# ========== DATA LOADING ==========
@st.cache_data
def load_data():
    try:
        # Specify the engine for reading Excel files
        df = pd.read_excel("Adidas data.xlsx", engine="openpyxl")
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], errors='coerce')  # Handle invalid dates
        df['Month_Year'] = df['InvoiceDate'].dt.strftime("%b'%y")
        return df
    except FileNotFoundError:
        st.error("The file 'Adidas data.xlsx' was not found. Please ensure it is in the correct directory.")
        return pd.DataFrame()  # Return an empty DataFrame if the file is missing

df = load_data()

if df.empty:
    st.stop()  # Stop execution if the data could not be loaded

# ========== HEADER ==========
try:
    image = Image.open('logo.jpg')
    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        st.image(image, width=200)
    with col2:
        st.markdown("""
        <center><h1 style='font-weight:bold; padding:5px; border-radius:6px;'>
        Adidas Interactive Sales Dashboard</h1></center>""", 
        unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("The logo image 'logo.jpg' was not found. Please ensure it is in the correct directory.")

# ========== SUMMARY METRICS ==========
total_units = df['UnitsSold'].sum()
total_sales = df['TotalSales'].sum()
total_profit = df['OperatingProfit'].sum()
sales_count = df.shape[0]

metrics = st.columns(4)
metrics[0].markdown(f"""
    <div class='metric-box'>
        <div class='metric-label'>Total Units Sold</div>
        <div class='metric-value'>{total_units/1000:.2f}K</div>
    </div>""", unsafe_allow_html=True)

metrics[1].markdown(f"""
    <div class='metric-box'>
        <div class='metric-label'>Total Sales</div>
        <div class='metric-value'>${total_sales/1000000:.2f}M</div>
    </div>""", unsafe_allow_html=True)

metrics[2].markdown(f"""
    <div class='metric-box'>
        <div class='metric-label'>Total Profit</div>
        <div class='metric-value'>${total_profit/1000000:.2f}M</div>
    </div>""", unsafe_allow_html=True)

metrics[3].markdown(f"""
    <div class='metric-box'>
        <div class='metric-label'>Transactions</div>
        <div class='metric-value'>{sales_count:,}</div>
    </div>""", unsafe_allow_html=True)

# ========== DASHBOARD TABS ==========
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Sales Overview", 
    "🗺 Geography", 
    "👟 Products", 
    "📥 Data", 
    "📈 Advanced"
])

with tab1:
    st.header("Sales Performance Overview")
    
    # Row 1: Retailer Sales and Time Series
    col1, col2 = st.columns([0.5, 0.5])
    
    with col1:
        retailer_sales = df.groupby("Retailer")["TotalSales"].sum().reset_index()
        fig = px.bar(retailer_sales, x="Retailer", y="TotalSales", 
                     title="Total Sales by Retailer",
                     labels={"TotalSales": "Sales ($)"},
                     color="Retailer", template="gridon")
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("View Retailer Data"):
            st.dataframe(retailer_sales.sort_values("TotalSales", ascending=False))
    
    with col2:
        time_series = df.groupby("Month_Year")["TotalSales"].sum().reset_index()
        fig = px.line(time_series, x="Month_Year", y="TotalSales", 
                      title="Monthly Sales Trend",
                      markers=True, template="gridon")
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("View Time Series Data"):
            st.dataframe(time_series)
    
    # Row 2: Combined State Analysis
    st.subheader("State-wise Performance")
    state_data = df.groupby("State")[["TotalSales", "UnitsSold"]].sum().reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=state_data["State"],
        y=state_data["TotalSales"],
        name="Total Sales"
    ))
    fig.add_trace(go.Scatter(
        x=state_data["State"],
        y=state_data["UnitsSold"],
        name="Units Sold",
        yaxis="y2"
    ))
    fig.update_layout(
        title="Sales vs Units Sold by State",
        yaxis=dict(title="Total Sales ($)"),
        yaxis2=dict(title="Units Sold", overlaying="y", side="right"),
        template="gridon",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("Geographical Analysis")
    
    # Row 1: Treemap
    st.subheader("Sales Distribution by Region/City")
    geo_data = df.groupby(["Region", "City"])["TotalSales"].sum().reset_index()
    fig = px.treemap(geo_data, path=["Region", "City"], values="TotalSales",
                     color="TotalSales", color_continuous_scale="Blues",
                     hover_data=["TotalSales"])
    st.plotly_chart(fig, use_container_width=True)
    
    # Row 2: Region Analysis
    col1, col2 = st.columns([0.6, 0.4])
    
    with col1:
        region_sales = df.groupby("Region")["TotalSales"].sum().reset_index()
        fig = px.bar(region_sales, x="Region", y="TotalSales",
                     title="Sales by Region", color="Region",
                     template="gridon")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.pie(region_sales, names="Region", values="TotalSales",
                     title="Sales Distribution", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("Product Performance Analysis")
    
    # Row 1: Product Sales
    product_sales = df.groupby("Product")[["TotalSales", "UnitsSold", "OperatingProfit"]].sum().reset_index()
    
    col1, col2 = st.columns([0.6, 0.4])
    
    with col1:
        fig = px.bar(product_sales, x="Product", y="TotalSales",
                     title="Total Sales by Product", color="Product",
                     template="gridon")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.pie(product_sales, names="Product", values="UnitsSold",
                     title="Units Sold by Product", hole=0.3)
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 2: Product Profit Analysis
    st.subheader("Profit Analysis")
    
    fig = px.scatter(product_sales, x="UnitsSold", y="OperatingProfit",
                     size="TotalSales", color="Product",
                     title="Profit vs Units Sold",
                     hover_name="Product", template="gridon")
    st.plotly_chart(fig, use_container_width=True)
    
    # Row 3: Distribution Analysis
    st.subheader("Sales Distribution by Product")
    fig = px.box(df, x="Product", y="TotalSales",
                 title="Sales Distribution", color="Product",
                 template="gridon")
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.header("Data Explorer")
    
    with st.expander("🔍 View Full Dataset", expanded=True):
        st.dataframe(df, height=400)
    
    st.subheader("Data Export")
    
    export_options = st.columns(3)
    
    with export_options[0]:
        st.download_button(
            "Download Retailer Data",
            data=df.groupby("Retailer")["TotalSales"].sum().reset_index().to_csv(index=False).encode("utf-8"),
            file_name="retailer_sales.csv",
            mime="text/csv"
        )
    
    with export_options[1]:
        st.download_button(
            "Download Product Data",
            data=df.groupby("Product")[["TotalSales", "UnitsSold"]].sum().reset_index().to_csv(index=False).encode("utf-8"),
            file_name="product_performance.csv",
            mime="text/csv"
        )
    
    with export_options[2]:
        st.download_button(
            "Download Full Dataset",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="adidas_full_data.csv",
            mime="text/csv"
        )

with tab5:
    st.header("Advanced Profit Analytics")
    
    # Waterfall Chart
    st.subheader("Profit Waterfall Analysis")
    costs = total_sales - total_profit
    waterfall_data = pd.DataFrame({
        "Category": ["Revenue", "Costs", "Profit"],
        "Amount": [total_sales, -costs, total_profit]
    })
    fig = go.Figure(go.Waterfall(
        x=waterfall_data["Category"],
        y=waterfall_data["Amount"],
        textposition="outside",
        connector={"line":{"color":"rgb(63, 63, 63)"}},
    ))
    fig.update_layout(
        title="Profit Breakdown",
        yaxis_title="Amount ($)",
        template="gridon"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Sunburst Chart
    st.subheader("Profit Hierarchy")
    sunburst_data = df.groupby(["Region", "State", "Retailer"])["OperatingProfit"].sum().reset_index()
    fig = px.sunburst(
        sunburst_data,
        path=["Region", "State", "Retailer"],
        values="OperatingProfit",
        color="OperatingProfit",
        title="Profit Distribution by Region > State > Retailer"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Funnel Chart
    st.subheader("Profit Funnel by Region")
    funnel_data = df.groupby("Region")["OperatingProfit"].sum().reset_index().sort_values("OperatingProfit")
    fig = px.funnel(funnel_data, x="OperatingProfit", y="Region",
                   title="Profit Concentration")
    st.plotly_chart(fig, use_container_width=True)
    
    # Faceted Line Chart
    st.subheader("Monthly Profit Trends")
    line_data = df.groupby(["Month_Year", "Region"])["OperatingProfit"].sum().reset_index()
    fig = px.line(line_data, x="Month_Year", y="OperatingProfit",
                 color="Region", facet_col="Region", facet_col_wrap=3,
                 title="Monthly Profit by Region",
                 template="gridon")
    st.plotly_chart(fig, use_container_width=True)
    
    # Data Downloads
    with st.expander("📥 Download Advanced Analytics Data"):
        cols = st.columns(4)
        with cols[0]:
            st.download_button(
                "Waterfall Data",
                data=waterfall_data.to_csv(index=False).encode("utf-8"),
                file_name="profit_waterfall.csv"
            )
        with cols[1]:
            st.download_button(
                "Sunburst Data",
                data=sunburst_data.to_csv(index=False).encode("utf-8"),
                file_name="profit_hierarchy.csv"
            )
        with cols[2]:
            st.download_button(
                "Funnel Data",
                data=funnel_data.to_csv(index=False).encode("utf-8"),
                file_name="profit_funnel.csv"
            )
        with cols[3]:
            st.download_button(
                "Faceted Line Data",
                data=line_data.to_csv(index=False).encode("utf-8"),
                file_name="monthly_profit_trends.csv"
            )

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; padding: 10px;">
        <p>Adidas Sales Dashboard • Last Updated: {}</p>
    </div>
""".format(datetime.datetime.now().strftime("%B %d, %Y")), unsafe_allow_html=True)