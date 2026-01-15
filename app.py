import streamlit as st
import pandas as pd

df = pd.read_excel("data/install_base.xlsx")

st.set_page_config(page_title="Install Base Chatbot", layout="wide")
st.title("📊 Install Base Chatbot")

query = st.chat_input("Ask about site, product, PM, go-live date...")

if query:
    st.chat_message("user").write(query)

    mask = df.apply(
        lambda row: row.astype(str).str.contains(query, case=False).any(),
        axis=1
    )

    result = df[mask]

    if not result.empty:
        st.chat_message("assistant").write("Here’s what I found:")
        st.dataframe(result)
    else:
        st.chat_message("assistant").write("No matching records found.")
