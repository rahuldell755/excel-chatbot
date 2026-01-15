import streamlit as st
import pandas as pd

# ================= LOAD DATA =================
df = pd.read_excel("install_base.xlsx")
df = df.fillna("").astype(str)
df.columns = df.columns.str.strip().str.lower()

st.set_page_config(page_title="Install Base Chatbot", layout="wide")
st.title("📊 Install Base Chatbot")

# ================= SESSION STATE =================
if "pending_client" not in st.session_state:
    st.session_state.pending_client = None
if "pending_intent" not in st.session_state:
    st.session_state.pending_intent = None

# ================= HELPERS =================
def find_client(text):
    for c in df["client name"].unique():
        if c.lower() in text:
            return c
    return None

def find_country(text):
    for c in df["country"].unique():
        if c.lower() in text:
            return c
    return None

def apply_filters(text, base_df):
    temp = base_df.copy()

    if "emea" in text:
        temp = temp[temp["regioncode"].str.contains("emea", case=False)]
    if "africa" in text:
        temp = temp[temp["regioncode"].str.contains("africa", case=False)]
    if "europe" in text:
        temp = temp[temp["regioncode"].str.contains("europe", case=False)]
    if "flexcube" in text:
        temp = temp[temp["products used"].str.contains("flexcube", case=False)]
    if "oci" in text:
        temp = temp[temp["deployment type"].str.contains("oci", case=False)]
    if "aws" in text:
        temp = temp[temp["deployment type"].str.contains("aws", case=False)]

    return temp

# ================= CHAT INPUT =================
query = st.chat_input(
    "Ask: How many customers in EMEA? Consulting contact for ABC Bank?"
)

# ================= CHAT LOGIC =================
if query:
    st.chat_message("user").write(query)
    q = query.lower().strip()

    response = ""
    result_df = pd.DataFrame()

    client = find_client(q)
    country = find_country(q)

    # ---------- FOLLOW-UP COUNTRY HANDLING ----------
    if st.session_state.pending_client and country:
        client = st.session_state.pending_client
        intent = st.session_state.pending_intent

        row = df[
            (df["client name"] == client) &
            (df["country"].str.lower() == country.lower())
        ]

        if not row.empty:
            if intent == "consulting":
                val = row["consulting contact"].iloc[0]
                response = f"The consulting contact for **{client} ({country})** is **{val}**."
            elif intent == "gsup":
                val = row["gsup contact"].iloc[0]
                response = f"The GSUP contact for **{client} ({country})** is **{val}**."

        st.session_state.pending_client = None
        st.session_state.pending_intent = None

    # ---------- HOW MANY / COUNT ----------
    elif "how many" in q or "count" in q:
        temp_df = apply_filters(q, df)

        if "customer" in q:
            count = temp_df["client name"].nunique()
            response = f"There are **{count} unique customer(s)** matching your criteria."
            result_df = temp_df[["client name"]].drop_duplicates()

        else:  # client / site
            response = f"I found **{len(temp_df)} client site(s)** matching your criteria."
            result_df = temp_df

    # ---------- CONSULTING CONTACT ----------
    elif "consulting" in q and client:
        rows = df[df["client name"] == client]
        countries = rows["country"].unique()

        if len(countries) > 1 and not country:
            st.session_state.pending_client = client
            st.session_state.pending_intent = "consulting"
            response = (
                f"**{client}** exists in multiple countries: "
                f"{', '.join(countries)}. Please specify the country."
            )
        else:
            if not country:
                country = countries[0]
            val = rows[rows["country"] == country]["consulting contact"].iloc[0]
            response = f"The consulting contact for **{client} ({country})** is **{val}**."

    # ---------- GSUP CONTACT ----------
    elif ("gsup" in q or "support" in q) and client:
        rows = df[df["client name"] == client]
        countries = rows["country"].unique()

        if len(countries) > 1 and not country:
            st.session_state.pending_client = client
            st.session_state.pending_intent = "gsup"
            response = (
                f"**{client}** exists in multiple countries: "
                f"{', '.join(countries)}. Please specify the country."
            )
        else:
            if not country:
                country = countries[0]
            val = rows[rows["country"] == country]["gsup contact"].iloc[0]
            response = f"The GSUP contact for **{client} ({country})** is **{val}**."

    # ---------- STATUS ----------
    elif "status" in q and client:
        rows = df[df["client name"] == client]
        countries = rows["country"].unique()

        if len(countries) > 1 and not country:
            st.session_state.pending_client = client
            st.session_state.pending_intent = "status"
            response = (
                f"**{client}** exists in multiple countries: "
                f"{', '.join(countries)}. Please specify the country."
            )
        else:
            if not country:
                country = countries[0]
            row = rows[rows["country"] == country]
            response = (
                f"**{client} ({country})** current status is "
                f"**{row['current status'].iloc[0]}**, "
                f"implementation status is **{row['impl status'].iloc[0]}**."
            )

    # ---------- FALLBACK SEARCH ----------
    else:
        temp_df = apply_filters(q, df)
        if not temp_df.empty:
            response = (
                f"I found **{temp_df['client name'].nunique()} unique customer(s)** "
                f"and **{len(temp_df)} client site(s)**."
            )
            result_df = temp_df

    # ================= OUTPUT =================
    if response:
        st.chat_message("assistant").write(response)

    if not result_df.empty:
        st.dataframe(result_df)

    if not response:
        st.chat_message("assistant").write(
            "I couldn’t find an exact match. Try customer, client, country, region, or product."
        )
