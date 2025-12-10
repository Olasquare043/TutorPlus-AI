import streamlit as st
import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(layout="wide")
st.title("TutorPlus hmmm Databasert Viewer")

# database connection details
DATABASE_URL = os.getenv("DATABASE_URL")

@st.cache_data(ttl=60) # cache data for 60 seconds
def get_users_data():
    conn = None
    df = pd.DataFrame()
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT * FROM users;")
        
        # fetch column names
        column_names = [desc[0] for desc in cur.description]
        
        # fetch data
        data = cur.fetchall()
        df = pd.DataFrame(data, columns=column_names)
        
        cur.close()
    except Exception as e:
        st.error(f"Error connecting to database or fetching data: {e}")
    finally:
        if conn:
            conn.close()
    return df

st.header("Users Table")

# button to refresh data
if st.button("Refresh Data"):
    st.cache_data.clear() # clear cache to get fresh data
    st.success("Data refreshed!")

users_df = get_users_data()

if not users_df.empty:
    st.dataframe(users_df)
else:
    st.info("No data found in the 'users' table, or connection failed.")

# to run it
# streamlit run TutorPlus_AI/backend/app.py