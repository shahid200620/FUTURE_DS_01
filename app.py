import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Ultra Pro Dashboard", layout="wide")

# ===== STYLE =====
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e293b, #020617);
    color: white;
}
.filter-box {
    background-color: #111827;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #1f2937;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# ===== LOAD DATA =====
df = pd.read_csv("data/Sample - Superstore.csv", encoding='latin1')
df["Order Date"] = pd.to_datetime(df["Order Date"])

# ===== NAVIGATION =====
st.sidebar.title("📊 Navigation")
page = st.sidebar.radio("Go to", [
    "Overview",
    "Revenue Intelligence",
    "Product Analytics",
    "Category Deep Dive",
    "Regional Insights",
    "Business Insights"
])

# ===== HEADER =====
st.markdown("<h1 style='text-align:center; color:#38bdf8;'>🚀 Business Dashboard</h1>", unsafe_allow_html=True)

# ===== FILTERS (NOT FOR INSIGHTS PAGE) =====
if page != "Business Insights":

    st.markdown("<div class='filter-box'>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    region_filter = col1.multiselect("Region", df["Region"].unique(), df["Region"].unique())
    category_filter = col2.multiselect("Category", df["Category"].unique(), df["Category"].unique())
    subcat_filter = col3.multiselect("Sub-Category", df["Sub-Category"].unique(), df["Sub-Category"].unique())
    date_range = col4.date_input("Date Range", [df["Order Date"].min(), df["Order Date"].max()])

    st.markdown("</div>", unsafe_allow_html=True)

    df = df[
        (df["Region"].isin(region_filter)) &
        (df["Category"].isin(category_filter)) &
        (df["Sub-Category"].isin(subcat_filter)) &
        (df["Order Date"] >= pd.to_datetime(date_range[0])) &
        (df["Order Date"] <= pd.to_datetime(date_range[1]))
    ]

# ================= OVERVIEW =================
if page == "Overview":

    sales = df["Sales"].sum()
    profit = df["Profit"].sum()
    orders = df["Order ID"].nunique()
    margin = (profit / sales) * 100

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Revenue", f"{sales:,.0f}")
    c2.metric("Profit", f"{profit:,.0f}")
    c3.metric("Margin %", f"{margin:.2f}")
    c4.metric("Orders", orders)

    col1, col2 = st.columns(2)

    cat = df.groupby("Category")["Sales"].sum().reset_index()
    col1.plotly_chart(px.pie(cat, names="Category", values="Sales"), use_container_width=True)

    region = df.groupby("Region")["Sales"].sum().reset_index()
    col2.plotly_chart(px.bar(region, x="Region", y="Sales", color="Region"), use_container_width=True)

    col3, col4 = st.columns(2)

    col3.plotly_chart(px.bar(cat, x="Category", y="Sales", color="Category"), use_container_width=True)

    orders_df = df.groupby("Region")["Order ID"].count().reset_index()
    col4.plotly_chart(px.pie(orders_df, names="Region", values="Order ID"), use_container_width=True)

    st.dataframe(df.head(10))

# ================= REVENUE =================
elif page == "Revenue Intelligence":

    df["Year"] = df["Order Date"].dt.year
    df["Month"] = df["Order Date"].dt.to_period("M").astype(str)

    col1, col2 = st.columns(2)

    monthly = df.groupby("Month")["Sales"].sum().reset_index()
    col1.plotly_chart(px.line(monthly, x="Month", y="Sales", markers=True), use_container_width=True)

    yearly = df.groupby("Year")[["Sales", "Profit"]].sum().reset_index()
    col2.plotly_chart(px.bar(yearly, x="Year", y=["Sales", "Profit"], barmode="group"), use_container_width=True)

    col3, col4 = st.columns(2)

    col3.plotly_chart(px.line(yearly, x="Year", y="Profit"), use_container_width=True)
    col4.plotly_chart(px.scatter(df, x="Sales", y="Profit", color="Category"), use_container_width=True)

    st.dataframe(yearly)

# ================= PRODUCTS =================
elif page == "Product Analytics":

    col1, col2 = st.columns(2)

    top_sales = df.groupby("Product Name")["Sales"].sum().reset_index().sort_values(by="Sales", ascending=False).head(10)
    col1.plotly_chart(px.bar(top_sales, x="Sales", y="Product Name", orientation="h"), use_container_width=True)

    top_profit = df.groupby("Product Name")["Profit"].sum().reset_index().sort_values(by="Profit", ascending=False).head(10)
    col2.plotly_chart(px.bar(top_profit, x="Profit", y="Product Name", orientation="h"), use_container_width=True)

    col3, col4 = st.columns(2)

    quantity = df.groupby("Product Name")["Quantity"].sum().reset_index().sort_values(by="Quantity", ascending=False).head(10)
    col3.plotly_chart(px.bar(quantity, x="Quantity", y="Product Name", orientation="h"), use_container_width=True)

    # BIGGER PIE CHART
    fig_big_pie = px.pie(top_sales, names="Product Name", values="Sales")
    fig_big_pie.update_layout(height=500)
    col4.plotly_chart(fig_big_pie, use_container_width=True)

    st.dataframe(top_sales)

# ================= CATEGORY =================
elif page == "Category Deep Dive":

    col1, col2 = st.columns(2)

    cat = df.groupby("Category")[["Sales", "Profit"]].sum().reset_index()
    col1.plotly_chart(px.bar(cat, x="Category", y=["Sales", "Profit"], barmode="group"), use_container_width=True)

    cat["Margin %"] = (cat["Profit"] / cat["Sales"]) * 100
    col2.plotly_chart(px.bar(cat, x="Category", y="Margin %", color="Category"), use_container_width=True)

    col3, col4 = st.columns(2)

    col3.plotly_chart(px.pie(cat, names="Category", values="Sales"), use_container_width=True)

    sub = df.groupby("Sub-Category")["Sales"].sum().reset_index()
    col4.plotly_chart(px.bar(sub, x="Sub-Category", y="Sales"), use_container_width=True)

    st.dataframe(cat)

# ================= REGION =================
elif page == "Regional Insights":

    col1, col2 = st.columns(2)

    region_sales = df.groupby("Region")["Sales"].sum().reset_index()
    col1.plotly_chart(px.bar(region_sales, x="Region", y="Sales", color="Region"), use_container_width=True)

    region_profit = df.groupby("Region")["Profit"].sum().reset_index()
    col2.plotly_chart(px.bar(region_profit, x="Region", y="Profit", color="Region"), use_container_width=True)

    col3, col4 = st.columns(2)

    df["Discount Bin"] = pd.cut(df["Discount"], bins=5).astype(str)
    discount = df.groupby("Discount Bin")["Profit"].mean().reset_index()
    col3.plotly_chart(px.bar(discount, x="Discount Bin", y="Profit"), use_container_width=True)

    orders = df.groupby("Region")["Order ID"].count().reset_index()
    col4.plotly_chart(px.pie(orders, names="Region", values="Order ID"), use_container_width=True)

    st.dataframe(region_sales)

# ================= INSIGHTS =================
elif page == "Business Insights":

    st.markdown("""
    ### 🔍 Insights
    - Revenue is increasing over time  
    - Top products dominate sales  
    - Discounts reduce profit  
    - Technology category leads  

    ### 🚀 Recommendations
    - Focus on best products  
    - Reduce discounts  
    - Expand strong regions  
    - Improve low-margin areas  
    """)