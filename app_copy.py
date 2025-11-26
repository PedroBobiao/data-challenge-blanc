import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px


def create_engine_connection():
    try:
      
        engine = create_engine("postgresql+psycopg2://analytics:analytics@localhost/superstore")
        print("PostgreSQL connection engine created")
        return engine
    except Exception as e:
        print("Error creating engine:", e)
        return None


engine = create_engine_connection()
if engine:
    st.success("PostgreSQL connection engine created successfully")

    query = "SELECT * FROM public_marts.fct__orders;"  
    df = pd.read_sql(query, con=engine, parse_dates=["order_date", "ship_date"])
    st.write(df)

  
    df_grouped = df.groupby(df.order_date.dt.to_period("Y")).agg({"sales": "sum", "profit": "sum"}).reset_index()
    df_grouped["order_year"] = df_grouped["order_date"].dt.year 
    fig = px.bar(df_grouped, x="order_year", y="sales", title="Sales by Year")
    st.plotly_chart(fig)

   
    engine.dispose()
