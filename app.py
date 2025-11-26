import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import plotly.graph_objects as go

# --- 1. CONFIGURATION AND CONNECTION ---

st.set_page_config(
    page_title="Superstore dbt Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

def create_engine_connection():
    """Creates and returns the SQLAlchemy engine."""
    try:

        engine = create_engine("postgresql+psycopg2://analytics:analytics@localhost/superstore")
        return engine
    except Exception as e:
        st.error(f"Error creating PostgreSQL connection engine: {e}")
        return None


@st.cache_data(ttl=600)
def fetch_data(_engine, query, **kwargs):
    """Fetches data from the database using a query."""
    try:
        df = pd.read_sql(query, con=_engine, **kwargs)
        return df
    except Exception as e:
        st.error(f"Database query error: {e}")
        st.stop()
        return pd.DataFrame()

# --- 2. MAIN APPLICATION LOGIC ---

st.title("📊 Superstore Analytics: Key Performance Indicators")
st.markdown("---")

engine = create_engine_connection()

if engine:
    
    # -----------------------------------
    # ➡️ QUERY DEFINITION BLOCK 
    # -----------------------------------

    # 1. Total Sales & Profits
    kpi_query = """
    SELECT 
        ROUND(SUM(sales),2) AS total_sales,
        ROUND(SUM(profit),2) AS total_profit
    FROM public_marts.fct__orders
    where is_returned_flag = false;
    """ 

    # 2. Return Rate
    return_query = """
    SELECT 
        COUNT(*) FILTER (WHERE is_returned_flag = TRUE) * 1.0 / COUNT(*) AS pct_returned
    FROM public_marts.fct__orders;
    """
    
    # 3. Monthly Sales Trend
    monthly_query = """
    SELECT
        DATE_TRUNC('month', order_date) AS order_month,
        ROUND(SUM(sales),2) AS monthly_sales
    FROM public_marts.fct__orders
    where is_returned_flag = false
    GROUP BY 1
    ORDER BY 1;
    """

    # 4. Top 4 Region by Profit (Bar Chart Data)
    state_query = """
    SELECT
        region,
        ROUND(SUM(profit),2) AS total_profit
    FROM public_marts.fct__orders
    where is_returned_flag = false
    GROUP BY 1
    ORDER BY total_profit DESC
    LIMIT 5;
    """

    # 5. Scatter Plot Data (Get all state metrics)
    profit_discount_query = """
    SELECT
        state,
        ROUND(SUM(profit), 2) AS total_profit,
        AVG(discount) AS average_discount,
        ROUND(SUM(sales), 2) AS total_sales
    FROM public_marts.fct__orders
    where is_returned_flag = false
    GROUP BY 1;
    """
    

    # 6. Best Seller Item (by count) - MaisVendido
    best_seller_query = """
    SELECT 
        sub_category AS item_group,
        COUNT(*) as MaisVendido
    FROM public_marts.fct__orders
    WHERE is_returned_flag = FALSE
    GROUP BY 1
    ORDER BY 2 DESC
    LIMIT 1;
    """

    # 7. Most Profitable Item (by total profit) - MaisLucrativo
    most_profitable_query = """
    SELECT 
        sub_category AS item_group,
        ROUND(SUM(profit),2) as MaisLucrativo
    FROM public_marts.fct__orders
    WHERE is_returned_flag = FALSE
    GROUP BY 1
    ORDER BY 2 DESC
    LIMIT 1;
    """

    # 8. Most Expensive Item (by max single sales price) - PrecoCaro
    most_expensive_query = """
    SELECT 
        sub_category AS item_group,
        ROUND(MAX(SALES),2) as PrecoCaro
    FROM public_marts.fct__orders
    WHERE is_returned_flag = FALSE
    GROUP BY 1
    ORDER BY 2 DESC
    LIMIT 1;
    """
    
    # 9. Most Returned Item - MaisDevolvido
    most_returned_query = """
    SELECT 
        sub_category AS item_group,
        COUNT(*) as MaisDevolvido
    FROM public_marts.fct__orders
    WHERE is_returned_flag = TRUE
    GROUP BY 1
    ORDER BY 2 DESC
    LIMIT 1;
    """

    # -----------------------------------
    # ➡️ DATA FETCHING BLOCK 
    # -----------------------------------
    
    # Fetch Top-Level KPIs
    kpi_df = fetch_data(engine, kpi_query)
    return_df = fetch_data(engine, return_query)

    # Fetch Item Metrics
    df_bs = fetch_data(engine, best_seller_query)
    df_mp = fetch_data(engine, most_profitable_query)
    df_me = fetch_data(engine, most_expensive_query)
    df_mr = fetch_data(engine, most_returned_query) 


    # --- 1. TOP-LEVEL KPI METRICS DISPLAY ---

    if not kpi_df.empty and not return_df.empty:
        col1, col2, col3 = st.columns(3)

        # Total Sales
        total_sales = kpi_df['total_sales'].iloc[0]
        col1.metric("Total Sales", f"${total_sales:,.0f}")

        # Total Profit
        total_profit = kpi_df['total_profit'].iloc[0]
        col2.metric("Total Profit", f"${total_profit:,.0f}", 
                     delta=f"{total_profit/total_sales*100:.1f}% Margin")

        # Return Rate
        pct_returned = return_df['pct_returned'].iloc[0]
        col3.metric("Return Rate", f"{pct_returned*100:.2f}%", 
                     delta=f"{pct_returned*100:.2f}% (Items Returned)", 
                     delta_color="inverse") 

    st.markdown("---")
    
    # --- 2. ITEM METRICS DISPLAY (UPDATED with Category-Subcategory grouping) ---

    st.header("🏆 Top Item Metrics")
    col_bs, col_mp, col_me, col_mr = st.columns(4)


    # 1. Best Seller Item
    if not df_bs.empty:
        # 'item_group' contains the CATEGORY - SUB_CATEGORY string
        item_group = df_bs['item_group'].iloc[0]
        # FIX: Access the column using the lowercase alias 'maisvendido'
        count = df_bs['maisvendido'].iloc[0]
        col_bs.metric(
            "🥇 Best Seller (Units)",
            item_group,
            f"{count} units sold"
        )

    # 2. Most Profitable Item
    if not df_mp.empty:
        item_group = df_mp['item_group'].iloc[0]
        # FIX: Access the column using the lowercase alias 'maislucrativo'
        profit = df_mp['maislucrativo'].iloc[0]
        col_mp.metric(
            "💰 Most Profitable Item",
            item_group,
            f"${profit:,.0f} total profit"
        )

    # 3. Most Expensive Item
    if not df_me.empty:
        item_group = df_me['item_group'].iloc[0]
        # FIX: Access the column using the lowercase alias 'precocaro'
        price = df_me['precocaro'].iloc[0]
        col_me.metric(
            "💎 Most Expensive Sale",
            item_group,
            f"${price:,.0f} max sale price"
        )
        
    # 4. Most Returned Item (Units returned in RED)
    if not df_mr.empty:
        item_group = df_mr['item_group'].iloc[0]
        # FIX: Access the column using the lowercase alias 'maisdevolvido'
        count = df_mr['maisdevolvido'].iloc[0]
        col_mr.metric(
            "💔 Most Returned Item",
            item_group,
            f"{count} units returned",
            delta_color="inverse" # Makes the delta (units returned) appear red
        )

    st.markdown("---")


    # --- VISUALIZATION QUERIES & PLOTS ---

    # 5. Monthly Sales Trend (Line Plot)
    st.header("📈 Monthly Sales Trend")
    df_monthly = fetch_data(engine, monthly_query, parse_dates=["order_month"])

    if not df_monthly.empty:
        fig_monthly = px.line(
            df_monthly, 
            x="order_month", 
            y="monthly_sales", 
            title="Monthly Sales Over Time",
            markers=True
        )
        fig_monthly.update_layout(xaxis_title="Order Month", yaxis_title="Total Sales")
        st.plotly_chart(fig_monthly, use_container_width=True)

    st.markdown("---")

    # 6. Top 5 Regions by Profit (Bar Chart)
    st.header("💰 Top 4 Regions by Profit")
    df_regions = fetch_data(engine, state_query)

    if not df_regions.empty:
        fig_regions = px.bar(
            df_regions, 
            x="region", 
            y="total_profit", 
            title="Top 4 Regions by Profit",
            color="total_profit",
            color_continuous_scale=px.colors.sequential.Plasma
        )
        fig_regions.update_layout(xaxis_title="Region", yaxis_title="Total Profit ($)")
        st.plotly_chart(fig_regions, use_container_width=True)

    # 7. SCATTER PLOT VISUALIZATION
    st.markdown("---")
    st.header("⚖️ Discount-Profit Correlation (Top/Bottom States)")
    
    df_state_metrics = fetch_data(engine, profit_discount_query)

    if not df_state_metrics.empty:
        
        # Get Top 2 and Bottom 2 states by profit using Pandas
        df_top = df_state_metrics.sort_values(by='total_profit', ascending=False).head(2)
        df_bottom = df_state_metrics.sort_values(by='total_profit', ascending=True).head(2)
        df_visual = pd.concat([df_top, df_bottom]).drop_duplicates(subset=['state']).reset_index(drop=True)

        # Create Plotly Scatter Plot
        fig_scatter = px.scatter(
            df_visual, 
            x="average_discount", 
            y="total_profit", 
            size="total_sales", 
            color="state", 
            text="state",
            title="Average Discount vs. Total Profit (Top/Bottom 2 States)",
            hover_data=['total_profit', 'average_discount', 'total_sales']
        )
        
        # Customizing the layout
        fig_scatter.update_traces(textposition='top center')
        fig_scatter.update_layout(
            xaxis_tickformat=".1%", 
            yaxis_tickformat="$,.0f",
            xaxis_title="Average Discount",
            yaxis_title="Total Profit",
            annotations=[
                dict(
                    xref='paper', yref='paper',
                    x=0.0, y=1.05,
                    showarrow=False,
                    text='Circle size represents Total Sales.',
                    font=dict(size=10)
                )
            ]
        )
        
        st.plotly_chart(fig_scatter, use_container_width=True)

    # Dispose the engine when done
    engine.dispose()