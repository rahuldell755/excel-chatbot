import streamlit as st
import pandas as pd
import os

# ---------------- LOAD DATA ----------------
df = pd.read_excel("install_base.xlsx")
df = df.fillna("").astype(str)
df.columns = df.columns.str.strip().str.lower()

# ---------------- PAGE SETUP ----------------
st.set_page_config(page_title="Install Base Chatbot", layout="wide")
st.title("📊 Install Base Intelligence Bot")

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("🔍 Filters")

region = st.sidebar.selectbox(
    "Region",
    ["All"] + sorted(df["regioncode"].unique())
)

country = st.sidebar.selectbox(
    "Country",
    ["All"] + sorted(df["country"].unique())
)

deployment = st.sidebar.selectbox(
    "Deployment Type",
    ["All"] + sorted(df["deployment type"].unique())
)

product = st.sidebar.selectbox(
    "Product",
    ["All"] + sorted(
        {p.strip() for x in df["products used"] for p in x.split(",")}
    )
)

# Apply filters
filtered_df = df.copy()

if region != "All":
    filtered_df = filtered_df[filtered_df["regioncode"] == region]

if country != "All":
    filtered_df = filtered_df[filtered_df["country"] == country]

if deployment != "All":
    filtered_df = filtered_df[filtered_df["deployment type"] == deployment]

if product != "All":
    filtered_df = filtered_df[
        filtered_df["products used"].str.contains(product, case=False)
    ]

# ---------------- CHAT INPUT ----------------
query = st.chat_input(
    "Ask: How many Flexcube clients in Africa? Consulting contact for Mashreq?"
)

# ---------------- HELPER ----------------
def find_client(text):
    for c in df["client name"].unique():
        if c.lower() in text:
            return c
    return None

# ---------------- CHAT LOGIC ----------------
if query:
    st.chat_message("user").write(query)
    q = query.lower()

    response = ""
    result_df = pd.DataFrame()
    client = find_client(q)

    # ---- HOW MANY QUESTIONS ----
    if "how many" in q or "count" in q:
        count = len(filtered_df)
        response = f"I found **{count} client(s)** matching your criteria."
        result_df = filtered_df

    # ---- CONSULTING CONTACT
