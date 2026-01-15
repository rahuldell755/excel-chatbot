import streamlit as st
import pandas as pd

# ---------------- LOAD DATA ----------------
df = pd.read_excel("install_base.xlsx")
df = df.fillna("").astype(str)
df.columns = df.columns.str.strip().str.lower()

st.set_page_config(page_title="Install Base Chatbot", layout="wide")
st.title("📊 Install Base Chatbot")

# ---------------- CHAT INPUT ----------------
query = st.chat_input(
    "Ask like: How many Flexcube clients in Africa? Consulting contact for Mashreq?"
)

# ---------------- HELPERS ----------------
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

    # -------- HOW MANY QUESTIONS --------
    if "how many" in q or "count" in q:
        temp_df = df.copy()

        if "africa" in q or "emea" in q:
            temp_df = temp_df[temp_df["regioncode"].str.contains("africa|emea", case=False)]
        if "europe" in q:
            temp_df = temp_df[temp_df["regioncode"].str.contains("europe", case=False)]
        if "flexcube" in q:
            temp_df = temp_df[temp_df["products used"].str.contains("flexcube", case=False)]
        if "oci" in q:
            temp_df = temp_df[temp_df["deployment type"].str.contains("oci", case=False)]
        if "aws" in q:
            temp_df = temp_df[temp_df["deployment type"].str.contains("aws", case=False)]

        response = f"I found **{len(temp_df)} client(s)** matching your criteria."
        result_df = temp_df

    # -------- CONSULTING CONTACT --------
    elif "consulting" in q:
        if client:
            val = df[df["client name"] == client]["consulting contact"].iloc[0]
            response = f"The consulting contact for **{client}** is **{val}**."

    # -------- GSUP CONTACT --------
    elif "gsup" in q or "support" in q:
        if client:
            val = df[df["client name"] == client]["gsup contact"].iloc[0]
            response = f"The GSUP contact for **{client}** is **{val}**."

    # -------- DEPLOYMENT --------
    elif "deployment" in q or "oci" in q or "aws" in q:
        if client:
            val = df[df["client name"] == client]["deployment type"].iloc[0]
            response = f"**{client}** is deployed on **{val}**."

    # -------- STATUS --------
    elif "status" in q or "live" in q:
        if client:
            curr = df[df["client name"] == client]["current status"].iloc[0]
            impl = df[df["client name"] == client]["impl status"].iloc[0]
            response = (
                f"**{client}** current status is **{curr}**, "
                f"implementation status is **{impl}**."
            )

    # -------- PRODUCTS --------
    elif "product" in q or "flexcube" in q:
        if client:
            val = df[df["client name"] == client]["products used"].iloc[0]
            response = f"**{client}** is using **{val}**."
        else:
            temp_df = df[df["products used"].str.contains("flexcube", case=False)]
            response = f"I found **{len(temp_df)} Flexcube client(s)**."
            result_df = temp_df

    # -------- FALLBACK SEARCH --------
    else:
        temp_df = df[df.apply(lambda r: q in " ".join(r).lower(), axis=1)]
        if not temp_df.empty:
            response = f"I found **{len(temp_df)} matching record(s)**."
            result_df = temp_df

    # ---------------- OUTPUT ----------------
    if response:
        st.chat_message("assistant").write(response)

    if not result_df.empty:
        st.dataframe(result_df)

    if not response and result_df.empty:
        st.chat_message("assistant").write(
            "I couldn’t find an exact match. Try client name, region, product, or deployment."
        )
