import streamlit as st
import pandas as pd

# Load Excel
df = pd.read_excel("install_base.xlsx")

# Normalize data
df = df.fillna("").astype(str)
df.columns = df.columns.str.strip().str.lower()

st.set_page_config(page_title="Install Base Chatbot", layout="wide")
st.title("📊 Install Base Chatbot")

query = st.chat_input(
    "Ask like: Consulting contact for Mashreq, Products used by Bandhan Bank, Africa Flexcube clients..."
)

if query:
    st.chat_message("user").write(query)
    q = query.lower().strip()

    response = ""
    result_df = pd.DataFrame()

    # Helper: find client name in query
    def find_client():
        for c in df["client name"].unique():
            if c.lower() in q:
                return c
        return None

    client = find_client()

    # --- Intent: Consulting Contact ---
    if "consulting" in q or "consultant" in q:
        if client:
            contact = df[df["client name"] == client]["consulting contact"].iloc[0]
            response = f"The consulting contact for **{client}** is **{contact}**."

    # --- Intent: GSUP Contact ---
    elif "gsup" in q or "support" in q:
        if client:
            contact = df[df["client name"] == client]["gsup contact"].iloc[0]
            response = f"The GSUP contact for **{client}** is **{contact}**."

    # --- Intent: Products Used ---
    elif "product" in q or "flexcube" in q:
        if client:
            products = df[df["client name"] == client]["products used"].iloc[0]
            response = f"**{client}** is using **{products}**."
        else:
            result_df = df[df["products used"].str.lower().str.contains(q)]
            if not result_df.empty:
                response = f"I found **{len(result_df)} client(s)** using this product."

    # --- Intent: Deployment Type ---
    elif "deployment" in q or "cloud" in q or "oci" in q or "aws" in q:
        if client:
            deploy = df[df["client name"] == client]["deployment type"].iloc[0]
            response = f"**{client}** is deployed on **{deploy}**."

    # --- Intent: Status ---
    elif "status" in q or "live" in q:
        if client:
            curr = df[df["client name"] == client]["current status"].iloc[0]
            impl = df[df["client name"] == client]["impl status"].iloc[0]
            response = (
                f"**{client}** current status is **{curr}**, "
                f"and implementation status is **{impl}**."
            )

    # --- Intent: Implementation Date ---
    elif "impl date" in q or "implementation date" in q or "go live" in q:
        if client:
            date = df[df["client name"] == client]["impl date"].iloc[0]
            response = f"**{client}** implementation date is **{date}**."

    # --- Intent: Region / Country ---
    elif "region" in q or "country" in q or "africa" in q or "europe" in q:
        result_df = df[df.apply(lambda r: q in " ".join(r).lower(), axis=1)]
        if not result_df.empty:
            response = f"I found **{len(result_df)} matching client(s)**."

    # --- Fallback Search ---
    else:
        result_df = df[df.apply(lambda r: q in " ".join(r).lower(), axis=1)]
        if not result_df.empty:
            response = f"I found **{len(result_df)} matching record(s)**."

    # --- Output ---
    if response:
        st.chat_message("assistant").write(response)

    if not result_df.empty:
        st.dataframe(result_df)

    if not response and result_df.empty:
        st.chat_message("assistant").write(
            "I couldn’t find an exact match. Try using client name, product, region, or contact."
        )
