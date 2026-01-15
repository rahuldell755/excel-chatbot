import streamlit as st
import pandas as pd

# Load Excel
df = pd.read_excel("install_base.xlsx")

# Normalize dataframe (important!)
df = df.fillna("").astype(str)
df.columns = df.columns.str.strip().str.lower()

st.set_page_config(page_title="Install Base Chatbot", layout="wide")
st.title("📊 Install Base Chatbot")

query = st.chat_input("Ask about site, product, PM, go-live date...")

if query:
    st.chat_message("user").write(query)

    q = query.lower().strip()

    mask = df.apply(
        lambda row: any(q in cell.lower() for cell in row),
        axis=1
    )

    result = df[mask]

    if not result.empty:
        st.chat_message("assistant").write("Here’s what I found:")
        st.dataframe(result)
    else:
        st.chat_message("assistant").write("No matching records found.")
